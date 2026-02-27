from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Any, Optional
from services.ingestion import IngestionService
from services.retrieval import RetrievalService

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    filters: Optional[dict] = None

class QueryResponse(BaseModel):
    results: List[Any]

class EmbedRequest(BaseModel):
    loader_type: str
    chunker_type: str
    source: str
    transform_pipeline: List[str]

class EmbedResponse(BaseModel):
    status: str

ingestion_service = IngestionService()
retrieval_service = RetrievalService()

@router.post("/query", response_model=QueryResponse)
async def query_docs(request: QueryRequest):
    try:
        print(request)
        results = await retrieval_service.query(
            query_text=request.query,
            top_k=request.top_k,
            filter= request.filters
        )
        return QueryResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/docs/ingest", response_model=EmbedResponse)
async def embed_docs(request: EmbedRequest):
    try:
        status = await ingestion_service.run_ingestion(
            loader_type=request.loader_type,
            source=request.source,
            chunker_type=request.chunker_type,
            transform_types=request.transform_pipeline
        )
        return EmbedResponse(status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/vs/reset")
async def reset_store():
    """
    Endpoint que deleta tudo no vector store instanciado -- dev only
    """
    result = await ingestion_service.reset()

    return result