import os

import pandas as pd


class CodeLookup:
    def __init__(self, data_file="./data/neiss_fmt.csv"):
        self.data_file = data_file
        self.data = {}
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file not found: {self.data_file}")

        df = pd.read_csv(self.data_file)
        categories = df["Format name"].unique()

        for category in categories:
            category_df = df[df["Format name"] == category].copy()
            category_df["Starting value for format"] = pd.to_numeric(
                category_df["Starting value for format"], errors="coerce"
            )
            category_df["Ending value for format"] = pd.to_numeric(
                category_df["Ending value for format"], errors="coerce"
            )
            self.data[category] = category_df

        print(f"Loaded NEISS FMT data from {self.data_file}")

    def get_description(self, category, code):
        if category not in self.data:
            return f"Category '{category}' not found"

        df = self.data[category]
        code = int(code)
        result = df[
            (df["Starting value for format"] <= code)
            & (df["Ending value for format"] >= code)
        ]

        if not result.empty:
            return f"{code} - {result.iloc[0]['Format value label']}"
        return f"Code {code} not found in the category '{category}'"

    def lookup_multiple(self, **kwargs):
        results = {}
        for field, code in kwargs.items():
            category = self.get_category_for_field(field)
            results[field] = self.get_description(category, code)
        return results

    def get_category_for_field(self, field):
        field = field.upper()
        if field in ["SEX", "GENDER"]:
            return "GENDER"
        elif field in ["RACE", "HISP"]:
            return field
        elif field.startswith("BODY_PART"):
            return "BDYPT"
        elif field.startswith("DIAGNOSIS"):
            return "DIAG"
        elif field == "DISPOSITION":
            return "DISP"
        elif field == "LOCATION":
            return "LOC"
        elif field == "FIRE_INVOLVEMENT":
            return "FIRE"
        elif field.startswith("PRODUCT"):
            return "PROD"
        elif field == "ALCOHOL" or field == "DRUG":
            return "ALC_DRUG"
        elif field == "HISPANIC":
            return "HISP"
        else:
            return field
