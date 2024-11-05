import csv
import json
import os
import threading
import time
from pathlib import Path
from queue import Queue

from constants import MODEL_GEMINI, NEW_COLUMN_FIELDS, PROMPT_EXTRACT_FIELDS
from gen_model import send_message

# Configuration
NUM_THREADS = 8
REQUESTS_PER_THREAD = 150  # requests per minute per thread
WINDOW_SIZE = 60  # seconds
OUTPUT_DIR = (
    "./data/neiss_10p_sample_with_text_results"  # Directory to store individual results
)


class ThreadRateLimiter:
    def __init__(self, requests_per_minute: int):
        self.interval = 60.0 / requests_per_minute
        self.last_request = time.time() - self.interval
        self.lock = threading.Lock()

    def wait(self):
        with self.lock:
            now = time.time()
            time_since_last = now - self.last_request
            if time_since_last < self.interval:
                time.sleep(self.interval - time_since_last)
            self.last_request = time.time()


def generate_fields(
    data: dict, model_name: str, rate_limiter: ThreadRateLimiter
) -> dict:
    rate_limiter.wait()
    message = PROMPT_EXTRACT_FIELDS.format(columns=NEW_COLUMN_FIELDS, data=data)
    response = send_message(model_name, message)
    return {**data, **response}


def worker_thread(thread_id: int, work_queue: Queue, model_name: str, output_dir: Path):
    rate_limiter = ThreadRateLimiter(REQUESTS_PER_THREAD)
    processed = 0
    start_time = time.time()

    while True:
        try:
            item = work_queue.get_nowait()
        except Queue.Empty:
            break

        case_number = item.get("CPSC_Case_Number")
        if not case_number:
            work_queue.task_done()
            continue

        output_file = output_dir / f"{case_number}.json"
        if output_file.exists():
            work_queue.task_done()
            continue

        try:
            result = generate_fields(item, model_name, rate_limiter)

            # Save individual result
            with open(output_file, "w") as f:
                json.dump(result, f)

            processed += 1
            if processed % 10 == 0:
                elapsed = time.time() - start_time
                rate = processed / elapsed * 60
                print(
                    f"Thread {thread_id}: Processed {processed} items, "
                    f"Current rate: {rate:.1f} requests/minute"
                )

        except Exception as e:
            print(f"Thread {thread_id}: Error processing case {case_number}: {str(e)}")
        finally:
            work_queue.task_done()


def combine_results(output_dir: Path, output_file: str):
    """Combine all JSON files into a single CSV"""
    all_results = []
    for file in output_dir.glob("*.json"):
        with open(file, "r") as f:
            all_results.append(json.load(f))

    if all_results:
        fieldnames = all_results[0].keys()
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in all_results:
                writer.writerow(row)


def main():
    # Setup
    input_file = "./data/neiss_10p_sample_with_text.csv"
    model_name = MODEL_GEMINI
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    # Read input data
    with open(input_file, "r") as f:
        reader = csv.DictReader(f)
        data = list(reader)
    print(f"Total cases to process: {len(data)}")

    # Create work queue
    work_queue = Queue()
    for item in data:
        work_queue.put(item)

    # Start worker threads
    threads = []
    for i in range(NUM_THREADS):
        thread = threading.Thread(
            target=worker_thread, args=(i, work_queue, model_name, output_dir)
        )
        thread.start()
        threads.append(thread)

    # Wait for completion
    work_queue.join()
    for thread in threads:
        thread.join()

    # Combine results
    final_output = (
        f"./data/neiss_10p_sample_with_text_{model_name.replace('-', '_')}.csv"
    )
    combine_results(output_dir, final_output)
    print(f"Results combined into {final_output}")


if __name__ == "__main__":
    main()
