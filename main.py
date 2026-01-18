import os
import time
from dotenv import load_dotenv

# New Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

#Importing a specific exception from Google
from google.api_core.exceptions import ResourceExhausted

# New function addition
from functions import search_notes


load_dotenv()

def main():
    # Checking the API Key
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found in .env")
        return
    
    # Setting up the model, best suitable for speed!
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3
    ) 

    # Hypnotizing AI for best performance 👁️👄👁️ -> 😵‍💫 -> ⚡😎⚡
    system_prompt = """
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
    
    # Feeding the input_prompt placed into the system_prompt to the Model!
    prompt = ChatPromptTemplate.from_template(system_prompt)
    
    # Establishing the Chat Loop
    print("\n🧠 Obsidian RAG Agent Ready! (Type 'exit' to quit)\n")
    
    while True:
        try:
            user_query = input("\n🧑You: ")
            if user_query.lower() in ("exit", "quit"):
                break
            
            print("🔍 Searching in yout notes...")

            # Step-1: Gather the relevant notes from the Vault
            retrieved_context = search_notes(user_query)

            # Step-2: Generating the Answer
            prompt_chain = prompt | llm | StrOutputParser()
            # Pipe-1: Takes a Dictionary -> Turns it into a Formatted String
            # Pipe-2: Takes a String -> Turns it into an AI Message
            # Pipe-3: Takes AI Message -> Turns it into a Clean Message
            # So, the process is just 'Input -> Prompt -> LLM -> Text'

            # Step-3: Returning the response, with a Cool-factor
            print("🤖AI: ", end="")
            max_retries = 3 # Defining a standard number for retries
            for retry in range(max_retries):
                try:
                    for chunk in prompt_chain.stream({
                            "context": retrieved_context,
                            "question": user_query
                        }):
                        print(chunk, end=" ", flush=True) # flush=True is for the cool-factor, default is False
                    break # Breaking out of the loop for Success in Trying
                
                except ResourceExhausted: # Imported Exception from Google's Module
                    wait_time = 30 * (retry + 1) # Waiting for an Exponential Time
                    print(f"\n Rate Limit hit! Cooling down for {wait_time}s.\nAttempt(s): {(retry + 1)}/{max_retries}")
                    time.sleep(wait_time)
                    print("Retrying....")
                
                except Exception as e: # This except block is for cathcing all other kinds of errors
                    print(f"Error: {e}")
                    break # Breaking out of loop if error is not ResourceWarning
                    
            print("\n")
        except KeyboardInterrupt:
            print("\n Exiting by Keyboard Interrupt")
            break
        except Exception as e:
            print(f"\nError / Critical Error: {e}")

if __name__=="__main__":
    main()