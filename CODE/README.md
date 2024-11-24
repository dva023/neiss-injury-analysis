# NEISS Injury Analysis

## Table of Contents

- [Installation](#installation)
- [Data Sources](#data-sources)
- [Development Process](#development-process)

## Installation

To get started with the project, clone the repository and install the necessary dependencies:

```sh
git clone https://github.com/dva023/neiss-injury-analysis.git
cd neiss-injury-analysis
python -m venv .venv  # create virtual env
source .venv/bin/activate  # activate the virtual env
pip install -r requirements.txt
```

For the AI-powered field extraction, copy `.env.example` to `.env` and add your API tokens.

## Data Sources

Primary data files required for this project:

- `consolidated_cleaned_neiss_2014_2023.csv`: Raw NEISS data (2014-2023)
  - Download from [SharePoint](https://gtvault.sharepoint.com/:x:/s/cse6242groupprojectchat/EbMcEGz4dzpKnl6qIT-oSG4BqToa0ZMSI4rVL9CFyb-gVg?e=cTygq0) (GaTech email login required)
- `neiss_code_text_mapping.csv`: Code-to-text mapping reference table
  - Located in `./data/`

## Development Process

![dev-process](./images/dev-process.png)

Our analysis follows these key steps:

1. **Data Aggregation & Cleaning**
   - Clean raw NEISS data (`notebooks/data_cleaning.ipynb`)
   - Process and consolidate data from 2014-2023

2. **Data Enrichment**
   - Replace numeric codes with descriptions (`narrative_extraction/data_processor.py`)
   - Extract new fields using LLMs:
     - Define field extraction rules (`narrative_extraction/create_new_fields.py`)
     - Generate fields for each record (`narrative_extraction/generate_new_fields.py`)

3. **Model Development**
   - Perform descriptive analysis (`notebooks/descriptive_analysis.ipynb`)
   - Generate embeddings for narrative field (`notebooks/embedding_generation.ipynb`)
   - Compare model performance (`notebooks/model_comparison_on_10p.ipynb`)
     - Test three XGBoost configurations on different training data setups
   - Train final model (`notebooks/model_training_v1.ipynb`)

4. **Tableau Development**

   - Tabpy server setup (`notebooks/tabpy_v6_no_db.ipynb`)
   - Database for analysis setup
   - Tableau dashboard development (`./tableau/tableau_v6.twb`)
