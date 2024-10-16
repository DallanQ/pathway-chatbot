from llama_index.llms.openai import OpenAI
import os
import openai
import dotenv

dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(temperature=0)

# Definir el prompt para evaluar las respuestas
# Definir el prompt para evaluar las respuestas
def eval_prompt(question, ideal, generated, nodes):
    return f"""
    [BEGIN DATA]
    ************
    [Question]: {question}
    ************
    [Ideal Answer]: {ideal}
    ************
    [Generated Answer]: {generated}
    ************
    [Retrieved Content]: {nodes}
    ************
    [END DATA]

    Compare the factual content of the generated answer with the Ideal answer. Ignore any differences in style, grammar, or punctuation.
    The generated answer was given by a RAG model and you are testing. The RAG first retrieves content, then generates an answer based on that content. Determine which case applies. 

    Take into account the following exceptions:
    - If the generated answer is richer than the ideal answer but includes all the necessary information from the ideal answer and remains within the context without hallucinating, this is acceptable.
    - Sometimes, the generated answer may show an alternative, but well-founded way to achieve the goal of the ideal answer, as long as it is based on the retrieved content.

    Consider the following contextual definitions:
    - student portal = BYU-Pathway Portal
    - PathwayConnect program = program to gain skills for life and university
    - Online Degree program = program to gain a degree, also associate and certificates, this comes after the PathwayConnect program through BYU-Pathway

    Answer the question by selecting one of the following options:
    (1) generated answer disagrees with the ideal answer (a few of the gold answers disagree with the retrieved content - make a note of these cases)
    (2) generated answer contains significant facts that are not in the gold answer and are not in the retrieved content - hallucinations
    (3) no answer - generated answer is something like “I don’t know” but an ideal answer exists.
    (4) generated answer is only a partial answer - generated answer is more than "I don’t know", but the ideal answer contains significant facts that are not in the generated answer
    (5) the differences between ideal answer and generated answer are insignificant

    Analyze step by step. Compare each situation. Think carefully about your answer and then select the number that best fits the situation.

    Return your answer in this format (i.e.):
    (Number of the option that best fits the situation) - (short and direct justification)
    """



def evaluate_response(question, ideal, generated, nodes):
    prompt = eval_prompt(question, ideal, generated, nodes)
    response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI QA. You will give score to the answer.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
    
    score = response.choices[0].message.content
    return score