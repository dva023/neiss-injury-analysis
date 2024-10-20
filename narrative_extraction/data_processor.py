"""
Replace numeric codes with their corresponding descriptions and dump to a new CSV file.
"""

import multiprocessing as mp
from functools import partial

import pandas as pd
from code_lookup import CodeLookup

codeLookup = CodeLookup()


def process_chunk(chunk, lookups, columns_to_process, keep_original):
    for column in columns_to_process:
        category = codeLookup.get_category_for_field(column)
        # if column is age and value >= 200, % 200 / 12
        if column == "Age":
            description = (
                chunk[column]
                .map(lambda x: round((x % 200) / 12, 2) if x >= 200 else x)
                .fillna("")
            )
        else:
            description = chunk[column].map(lookups.get(category, {})).fillna("")

        if keep_original:
            chunk[f"{column}_Desc"] = description
        else:
            chunk[column] = description  # .where(description != "", chunk[column])
    return chunk


def process_neiss_data(input_file, output_file, keep_original=True, chunk_size=100000):
    lookups = codeLookup.get_lookups()

    columns_to_process = [
        "Age",
        "Sex",
        "Race",
        "Other_Race",
        "Hispanic",
        "Body_Part",
        "Diagnosis",
        "Body_Part_2",
        "Diagnosis_2",
        "Disposition",
        "Location",
        "Fire_Involvement",
        "Product_1",
        "Product_2",
        "Product_3",
        "Alcohol",
        "Drug",
    ]

    # Create a partial function with fixed arguments
    process_chunk_partial = partial(
        process_chunk,
        lookups=lookups,
        columns_to_process=columns_to_process,
        keep_original=keep_original,
    )

    pool = mp.Pool(mp.cpu_count())

    # Process the file in chunks
    chunks = pd.read_csv(input_file, chunksize=chunk_size)
    processed_chunks = pool.imap(process_chunk_partial, chunks)

    # Write the processed data to the output CSV file
    first_chunk = True
    for chunk in processed_chunks:
        if first_chunk:
            chunk.to_csv(output_file, index=False, mode="w")
            first_chunk = False
        else:
            chunk.to_csv(output_file, index=False, mode="a", header=False)

    pool.close()
    pool.join()

    print(f"Processed data written to {output_file}")


if __name__ == "__main__":
    input_file = "./data/consolidated_cleaned_neiss_2014_2023.csv"
    output_file = "./data/code_replaced_neiss_2014_2023.csv"
    process_neiss_data(input_file, output_file, False)
