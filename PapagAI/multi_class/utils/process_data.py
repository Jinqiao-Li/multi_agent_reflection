import pandas as pd
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Process TSV file and output results.")
parser.add_argument("input_file", help="Path to input TSV file")
parser.add_argument("output_file", help="Path to save output CSV file")
args = parser.parse_args()

# Load the TSV file
df = pd.read_csv(args.input_file, sep='\t')

# Define valid gibbs labels
valid_labels = {0, 1, 2, 3, 4, 5}

# Filter out rows with invalid gibbs values
df = df[df['gibbs'].isin(valid_labels)]

# Convert gibbs column to multi-class encoding
def encode_label(gibbs_values):
    label = [0, 0, 0, 0]
    for val in gibbs_values:
        if val == 0:
            label[0] = 1
        if val == 1:
            label[1] = 1
        if val in {2, 3}:
            label[2] = 1
        if val in {4, 5}:
            label[3] = 1
    return label

# Group by student_id and aggregate labels and text
concatenated_df = df.groupby('student_id').agg({
    'TRANSLATION': lambda x: ' '.join(x).replace('"', '').strip(),  # Concatenate text
    'gibbs': lambda x: encode_label(set(x))  # Ensure all labels are accounted for
}).reset_index()

# Rename columns
concatenated_df.rename(columns={'TRANSLATION': 'text', 'gibbs': 'label'}, inplace=True)

# Save output to file
concatenated_df.to_csv(args.output_file, index=False)

# Print success message
print(f"✅ Processed data saved to {args.output_file}")
