import os
import sys

from dotenv import load_dotenv

from langchain_community.document_loaders import ObsidianLoader
from langchain_text_spliters import RecursiveCharacterTextSpliter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Beginning by Loading the .env variables
load_dotenv()

# Hardcoded the Vault Path

# Hardcoded Database Path
DB_PATH = "./chroma_db"

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
    
    if not raw_docs:
        print("WANING!! No .md files found in the given Vault Path")
        return
    
    print(f"    Found {len(raw_docs)} notes")
    