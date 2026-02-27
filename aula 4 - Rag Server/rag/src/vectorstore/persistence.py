from typing import List
from llama_index.core.schema import BaseNode
from llama_index.core.vector_stores.types import BasePydanticVectorStore
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class DocumentPersistenceResult(BaseModel):
    status: str = Field(..., examples=["success"])
    collection: Optional[str] = Field(None, examples=["cct_documents"])
    total_chunks: int
    timestamp: datetime

class DocumentPersistence:

    def __init__(self, vector_store: BasePydanticVectorStore):
        self._vector_store = vector_store

    def save(self, nodes: List[BaseNode]) -> DocumentPersistenceResult:
        if not nodes:
            raise ValueError("Nodes list cannot be empty")

        self._vector_store.add(nodes)

        collection_name = getattr(self._vector_store, "collection_name", None)

        return DocumentPersistenceResult(
            status="success",
            collection=collection_name,
            total_chunks=len(nodes),
            timestamp=datetime.now(),
        )
