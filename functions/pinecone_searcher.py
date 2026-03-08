import os

# Importing the HTTPException
from fastapi import HTTPException

# Importing the Langchain Modules
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_vector_store(): # Connects to the Pinecone Cloud Index
    # Must use the same model as the Uploader Script
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
    if not PINECONE_INDEX_NAME:
        raise ValueError("Error: 'PINECONE_INDEX_NAME' is missing from the '.env' file.")
    
    vector_store = PineconeVectorStore(
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings,
    )
    return vector_store

def pinecone_search_notes(query: str, top_k: int = 4):
    """
    Searches Pinecone for top 4 most relevant chunks. (4 is default & can be changed)
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
        raise HTTPException(status_code=500, detail=f"Database / Embedding Error: {str(e)}\n")