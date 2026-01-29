from retrieval import load_retrieval

retriever = load_retrieval()

def get_relevant_docs(query):
    """
    Perform a similarity search on the vectorstore about owasp top 10 llm security vulns.
    Args:
        query (str): The search query.
    Returns:
        List of relevant documents.
    """
    docs = retriever.invoke(query)

    return "\n\n".join(doc.page_content for doc in docs)