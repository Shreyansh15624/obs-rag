import os
import sys
from dotenv import load_dotenv

# New Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassThrough

# New function addition
from functions import search_notes

from enum import Enum


load_dotenv()

def main():
    # Settign up the model, best suitable for speed!
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found in .env")
        return
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3) 

    # Hypnotizing AI for best performance 👁️👄👁️ -> 😵‍💫 -> ⚡😎⚡
    system_prompt = f"""
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
    # 'context' & 'question' variables will make appearance in the later part of the code!
    
    # Feeding the input_prompt placed into the system_prompt to the Model!
    prompt = ChatPromptTemplate.from_template(system_prompt)
    
    # Establishing the Chat Loop
    print("\n🧠Obsidian RAG Agent Ready! (Type 'exit' to quit)\n")
    
    while True:
        user_query = input("\nYou: ")
        if user_query.lower() in ("exit", "quit"):
            break
        
        print("🔍Searching in yout notes...")
        
        # Step-1: Gather the relevant notes from the Vault
        retieved_context = search_notes(user_query)
        
        # Step-2: Generating the Answer
        prompt_chain = (
            {"context": lambda x: retieved_context, "question": lambda x: user_query}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # Step-3: Returning the response, with a Cool-factor
        print("🤖AI: ", end=" ")
        for chunk in prompt_chain.stream({}):
            print(chunk, end=" ", flush=True)
        print("\n")

if __name__=="__main__":
    main()