import os

import numpy as np
import pandas as pd


class CodeLookup:
    def __init__(self, data_file="./data/neiss_fmt.csv"):
        self.data_file = data_file
        self.data = {}
        self.categories = []
        self.lookups = self.precompute_lookups()

    def load_data(self):
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file not found: {self.data_file}")

        df = pd.read_csv(self.data_file)
        self.categories = df["Format name"].unique()

        for category in self.categories:
            category_df = df[df["Format name"] == category].copy()
            category_df["Starting value for format"] = pd.to_numeric(
                category_df["Starting value for format"], errors="coerce"
            )
            category_df["Ending value for format"] = pd.to_numeric(
                category_df["Ending value for format"], errors="coerce"
            )
            # if category == "AGELTTWO":
            #     category_df["Format value label"] = np.round(
            #         np.where(
            #             category_df["Starting value for format"] >= 200,
            #             (category_df["Starting value for format"] % 200) / 12,
            #             -1,
            #         ),
            #         2,
            #     )
            self.data[category] = category_df
        print(f"Loaded NEISS FMT data from {self.data_file}")

    def get_category_for_field(self, field):
        field = field.upper()
        if field == "RACE":
            return field
        # elif field == "AGE":
        #     return "AGELTTWO"
        elif field in ["SEX", "GENDER"]:
            return "GENDER"
        elif field.startswith("BODY_PART"):
            return "BDYPT"
        elif "DIAGNOSIS" in field:
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

    def precompute_lookups(self):
        self.load_data()
        lookups = {}
        for category in self.categories:
            category_data = self.data.get(category, pd.DataFrame())
            if not category_data.empty:
                lookups[category] = dict(
                    zip(
                        category_data["Starting value for format"],
                        (
                            category_data["Format value label"].str.split(" - ").str[-1]
                            if category != "AGELTTWO"
                            else category_data["Format value label"]
                        ),
                    )
                )
        return lookups

    def get_lookups(self):
        return self.lookups
