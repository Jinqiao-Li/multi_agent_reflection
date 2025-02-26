import os
import pandas as pd
import argparse
import json


def clean_and_filter_data(input_file, text_column, label_column, output_file):
    """
    Cleans and filters a dataset:
    - Extracts the specified text and label columns.
    - Removes rows with missing values.
    - Keeps only rows where labels are in {0, 1, 2, 3, 4, 5}.
    - Converts labels to strings.
    - Saves the cleaned data to the 'data/' folder in JSONL format.

    Parameters:
        input_file (str): Path to the dataset file (TSV, CSV, Excel).
        text_column (str): Name of the column containing text.
        label_column (str): Name of the column containing labels.
        output_file (str): Name of the output JSONL file (inside the 'data/' folder).
    """

    # Ensure the output directory exists
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    # Full output path
    output_path = os.path.join(output_dir, output_file)

    # Determine file format and load accordingly
    if input_file.endswith(".tsv"):
        df = pd.read_csv(input_file, sep="\t")
    elif input_file.endswith(".csv"):
        df = pd.read_csv(input_file)
    elif input_file.endswith((".xls", ".xlsx")):
        df = pd.read_excel(input_file)
    else:
        raise ValueError("Unsupported file format! Use TSV, CSV, or Excel.")

    # Ensure required columns exist
    if text_column not in df.columns or label_column not in df.columns:
        raise ValueError(f"Columns '{text_column}' or '{label_column}' not found in dataset!")

    # Capture the initial row count before cleaning
    initial_row_count = len(df)

    # Keep only required columns
    df = df[[text_column, label_column]]

    # Drop rows with missing values
    df = df.dropna()

    # Convert labels to integers (handle errors)
    df[label_column] = pd.to_numeric(df[label_column], errors="coerce").astype("Int64")

    # Keep only rows where label is in {0, 1, 2, 3, 4, 5}
    valid_labels = {"0", "1", "2", "3", "4", "5"}
    df[label_column] = df[label_column].astype(str)  # Convert labels to string
    df = df[df[label_column].isin(valid_labels)]

    # Rename columns for consistency
    df = df.rename(columns={text_column: "text", label_column: "answer"})

    # Ensure correct text formatting (strip leading/trailing whitespace and remove extra quotes)
    df["text"] = df["text"].apply(lambda x: x.strip().strip('"').strip("'"))

    # Save cleaned dataset to JSONL format in the 'data/' folder
    with open(output_path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            json.dump({"text": row["text"], "answer": row["answer"]}, f, ensure_ascii=False)
            f.write("\n")

    # Capture the final row count after cleaning
    final_row_count = len(df)

    print(f"✅ Cleaned data saved to: {output_path}")
    print(f"📊 Rows before cleaning: {initial_row_count} | Rows after cleaning: {final_row_count}")


# Command-line arguments for flexibility
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean and filter a dataset.")
    parser.add_argument("input_file", type=str, help="Path to the input dataset file.")
    parser.add_argument("text_column", type=str, help="Column name containing text.")
    parser.add_argument("label_column", type=str, help="Column name containing labels.")
    parser.add_argument("output_file", type=str, help="Output filename (inside 'data/' folder).")

    args = parser.parse_args()

    clean_and_filter_data(args.input_file, args.text_column, args.label_column, args.output_file)