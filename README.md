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