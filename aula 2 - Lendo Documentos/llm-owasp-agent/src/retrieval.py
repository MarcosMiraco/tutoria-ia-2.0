from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def load_retrieval():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2") 
    loaded_vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    retriever = loaded_vectorstore.as_retriever(kwargs={ "search_type": "similarity", "search_kwargs": { "k": 5 }})
    return retriever


