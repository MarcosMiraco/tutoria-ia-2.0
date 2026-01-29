#EMBEDDING PHASE
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings  # Free local embeddings

from ingestion import get_markdown_doc
from chunking import get_doc_chunks

def create_vectorstore_with_embeddings(chunks) :
    print("CRIANDO VECTORSTORE")
    # Assume 'chunks' is list of Document from splitter (e.g., md_chunks)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # ~22MB local model

    # One-liner: embeds + indexes all chunks
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # Persist locally (optional)
    vectorstore.save_local("faiss_index")


doc = get_markdown_doc()

chunks = get_doc_chunks(doc)

create_vectorstore_with_embeddings(chunks)