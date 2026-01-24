import os
import time
import uvicorn
from dotenv import load_dotenv

# Importing the FastAPI & Google's  Modules
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.api_core.exceptions import ResourceExhausted

# Importing the Langchain Modules
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from functions import search_notes

# Loading the Environment Variables
load_dotenv()

# Configuring the App
app = FastAPI(
    title="Obsidian RAG API",
    description="A Second Brain API that answers your questions based on your Local Obsidian Notes.",
    version="1.0.0"
)

# Security Configuration
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    # 1. Accessing the real password from environment variables
    SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")
    
    # 2. Check if the user provided the correct password
    if api_key_header == SERVER_PASSWORD:
        return api_key_header
    else:
        raise HTTPException(
            status_code=403,
            detail="Access Denied! You need a valid API Key to Access the Second Brain.\n"
        )

# Enabling CORS for future front-end to talk with AI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Step-1: We definte the data's models, basically what kind of input should be Accepted
# & what kind of output should be Returned
class QueryRequest(BaseModel):
    question: str
    top_k: int = 4 # No. of notes to refer for the answer, default is 4, can be increased

class AIResponse(BaseModel):
    answer: str
    context_used: str # For debugging purposes, will show sources

# Step-2: Setting up the Brain of the Resources, only need to initialize once
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY Not Found! Please check your '.env' file!")

# Setting the model up
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", # Again 2.5-flash for speed
    temperature=0.3,
)

# Hypnotizing AI for best performance 👁️👄👁️ -> 😵‍💫 -> ⚡😎⚡
system_prompt="""
You are an intelligent "Second Brain" AI Assistant Agent.
You have access to the user's personal notes.

Here is the context retrieved from the notes.
{context}

Question: {question}

Instructions:
- Answer the question using ONLY the context provided above.
- If the context doesn't contain the answer, admit that you do not know based on the notes.
- Cite the source (filename) if available in the context.
"""

prompt_template = ChatPromptTemplate.from_template(system_prompt)


@app.get("/")
async def health_check():
    """A simple heartbeat endpoint to check if the server is running."""
    return {"status": "online", "model": "gemini-2.5-flash"}

@app.post("/chat", response_model=AIResponse)
async def chat_endpoint(
    request: QueryRequest,
    api_key: str= Depends(get_api_key)
):
    """
    MAIN RAG Endpoint.
    1. Receives the input question / prompt.
    2. Searches the embedded VectorDB.
    3. Generates Answer with Auto-Retry for Rate Limits.
    """
    try:
        # A. Logging the request Serverside!
        print(f"Request Received: {request.question}")
        
        # B. Retrieving relevant information based on the Context provided
        context_text = search_notes(request.question)
        print(f"Retrieved Context Length: {len(context_text)} chars.")
        
        # C. Generating the Answer
        prompt_chain = prompt_template | llm | StrOutputParser()
        
        response_text = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # '.invoke()' is used instead of '.stream()' for standard HTTP requests
                response_text = prompt_chain.invoke({
                    "context": context_text,
                    "question": request.question
                })
                break # Breaking out of the retry loop upon Success!
            
            except ResourceExhausted:
                wait_time = 2 * (attempt + 1) # Short Exponential Backoff
                print(f"⚠️Quota Hit! Retrying in {wait_time}s...")
                time.sleep(wait_time)
                if attempt == max_retries - 1:
                    raise HTTPException(status_code=429, detail="AI Overlaod! Please Try Again in a minute.")
            
        # D. Returning a structured JSON
        return AIResponse(
            answer=response_text,
            context_used=context_text[:500] + "..." # Sending back a limited snippet, for debugging
        )
    
    except Exception as e:
        print(f"❌Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# Step-4: The Entry Point into the Program
if __name__=="__main__":
    # With this we run the 'python server.py' directly
    print("🚀Starting the Second Brain API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)