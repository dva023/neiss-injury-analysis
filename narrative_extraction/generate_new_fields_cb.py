import csv
import json
import math
import threading
import time
from datetime import datetime
from pathlib import Path
from queue import Queue
from typing import Dict, List, Set

from constants import (
    MODEL_CLAUDE,
    MODEL_GEMINI,
    MODEL_GPT_4,
    MODEL_GPT_4_MINI,
    MODEL_LOCAL,
    NEW_COLUMN_FIELDS,
    PROMPT_EXTRACT_FIELDS,
)
from gen_model import send_message

# Configuration
NUM_THREADS = 8
REQUESTS_PER_THREAD = 150  # requests per minute per thread
WINDOW_SIZE = 60  # seconds
CHECKPOINT_INTERVAL = 10  # Save checkpoint every N items


class ThreadRateLimiter:
    def __init__(self, requests_per_minute: int, window_size: int):
        self.window_size = window_size
        self.requests_per_minute = requests_per_minute
        self.interval = window_size / requests_per_minute  # seconds per request
        self.last_request_time = 0
        self.request_count = 0
        self.start_time = time.time()
        self.lock = threading.Lock()

    def wait_if_needed(self):
        with self.lock:
            current_time = time.time()

            # If we're starting a new minute window
            if current_time - self.start_time >= self.window_size:
                self.start_time = current_time
                self.request_count = 0

            # If we've hit our rate limit for this window
            if self.request_count >= self.requests_per_minute:
                sleep_time = self.window_size - (current_time - self.start_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                self.start_time = time.time()
                self.request_count = 0

            # Ensure minimum interval between requests
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.interval:
                time.sleep(self.interval - time_since_last)

            self.last_request_time = time.time()
            self.request_count += 1


class ThreadCheckpoint:
    def __init__(self, checkpoint_dir: str, thread_id: int, model_name: str):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.thread_id = thread_id
        self.model_name = model_name
        self.processed_cases = set()
        self.results = {}

        # Create thread-specific checkpoint file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.checkpoint_file = (
            self.checkpoint_dir
            / f"checkpoint_thread_{thread_id}_{model_name}_{timestamp}.json"
        )
        self.load_checkpoint()

    def load_checkpoint(self):
        # Find the latest checkpoint for this thread
        checkpoints = list(
            self.checkpoint_dir.glob(
                f"checkpoint_thread_{self.thread_id}_{self.model_name}_*.json"
            )
        )
        if checkpoints:
            latest_checkpoint = max(checkpoints, key=lambda x: x.stat().st_mtime)
            print(f"Thread {self.thread_id}: Loading checkpoint: {latest_checkpoint}")
            try:
                with open(latest_checkpoint, "r") as f:
                    checkpoint_data = json.load(f)
                    self.processed_cases = set(checkpoint_data["processed_cases"])
                    self.results = checkpoint_data["results"]
                print(
                    f"Thread {self.thread_id}: Loaded {len(self.processed_cases)} processed cases"
                )
            except Exception as e:
                print(f"Thread {self.thread_id}: Error loading checkpoint: {e}")
                self.processed_cases = set()
                self.results = {}

    def save_checkpoint(self):
        try:
            with open(self.checkpoint_file, "w") as f:
                checkpoint_data = {
                    "processed_cases": list(self.processed_cases),
                    "results": self.results,
                }
                json.dump(checkpoint_data, f)
            print(
                f"Thread {self.thread_id}: Saved {len(self.processed_cases)} cases to checkpoint"
            )
        except Exception as e:
            print(f"Thread {self.thread_id}: Error saving checkpoint: {e}")

    def is_processed(self, case_number: str) -> bool:
        return case_number in self.processed_cases

    def mark_processed(self, case_number: str, result: Dict):
        self.processed_cases.add(case_number)
        self.results[case_number] = result


class CheckpointManager:
    def __init__(self, checkpoint_dir: str, num_threads: int, model_name: str):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.thread_checkpoints = [
            ThreadCheckpoint(checkpoint_dir, i, model_name) for i in range(num_threads)
        ]

    def get_all_processed_cases(self) -> Set[str]:
        processed = set()
        for checkpoint in self.thread_checkpoints:
            processed.update(checkpoint.processed_cases)
        return processed

    def get_all_results(self) -> List[Dict]:
        all_results = []
        for checkpoint in self.thread_checkpoints:
            all_results.extend(checkpoint.results.values())
        return all_results


def generate_fields(
    data: Dict, model_name: str, rate_limiter: ThreadRateLimiter
) -> Dict:
    rate_limiter.wait_if_needed()
    message = PROMPT_EXTRACT_FIELDS.format(columns=NEW_COLUMN_FIELDS, data=data)
    response = send_message(model_name, message)
    return {**data, **response}


def worker_thread(
    thread_id: int, work_queue: Queue, model_name: str, checkpoint: ThreadCheckpoint
):
    rate_limiter = ThreadRateLimiter(REQUESTS_PER_THREAD, WINDOW_SIZE)
    processed_count = 0
    checkpoint_count = 0
    start_time = time.time()

    while True:
        try:
            item = work_queue.get_nowait()
        except Queue.Empty:
            checkpoint.save_checkpoint()
            break

        case_number = item.get("CPSC_Case_Number")
        if not case_number:
            print(f"Thread {thread_id}: Warning: Missing CPSC_Case_Number in item")
            work_queue.task_done()
            continue

        if checkpoint.is_processed(case_number):
            work_queue.task_done()
            continue

        try:
            result = generate_fields(item, model_name, rate_limiter)
            checkpoint.mark_processed(case_number, result)
            processed_count += 1
            checkpoint_count += 1

            # Save checkpoint periodically
            if checkpoint_count >= CHECKPOINT_INTERVAL:
                checkpoint.save_checkpoint()
                elapsed_time = time.time() - start_time
                rate = processed_count / elapsed_time * 60
                print(
                    f"Thread {thread_id}: Processed {processed_count} items, "
                    f"Current rate: {rate:.1f} requests/minute"
                )
                checkpoint_count = 0

        except Exception as e:
            print(f"Thread {thread_id}: Error processing case {case_number}: {str(e)}")
        finally:
            work_queue.task_done()


def main():
    filename = "./data/neiss_10p_sample_with_text.csv"
    model_name = MODEL_GEMINI
    checkpoint_dir = "./data/neiss_10p_sample_with_text_checkpoints"

    # Initialize checkpoint manager
    checkpoint_manager = CheckpointManager(checkpoint_dir, NUM_THREADS, model_name)

    # Read input data
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        data = list(reader)
        total_cases = len(data)
        print(f"Total cases to process: {total_cases}")

    # Get already processed cases
    processed_cases = checkpoint_manager.get_all_processed_cases()
    remaining_data = [
        item for item in data if item.get("CPSC_Case_Number") not in processed_cases
    ]
    print(f"Remaining cases to process: {len(remaining_data)}")

    if not remaining_data:
        print("All cases have been processed. Writing final output...")
    else:
        # Create work queue and distribute work
        work_queue = Queue()
        for item in remaining_data:
            work_queue.put(item)

        # Start worker threads
        threads = []
        for i in range(NUM_THREADS):
            thread = threading.Thread(
                target=worker_thread,
                args=(
                    i,
                    work_queue,
                    model_name,
                    checkpoint_manager.thread_checkpoints[i],
                ),
            )
            thread.start()
            threads.append(thread)

        # Wait for all work to complete
        work_queue.join()
        for thread in threads:
            thread.join()

    # Write final output
    all_results = checkpoint_manager.get_all_results()
    output_file = f"neiss_10p_sample_with_text_{model_name.replace('-', '_')}.csv"

    if all_results:
        fieldnames = all_results[0].keys()
        with open(f"./data/{output_file}", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in all_results:
                writer.writerow(row)
        print(f"Results written to {output_file}")
    else:
        print("No results to write")


if __name__ == "__main__":
    main()
