import os
import sys

from dotenv import load_dotenv

from langchain_community.document_loaders import ObsidianLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Beginning by Loading the .env variables
load_dotenv()

# Hardcoded the Vault Path

# Hardcoded Database Path
DB_PATH = "./chroma_db"
SKIP_FILES = None
"""
Creating a Gatekeeper Function, that will essentially not let any non-markdown documents 
be converted to embeddings. As the embeddings mdel we are using is only for text embeddings
& the data fed into the AI Studio will be quite a lot & may go over the free-tier limits. 
"""
def gatekeeper(raw_docs, skip_list):
    valid_docs = []
    print(f"    Filtering {len(raw_docs)} files... ")
    
    if skip_list == None:
        skip_list = []
    
    for doc in raw_docs:
        source_path = doc.metadata.get("source", "")
        filename = os.path.basename(source_path)
        
        if not source_path.lower().endswith(".md"):
            continue
        
        if filename in skip_list:
            print(f"    🚫 Skipping ignored files: {filename}")
            continue
        
        valid_docs.append(doc)
    return valid_docs

def main():
    # Safety Checking the API Key
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found in .env file")
        sys.exit(1)
    
    # Getting Obsidian Vault Path
    VAULT_PATH = os.getenv("VAULT_PATH")
    if not VAULT_PATH:
        print("Error: Obsidian Vault Location is not given!")
        sys.exit(1)
    
    # Safety Checking the Vault Path
    if not os.path.exists(VAULT_PATH):
        print(f"Error: Vault Path Not Found: {VAULT_PATH}")
        sys.exit(1)
        
    print(f"Loading the Obsidian Notes from: {VAULT_PATH}")
    
    # Loading the Notes! Also the 'ObsidianLoader' Automatically handles the metadata
    loader = ObsidianLoader(VAULT_PATH)
    raw_docs = loader.load()
    # Safety Stopping the Program 
    if not raw_docs:
        print("WARNING!! No .md files found in the given Vault Path")
        return
    
    documents = gatekeeper(raw_docs, SKIP_FILES)
    
    # Splitting the Notes!(f"    Splitting ({len()})")
    print(f"    Found {len(documents)} notes")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    
    # Creating Embeddings & Saving them as Vectors to ChromaDB
    print("🧠 Building the Vector Database... ")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    # Now Embeddings are Created!
    
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    # Now VectorDB is Created!
    
    print(f"Successfully Saved {len(chunks)} chunks ot '{DB_PATH}'.")
    
if __name__=="__main__":
    main()