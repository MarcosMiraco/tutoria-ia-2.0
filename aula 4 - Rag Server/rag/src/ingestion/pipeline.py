
from llama_index.core.ingestion import IngestionPipeline
# from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModeModel
from llama_index.embeddings.ollama import OllamaEmbedding
from ingestion.loaders import LoaderStrategy, LoaderRegistry
from ingestion.chunker import ChunkerStrategy,ChunkerRegistry
from ingestion.transformers import apply_document_transforms
from dotenv import load_dotenv

load_dotenv()

class IngestionPipelineFactory:
    def __init__(
            self, 
            loader_type: str, 
            source: str, 
            chunker_type: str, 
            transform_types: list[str]
        ):
        self.loader: LoaderStrategy = LoaderRegistry.create(loader_type)
        self.source = source
        self.chunker: ChunkerStrategy = ChunkerRegistry.create(chunker_type)
        self.doc_transf_pipeline = transform_types

    def ingest(self):
        # DATASOURCE LOADER
        docs = self.loader.load(self.source)
        # TRANSFORMERS
        docs = apply_document_transforms(docs, self.doc_transf_pipeline)

        transformations = [
            self.chunker.get_transform(),
            # OpenAIEmbedding(
            #     model=OpenAIEmbeddingModeModel.TEXT_EMBED_3_LARGE
            # ),
            OllamaEmbedding(model_name="nomic-embed-text", base_url="http://localhost:11434")
        ]
        # CHUNK/EMBED
        pipeline = IngestionPipeline(
            transformations=transformations
        )
        nodes = pipeline.run(documents=docs)

        return nodes