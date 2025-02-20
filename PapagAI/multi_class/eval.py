import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, f1_score, multilabel_confusion_matrix

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Evaluate multi-label classification and generate a confusion matrix.")
parser.add_argument("input_file", help="Path to the predictions TSV file")
parser.add_argument("output_file", help="Filename for the confusion matrix image (saved in data/confusion_matrix/)")
args = parser.parse_args()

# Load predictions
df = pd.read_csv(args.input_file, sep="\t")

# Convert labels and predictions to arrays
true_labels = np.array([eval(label) for label in df["label"]])  # Convert string lists to actual lists
predicted_labels = np.array([eval(pred) for pred in df["predicted"]])

# Define class names (Gibbs Cycle Categories)
class_names = ["Description", "Feelings", "Evaluation_Analysis", "Conclusion_Action_Plan"]

# Compute per-class accuracy and F1 scores
accuracy_per_class = [accuracy_score(true_labels[:, i], predicted_labels[:, i]) for i in range(len(class_names))]
f1_per_class = [f1_score(true_labels[:, i], predicted_labels[:, i]) for i in range(len(class_names))]

# Compute average accuracy and overall F1 scores
avg_accuracy = np.mean(accuracy_per_class)
f1_macro = f1_score(true_labels, predicted_labels, average="macro")
f1_micro = f1_score(true_labels, predicted_labels, average="micro")

# Compute multi-label confusion matrix
cm = multilabel_confusion_matrix(true_labels, predicted_labels)

# Generate Confusion Matrix
plt.figure(figsize=(10, 6))
cm_counts = np.array([[cm[i][1, 1], cm[i][0, 1], cm[i][1, 0], cm[i][0, 0]] for i in range(len(class_names))])  # TP, FP, FN, TN
cm_percent = cm_counts.astype("float") / cm_counts.sum(axis=1, keepdims=True) * 100

# Create annotations (Count and %)
annot = np.array([
    [f"{int(cm[i][1, 1])} ({cm_percent[i, 0]:.1f}%)",  # TP
     f"{int(cm[i][0, 1])} ({cm_percent[i, 1]:.1f}%)",  # FP
     f"{int(cm[i][1, 0])} ({cm_percent[i, 2]:.1f}%)",  # FN
     f"{int(cm[i][0, 0])} ({cm_percent[i, 3]:.1f}%)"]   # TN
    for i in range(len(class_names))
])

sns.heatmap(cm_percent[:, :2], annot=annot[:, :2], fmt="", cmap="Blues",
            xticklabels=["Predicted Positive", "Predicted Negative"],
            yticklabels=class_names)

# Titles and labels
plt.xlabel("Predicted Labels")
plt.ylabel("True Labels")
plt.title("Confusion Matrix (Per Gibbs Cycle Step)")

# Create box for average accuracy and per-class F1 scores
metrics_text = f"Average Accuracy: {avg_accuracy:.2f}\n"
metrics_text += "\n".join([f"{class_names[i]} - Acc: {accuracy_per_class[i]:.2f}, F1: {f1_per_class[i]:.2f}" for i in range(len(class_names))])
metrics_text += f"\n\nF1-Macro: {f1_macro:.2f}\nF1-Micro: {f1_micro:.2f}\n"
metrics_text += f"\nTotal Samples: {len(df)}"

# Add metrics box
plt.text(2.5, len(class_names) / 2, metrics_text, fontsize=12,
         verticalalignment="center", bbox={"facecolor": "lightgray", "alpha": 0.6, "pad": 5})

# Save confusion matrix
os.makedirs("data/confusion_matrix", exist_ok=True)
plot_filename = os.path.join("data/confusion_matrix", args.output_file)
plt.savefig(plot_filename, bbox_inches="tight")

# Print evaluation metrics in terminal
print("\n🔹 **Evaluation Metrics:**")
print(f"Average Accuracy: {avg_accuracy:.2f}")
for i, class_name in enumerate(class_names):
    print(f"{class_name} - Accuracy: {accuracy_per_class[i]:.2f}, F1: {f1_per_class[i]:.2f}")

print(f"\n✅ F1-Macro: {f1_macro:.2f}")
print(f"✅ F1-Micro: {f1_micro:.2f}")
print(f"\n📂 Updated Confusion Matrix saved to: {plot_filename}")

# Show plot
#plt.show()
