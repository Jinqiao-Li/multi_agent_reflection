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
parser = argparse.ArgumentParser(description="Run text classification on a given JSONL file and save predictions.")
parser.add_argument("test_data", help="Path to the test data JSONL file")
parser.add_argument("output_file", help="Path to save the predictions JSONL file")
args = parser.parse_args()

# Load spaCy pipeline
nlp = assemble("config.cfg")

# Load test data
with open(args.test_data, "r") as f:
    test_data = [json.loads(line) for line in f]

predictions = []

# Define batch size (adjust for performance)
BATCH_SIZE = 10  # Can be increased to process faster

# Start timing the process
start_time = time.time()

# Process texts in batches
print("\n🔄 Running classification with batch processing...\n")
for i in tqdm.tqdm(range(0, len(test_data), BATCH_SIZE), desc="Processing", unit="batch", dynamic_ncols=True):
    batch = test_data[i: i + BATCH_SIZE]

    # Extract texts and their true labels
    texts = [item["text"] for item in batch]
    true_labels = [item["answer"] for item in batch]  # Keep the true label

    # Send the batch for classification
    docs = list(nlp.pipe(texts))  # Batch processing

    # Collect predictions
    for j, doc in enumerate(docs):
        predicted_label = max(doc.cats, key=doc.cats.get)  # Get highest confidence label as a string
        predictions.append({
            "text": texts[j],
            "answer": true_labels[j],  # Store the true label
            "predicted": predicted_label
        })

# Calculate total processing time
end_time = time.time()
total_time = end_time - start_time

# Save predictions to a file
with open(args.output_file, "w") as f:
    for pred in predictions:
        f.write(json.dumps(pred) + "\n")

print(f"\n✅ Classification complete. Results saved in `{args.output_file}`")
print(f"⏱️ Total Processing Time: {total_time:.2f} seconds")