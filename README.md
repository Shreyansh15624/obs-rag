# 🧠 Obsidian RAG: AI Second Brain

> A Retrieval-Augmented Generation (RAG) agent that allows you to chat with your personal Obsidian notes using Gemini 2.5 Flash and a local Vector Database.

![Demo](path_to_your_demo_gif_here.gif)
*(Coming Soon!)* //Didn't make because went over the Rate Daily Request Limit while testing!

## 🚀 Overview

This project converts a static Obsidian vault into an interactive "Second Brain." It uses **Google's Gemini 2.5** for reasoning and **ChromaDB** for semantic search. The system ingests markdown notes, embeds them into a vector space, and allows the user to query their knowledge base in natural language.

**Key Features:**
* **Context-Aware:** Retrieves exact paragraphs from notes to answer queries.
* **Source Citations:** Tells you exactly which file the information came from.
* **Modern Stack:** Built with `uv` for dependency management and `langchain-google-genai` v4+.
* **Resilient:** Handles rate limits and API quotas gracefully.

## 🛠️ Tech Stack

* **Language:** Python 3.11+
* **LLM:** Google Gemini 2.5 Flash
* **Vector Database:** ChromaDB (Local)
* **Orchestration:** LangChain (v0.3+)
* **Package Manager:** uv

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/obs-rag.git](https://github.com/yourusername/obs-rag.git)
    cd obs-rag
    ```

2.  **Install dependencies using `uv`:**
    ```bash
    uv sync
    ```

3.  **Set up Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key_here
    VAULT_PATH=your_obsidian_vault_path_here
    ```

4.  **Ingest your Notes:**
    *Modify the path in `ingest.py` to point to your Obsidian Vault, then run:*
    ```bash
    ./embed.sh
    ```

## 🏃 Usage

Start the chat agent:
```bash
uv run main.py
```
## Example Interaction:

    🧑‍🦰You: "What did I learn about <Queried_Subject>?"
    🤖AI:  "Based on your note '<relevant_file>.md', <Queried_Subject> is..."
---

## 🔄 Project Lifecycle & Engineering Challenges

This project evolved through several critical engineering phases, mirroring a real-world software development lifecycle:

### Phase 1: The "Import Race" Condition

Challenge: The application crashed immediately upon startup because the Embedding module attempted to initialize before environment variables were loaded. Solution: Implemented a strict initialization order and ensured dotenv loading occurred within the module scope, decoupling the module's dependency on the main entry point.

### Phase 2: Dependency Mismatch (The "List" Error)

Challenge: The system encountered an AttributeError: 'list' object has no attribute 'get' during the generation phase. Root Cause: The langchain-google-genai library (v2.0) was outdated and could not parse the response schema of the newer Gemini 2.5 model, which returned a list of candidates rather than a legacy dictionary. Solution: Performed a major version upgrade to langchain-google-genai v4.2.0 and google-genai v1.0+, aligning the library capabilities with the model's API standards.

### Phase 3: Protocol Conflicts (The Hang)

Challenge: The agent would hang indefinitely during the search phase on WSL (Windows Subsystem for Linux). Root Cause: Forcing transport="rest" on the updated library caused a conflict, as the new SDK defaults to REST but handles it differently than the legacy version. Solution: Refactored the initialization code to remove manual transport overrides, allowing the library to negotiate the optimal connection protocol automatically.
Phase 4: Rate Limit Optimization

Challenge: High-frequency querying triggered 429 Resource Exhausted errors on the Gemini Flash free tier. Solution: (Planned/In-Progress) Implementation of exponential backoff retry logic to handle quota bursts gracefully without crashing the user session.

## 🔮 Future Roadmap

    [ ] Add a GUI (Streamlit or Gradio).

    [ ] Implement "Watch Mode" to auto-ingest notes when they change.

    [ ] Add support for image recognition within notes.