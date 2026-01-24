import os
import time

# Importing the Environment Variables
from dotenv import load_dotenv

# Importing the Langchain Modules
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Importing the Pinecone Module
from pinecone import Pinecone

# Loading the Environment Variables
load_dotenv()

GOOGLE_API_KEY= os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
VAULT_PATH = os.getenv("VAULT_PATH")


# Quickly check for all the possible Environment Variables errors
if not PINECONE_API_KEY:
    raise ValueError("Error: 'PINECONE_API_KEY' is missing from the '.env' file!")
elif not GOOGLE_API_KEY:
    raise ValueError("Error: 'GOOGLE_API_KEY' is missing from the '.env' file!")
elif not PINECONE_INDEX_NAME:
    raise ValueError("Error: 'PINECONE_INDEX_NAME' is missing from the '.env' file!")
elif not VAULT_PATH:
    raise ValueError("Error: 'VAULT_PATH' is missing from the '.env' file!")

print("💉 Beginning the Brain Transplant to Pinecone.")

# Initializing the embeddings exactly to the dimensions value '768'
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Loading the notes from the disk
print(f"📁 Loading notes from: {VAULT_PATH}")
loader = DirectoryLoader(
    VAULT_PATH,
    glob="**/*.md",
    loader_cls=TextLoader,
    show_progress=True
)
docs = loader.load()
print(f"Loaded {len(docs)} documents.")

# Splitting the text into Chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
splits = text_splitter.split_documents(docs)
print(f"Splitting text into {len(splits)} chunks.")

# Connecting to Pinecone
print("Connecting to Pinecone...")
vector_store = PineconeVectorStore(
    index_name=PINECONE_INDEX_NAME,
    embedding=embeddings,
)

# Defining the Upload Batch Sizes
batch_size = 10
total_batches = len(splits) // batch_size + 1

print(f"Uploading in batches of {batch_size} to avoid rate limits...")

# Uploading in slow batches
for i in range(0, len(splits), batch_size):
    # Getting each batch according to the 'batch_size'
    batch = splits[i: i + batch_size]
    if batch:
        print(f"Uploading batch {i} to {i + len(batch)}...")
        vector_store.add_documents(batch)
        time.sleep(5) # Sleep for 5 seconds to let the Google API Cooldown


print("🎉 Successfully uploaded Brain to Cloud.")