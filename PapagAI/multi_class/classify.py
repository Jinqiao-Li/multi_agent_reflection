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

# test 4
# Optimized classification prompt
# prompt_template = (
#     "You are an expert in analyzing reflective writing based on Gibbs' Reflective Cycle. "
#     "Your task is to classify the given paragraph into one or more relevant steps of the cycle: "
#     "Description, Feelings, Evaluation/Analysis, Conclusion/Action Plan. "
#
#     "**Category Definitions:**\n"
#     "- **Description (D):** Includes objective facts, actions, or events. "
#     "- **Feelings (F):** Expresses personal emotions, motivations, or reactions. "
#     "- **Evaluation (EA):** Involves judgment, self-assessment, or recognizing difficulties, but does NOT explain causes. "
#     "- **Analysis (A):** Explains reasons, builds relations between events, or explores cause-effect relationships. "
#     "- **Conclusion/Action Plan (CAP):** Describes lessons learned, future actions, or proposed strategies.\n"
#
#     "**Instructions:**\n"
#     "- Assign `1` to a category **only if it is explicitly present** in the text.\n"
#     "- If a category is **not present**, assign `0`.\n"
#     "- **Do not assume missing steps**—mark only what is clearly stated.\n"
#
#     "**Output Format:**\n"
#     "Return only a **binary list** `[D, F, EA, CAP]`, with:\n"
#     "- `1` for present categories.\n"
#     "- `0` for absent categories.\n"
#     "- **No extra text or explanation—just the list.**\n\n"
#
#     "**Example:**\n"
#     "If the text expresses emotions and describes lessons learned, but lacks objective facts and analysis, return:\n"
#     "[0, 1, 0, 1]\n\n"
#
#     "**Text for Classification:**\n"
#     "{text}"
# )

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

# Define batch size for efficiency
# BATCH_SIZE = 5
predictions = []
start_time = time.time()

print("\n🔄 Classifying text using GPT-4 Mini...\n")
for i in tqdm.tqdm(range(0, len(df)), desc="Processing", unit="batch", dynamic_ncols=True):
    batch = df.iloc[i: i + 1]  # Process one at a time now
    texts = batch["text"].tolist()

    try:
        # Make GPT-4 Mini API call
        responses = [llm.invoke(prompt_template.format(text=text)).content.strip() for text in texts]
    except Exception as e:
        print(f"⚠️ API Error: {e}. Skipping batch.")
        responses = ["[0, 0, 0, 0]"] * len(texts)  # Default to neutral output

    # Store results
    for j, response in enumerate(responses):
        predictions.append({
            "student_id": batch.iloc[j]["student_id"],
            "text": texts[j],
            "label": batch.iloc[j]["label"],
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
