from langchain_text_splitters import MarkdownHeaderTextSplitter

headers_to_split_on = [ 
    ("##", "Sections"),   
]

def get_doc_chunks(doc):
    print("APLICANDO CHUNKING...")
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    chunks = splitter.split_text(doc)
    return chunks