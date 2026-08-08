import os

# Importing the Langchain Modules
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DB_PATH = "./chroma_db"

# '(query: str) -> str' Its only for the ease of understanding
def local_search_notes(query: str, top_k: int = 12) -> str:
    """
    Searches the local Chroma DB using the all-MiniLM-L6-v2 model and returns a
    concatenated string of the most relevant note snippets.
    """
    if not os.path.exists(DB_PATH):
        return "Error: Local Vector DB not found. Please run `ingest.py` first!"
    
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # Loading the existing DB
        vector_db = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings
        )
        
        # Seaching the top 4 most relevant results
        results = vector_db.similarity_search(query, k=top_k)
        
        if not results: # Empty Vault Case handled
            return "No relevant notes found in the Vault"
        
        # Compiling the results into a single context string
        context = ""
        for doc in results:
            source = doc.metadata.get("source", "Unknown Source")
            filename = os.path.basename(source)
            context += f"\n--- From {filename} ---\n"
            context += doc.page_content + "\n"
        
        return context

    except Exception as e:
        print(f"Search Error: {e}")
        return f"An error occurred while searching the Vector DB: {e}"