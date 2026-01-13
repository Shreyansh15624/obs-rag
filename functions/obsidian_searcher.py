from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def search_notes(query: str) -> str:
    # Give 'str' input & generate 'str' output
    try:
        # Loading the existing DB        
        vector_db = Chroma(
            persistant_directory="./chroma_db",
            embedding_function=embeddings
        )
        
        # Seaching the top 4 most relevant results
        results = vector_db.similarity_search(query, k=4)
        
        if not results:
            return "No relevant notes found in the Vault"
        
        # Combining results into a string for the Ai to read 
        knowledge = "\n\n".join([f"[Source: {doc.metadata.get('source','Unknown')}]\n{doc.page_content}" for doc in results])
        return knowledge

    except Exception as e:
        return f"Error Searching Vault: {str(e)}"