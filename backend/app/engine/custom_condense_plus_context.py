import asyncio
import logging
from typing import Any, List, Optional, Tuple, Dict
from collections import defaultdict
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.indices.query.schema import QueryBundle
from llama_index.core.schema import MetadataMode, NodeWithScore
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.callbacks import CallbackManager, trace_method
from llama_index.core.types import Thread
from llama_index.core.schema import TextNode, NodeWithScore


from app.engine.custom_node_with_score import CustomNodeWithScore

from llama_index.core.chat_engine.types import (
    AgentChatResponse,
    BaseChatEngine,
    StreamingAgentChatResponse,
    ToolOutput,
)


logger = logging.getLogger(__name__)

def node_to_dict(node) -> Dict[str, Any]:
    return {
        'text': node.get_text(),
        'metadata': node.metadata
    }

# Modified organize_nodes to handle dictionary keys
def organize_nodes(nodes: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    # Step 1: Group nodes by page (URL)
    pages = defaultdict(list)
    for node in nodes:
        url = node['metadata']['url']  # Access 'metadata' using dictionary key
        pages[url].append(node)
    
    # Step 2: Order nodes on each page by sequence number
    for url, page_nodes in pages.items():
        pages[url] = sorted(page_nodes, key=lambda x: x['metadata']['sequence'])
    
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
        node_text = node['text']  # Access 'text' using dictionary key
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
    lines = text.split('\n', 1)
    if len(lines) > 1:
        return lines[0] + '\n', lines[1]
    return '', text

def merge_content(existing: str, new: str) -> str:
    combined = existing + ' ' + new
    words = combined.split()
    return ' '.join(sorted(set(words), key=words.index))

class CustomCondensePlusContextChatEngine(CondensePlusContextChatEngine):

    def _retrieve_context(self, message: str) -> Tuple[str, List[CustomNodeWithScore]]:
        """Build context for a message from retriever."""
        nodes = self._retriever.retrieve(message)
        for postprocessor in self._node_postprocessors:
            nodes = postprocessor.postprocess_nodes(
                nodes, query_bundle=QueryBundle(message)
            )

        # Step 1: Organize nodes based on the provided utility functions
        nodes_list = [node_to_dict(node) for node in nodes]  # Convert nodes to dictionary format
        organized_nodes = organize_nodes(nodes_list)
        # logging.debug(organized_nodes)

        # Step 2: Custom formatting of context_str
        context_str = "We have {} nodes grouped by URLs:\n".format(len(organized_nodes))
        nodes_with_citation_node_id = []
        
        node_counter = 1
        for url, grouped_nodes in organized_nodes.items():
            context_str += f'URL: {url}\n'
            for node_text in grouped_nodes:
                context_str += f'node_id: {node_counter}\ntext: {node_text}\n\n'
                
                # Create a new TextNode instance with the correct attributes
                new_node = TextNode(
                    text=node_text,
                    metadata={"url": url}
                )
                
                # Create a new CustomNodeWithScore using the TextNode instance
                custom_node_with_score = CustomNodeWithScore(
                    node=new_node,  # Pass the TextNode instance
                    score=None
                )
                custom_node_with_score.citation_node_id = str(node_counter)
                nodes_with_citation_node_id.append(custom_node_with_score)
                node_counter += 1

        return context_str, nodes_with_citation_node_id

    async def _aretrieve_context(self, message: str) -> Tuple[str, List[CustomNodeWithScore]]:
        """Build context for a message from retriever asynchronously."""
        nodes = await self._retriever.aretrieve(message)
        for postprocessor in self._node_postprocessors:
            nodes = postprocessor.postprocess_nodes(
                nodes, query_bundle=QueryBundle(message)
            )

        # Step 1: Organize nodes based on the provided utility functions
        nodes_list = [node_to_dict(node) for node in nodes]  # Convert nodes to dictionary format
        organized_nodes = organize_nodes(nodes_list)
        # logging.debug(organized_nodes)

        # Step 2: Custom formatting of context_str
        context_str = "We have {} nodes grouped by URLs:\n".format(len(organized_nodes))
        nodes_with_citation_node_id = []
        
        node_counter = 1
        for url, grouped_nodes in organized_nodes.items():
            context_str += f'URL: {url}\n'
            for node_text in grouped_nodes:
                context_str += f'node_id: {node_counter}\ntext: {node_text}\n\n'
                
                # Create a new TextNode instance with the correct attributes
                new_node = TextNode(
                    text=node_text,
                    metadata={"url": url}
                )

                # Create a new CustomNodeWithScore using the TextNode instance
                custom_node_with_score = CustomNodeWithScore(
                    node=new_node,  # Pass the TextNode instance
                    score=None
                )
                custom_node_with_score.citation_node_id = str(node_counter)
                nodes_with_citation_node_id.append(custom_node_with_score)
                node_counter += 1

        return context_str, nodes_with_citation_node_id
