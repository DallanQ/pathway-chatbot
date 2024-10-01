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


from app.engine.custom_node_with_score import CustomNodeWithScore

from llama_index.core.chat_engine.types import (
    AgentChatResponse,
    BaseChatEngine,
    StreamingAgentChatResponse,
    ToolOutput,
)


logger = logging.getLogger(__name__)

class CustomCondensePlusContextChatEngine(CondensePlusContextChatEngine):
    
    def _retrieve_context(self, message: str) -> Tuple[str, List[NodeWithScore]]:
        """Build context for a message from retriever."""
        nodes = self._retriever.retrieve(message)
        for postprocessor in self._node_postprocessors:
            nodes = postprocessor.postprocess_nodes(
                nodes, query_bundle=QueryBundle(message)
            )
        print(len(nodes))

        # **Organize nodes using the earlier functions**
        organized_nodes = self._organize_nodes(nodes)
        print(len(organized_nodes))

        # Custom formatting of context_str
        context_str = "We have {} nodes:\n".format(len(organized_nodes))
        
        nodes_with_citation_node_id = []
        
        for i, node_with_score in enumerate(organized_nodes, start=1):
            node_text = node_with_score.node.get_text()
            context_str += f'node_id: {i}\ntext: {node_text}\n\n'

            # Create a new node with citation_node_id
            new_node = CustomNodeWithScore(node=node_with_score.node, score=node_with_score.score)

            # Assign citation_node_id to the new node
            new_node.citation_node_id = str(i)
            nodes_with_citation_node_id.append(new_node)
            
        return context_str, nodes_with_citation_node_id

    async def _aretrieve_context(self, message: str) -> Tuple[str, List[CustomNodeWithScore]]:
        """Build context for a message from retriever asynchronously."""
        nodes = await self._retriever.aretrieve(message)
        for postprocessor in self._node_postprocessors:
            nodes = postprocessor.postprocess_nodes(
                nodes, query_bundle=QueryBundle(message)
            )
        print(len(nodes))
        # **Organize nodes using the earlier functions**
        organized_nodes = self._organize_nodes(nodes)
        print(len(organized_nodes))

        # Custom formatting of context_str
        context_str = "We have {} nodes:\n".format(len(organized_nodes))
        
        nodes_with_citation_node_id = []
        
        for i, node_with_score in enumerate(organized_nodes, start=1):
            node_text = node_with_score.node.get_text()
            context_str += f'node_id: {i}\ntext: {node_text}\n\n'

            # Create a new node with citation_node_id
            new_node = CustomNodeWithScore(node=node_with_score.node, score=node_with_score.score)

            # Assign citation_node_id to the new node
            new_node.citation_node_id = str(i)
            nodes_with_citation_node_id.append(new_node)

        return context_str, nodes_with_citation_node_id

    def _organize_nodes(self, nodes: List[NodeWithScore]) -> List[NodeWithScore]:
        """Organize nodes by URL, sequence, and merge overlapping nodes."""
        # Step 1: Group nodes by page (URL)
        pages = defaultdict(list)
        for node_with_score in nodes:
            node = node_with_score.node
            url = node.metadata.get('url', 'unknown_url')
            pages[url].append(node_with_score)
        
        # Step 2: Order nodes on each page by sequence number
        for url, page_nodes in pages.items():
            pages[url] = sorted(page_nodes, key=lambda x: x.node.metadata.get('sequence', 0))
        
        # Step 3: Merge overlapping nodes
        organized_nodes = []
        for url, page_nodes in pages.items():
            merged_nodes = self._merge_nodes_with_headers(page_nodes)
            organized_nodes.extend(merged_nodes)
        
        return organized_nodes

    def _merge_nodes_with_headers(self, nodes: List[NodeWithScore]) -> List[NodeWithScore]:
        """Merge nodes with the same headers and remove duplicate words."""
        merged_results = []
        current_merged_text = ""
        current_header = ""
        current_node_with_score = None

        for node_with_score in nodes:
            node = node_with_score.node
            node_text = node.get_text()
            header, content = self._split_header_content(node_text)

            if header != current_header:
                if current_node_with_score:
                    # Update the text of the current node
                    current_node_with_score.node.text = current_header + current_merged_text
                    merged_results.append(current_node_with_score)
                current_header = header
                current_merged_text = content
                current_node_with_score = node_with_score
            else:
                # Merge content and update score
                current_merged_text = self._merge_content(current_merged_text, content)
                # Example: average the scores
                current_node_with_score.score = (current_node_with_score.score + node_with_score.score) / 2

        if current_node_with_score:
            # Update the text of the last node
            current_node_with_score.node.text = current_header + current_merged_text
            merged_results.append(current_node_with_score)
        
        return merged_results

    def _split_header_content(self, text: str) -> Tuple[str, str]:
        """Split the text into header and content."""
        lines = text.split('\n', 1)
        if len(lines) > 1:
            return lines[0] + '\n', lines[1]
        return '', text

    def _merge_content(self, existing: str, new: str) -> str:
        """Merge two content strings, removing duplicate words."""
        combined = existing + ' ' + new
        words = combined.split()
        return ' '.join(sorted(set(words), key=words.index))
