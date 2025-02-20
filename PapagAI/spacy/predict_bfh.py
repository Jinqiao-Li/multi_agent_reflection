import spacy
import os
import json
import time
import tqdm
import argparse
from dotenv import load_dotenv
from spacy_llm.util import assemble

# Load environment variables
load_dotenv()

# Ensure API Key is set
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Error: OPENAI_API_KEY is not set. Please add it to your .env file.")

print(f"✅ OpenAI API Key loaded successfully: {api_key[:5]}*****")

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Run text classification using spaCy LLM pipeline.")
parser.add_argument("input_file", help="Path to the input JSONL file containing segmented reflection texts.")
parser.add_argument("output_file", help="Path to save the predictions JSONL file.")
args = parser.parse_args()

# Load spaCy pipeline
nlp = assemble("config.cfg")

# Load test data
with open(args.input_file, "r", encoding="utf-8") as f:
    test_data = [json.loads(line) for line in f]

predictions = []

# Define batch size (adjust for performance)
BATCH_SIZE = 10  # Adjust for better performance based on API limits

# Start timing the process
start_time = time.time()

# Process texts in batches with tqdm progress bar
print("\n🔄 Running classification with batch processing...\n")
for i in tqdm.tqdm(range(0, len(test_data), BATCH_SIZE), desc="Processing", unit="batch", dynamic_ncols=True):
    batch = test_data[i: i + BATCH_SIZE]

    # Extract texts
    texts = [item["text"] for item in batch]

    # Send the batch for classification
    docs = list(nlp.pipe(texts))  # Batch processing

    # Collect predictions
    for j, doc in enumerate(docs):
        predicted_label = max(doc.cats, key=doc.cats.get)  # ✅ FIXED: No int() conversion
        predictions.append({
            "text_id": batch[j]["text_id"],  # Keep track of the original text ID
            "text": texts[j],
            "predicted": predicted_label  # Label remains a string
        })

# Calculate total processing time
end_time = time.time()
total_time = end_time - start_time

# Save predictions to the specified output file
with open(args.output_file, "w", encoding="utf-8") as f:
    for pred in predictions:
        f.write(json.dumps(pred) + "\n")

print(f"\n✅ Classification complete. Results saved in `{args.output_file}`")
print(f"⏱️ Total Processing Time: {total_time:.2f} seconds")
