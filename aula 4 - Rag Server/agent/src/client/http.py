import requests

def rag_service_query(query: str, top_k: int = 5, filters = None):
	url = "http://127.0.0.1:8000/query"
	payload = {"query": query, "top_k": top_k, "filters": filters}
	print(payload)
	response = requests.post(url, json=payload)
	response.raise_for_status()
	return response.json()
