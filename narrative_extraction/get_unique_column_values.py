import pandas as pd


def analyze_unique_values(input_file_path, output_file_path):
    # Read the CSV file
    df = pd.read_csv(input_file_path)

    # Columns to analyze
    columns_of_interest = ["activity_at_injury", "injury_mechanism", "object_involved"]

    # Dictionary to store unique values
    unique_values_dict = {}

    # Get unique values for each column
    for column in columns_of_interest:
        unique_values = df[column].fillna("").astype(str).unique()
        # Sort values (after converting all to strings)
        unique_values = sorted([str(x) for x in unique_values if x != ""])
        # Store in dictionary with column name as key
        unique_values_dict[f"{column}_unique"] = pd.Series(unique_values)

    # Convert to DataFrame
    result_df = pd.DataFrame(unique_values_dict)

    # Save to CSV
    result_df.to_csv(output_file_path, index=False)

    # Print summary
    print(f"Analysis complete. Results saved to {output_file_path}")
    for column in columns_of_interest:
        print(f"Total unique values in {column}: {len(df[column].unique())}")


if __name__ == "__main__":
    input_file_path = "./data/neiss_10p_sample_with_text_gemini_1.5_flash_002.csv"
    output_file_path = (
        "./data/neiss_10p_sample_with_text_gemini_1.5_flash_002_unique.csv"
    )
    analyze_unique_values(input_file_path, output_file_path)
