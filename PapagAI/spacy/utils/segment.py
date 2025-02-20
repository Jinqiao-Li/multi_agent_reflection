import pandas as pd
import json
import re

# Function to split text into sentences using regex
def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())  # Splitting at sentence boundaries
    return [s.strip() for s in sentences if s]  # Remove empty strings

# Load the Excel file
file_path = "your_file_path_here.xlsx"  # Change this to the actual file path
df = pd.read_excel(file_path)

# Check for the correct column name
column_name = "Reflection text"
if column_name not in df.columns:
    raise ValueError(f"Column '{column_name}' not found in the provided Excel file.")

# Extract the "Reflection text" column, dropping NaN values
reflection_texts = df[column_name].dropna().reset_index(drop=True)

# Output JSONL file path
output_file_path = "segmented_reflections.jsonl"

# Process and segment each reflection into sentences
with open(output_file_path, "w", encoding="utf-8") as outfile:
    for text_id, paragraph in enumerate(reflection_texts):
        sentences = split_into_sentences(paragraph)  # Use regex-based sentence segmentation
        for sentence in sentences:
            entry = {"text_id": text_id, "text": sentence}
            outfile.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"✅ Segmented reflections saved to {output_file_path}")
