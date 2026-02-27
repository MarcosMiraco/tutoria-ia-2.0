from fastapi import FastAPI
from api.routes import router
from contextlib import asynccontextmanager
from instances import get_vector_store

@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_vector_store()
    print("Vectorstore initialized at startup")
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
