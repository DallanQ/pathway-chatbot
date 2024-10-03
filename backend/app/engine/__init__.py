import os

from app.engine.index import get_index
from app.engine.node_postprocessors import NodeCitationProcessor
from fastapi import HTTPException

from app.engine.custom_condense_plus_context import CustomCondensePlusContextChatEngine

def get_chat_engine(filters=None, params=None):
    system_prompt = os.getenv("SYSTEM_PROMPT")
    # citation_prompt = os.getenv("SYSTEM_CITATION_PROMPT", None)
    top_k = int(os.getenv("TOP_K", 3))

    node_postprocessors = []
    # if citation_prompt:
    #     node_postprocessors = [NodeCitationProcessor()]
    #     system_prompt = f"{system_prompt}\n{citation_prompt}"
    
    node_postprocessors = [NodeCitationProcessor()]
        
    index = get_index(params)
    if index is None:
        raise HTTPException(
            status_code=500,
            detail=str(
                "StorageContext is empty - call 'poetry run generate' to generate the storage first"
            ),
        )

    retriever = index.as_retriever(
        similarity_top_k=top_k,
        filters=filters,
    )

    SYSTEM_CITATION_PROMPT = """
    You are a helpful assistant who assists service missionaries with their BYU Pathway questions. You are responding with information from a knowledge base that consists of multiple nodes. Each node contains metadata such as node ID, file name, and other relevant details. To ensure accuracy and transparency, please include a citation for every fact or statement derived from the knowledge base.

    Use the following format for citations: [^context number], as the identifier of the data node.

    Example:
    We have two nodes:
      node_id: 1
      text: Information about how service missionaries support BYU Pathway students.

      node_id: 2
      text: Details on training for service missionaries.

    User question: How do service missionaries help students at BYU Pathway?
    Your answer:
    Service missionaries provide essential support by mentoring students and helping them navigate academic and spiritual challenges [^1]. They also receive specialized training to ensure they can effectively serve in this role [^2]. 

    Make sure each piece of referenced information is correctly cited. If you are unsure about a fact, provide clarification to the best of your ability.
    """

    CONTEXT_PROMPT = """
    Answer the question as truthfully as possible using the numbered contexts below. If the answer isn't in the text, please say "Sorry, I'm not able to answer this question. Could you rephrase it?" Please provide a detailed answer. For each sentence in your answer, include a link to the contexts the sentence came from using the format [^context number].

    Contexts:
    {context_str}
    
    Instruction: Based on the above documents, provide a detailed answer for the user question below. Ensure that each statement is clearly cited, e.g., "This is the answer based on the source [^1]. This is part of the answer [^2]..."
    """
    
    CONDENSE_PROMPT_TEMPLATE = """
    Based on the following follow-up question from the user,
    rephrase it to form a complete, standalone question.
    
    Follow Up Input: {question}
    Standalone question:
    """

    return CustomCondensePlusContextChatEngine.from_defaults(
        system_prompt=SYSTEM_CITATION_PROMPT,
        context_prompt=CONTEXT_PROMPT,
        condense_prompt=CONDENSE_PROMPT_TEMPLATE,
        retriever=retriever,
        node_postprocessors=node_postprocessors,
        verbose=True,
    )
