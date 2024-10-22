"""
Generate new field names by extracting information from the `narrative` fields.
"""

import json
from collections import Counter
from typing import Dict, List

from constants import (
    MODEL_CLAUDE,
    MODEL_GEMINI,
    MODEL_GPT_4,
    MODEL_GPT_4_MINI,
    MODEL_LOCAL,
    PROMPT_CREATE_NEW_FIELDS,
)
from gen_model import send_message


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


def extract_columns(dataset, model_name: str) -> List[Dict]:
    message = PROMPT_CREATE_NEW_FIELDS.format(dataset=dataset)
    response = send_message(model_name, message)
    print(response)
    return response["proposed_columns"]  # type: ignore


def consolidate_results(results: List[Dict]) -> List[Dict]:

    # Count frequencies and create unique list with frequencies
    column_names = [item["column_name"] for item in results]
    frequency_dict = Counter(column_names)

    unique_items = {}
    for item in results:
        column_name = item["column_name"]
        if column_name not in unique_items:
            new_item = item.copy()
            new_item["frequency"] = frequency_dict[column_name]
            unique_items[column_name] = new_item

    # Sort the list
    sorted_unique_list = sorted(
        unique_items.values(), key=lambda x: (-x["frequency"], x["column_name"])
    )

    return sorted_unique_list


def main():
    filename = "./data/code_replaced_neiss_2014_2023_100_samples.csv"
    chunks = split_samples(filename, 10)

    model_name = MODEL_GEMINI

    results = []
    for chunk in chunks:
        result = extract_columns(chunk, model_name)
        results += result

    with open(f"./data/new_columns_{model_name.replace('-', '_')}.json", "w") as f:
        json.dump(results, f, indent=2)

    # with open(f"./data/new_columns_{model_name.replace('-', '_')}.json", "r") as f:
    #     results = json.load(f)

    consolidated_results = consolidate_results(results)

    with open(
        f"./data/sorted_unique_columns_{model_name.replace('-', '_')}.json", "w"
    ) as f:
        json.dump(consolidated_results, f, indent=2)

    print(json.dumps(consolidated_results, indent=2))


if __name__ == "__main__":
    main()
