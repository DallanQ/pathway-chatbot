import logging
from typing import Tuple, List, Dict, Any
from collections import defaultdict
import traceback
import sys

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from llama_index.core.chat_engine.types import BaseChatEngine, NodeWithScore
from llama_index.core.llms import MessageRole

from app.api.routers.events import EventCallbackHandler
from app.api.routers.models import (
    ChatData,
    Message,
    Result,
    SourceNodes,
    ThumbsRequest,
)
from app.api.routers.vercel_response import VercelStreamResponse
from app.engine import get_chat_engine
from app.engine.query_filter import generate_filters
from langfuse.decorators import langfuse_context, observe
from app.langfuse import langfuse

chat_router = r = APIRouter()

logger = logging.getLogger("uvicorn")


def _log_exception_trace():
    """
    Log the full exception traceback when an exception occurs.
    Should be called within an except block.
    """
    exc_info = sys.exc_info()
    if exc_info[0] is not None:  # If there's an active exception
        exc_trace = "".join(traceback.format_exception(*exc_info))
        logger.error(f"Exception traceback:\n{exc_trace}")


# streaming endpoint - delete if not needed
@r.post("")
@observe()
async def chat(
    request: Request,
    data: ChatData,
    background_tasks: BackgroundTasks,
):
    try:
        last_message_content = data.get_last_message_content()
        # Delete the chat_history of the engine and
        data.clear_chat_messages()
        messages = data.get_history_messages()

        doc_ids = data.get_chat_document_ids()
        filters = generate_filters(doc_ids)
        params = data.data or {}
        logger.info(
            f"Creating chat engine with filters: {str(filters)}",
        )
        chat_engine = get_chat_engine(filters=filters, params=params)
        # Delete the chat_history from the chat_engine
        chat_engine.reset()

        event_handler = EventCallbackHandler()
        chat_engine.callback_manager.handlers.append(event_handler)  # type: ignore

        response = await chat_engine.astream_chat(last_message_content, messages)

        retrieved = "\n\n".join(
            [
                f"node_id: {idx+1}\n{node.metadata['url']}\n{node.text}"
                for idx, node in enumerate(response.source_nodes)
            ]
        )

        # await response.aprint_response_stream()
        tokens = []
        async for token in response.async_response_gen():
            tokens.append(token)

        langfuse_context.update_current_trace(
            input=last_message_content, output=response.response, metadata=retrieved
        )

        trace_id = langfuse_context.get_current_trace_id()
        logger.info(f"We got the trace id to be : {trace_id}")

        return VercelStreamResponse(
            request, event_handler, response, data, tokens, trace_id=trace_id
        )
        # return VercelStreamResponse(request, event_handler, response, data, tokens)
    except Exception as e:
        logger.exception("Error in chat engine", exc_info=True)
        _log_exception_trace()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in chat engine: {e}",
        ) from e


# non-streaming endpoint - delete if not needed
@r.post("/request")
@observe()
async def chat_request(
    data: ChatData,
) -> Result:
    try:
        last_message_content = data.get_last_message_content()
        # Delete the chat_history of the engine and
        data.clear_chat_messages()
        messages = data.get_history_messages()

        doc_ids = data.get_chat_document_ids()
        filters = generate_filters(doc_ids)
        params = data.data or {}
        logger.info(
            f"Creating chat engine with filters: {str(filters)}",
        )
        chat_engine = get_chat_engine(filters=filters, params=params)
        # Delete the chat_history from the chat_engine
        chat_engine.reset()

        response = await chat_engine.achat(last_message_content, messages)

        retrieved = "\n\n".join(
            [
                f"node_id: {idx+1}\n{node.metadata['url']}\n{node.text}"
                for idx, node in enumerate(response.source_nodes)
            ]
        )

        # Set the input, output and metadata of Langfuse
        langfuse_context.update_current_trace(
            input=last_message_content,
            output=response.response,
            metadata={"nodes": retrieved},
        )

        # Get the trace_id of Langfuse
        trace_id = langfuse_context.get_current_trace_id()
        logger.info(f"We got the trace id to be : {trace_id}")

        # Delete the chat_history from the chat_engine
        chat_engine.reset()

        return Result(
            result=Message(
                role=MessageRole.ASSISTANT, content=response.response, trace_id=trace_id
            ),
            nodes=SourceNodes.from_source_nodes(response.source_nodes),
        )
    except Exception as e:
        logger.exception("Error in chat_request", exc_info=True)
        _log_exception_trace()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in chat engine: {e}",
        ) from e


@r.post("/thumbs_request")
async def thumbs_request(request: ThumbsRequest):
    trace_id = request.trace_id
    value = request.value
    score_id = f'{trace_id}_feedback'

    langfuse.score(
        id=score_id,
        trace_id=trace_id,
        name="user_feedback",
        data_type="CATEGORICAL",
        value=value,
    )

    return {"feedback": value}


def split_header_content(text: str) -> Tuple[str, str]:
    lines = text.split("\n", 1)
    if len(lines) > 1:
        return lines[0] + "\n", lines[1]
    return "", text


def organize_nodes(nodes: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    # Step 1: Group nodes by page (URL)
    pages = defaultdict(list)
    for node in nodes:
        url = node.metadata["url"]
        pages[url].append(node)

    # Step 2: Order nodes on each page by sequence number
    for url, page_nodes in pages.items():
        pages[url] = sorted(page_nodes, key=lambda x: x.metadata["sequence"])

    # Step 3: Merge overlapping nodes
    organized_pages = {}
    for url, page_nodes in pages.items():
        merged_nodes = merge_nodes_with_headers(page_nodes)
        organized_pages[url] = merged_nodes

    return organized_pages


def merge_nodes_with_headers(nodes: List[Dict[str, Any]]) -> List[str]:
    merged_results = []
    current_merged = ""
    current_header = ""

    for node in nodes:
        node_text = node.text
        header, content = split_header_content(node_text)

        if header != current_header:
            if current_merged:
                merged_results.append(current_header + current_merged)
            current_header = header
            current_merged = content
        else:
            current_merged = merge_content(current_merged, content)

    if current_merged:
        merged_results.append(current_header + current_merged)

    return merged_results


def split_header_content(text: str) -> Tuple[str, str]:
    lines = text.split("\n", 1)
    if len(lines) > 1:
        return lines[0] + "\n", lines[1]
    return "", text


def merge_content(existing: str, new: str) -> str:
    # This is a simple merge function. You might need to implement
    # a more sophisticated merging logic based on your specific requirements.
    combined = existing + " " + new
    words = combined.split()
    return " ".join(sorted(set(words), key=words.index))


def process_response_nodes(
    nodes: List[NodeWithScore],
    background_tasks: BackgroundTasks,
):
    # organize_nodes(nodes)

    try:
        # Start background tasks to download documents from LlamaCloud if needed
        from app.engine.service import LLamaCloudFileService

        LLamaCloudFileService.download_files_from_nodes(nodes, background_tasks)
    except ImportError:
        logger.debug("LlamaCloud is not configured. Skipping post processing of nodes")
        pass
