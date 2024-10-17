from llama_index.llms.openai import OpenAI
import os
import openai
import dotenv

dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(model="gpt-4o",temperature=0)

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
    The generated answer was produced by a RAG (Retrieval-Augmented Generation) model, and you are testing it. The RAG first retrieves content, then generates an answer based on that content. Your job is to determine whether the generated answer aligns factually with the ideal answer, using the following cases:

    Take into account the following exceptions:
    - If the generated answer is richer than the ideal answer but includes all the necessary information from the ideal answer and remains within the context without hallucinating, this is acceptable.
    - The generated answer may show an alternative but well-founded approach to addressing the question, as long as it is based on the retrieved content.

    Consider the following contextual definitions:
    - "Student portal" and "BYU-Pathway Portal" are the same.
    - PathwayConnect program: Program designed to gain skills for life and university.
    - Online Degree program: Program designed to gain a degree (including associate and certificates), typically pursued after the PathwayConnect program. Also referred as BYU-Pathway.
    - Friend of the Church: A non-member with a positive relationship to the Church.

    Use the following guidelines to score the generated answer:

    (1) **Disagrees with the ideal answer**: The generated answer disagrees with the ideal answer or contains a significant factual error not present in the ideal answer. (Note: Evaluate whether the generated content goes against retrieved content.)
    
    (2) **Contains hallucinations**: The generated answer introduces new information or facts that are not part of the ideal answer, the retrieved content, or the context.
    
    (3) **No answer**: The generated answer is "I don’t know," but an ideal answer exists. Use this if the model generates no substantive content but should have.
    
    (4) **Partial answer**: The generated answer includes some correct facts, but it omits critical parts of the ideal answer.
    
    (5) **Insignificant differences**: The generated answer might vary in phrasing or structure, but all key facts align with the ideal answer and no critical information is omitted.

    Think step by step and analyze the entire generated answer before giving your score. Compare each situation carefully. Then select the number that best fits the situation.

    Return your answer in this format:
    (Number) - (short and direct justification)
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