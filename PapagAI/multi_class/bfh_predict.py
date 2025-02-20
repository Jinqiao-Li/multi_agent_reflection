import os
import json
import time
import tqdm
import argparse
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Error: OPENAI_API_KEY is not set. Please add it to your .env file.")

# Parse command-line arguments
parser = argparse.ArgumentParser(
    description="Classify text paragraphs based on Gibbs' Reflective Cycle using GPT-4 Mini.")
parser.add_argument("input_file", help="Path to the input TSV file")
parser.add_argument("output_file", help="Path to save the output TSV file with predictions")
args = parser.parse_args()

# Load input data (TSV format)
df = pd.read_csv(args.input_file, sep="\t", engine="python")

# Initialize GPT-4 Mini model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0, openai_api_key=api_key)

# Optimized classification prompt
prompt_template = (
    "You are an expert in analyzing reflective writing based on Gibbs' Reflective Cycle. "
    "Your task is to classify the given paragraph into one or more relevant steps of the cycle: "
    "Description, Feelings, Evaluation/Analysis, Conclusion/Action Plan. "
    "The output should be in the format of a binary list [D, F, EA, CAP] where: "
    "D=1 if the text includes objective facts/actions (Description), "
    "F=1 if emotions/motivations are expressed (Feelings), "
    "EA=1 if reasoning, cause-effect, or assessment is included (Evaluation/Analysis), "
    "CAP=1 if conclusions, lessons, or future actions are described (Conclusion/Action Plan). "
    "Return only the binary list in your response, with no extra text. Here is the text: \n\n{text}")

# Predictions list
predictions = []
start_time = time.time()

print("\n🔄 Classifying text using GPT-4 Mini...\n")
for i in tqdm.tqdm(range(0, len(df)), desc="Processing", unit="batch", dynamic_ncols=True):
    text = df.iloc[i]["text"]  # Extract text only

    try:
        # Make GPT-4 Mini API call
        response = llm.invoke(prompt_template.format(text=text)).content.strip()
    except Exception as e:
        print(f"⚠️ API Error: {e}. Skipping entry.")
        response = "[0, 0, 0, 0]"  # Default to neutral output

    # Store results
    predictions.append({
        "text": text,
        "predicted": response
    })

# Convert results to DataFrame
output_df = pd.DataFrame(predictions)

# Save results to TSV
output_df.to_csv(args.output_file, sep="\t", index=False)

# Calculate total processing time
end_time = time.time()
total_time = end_time - start_time

print(f"\n✅ Classification complete. Results saved in `{args.output_file}`")
print(f"⏱️ Total Processing Time: {total_time:.2f} seconds")
