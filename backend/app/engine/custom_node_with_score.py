from typing import Optional
from llama_index.core.schema import NodeWithScore

class CustomNodeWithScore(NodeWithScore):
    citation_node_id: Optional[str] = None