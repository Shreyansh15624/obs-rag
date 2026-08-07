import os
import sys

import time
from dotenv import load_dotenv

from langchain_community.document_loaders import ObsidianLoader
from langchain_text_splitters import MarkdownTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Beginning by Loading the .env variables
load_dotenv()

# Hardcoded Database Path
DB_PATH = "./chroma_db"
SKIP_FILES = None
BATCH_SIZE = 100 # Massive increase, because we are running locally


"""
Creating a Gatekeeper Function, that will essentially not let any non-markdown documents 
be converted to embeddings. As the embeddings mdel we are using is only for text embeddings
& the data fed into the AI Studio will be quite a lot & may go over the free-tier limits. 
"""
def gatekeeper(raw_docs, skip_list):
    valid_docs = []
    print(f"    Filtering {len(raw_docs)} files... ")
    
    if skip_list is None:
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
    text_splitter = MarkdownTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = text_splitter.split_documents(documents)
    
    # Creating Embeddings & Saving them as Vectors to ChromaDB
    print("⚡ Loading the Local 'all-MiniLM-L6-v2' Model... (May take a moment to download on the first run)")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    # Now Embeddings are Created!
    
    # Changed to serve the embeddings at a consistent rate & avoid crossing over rate-limits
    print("🧠 Building the Vector Database... ")
    vector_db = Chroma(
        embedding_function=embeddings,
        persist_directory=DB_PATH
    )
    # Now VectorDB is Created!
    
    total = len(chunks)
    print(f"Successfully Saved {total} chunks to '{DB_PATH}'.")
    
    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        try:
            vector_db.add_documents(batch)
            print(f"    Batch{i // (BATCH_SIZE + 1)} ({len(batch)} chunks of {total}) done.")
            time.sleep(1.5) # To prevent Rate Limit Errors line Error-429
        except Exception as e:
            print(f"    Error on batch size starting at index: {i}: {e}")

    print(f"Successfully Knowledge Base Build at path: {DB_PATH}")
    
if __name__=="__main__":
    main()