import csv
import json
import multiprocessing
import os
import random
import readline
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from libs.constants import (
    MODEL_CLAUDE,
    MODEL_GEMINI,
    MODEL_GPT_4,
    MODEL_GPT_4_MINI,
    MODEL_LOCAL,
    NEW_COLUMN_FIELDS,
    PROMPT_CREATE_NEW_FIELDS,
    PROMPT_EXTRACT_FIELDS,
)
from libs.gen_model import send_message


def split_samples(filename: str, num_chunks: int) -> List[Dict]:
    with open(filename, "r") as f:
        all_columns = f.readline().strip().split(",")
        data = f.readlines()

    chunk_size = len(data) // num_chunks
    chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]

    samples = []
    for chunk in chunks:
        sample_data = [line.strip().split(",") for line in chunk]
        samples.append({"columns": all_columns, "sample_data": sample_data})
    return samples


def generate_fields(data, model_name: str) -> List[Dict]:
    message = PROMPT_EXTRACT_FIELDS.format(columns=NEW_COLUMN_FIELDS, data=data)
    response = send_message(model_name, message)
    print(response)
    data = {**data, **response}
    return data  # type: ignore


def process_chunk(chunk: List[Dict], model_name: str) -> List[Dict]:
    with ThreadPoolExecutor() as executor:
        return list(executor.map(lambda item: generate_fields(item, model_name), chunk))  # type: ignore


def main():
    filename = "./data/code_replaced_neiss_2014_2023_1000_samples.csv"
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        data = list(reader)

    model_name = MODEL_GEMINI

    # Determine the number of CPU cores to use
    num_cores = multiprocessing.cpu_count()
    chunk_size = len(data) // num_cores

    # Split the data into chunks
    chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]

    # Process chunks in parallel
    with ThreadPoolExecutor(max_workers=num_cores) as executor:
        results = list(
            executor.map(lambda chunk: process_chunk(chunk, model_name), chunks)
        )

    # Flatten the results
    flattened_results = [item for sublist in results for item in sublist]

    # Write the results to a CSV file
    output_file = f"neiss_with_new_fields_{model_name.replace('-', '_')}.csv"
    fieldnames = flattened_results[0].keys()

    with open(f"./data/{output_file}", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in flattened_results:
            writer.writerow(row)

    # results = []
    # for item in data:
    #     result = generate_fields(item, model_name)
    #     results.append(result)

    # fieldnames = results[0].keys()
    # output_file = f"neiss_with_new_fields_{model_name.replace('-', '_')}.csv"
    # with open(f"./data/{output_file}", "w") as f:
    #     writer = csv.DictWriter(f, fieldnames=fieldnames)
    #     writer.writeheader()
    #     for row in results:
    #         writer.writerow(row)


if __name__ == "__main__":
    main()
