import os

# Importing the Langchain Modules
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_vector_store(): # Connects to the Pinecone Cloud Index
    # Must use the same model as the Uploader Script
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
    if not PINECONE_INDEX_NAME:
        raise ValueError("Error: 'PINECONE_INDEX_NAME' is missing from the '.env' file.")
    
    vector_store = PineconeVectorStore(
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings,
    )
    return vector_store

def search_notes(query: str, top_k: int = 4):
    """
    Searches Pinecone for most relevant chunks.
    """
    try:
        vecotr_store = get_vector_store()
        retriever = vecotr_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k}
        )
        
        docs = retriever.invoke(query)
        
        # Format the results
        context_text = "\n\n---\n\n".join([d.page_content for d in docs])
        return context_text
    
    except Exception as e:
        print(f"Pinecone Error: {e}")
        return ""