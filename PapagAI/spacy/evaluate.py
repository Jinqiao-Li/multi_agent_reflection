import os
import json
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
from sklearn.metrics import f1_score, accuracy_score, confusion_matrix

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Evaluate classification results and generate a confusion matrix.")
parser.add_argument("predictions", help="Path to the predictions JSONL file")
parser.add_argument("output_filename", help="Filename for the saved confusion matrix image")
args = parser.parse_args()

# Load predictions
with open(args.predictions, "r") as f:
    predicted_data = [json.loads(line) for line in f]

# Extract true and predicted labels
true_labels = [item["answer"] for item in predicted_data]  # Using text labels directly
predicted_labels = [item["predicted"] for item in predicted_data]  # Using text labels directly

# Compute evaluation metrics
accuracy = accuracy_score(true_labels, predicted_labels)
f1_macro = f1_score(true_labels, predicted_labels, average="macro")
f1_micro = f1_score(true_labels, predicted_labels, average="micro")

# Print evaluation results in terminal
print("\n🔹 **Evaluation Metrics:**")
print(f"✅ Accuracy: {accuracy:.4f}")
print(f"✅ F1-Macro: {f1_macro:.4f}")
print(f"✅ F1-Micro: {f1_micro:.4f}")

# Generate Confusion Matrix
labels = sorted(set(true_labels + predicted_labels))  # Get all unique labels (now in text format)
cm = confusion_matrix(true_labels, predicted_labels, labels=labels)
cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100  # Convert to percentages

# Create annotation text for the confusion matrix
annot = np.empty_like(cm).astype(str)
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        count = cm[i, j]
        percent = cm_percent[i, j] if cm.sum(axis=1)[i] > 0 else 0
        annot[i, j] = f"{count} ({percent:.1f}%)" if count > 0 else "0"

# Plot Confusion Matrix
plt.figure(figsize=(12, 8))
ax = sns.heatmap(cm_percent, annot=annot, fmt="", cmap="Blues",
                 xticklabels=labels, yticklabels=labels)

# Titles and labels
plt.xlabel("Predicted Labels")
plt.ylabel("True Labels")
plt.title("Confusion Matrix (Count and Percentages)")

# Commented out: Add legend on the side since labels are now text
# class_labels = {
#     0: "0 - Description",
#     1: "1 - Feelings",
#     2: "2 - Evaluation/Analysis",
#     3: "3 - Conclusion/Action Plan",
# }
# legend_text = "\n".join([f"{key}: {value}" for key, value in class_labels.items()])
# plt.text(len(labels) + 0.5, len(labels) / 2, legend_text, fontsize=12,
#          verticalalignment="center", bbox={"facecolor": "white", "alpha": 0.6, "pad": 5})

# Compute additional statistics
total_samples = np.sum(cm)
correct_predictions = np.trace(cm)
accuracy_percentage = (correct_predictions / total_samples) * 100

# Display evaluation metrics in a box below the confusion matrix
metrics_text = f"Accuracy: {accuracy:.4f}\nF1-Macro: {f1_macro:.4f}\nF1-Micro: {f1_micro:.4f}"
plt.text(len(labels) + 0.5, len(labels) / 1.5, metrics_text, fontsize=12,
         verticalalignment="center", bbox={"facecolor": "lightgray", "alpha": 0.6, "pad": 5})

# Save confusion matrix
output_dir = "confusion_matrix"
os.makedirs(output_dir, exist_ok=True)
plot_filename = os.path.join(output_dir, args.output_filename)
plt.savefig(plot_filename, bbox_inches="tight")

# Print where the file is saved
print(f"\n📂 Updated Confusion Matrix saved to: {plot_filename}")

# Show plot
plt.show()
