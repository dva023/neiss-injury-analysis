import csv
import json
import math
import sys
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
NUM_THREADS = 10
REQUESTS_PER_THREAD = 200  # requests per minute per thread
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
        self.processed_cases = {}  # Changed to dict to store thread_id with each case
        self.results = {}

        # Create thread-specific checkpoint file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.checkpoint_file = (
            self.checkpoint_dir
            / f"checkpoint_thread_{thread_id}_{model_name}_{timestamp}.json"
        )
        self.loaded_from_file = None
        self.load_checkpoint()

    def load_checkpoint(self):
        # Find all checkpoint files for all threads to check for cross-thread cases
        checkpoints = []
        for thread_id in range(NUM_THREADS):
            thread_checkpoints = list(
                self.checkpoint_dir.glob(
                    f"checkpoint_thread_{thread_id}_{self.model_name}_*.json"
                )
            )
            if thread_checkpoints:
                latest = max(thread_checkpoints, key=lambda x: x.stat().st_mtime)
                checkpoints.append((thread_id, latest))

        print(
            f"\nThread {self.thread_id}: Found checkpoints: {[cp[1].name for cp in checkpoints]}"
        )

        # Load all checkpoints to check for any cases processed by any thread
        for thread_id, checkpoint_file in checkpoints:
            try:
                with open(checkpoint_file, "r") as f:
                    checkpoint_data = json.load(f)
                    if isinstance(checkpoint_data, dict):
                        # Handle both old and new format
                        if "processed_cases_with_threads" in checkpoint_data:
                            # New format
                            cases = checkpoint_data["processed_cases_with_threads"]
                            for case_num, processing_thread_id in cases.items():
                                self.processed_cases[case_num] = processing_thread_id
                            if (
                                thread_id == self.thread_id
                            ):  # Only load results for our thread
                                self.results.update(checkpoint_data.get("results", {}))
                        else:
                            # Old format - assume cases belong to the thread that saved them
                            cases = checkpoint_data.get("processed_cases", [])
                            for case_num in cases:
                                self.processed_cases[case_num] = thread_id
                            if thread_id == self.thread_id:
                                self.results.update(checkpoint_data.get("results", {}))

                if thread_id == self.thread_id:
                    self.loaded_from_file = checkpoint_file
                    print(
                        f"Thread {self.thread_id}: Loaded own checkpoint: {checkpoint_file}"
                    )

            except Exception as e:
                print(
                    f"Thread {self.thread_id}: Error loading checkpoint {checkpoint_file}: {e}"
                )

        # Report loading results
        owned_cases = sum(
            1 for t in self.processed_cases.values() if t == self.thread_id
        )
        other_cases = len(self.processed_cases) - owned_cases
        print(
            f"Thread {self.thread_id}: Found {owned_cases} own processed cases and {other_cases} cases processed by other threads"
        )

    def save_checkpoint(self):
        try:
            checkpoint_data = {
                "processed_cases_with_threads": self.processed_cases,
                "results": self.results,
                "timestamp": datetime.now().isoformat(),
                "loaded_from": (
                    str(self.loaded_from_file) if self.loaded_from_file else None
                ),
            }

            with open(self.checkpoint_file, "w") as f:
                json.dump(checkpoint_data, f)

            owned_cases = sum(
                1 for t in self.processed_cases.values() if t == self.thread_id
            )
            print(
                f"Thread {self.thread_id}: Saved {owned_cases} cases to {self.checkpoint_file}"
            )
        except Exception as e:
            print(f"Thread {self.thread_id}: Error saving checkpoint: {e}")

    def is_processed(self, case_number: str) -> bool:
        return case_number in self.processed_cases

    def is_processed_by_other_thread(self, case_number: str) -> bool:
        """Check if case was processed by a different thread"""
        if case_number in self.processed_cases:
            processing_thread = self.processed_cases[case_number]
            return processing_thread != self.thread_id
        return False

    def mark_processed(self, case_number: str, result: Dict):
        self.processed_cases[case_number] = self.thread_id
        self.results[case_number] = result


class CheckpointManager:
    def __init__(self, checkpoint_dir: str, num_threads: int, model_name: str):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.thread_checkpoints = [
            ThreadCheckpoint(checkpoint_dir, i, model_name) for i in range(num_threads)
        ]

        # Print summary of loaded checkpoints
        total_processed = len(self.get_all_processed_cases())
        print("\nCheckpoint Loading Summary:")
        print(f"Total previously processed cases across all threads: {total_processed}")
        for thread_id, checkpoint in enumerate(self.thread_checkpoints):
            print(f"Thread {thread_id}: {len(checkpoint.processed_cases)} cases")
            if checkpoint.loaded_from_file:
                print(f"  Loaded from: {checkpoint.loaded_from_file}")

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
    skipped_own_count = 0
    skipped_other_count = 0
    checkpoint_count = 0
    start_time = time.time()

    print(f"\nThread {thread_id} starting")

    while True:
        try:
            # Get item from queue with timeout
            try:
                item = work_queue.get(timeout=1)  # 1 second timeout
            except Exception:
                # If queue is empty, thread can exit
                break

            case_number = item.get("CPSC_Case_Number")
            if not case_number:
                print(f"Thread {thread_id}: Warning: Missing CPSC_Case_Number in item")
                work_queue.task_done()
                continue

            if checkpoint.is_processed_by_other_thread(case_number):
                skipped_other_count += 1
                if skipped_other_count % 100 == 0:
                    print(
                        f"Thread {thread_id}: Skipped {skipped_other_count} cases processed by other threads"
                    )
                work_queue.task_done()
                continue

            if checkpoint.is_processed(case_number):
                skipped_own_count += 1
                if skipped_own_count % 100 == 0:
                    print(
                        f"Thread {thread_id}: Skipped {skipped_own_count} previously processed cases"
                    )
                work_queue.task_done()
                continue

            try:
                result = generate_fields(item, model_name, rate_limiter)
                checkpoint.mark_processed(case_number, result)
                processed_count += 1
                checkpoint_count += 1

                if checkpoint_count >= CHECKPOINT_INTERVAL:
                    checkpoint.save_checkpoint()
                    elapsed_time = time.time() - start_time
                    rate = processed_count / elapsed_time * 60
                    print(f"\nThread {thread_id} progress:")
                    print(f"  Processed {processed_count} new cases")
                    print(
                        f"  Skipped {skipped_own_count} own previously processed cases"
                    )
                    print(
                        f"  Skipped {skipped_other_count} cases processed by other threads"
                    )
                    print(f"  Current rate: {rate:.1f} requests/minute")
                    checkpoint_count = 0

            except Exception as e:
                print(
                    f"Thread {thread_id}: Error processing case {case_number}: {str(e)}"
                )

            finally:
                work_queue.task_done()

        except Exception as e:
            print(f"Thread {thread_id}: Error in main loop: {str(e)}")
            # Don't break here - continue trying to process queue items

    print(f"\nThread {thread_id} finished:")
    print(f"  Processed: {processed_count} new cases")
    print(f"  Skipped own: {skipped_own_count} cases")
    print(f"  Skipped other threads: {skipped_other_count} cases")
    checkpoint.save_checkpoint()


def write_results_to_csv(results, output_file):
    if not results:
        print("No results to write")
        return

    fieldnames = [
        "CPSC_Case_Number",
        "activity_at_injury",
        "injury_mechanism",
        "object_involved",
    ]

    # Get all possible field names from all results
    # all_fields = set()
    # for result in results:
    #     all_fields.update(result.keys())
    #
    # fieldnames = sorted(list(all_fields))

    with open(f"./data/{output_file}", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"Results written to {output_file}")


def main():
    filename = "./data/neiss_10p_sample_with_text.csv"
    model_name = MODEL_GEMINI
    checkpoint_dir = "./data/neiss_10p_sample_with_text_checkpoints"

    print(f"\nStarting processing with configuration:")
    print(f"Number of threads: {NUM_THREADS}")
    print(f"Requests per thread: {REQUESTS_PER_THREAD}/minute")
    print(f"Total maximum rate: {NUM_THREADS * REQUESTS_PER_THREAD}/minute")

    # Initialize checkpoint manager
    checkpoint_manager = CheckpointManager(checkpoint_dir, NUM_THREADS, model_name)

    # Read input data
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        data = list(reader)
        total_cases = len(data)
        print(f"\nTotal cases in input file: {total_cases}")

    # Get already processed cases
    processed_cases = checkpoint_manager.get_all_processed_cases()
    remaining_data = [
        item for item in data if item.get("CPSC_Case_Number") not in processed_cases
    ]
    print(f"Previously processed cases: {len(processed_cases)}")
    print(f"Remaining cases to process: {len(remaining_data)}")
    print(
        f"First few remaining cases: {[item.get('CPSC_Case_Number') for item in remaining_data[:5]]}"
    )

    if not remaining_data:
        print("All cases have been processed. Writing final output...")
    else:
        # Create work queue and distribute work
        work_queue = Queue()
        for item in remaining_data:
            work_queue.put(item)

        print(f"\nCreated queue with {work_queue.qsize()} items")

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
            thread.daemon = (
                True  # Make threads daemon so they exit when main thread exits
            )
            thread.start()
            threads.append(thread)

        try:
            # Wait for all work to complete
            work_queue.join()

            # Wait for all threads to finish
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            print("\nReceived keyboard interrupt, waiting for threads to finish...")
            # Let the queue finish processing current items
            work_queue.join()
            sys.exit(1)

    # Write final output
    all_results = checkpoint_manager.get_all_results()
    output_file = f"neiss_10p_sample_with_text_{model_name.replace('-', '_')}.csv"
    write_results_to_csv(all_results, output_file)


if __name__ == "__main__":
    main()
