import os
import sys
from dotenv import load_dotenv

# New Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# New function addition
from functions import search_notes


load_dotenv()

def main():
    # Checking the API Key
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found in .env")
        return
    
    # Setting up the model, best suitable for speed!
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3) 

    # Hypnotizing AI for best performance 👁️👄👁️ -> 😵‍💫 -> ⚡😎⚡
    system_prompt = """
You are an intelligent "Second Brain" AI Assistant Agent.
You have access to the user's personal notes.

Here is the context retrieved from the notes.
{{context}}

Question: {{question}}

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
            retieved_context = search_notes(user_query)

            # Step-2: Generating the Answer
            prompt_chain = prompt | llm | StrOutputParser()
            # Pipe-1: Takes a Dictionary -> Turns it into a Formatted String
            # Pipe-2: Takes a String -> Turns it into an AI Message
            # Pipe-3: Takes AI Message -> Turns it into a Clean Message
            # So, the process is just 'Input -> Prompt -> LLM -> Text'
            prompt_chain.stream({"context": lambda x: retieved_context, "question": lambda x: user_query})

            # Step-3: Returning the response, with a Cool-factor
            print("🤖AI: ", end="")
            for chunk in prompt_chain.stream({}): # The .stream({}) recieves one token at a time from the model remotely / locally.
                print(chunk, end=" ", flush=True) # flush=True is for the cool-factor, default is False
            print("\n")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__=="__main__":
    main()