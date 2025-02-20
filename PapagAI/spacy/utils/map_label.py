import json
import argparse


def map_labels(input_file, output_file):
    label_mapping = {
        "0": "Description",
        "1": "Feelings",
        "2": "Evaluation",
        "3": "Analysis",
        "4": "Conclusion",
        "5": "Action_Plan"
    }

    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            data = json.loads(line.strip())
            if "answer" in data:
                data["answer"] = label_mapping.get(str(data["answer"]), "Unknown")
            outfile.write(json.dumps(data) + '\n')

    print(f"Processed file saved as: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Map numerical labels to descriptive text labels in a JSONL file.")
    parser.add_argument("input_file", help="Path to the input JSONL file")
    parser.add_argument("output_file", help="Path to save the output JSONL file with mapped labels")

    args = parser.parse_args()
    map_labels(args.input_file, args.output_file)
