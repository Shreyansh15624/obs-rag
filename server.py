import os
import time
import asyncio
import uvicorn
from dotenv import load_dotenv

# Importing the current Date & Time
from datetime import datetime

# Importing the FastAPI & Google's  Modules
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from google.api_core.exceptions import ResourceExhausted

# Importing the Langchain Modules
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Importing Locally Written Search Functions
from functions.obsidian_searcher import local_search_notes # Offline-Chroma-db

# Loading the Environment Variables
load_dotenv()

# Configuring the App
app = FastAPI(
    title="Obsidian RAG API",
    description="A Second Brain API that answers your questions based on your Local Obsidian Notes.",
    version="1.0.0"
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
class Message(BaseModel):
    role: str                       # Is either 'user' / 'ai'
    content: str                    # The actual content of the message / query / prompt

class QueryRequest(BaseModel):
    question: str
    history: List[Message] = []     # Defaults to an empty list
    top_k: int = 5                  # No. of notes to refer for the answer, default is 4, can be increased
    provider: str = "google"
    model: str = "gemini-2.5-flash"

class AIResponse(BaseModel):
    answer: str
    context_used: str               # For debugging purposes, will show sources

VAULT_PATH = os.getenv("VAULT_PATH")

# Defining the Write back Data Structure!
class NotePayLoad(BaseModel):
    filename: str
    content: str
    folder: str = "My_Obs_RAG"      # Specifying a subfolder to save chats


# Step-2: Setting up the Brain of the Resources, only need to initialize once
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY Not Found! Please check your '.env' file!")


# Hypnotizing AI for best performance 👁️👄👁️ -> 😵‍💫 -> ⚡😎⚡
system_prompt="""
You are an elite, highly precise "Second Brain" AI Assistant. Your sole purpose is to synthesize and retrieve information strictly from the user's personal markdown notes.

<CONSTRAINTS>
1. STRICT ZERO-HALLUCINATION POLICY: You must answer the user's question using ONLY the provided <CONTEXT>. 
2. NO OUTSIDE KNOWLEDGE: If the answer is not explicitly contained within the <CONTEXT>, you must reply with exactly: "I cannot answer this based on the provided notes." Do not offer outside general knowledge under any circumstances.
3. CITATIONS: Every factual claim must be followed by an inline citation using the exact filename provided in the context. Format exactly like this:.
4. FORMATTING: Use clean, standard Markdown. If asked to compare items, ALWAYS output a properly formatted Markdown table.
</CONSTRAINTS>

<CHAT_HISTORY>
{chat_history}
</CHAT_HISTORY>

<CONTEXT>
{context}
</CONTEXT>

Current Question: {question}

Assistant Response:
"""

prompt_template = ChatPromptTemplate.from_template(system_prompt)


@app.get("/")
async def health_check():
    """A simple heartbeat endpoint to check if the server is running."""
    return {"status": "online", "model": "dynamic"}

@app.post("/chat", response_model=AIResponse)
async def chat_endpoint(request: QueryRequest,):
    """
    MAIN RAG Endpoint.
    1. Receives the input question / prompt.
    2. Searches the embedded VectorDB.
    3. Generates Answer with Auto-Retry for Rate Limits.
    """
    # Formatting the Chat History into a readable block of text!
    formatted_history = ""
    if request.history:
        for msg in request.history[-4:]:
            formatted_history += f"{msg.role.capitalize()}: {msg.content}\n"
    
    try:
        # A. Logging the request Serverside!
        print(f"Request Received: {request.question}")
        
        # B. Retrieving relevant information based on the Context provided
        print("🏠 Connecting to Local Chroma DB...")
        context_snippet = local_search_notes(request.question)
        print(f"Retrieved Context Length: {len(context_snippet)} chars.")
        
        # C. Generating the Answer
        if request.provider.lower() == "ollama":
            llm = ChatOllama(model=request.model, temperature=0.3)
        else:
            llm = ChatGoogleGenerativeAI(model=request.model, temperature=0.3)
        prompt_chain = prompt_template | llm | StrOutputParser()
        
        response_text = ""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # '.invoke()' is used instead of '.stream()' for standard HTTP requests
                response_text = prompt_chain.invoke({
                    "chat_history": formatted_history,
                    "context": context_snippet,
                    "question": request.question
                })
                break # Breaking out of the retry loop upon Success!
            
            except ResourceExhausted:
                wait_time: int = 2 * (attempt + 1) # Short Exponential Backoff
                print(f"⚠️Quota Hit! Retrying in {wait_time}s...")
                time.sleep(wait_time)
                if attempt == max_retries - 1:
                    raise HTTPException(status_code=429, detail="AI Overlaod! Please Try Again in a minute.")
        
        # The Chat Saving Function getting called!
        try:
            # 1. Grabbing the current date & time for file creation!
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # 2. Formatting the User's & AI's messages
            md_content = f"Chat Record: {timestamp}\n\n"
            md_content += f"**User:** {request.question}\n\n"
            md_content += f"**AI:** {response_text}\n\n"
            md_content += f"---\n*Context Snippet:* {context_snippet[:50]}...\n"

            # 3. Packaging the Chat ready to be saved into Pydantic Model
            log_payload = NotePayLoad(
                filename=f"Log_{timestamp}.md",
                content=md_content,
                folder="My_Obs_RAG"
            )

            # 4. Firing the save function! (Passing the API Key we already checked)
            save_response = await save_obsidian_note(note=log_payload)
            
            if save_response.get("status") == "success":
                print(f"✅ Chat Successfully saved to: {save_response.get('file')}")
            else:
                print(f"❌ Auto-save Failed Internally: {save_response.get('message')}")

        except Exception as e:
            print(f"⚠️ Could not save chat log: {str(e)}")


        # D. Returning a structured JSON
        return AIResponse(
            answer=response_text,
            context_used=context_snippet[:500] + "..." # Sending back a limited snippet, for debugging
        )
    
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/api/notes/save")
async def save_obsidian_note(note: NotePayLoad):
    try:
        # Building the save location!
        save_location = os.path.join(VAULT_PATH, note.folder)
        os.makedirs(save_location, exist_ok=True)

        # Making sure '.md' extension exists!
        if not note.filename.endswith(".md"):
            note.filename += ".md"
        
        file_path = os.path.join(save_location, note.filename)

        # Thread-safe file Writing
        def write_file():
            with open(file_path, 'w', encoding="utf-8") as f1:
                f1.write(note.content)
        
        await asyncio.to_thread(write_file)
        
        print(f"Saved to: {file_path}")
        return {"status": "success", "file": file_path}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}



# Step-4: The Entry Point into the Program
if __name__=="__main__":
    # With this we run the 'python server.py' directly
    print("🚀 Starting the Second Brain API...")
    uvicorn.run(app, host="0.0.0.0", port=8080)