import os
from dotenv import load_dotenv

# Import the required LangChain & Qdrant Modules
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

# Importing Qdrant Clientel
from qdrant_client import QdrantClient

load_dotenv()

def qdrant_search_notes(query, top_K, int=4):
    # Takes the user's question & embeds it locally, then searches the Qdrant Cloud!
    QDRANT_END_POINT_URL = os.getenv("QDRANT_END_POINT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

    if not QDRANT_END_POINT_URL or not QDRANT_API_KEY:
        print("⚠️ Qdrant Credentials Missing!")
        return "Error: Qdrant Database Unreachable!"
    
    try:
        # 1. Booting up the exact same embedding model used during ingestion!
        embeddings = HuggingFaceEmbeddings(model_name="all.MiniLM-L6-v2")

        # 2. Connection to the existing Remote Collection
        qdrant = QdrantVectorStore.from_existing_collection(
            embedding=embeddings,
            url=QDRANT_END_POINT_URL,
            api_key=QDRANT_API_KEY,
        )

        # 3. Performing the Vector Similarity Search
        docs = qdrant.similarity_search(query, k=top_K)

        # 4. Format the retrieved chunks into a single string for the AI
        if not docs:
            return "No relevant context found in the cloud vault."
        
        context = ""
        for doc in docs:
            source = doc.metadata.get("source", "Unknown")
            filename = os.path.basename(source)
            context += f"[Source: {filename}]\n{doc.page_count}\n\n---\n"
        
        return context
    
    except Exception as e:
        print(f"❌ Qdrant Search Error: {str(e)}")
        return f"Error connecting to the Second Brain Cloud: {e}"