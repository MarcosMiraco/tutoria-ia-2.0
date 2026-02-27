from typing import Protocol
from llama_index.core.vector_stores.types import BasePydanticVectorStore
from typing import Type, Dict
from llama_index.vector_stores.milvus import MilvusVectorStore

class VectorStoreStrategy(Protocol):
    def build(self, **kwargs) -> BasePydanticVectorStore:
        ...

class VectorStoreFactory:
    _registry: Dict[str, Type[VectorStoreStrategy]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(strategy_cls: Type[VectorStoreStrategy]):
            cls._registry[name] = strategy_cls
            return strategy_cls
        return decorator

    @classmethod
    def create(cls, name: str, **kwargs) -> BasePydanticVectorStore:
        if name not in cls._registry:
            raise ValueError(f"VectorStore '{name}' not registered")

        strategy = cls._registry[name]()
        return strategy.build(**kwargs)
    

@VectorStoreFactory.register("milvus")
class MilvusVectorStoreStrategy:

    def build(
        self,
        collection_name: str,
        dim: int,
        uri: str = "http://localhost:19530",
        metric_type: str = "COSINE",
        M: int = 32,
        ef_construction: int = 300,
    ):
        return MilvusVectorStore(
            collection_name=collection_name,
            dim=dim,
            uri=uri,
            overwrite=False,
            index_config={
                "index_type": "HNSW",
                "metric_type": metric_type,
                "params": {
                    "M": M,
                    "efConstruction": ef_construction,
                },
            },
        )
    
    