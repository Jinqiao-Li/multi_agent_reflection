import argparse
import pandas as pd
import os
import ast
from sklearn.model_selection import train_test_split

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Split a TSV dataset into train, validation, and test sets.")
parser.add_argument("input_file", help="Path to the input TSV file")
parser.add_argument("output_dir", help="Path to the output directory where the split files will be saved")
args = parser.parse_args()

# Ensure output directory exists
os.makedirs(args.output_dir, exist_ok=True)

# Load the dataset correctly
try:
    with open(args.input_file, "r") as f:
        first_line = f.readline()
        sep = "," if "," in first_line else "\t"  # Detect delimiter
    df = pd.read_csv(args.input_file, sep=sep, engine="python")
except Exception as e:
    raise ValueError(f"Error reading TSV file: {e}")

# Normalize column names (strip spaces, lowercase, and ensure proper splitting)
if len(df.columns) == 1 and ("," in df.columns[0] or "\t" in df.columns[0]):
    df = pd.read_csv(args.input_file, sep=sep, engine="python", header=0)

df.columns = df.columns.str.strip().str.lower()

# Display column names for debugging
print("📌 Columns in the input file:", list(df.columns))

# Check if 'label' column exists
if 'label' not in df.columns:
    raise KeyError(f"The input file is missing the 'label' column. Found columns: {list(df.columns)}")

# Convert 'label' from string to list of integers
def parse_label(label):
    if isinstance(label, str):
        return ast.literal_eval(label)  # Safely convert string to list
    return label

df['label'] = df['label'].apply(parse_label)

# Check if stratification is possible (each class must have at least 2 instances)
label_counts = df['label'].apply(str).value_counts()
can_stratify = all(label_counts >= 2)

# Split data into Train (80%), Validation (10%), Test (10%)
if can_stratify:
    train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'].apply(str))
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['label'].apply(str))
else:
    print("⚠️ Some labels have only one instance, disabling stratification.")
    train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)

# Create a smaller subset of the test set for quick testing (e.g., 10% of the test set)
quick_test_df = test_df.sample(frac=0.1, random_state=42)

# Save the splits
train_df.to_csv(os.path.join(args.output_dir, "train_data.tsv"), sep="\t", index=False)
val_df.to_csv(os.path.join(args.output_dir, "val_data.tsv"), sep="\t", index=False)
test_df.to_csv(os.path.join(args.output_dir, "test_data.tsv"), sep="\t", index=False)
quick_test_df.to_csv(os.path.join(args.output_dir, "quick_test_data.tsv"), sep="\t", index=False)

print("✅ Dataset split and saved successfully!")
