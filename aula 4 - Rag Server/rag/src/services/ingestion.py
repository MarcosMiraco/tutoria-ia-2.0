from ingestion.pipeline import IngestionPipelineFactory
from instances import get_vector_store
from vectorstore.persistence import DocumentPersistence
from vectorstore.reset import reset_vector_store

class IngestionService:
    async def run_ingestion(self, loader_type: str, source: str, chunker_type: str, transform_types: list[str]):
        """
        Runs the ingestion pipeline with the provided parameters.
        """
        vs = await get_vector_store()

        pipeline = IngestionPipelineFactory(
            loader_type=loader_type,
            source=source,
            chunker_type=chunker_type,
            transform_types=transform_types
        )
        nodes = pipeline.ingest()
        if not nodes:
            raise ValueError("No nodes were ingested from the pipeline.")
        
        persistence = DocumentPersistence(vector_store=vs)

       # FOR DEBUG
        # last_nodes = nodes[:2]
        # for i, node in enumerate(last_nodes, start=1):
        #     print(f"\n--- Chunk {i} ---")
        #     print("Metadata:", node.metadata)
        #     print("Content:")
        #     print(node.get_content())
        # return "ok"
        result = persistence.save(nodes)

        return result.status 

    async def reset(self):
       vs = await get_vector_store()
       return reset_vector_store(vector_store=vs)
