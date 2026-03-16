from ingest import SKIP_FILES
import os
import sys
import re # For performing the Regex operations to acquire links

from dotenv import load_dotenv

from langchain_community.document_loaders import ObsidianLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

load_dotenv()

SKIP_FILES = []

def gateKeeper(raw_docs, skips):
    valid_docs = []
    for doc in raw_docs:
        source_path = doc.metadata.get("source", "")
        file_name = os.path.basename(source_path)
        if not source_path.lower().endswith(".md"):
            continue
        if file_name in skips:
            continue
        valid_docs.append(doc)
    return valid_docs

def enrich_chunk(chunk):
    text = chunk.page_content
    
    # Step-1: Capturing the Internal Links for Obsidian: [[Local Note]] or [[Local Note|Alias]]
    internal_links = [link.strip() for link in re.findall(r"\[\[([^|\]]+)(?:\|[^\]]+)?\]\]", text)]

    # Step-2: Capturing the external web links: [Display Text](https://...)
    external_links_raw = re.findall(r"(?<!\!)\[([^\]]+)\]\(([^)]+)\)", text)
    # The (?<!\!) is a negative lookbehind that prevents grabbing ![Image](url) tags!

    external_links = [url for _, url in external_links_raw]

    # Format them nicely for the AI to read them at the bottom of the chunk!
    external_formatted = [f"{desc} ({url})" for desc, url in external_links_raw]

    # Step-3: Tags: #words
    tags = re.findall(r"(?<!\S)#([a-zA-Z0-9_-]+)", text)

    # Step-4: Injecting the text into the HuggingFace Model to read it the context
    if internal_links or external_links or tags:
        text += "\n\n---"
        if internal_links:
            text += f"\nLinked Concepts: {', '.join(internal_links)}"
        if external_links:
            text += f"\nExternal Referenes: {', '.join(external_links)}"
        if tags:
            text += f"\nTags: {', '.join(tags)}"
    
    chunk.page_content = text

    # Step-5: Injecting into the Qdrant Metadata (Qdrant natively supports Python Lists)
    if internal_links:
        chunk.metadata["internal_links"] = internal_links
    if external_links:
        chunk.metadata["external_links"] = external_links
    if tags:
        chunk.metadata["tags"] = tags
    
    return chunk

def main():
    VAULT_PATH = os.getenv("VAULT_PATH")
    QDRANT_END_POINT_URL = os.getenv("QDRANT_END_POINT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

    if not all([VAULT_PATH, QDRANT_API_KEY, QDRANT_END_POINT_URL]):
        print("❌ Error: Missing VAULT_PATH, QDRANT_API_KEY or QDRANT_END_POINT_URL in '.env'")
        sys.exit(1)
    
    print(f"📁 Loading notes from Vault: {VAULT_PATH}")
    loader = ObsidianLoader(VAULT_PATH)
    raw_docs = loader.load()
    documents = gateKeeper(raw_docs, SKIP_FILES)

    print(f"🔪 Splitting {len(documents)} documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    print("🧠 Enriching chunks with Regex...")
    enriched_chunks = [enrich_chunk(chunk) for chunk in chunks]

    print("⚙️ Booting the Loacl HuggingFace Embedding Model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("☁️ Connecting to the Qdrant Cloud to upload vectors...")

    # This connects to the Qdrant Cloud, creates the collection if its missing & uploads in batches
    qdrant = QdrantVectorStore.from_documents(
        enriched_chunks,
        embeddings,
        url=QDRANT_END_POINT_URL,
        api_key=QDRANT_API_KEY,
        collection_name="vault_holding",
        force_recreate=True,
    )

    print("✅ Brain Transplant to Qdrant Cloud Complete!")

if __name__=="__main__":
    main()