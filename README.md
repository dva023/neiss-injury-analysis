# NEISS Injury Analysis

The NEISS Injury Analysis project aims to provide insights into injury trends and patterns.

## Table of Contents

- [Installation](#installation)
- [Scripts](#scripts)
- [Data](#data)

## Installation

To get started with the project, clone the repository and install the necessary dependencies:

```sh
git clone https://github.com/dva023/neiss-injury-analysis.git
cd neiss-injury-analysis
python -m venv .venv # create virtual env
source .venv/bin/activate # activate the virtual env
pip install -r requirements.txt
```

## Scripts

Here are some of the key notebooks/scripts included in the project:

- `data_cleaning/NEISS_data_cleaning.ipynb`: Notebook for cleaning the raw NEISS data.
- `narrative_extraction/`:
  - `data_processor.py`: Replace numeric codes with their corresponding descriptions and dump to a new CSV file.
  - `create_new_fields.py`: Generate new field names by extracting information from the `narrative` fields.
  - `generate_new_fields.py`: Generate new fields for each data record using AI models, append the fields by the end of columns.

## Data

- `code_replaced_neiss_2014_2023.csv`
  - You need to download the `consolidated_cleaned_neiss_2014_2023.csv` from Sharepoints and then run the script `./narrative_extraction/data_processor.py` to generate this file.
  - This file replaced all of the numeric codes with the corresponding descriptions from the FMT file.
- `./data/code_replaced_neiss_2014_2023_1000_samples.csv`
  - 100 random examples picked from the `code_replaced_neiss_2014_2023.csv`.
- `./data/code_replaced_neiss_2014_2023_100_samples.csv`
  - 1000 random examples picked from the `code_replaced_neiss_2014_2023.csv`.
- `./data/new_columns_gemini_1.5_flash_002.json`
  - Using Gemini-1.5-flash model to create the field names by using the 100 sample data.
- `./data/new_columns_gpt_4o_mini.json`
  - Using GPT-4o-mini model to create the field names by using the 100 sample data.
- `./data/new_columns_gpt_4o.json`
  - Using GPT-4o model to create the field names by using the 100 sample data.
- `./data/sorted_unique_columns_gemini_1.5_flash_002.json`
  - Merge the identical field names and sort by the frequencies.
- `./data/sorted_unique_columns_gpt_4o_mini.json`
  - Merge the identical field names and sort by the frequencies.
- `./data/sorted_unique_columns_gpt_4o.json`
  - Merge the identical field names and sort by the frequencies.
- `./data/neiss_with_new_fields_gemini_1.5_flash_002.csv`
  - Using Gemini-1.5-flash model to generate the fields(injury_mechanism, location_of_injury, injury_type, activity_at_injury) by using the 1000 sample data.
