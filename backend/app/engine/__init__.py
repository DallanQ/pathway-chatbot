import os

from app.engine.index import get_index
from app.engine.node_postprocessors import NodeCitationProcessor
from fastapi import HTTPException
from llama_index.core.vector_stores.types import VectorStoreQueryMode

from app.engine.custom_condense_plus_context import CustomCondensePlusContextChatEngine

def get_chat_engine(filters=None, params=None) -> CustomCondensePlusContextChatEngine:
    system_prompt = os.getenv("SYSTEM_PROMPT")
    # citation_prompt = os.getenv("SYSTEM_CITATION_PROMPT", None)
    top_k = int(os.getenv("TOP_K", 3))

    node_postprocessors = []
    
    node_postprocessors = [NodeCitationProcessor()]
        
    index = get_index(params)
    if index is None:
        raise HTTPException(
            status_code=500,
            detail=str(
                "StorageContext is empty - call 'poetry run generate' to generate the storage first"
            ),
        )

    retriever_k = 35
    sparse_k = retriever_k * 5
    query_mode = VectorStoreQueryMode.DEFAULT

    retriever = index.as_retriever(
        vector_store_query_mode=query_mode,
        similarity_top_k=retriever_k,
        sparse_top_k=sparse_k,
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

    Make sure each piece of referenced information is correctly cited. **If the information required to answer the question is not available in the retrieved nodes, respond with: "Sorry, I don't know."**

    Keep the description of the following terms in mind when you are asked questions about them:
    Friend of the Church: A term used to describe individuals who are not members of The Church of Jesus Christ of Latter-day Saints.
    Service Missionary: A church volunteer who serves as a guide and support for BYU Pathway students.
    BYU Pathway: A program that offers online courses to help individuals gain education and improve their lives.
    Peer mentor: Bloom staff who are also BYU Pathway students provide guidance and support to the students assigned to them. Mentors are helpful for students not for missionaries.
    Gathering: It can be online or in-person. Students must comply with attendance policies depending on whether it is online or in-person.
    
    
    Audience: Your primary audience is service missionaries.
    
    Instruction: You must tailor your responses based on the audience. If the question is related to service missionaries (e.g., "How can I get help with a broken link?"), provide information specifically for missionaries. If the question is about students, respond with information directed at students. Always keep the focus relevant to the specific audience based on the context of the question.
    
    Example:
    
    Question: "How can I get help with a broken link?" (from a missionary)
    Response: Provide resources specific to missionaries.
    Question: "How can I access the student portal?" (from a student)
    Response: Provide information specific to students.

    
    Follow this steps in the situations below:
    - questions about zoom and canvas, respond only based on the retrieved nodes and not make assumptions.
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
    Standalone question:"""

    return CustomCondensePlusContextChatEngine.from_defaults(
        system_prompt=SYSTEM_CITATION_PROMPT,
        context_prompt=CONTEXT_PROMPT,
        condense_prompt=CONDENSE_PROMPT_TEMPLATE,
        skip_condense=True,
        retriever=retriever,
        node_postprocessors=node_postprocessors,
        verbose=True,
        chat_history=None,
        memory=None
    )
