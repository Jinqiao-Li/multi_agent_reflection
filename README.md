# Project Overview

This project contains a multi-agent model designed to generate feedback for students' reflective writing tasks.

![Framework Overview](images/framework.png)

## File Descriptions

### Root Directory

1. **`multi_agent_model.py`**  
   This file contains the implementation of the multi-agent model used for generating feedback.

2. **`Evaluation.ipynb`**  
   This notebook provides examples of how to use the `multi_agent_model` on individual examples and datasets.

3. **`all_analyst_value.pickle`**  
   This pre-generated file includes analyst groups for each topic. It is utilized by the `multi_agent_model` when the `topic` variable is defined.

### Data Folder

1. **`50_evaluation_human.xlsx`**  
   Contains 50 records that were manually evaluated. This dataset can serve as the gold standard for testing and validating the model.

2. **`50_evaluation_gpt_4o.xlsx`**  
   Includes 50 records evaluated by the multi-agent model for comparison with the manually evaluated dataset.
