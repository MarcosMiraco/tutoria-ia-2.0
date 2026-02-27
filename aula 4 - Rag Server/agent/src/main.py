
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from controller.route import router

app = FastAPI()

# Habilita CORS para o frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)