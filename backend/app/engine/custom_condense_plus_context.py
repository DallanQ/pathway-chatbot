import asyncio
import logging
from typing import Any, List, Optional, Tuple
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

        # Custom formatting of context_str
        context_str = "We have {} nodes:\n".format(len(nodes))
        
        nodes_with_citation_node_id = []
        
        for i, node in enumerate(nodes, start=1):
            context_str += f'node_id: {i}\ntext: {node.get_text()}\n\n'

            # Create a new node with citation_node_id
            new_node = CustomNodeWithScore(node=node.node, score=node.score)

            # Assing citation_node_id to the new node
            new_node.citation_node_id = str(i)
            nodes_with_citation_node_id.append(new_node)
            
        return context_str, nodes

    async def _aretrieve_context(self, message: str) -> Tuple[str, List[CustomNodeWithScore]]:
        """Build context for a message from retriever asynchronously."""
        nodes = await self._retriever.aretrieve(message)
        for postprocessor in self._node_postprocessors:
            nodes = postprocessor.postprocess_nodes(
                nodes, query_bundle=QueryBundle(message)
            )
            
        # Custom formatting of context_str
        context_str = "We have {} nodes:\n".format(len(nodes))
        
        nodes_with_citation_node_id = []
        
        for i, node in enumerate(nodes, start=1):
            context_str += f'node_id: {i}\ntext: {node.get_text()}\n\n'

            # Create a new node with citation_node_id
            new_node = CustomNodeWithScore(node=node.node, score=node.score)

            # Assing citation_node_id to the new node
            new_node.citation_node_id = str(i)
            nodes_with_citation_node_id.append(new_node)

        return context_str, nodes_with_citation_node_id
