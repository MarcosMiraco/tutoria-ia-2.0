from typing import List, Any
from instances import get_vector_store
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
# from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModeModel
from llama_index.embeddings.ollama import OllamaEmbedding
from ingestion.filters import MetadataFilterFactory


class RetrievalService:
    _index: VectorIndexRetriever | None = None

    async def query(self, query_text: str, top_k: int, filter: dict ) -> List[Any]:
        vs = await get_vector_store()
        filters = MetadataFilterFactory.from_dict(filter) if filter else None
        
        storage_context = StorageContext.from_defaults(vector_store=vs)
        index = VectorStoreIndex.from_vector_store(
            vector_store=vs,
            storage_context=storage_context,
            response_mode="default",
            # embed_model=OpenAIEmbedding(
            #     model=OpenAIEmbeddingModeModel.TEXT_EMBED_3_LARGE
            # )            
            embed_model=OllamaEmbedding(model_name="nomic-embed-text", base_url="http://localhost:11434")
        )
        if filters:
            retriever = index.as_retriever(similarity_top_k=top_k, filters=filters)
        else:
            retriever = index.as_retriever(similarity_top_k=top_k)

        results = retriever.retrieve(query_text)

        docs_with_metadata = [
            {
                "doc": item.node.text,
                "metadata": getattr(item.node, "metadata", {})
            }
            for item in results
        ]

        return docs_with_metadata
