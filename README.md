# NEISS Injury Analysis

The NEISS Injury Analysis project aims to provide insights into injury trends and patterns.

## Table of Contents

- [Installation](#installation)
- [Contributing](#contributing)

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
