This folder includes the multi-agent model only in 3 dimentions.

- Experience = Description + Feelings  
- Analysis = Evaluation + Analysis  
- Action = Conclusion + Action Plan
  
**Model**: GPT-4.1-mini

# Evaluation Results

## Performance Metrics (with middle judgements)
**Time**: ～ 4s-7s

| Dimension         | Accuracy | F1 Score | Recall  |
|------------------|----------|----------|---------|
| is_reflection     | 0.80     | 0.8889   | 1.0000  |
| Experience        | 0.62     | 0.4571   | 0.2963  |
| Analysis          | 0.70     | 0.3473   | 0.2105  |
| Action            | 0.84     | 0.4286   | 0.3333  |

## Performance Metrics (**without** middle judgements)
**Time**: ～ 2s-5s
| Dimension         | Accuracy | F1 Score | Recall  |
|------------------|----------|----------|---------|
| is_reflection     | 0.94     | 0.9629   | 0.9750  |
| Experience        | 0.66     | 0.6792   | 0.6667  |
| Analysis          | 0.68     | 0.2727   | 0.1579  |
| Action            | 0.86     | 0.6316   | 0.6667  |

# Files & Folder
## Prompts Files:
 - final_feedback_instrction.py
 - analysts_judgements_instruction.py
 - analysts_no_judgements.py

## Analysts Persona File:
 - three_analyst_values.pickle

## Predictions:
 - results_41mini_no_judgements.xlsx
 - results_41mini.xlsx
  


