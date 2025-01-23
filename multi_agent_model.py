# -*- coding: utf-8 -*-

# Commented out IPython magic to ensure Python compatibility.
# %%capture --no-stderr
# %pip install -U langchain_openai langgraph

import os, getpass
from google.colab import userdata
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import operator
from typing import List, Annotated, Dict
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
import pickle
from langgraph.constants import Send
import json
from typing import Dict, Any
from IPython.display import Image
from langgraph.graph import END, StateGraph, START
import warnings

"""## environment setting"""

# Ignore the specific Pydantic warning
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")


os.environ['OPENAI_API_KEY'] = userdata.get('OPENAI_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "langchain-academy"
os.environ['LANGCHAIN_API_KEY'] = userdata.get('LANGCHAIN_API_KEY')

# LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

"""## Objects define"""

class Analyst(BaseModel):
    affiliation: str = Field(
        description="Primary affiliation of the analyst.",
    )
    name: str = Field(
        description="Name of the analyst."
    )
    step_role: str = Field(
        description="Specific step of Gibbs’ Cycle assigned to the analyst",
    )
    description: str = Field(
        description="Description of the analyst focus, concerns, and motives.",
    )
    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.step_role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"

class Perspectives(BaseModel):
    analysts: List[Analyst] = Field(
        description="Comprehensive list of analysts with their roles and affiliations.",
    )

class FinalFeedback(BaseModel):
    grades: Dict[str, int] = Field(..., description="Grades for each step of Gibbs' Cycle.")
    feedback: str = Field(..., description="Overall feedback on the reflection.")

class OverallState(TypedDict):
    topic: str
    reflection_input:str
    question:str
    course_name:str
    analysts: List[Analyst] # Analyst asking questions
    judgements: Annotated[list, operator.add]
    final_summarized_output: str


class JudgementState(TypedDict):
    analyst:Analyst
    course_name: str = Field(..., description="Name of the course relevant to the reflection.")
    question: str = Field(..., description="The specific question prompting the reflection.")
    reflection_input: str

class Judgement(BaseModel):
    judgement: str = Field(None, description="Detailed feedback for the step.")

def get_analysts(state: OverallState):

    topic=state["topic"]
    with open('all_analyst_values.pickle', 'rb') as file:
      loaded_dict = pickle.load(file)

    analysts = loaded_dict[topic]
    # Write the list of analysis to state
    return {"analysts": analysts}


def continue_to_judgements(state: OverallState):
    return [Send("generate_judgement", {"analyst": a,
                                        "reflection_input": state["reflection_input"],
                                        "question":state["question"],
                                        "course_name":state["course_name"],
                                        }) for a in state["analysts"]]


def generate_judgement(state: JudgementState):
    # Get state
    analyst = state["analyst"]
    course_name = state["course_name"]
    question = state["question"]
    reflection_input = state["reflection_input"]

    # Generate judgement for specific reflection text
    system_message = judgement_instructions.format(persona=analyst.persona,
                                                   step_role=analyst.step_role,
                                                   course_name=course_name,
                                                   question=question,
                                                   reflection_input=reflection_input)
    structured_llm = llm.with_structured_output(Judgement)
    response = structured_llm.invoke([SystemMessage(content=system_message),
                                                             HumanMessage(content=reflection_input)])
    return {"judgements": [response.judgement]}


def final_feedback(state: OverallState):

    judgements = "\n\n".join(state["judgements"])
    prompt = final_feedback_instruction.format(topic=state["topic"],
                                               reflection_input=state['reflection_input'],
                                               analysts_judgments=judgements)
    response = llm.with_structured_output(FinalFeedback, method="json_mode").invoke(prompt)
    return {"final_summarized_output": [response.model_dump()]}

judgement_instructions = """
You are part of a team of analysts specializing in different steps of Gibbs’ Reflective Cycle. Based on your role, clearly identify and focus on the specific step assigned to you.
Your task is to analyze a student’s reflective response, focusing solely on the step aligned with your role.

**Instructions:**

1. Identify Your Step: Based on your assigned role ({step_role}), determine your focus within Gibbs' Reflective Cycle (Description, Feelings, Evaluation, Analysis, Conclusion, Action Plan).
2. Analyze the Reflection: Carefully examine the student's reflection, considering the course context and the teacher's question.
   - Reflection Text: {reflection_input}
   - Course Name: {course_name}
   - Teacher's Question: {question}
3. Evaluate the Step: Judge whether the student has adequately addressed your assigned step in their reflection. Provide a score of 0 or 1:
   - 1: The step is clearly present and well-developed.
   - 0: The step is missing or inadequately addressed.
4. Provide specific advise: Offer detailed and actionable feedback related to your assigned step. Focus on clarity, depth, relevance, and alignment with the overall reflection goals.
    - Strengths: Highlight what the student did well within this step.
    - Weaknesses: Identify areas needing improvement.
    - Suggestions: Offer concrete advice for improvement, such as adding details, clarifying ambiguous parts, or enhancing the depth of reflection.

Here are two examples for grading standards, for each analyst only grade one step and add your corresponding judgement to this step.
**Standard Example 1**
   {{ "reflection_text": "We believe that one of the biggest risks to the success of our project about a bank or financial We believe that data is very crucial for big companies. Namely \"data disclosure\" and \"accuracy of data\". Mistakes in handling sensitive data or inaccuracies in calculations could lead to major issues. Therefore, it could be very sensitive. To mitigate this, we will ensure we follow strict data security protocols, double-check all financial data, and adhere to the guidelines provided by the company we are working with. By staying doing so, we will be able to minimize the chances of risks affecting our project. Personally, as team leader, I will make sure to inform myself and my team what the company does want/not want us to release or mention in our project as confidential data.",
   "grades": {{ "description": 1, "feelings": 0, "evaluation": 1, "analysis": 0, "conclusion": 1, "action_plan": 1 }}}}

**Standard Example 2**
  {{"reflection_text": "I need to know my other peers a bit better before I can ask stupid questions. I usually feel confident enough though, to say what I need. I do spent a fair bit of energy on asking for a language to be spoken, that I can understand. That gets tiring after a while but it is better than being left out. I try to encourage the more quiet people in the group to voice their opinion and try to include them in the discussion. I try to stay mindful of my connections in the group and avoid talking to much with people who I already have good connections with but take the chance to get to know a lesser known person more. I avoid sarcasm as I find that can lead to misunderstandings. When discussion go nowhere and people ramble on I do retreat or try to divert the discussion back on track, depending on how much energy I have left in the battery.",
  "grades": {{ "description": 1, "feelings": 1, "evaluation": 1, "analysis": 1, "conclusion": 0, "action_plan": 0 }} }}

**Example of Analyst Output Format**
      - step: Description
      - score: 1
      - judgement: The reflection effectively describes the events within your team during the environmental protection project. You clearly outlined your role and how the work was distributed among team members.

"""

final_feedback_instruction = """

You are an experienced expert designed to provide constructive feedback on student reflections using Gibbs' Reflective Cycle.
Your task is to analyze the reflection question and student's reflection, identify strengths and weaknesses, and offer actionable suggestions for improvement, using judgments from expert analysts as reference.

Input:
    - Judgments: {analysts_judgments}
    - Reflection Text: {reflection_input}
    - Topic: {topic}

Instructions:

    1. Gather Information: Collect all grades and insights from analysts for each step of Gibbs’ Cycle.
	  2. Rank Step Importance: Determine the importance of the six steps based on the context of the question.
	  3. Encourage Deeper Reflection: Focus on the two most important steps, especially any missed critical ones, and pose open-ended questions to stimulate deeper thinking about those aspects.
	  4. Provide Actionable Suggestions: Offer tailored advice to address identified weaknesses, such as adding details, clarifying ambiguities, or enhancing the depth of reflection for specific steps of Gibbs’ Cycle.
    6. Maintain a Positive and Encouraging Tone: While providing constructive criticism, ensure the overall tone is supportive and encouraging. Emphasize the student's strengths and potential for growth.
    7. Conciseness: Your answer should only include evaluation and final feedback 2parts. Keep the feedback concise and within 100 words.

**Example of Output JSON structure**
  json {{ "grades": {{ "Description": 1, "Feelings": 0, "Evaluation": 0, "Analysis": 1, "Conclusion": 0, "Action Plan": 0 }}, "feedback": "You listed some great takeaways from the self-assessment. You said some work is needed for you to explore these topics more deeply - how can you start? What one thing can you experiment with? How would you like to check in with your progress 1 year from now?" }}
"""

"""## build langgraph"""

# Construct the graph: here we put everything together to construct our graph
graph = StateGraph(OverallState)
graph.add_node("create_analysts", get_analysts)
graph.add_node("generate_judgement", generate_judgement)
graph.add_node("final_feedback", final_feedback)
graph.add_edge(START, "create_analysts")
graph.add_conditional_edges("create_analysts", continue_to_judgements, ["generate_judgement"])
graph.add_edge("generate_judgement", "final_feedback")
graph.add_edge("final_feedback", END)

# Compile the graph
app = graph.compile()
Image(app.get_graph().draw_mermaid_png())


def analyze_reflection(topic, reflection_input, course_name, question):
    generated_messages = []
    for s in app.stream({"topic": topic,
                         "reflection_input": reflection_input,
                         "course_name": course_name,
                         "question": question
                        }):
        generated_messages.append(s)
    result = generated_messages[-1].get('final_feedback').get('final_summarized_output')[0]
    return result

if __name__ == "__main__":
    topic = input("Enter the topic: ")
    reflection_input = input("Enter the reflection input: ")
    course_name = input("Enter the course name: ")
    question = input("Enter the question: ")

    result = analyze_reflection(topic, reflection_input, course_name, question)
    print(result)