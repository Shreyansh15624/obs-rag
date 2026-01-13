from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def search_notes(query):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_db = Chroma(persistant_directory="./chroma_db", embedding_function=embeddings)
    
    docs = vector_db.similarity_search(query, k=3)
    
    combined_content = "\n\n".join([doc.page_content for doc in docs])
    return combined_content