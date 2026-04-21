from vectorstore.connection import VectorStoreFactory
import asyncio

vector_store = None
_init_lock = asyncio.Lock() 

async def get_vector_store():
    global vector_store
    if vector_store is None:
        async with _init_lock:
            if vector_store is None:
                vector_store = VectorStoreFactory.create(
                    "milvus",
                    collection_name="cct_docs",
                    # dim=3072,
                    dim=768,
                    uri="http://localhost:19530",
                    metric_type="COSINE",
                    M=32,
                    ef_construction=300
                )
                
    return vector_store


