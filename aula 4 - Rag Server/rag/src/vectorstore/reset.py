# reset.py
from typing import Optional
from llama_index.vector_stores.milvus.base import MilvusVectorStore
from pydantic import BaseModel
from pymilvus import utility

class ResetResult(BaseModel):
    success: bool
    message: str
    collections_deleted: int = 0

def _get_milvus_conn(vector_store: MilvusVectorStore) -> Optional[str]:
    """
    Return the connection alias to use with pymilvus utility functions.
    """
    if hasattr(vector_store, "_milvusclient"):
        return vector_store._milvusclient._using  # sync client alias
    if hasattr(vector_store, "_async_milvusclient"):
        return vector_store._async_milvusclient._using  # async client alias
    return None

def reset_vector_store(vector_store: MilvusVectorStore) -> ResetResult:
    """
    Deletes all collections accessible via the given Milvus vector store.
    """
    conn_alias = _get_milvus_conn(vector_store)
    if conn_alias is None:
        raise ValueError("Vector store does not expose a Milvus client")

    # list collections
    collections = utility.list_collections(using=conn_alias)
    if not collections:
        return ResetResult(success=True, message="No collections to delete.", collections_deleted=0)

    # delete each collection
    for coll in collections:
        utility.drop_collection(coll, using=conn_alias)
        print(f"Collection {coll} deleted.")

    return ResetResult(
        success=True,
        message=f"{len(collections)} collections deleted.",
        collections_deleted=len(collections)
    )
