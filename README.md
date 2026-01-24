# 🧠 Obsidian RAG: AI Second Brain

> A Retrieval-Augmented Generation (RAG) agent that allows you to chat with your personal Obsidian notes using Gemini 2.5 Flash and a local Vector Database.

![Project Demo](video/obs-rag.mp4)
Link: https://github.com/Shreyansh15624/obs-rag/raw/main/video/obs-rag.mp4
_(In case the video doesn't play)_

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
    git clone https://github.com/Shreyansh15624/obs-rag
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

**Challenge:** The application crashed immediately upon startup because the Embedding module attempted to initialize before environment variables were loaded. Solution: Implemented a strict initialization order and ensured dotenv loading occurred within the module scope, decoupling the module's dependency on the main entry point.

### Phase 2: Dependency Mismatch (The "List" Error)

**Challenge:** The system encountered an AttributeError: 'list' object has no attribute 'get' during the generation phase. Root Cause: The langchain-google-genai library (v2.0) was outdated and could not parse the response schema of the newer Gemini 2.5 model, which returned a list of candidates rather than a legacy dictionary. Solution: Performed a major version upgrade to langchain-google-genai v4.2.0 and google-genai v1.0+, aligning the library capabilities with the model's API standards.

### Phase 3: Protocol Conflicts (The Hang)

**Challenge:** The agent would hang indefinitely during the search phase on WSL (Windows Subsystem for Linux). Root Cause: Forcing transport="rest" on the updated library caused a conflict, as the new SDK defaults to REST but handles it differently than the legacy version. Solution: Refactored the initialization code to remove manual transport overrides, allowing the library to negotiate the optimal connection protocol automatically.

### Phase 4: Rate Limit Optimization

**Challenge:** High-frequency querying triggered 429 Resource Exhausted errors on the Gemini Flash free tier. Solution: (Planned/In-Progress) Implementation of exponential backoff retry logic to handle quota bursts gracefully without crashing the user session.

### Phase 5: Moving from Script to Server (FastAPI)

**Challenge:** The first version of the project was just a simple Python script. It would run once, answer one question, and then stop. This was a problem because I couldn't connect it to a frontend website, and it couldn't handle more than one request at a time.

**Root Cause:** The code was written as a linear list of instructions (Step 1 -> Step 2 -> Exit). It blocked the computer's attention while waiting for things like the Google API to reply, meaning the whole program froze during every search.

**Solution:** I rewrote the application using **FastAPI** to turn it into a proper web server.
* **Concurrency:** I changed the functions to use `async` and `await`. This allows the server to "pause" waiting for Google's reply and handle other tasks (like a health check) in the meantime.
* **Data Safety:** I used **Pydantic** to create strict rules for the data coming in. If someone sends broken data, the server rejects it immediately with a clear error message instead of crashing.
* **Always On:** I used **Uvicorn** to run the app, which keeps the server alive and listening for new messages 24/7.

### Phase 6: The "Large File" Git Error

**Challenge:** When I tried to push my project to GitHub, it failed completely because of my demo video. Even though I had installed "Git Large File Storage" (LFS), GitHub kept rejecting the push saying the file was too big.

**Root Cause:** I learned that Git remembers everything. Even though I had configured LFS for future uploads, the "old" version of the video was still saved in my commit history (the previous saves I made locally). Git was trying to upload that old history, which contained the raw, heavy video file.

**Solution:** I had to perform a careful cleanup of the Git history without deleting my code.
* I used `git reset` to "undo" my recent commits while keeping the files on my computer.
* I used `git rm --cached` to force Git to completely "forget" the large video file ever existed in its tracking system.
* I re-added the files *after* the LFS rules were active, ensuring only the lightweight "pointer" was uploaded, not the heavy video.

### Phase 7: The Docker "Quotation Mark" Bug

**Challenge:** My code worked perfectly on my Windows laptop, but as soon as I ran it inside the Docker container, it crashed with an "Invalid API Key" error. This was confusing because I was using the exact same API key and `.env` file.

**Root Cause:** It turned out to be a subtle difference between Windows and Linux. On my Windows laptop, the system automatically ignored the quotation marks I put around my API key in the settings file. However, inside Docker (which runs on Linux), the system read the quotation marks literally. So instead of sending `12345` to Google, it was sending `"12345"`, which is a wrong password.

**Solution:** I fixed how the environment variables were handled.
* I manually removied all quotation marks to make it compatible with both systems.
* I use the specific `--env-file` command when running Docker. This tells Docker to read the file directly and safely, ensuring the password is passed correctly every time.

### Phase 8: Securing the Public Link

**Challenge:** Once I deployed the project to the cloud (Render), I realized a major security flaw: anyone with the link could use my Google API quota or, worse, ask the AI questions about my private notes.

**Solution:** I built a "Gatekeeper" system into the API.
* I added a security check that runs before the AI even wakes up.
* The server now looks for a secret password (an `X-API-Key`) in the headers of every request.
* If a stranger tries to access the API without this password, the server blocks them immediately with a "403 Forbidden" error, keeping my data and my API usage safe.

### Phase 9: The "Brain Transplant" (Local to Cloud Migration)

**Challenge:** My initial plan to store the database locally (`chroma_db` folder) failed in production. Cloud platforms like Render use "ephemeral filesystems," meaning every time the server restarts or deploys, any file saved to the disk is wiped clean. My AI was losing its memory every time I pushed code.

**Root Cause:** I was treating a cloud server like a laptop. Stateful data (like a database) cannot live inside a stateless container.

**Solution:** I migrated the storage layer to **Pinecone**, a serverless vector database.
* **Separation of Concerns:** I decoupled the "Compute" (Render) from the "Memory" (Pinecone).
* **The "Seeding" Script:** I wrote a dedicated utility script (`seed_pinecone.py`) to read my local Obsidian markdown files, embed them, and upload them to the Pinecone cloud.
* **Rate Limit Handling:** When uploading, I hit Google's API speed limit (`429 Resource Exhausted`). I engineered a "batching" logic that uploads documents in small groups of 10 and sleeps for 5 seconds between batches to respect the API quotas.
* **Dimensionality Fix:** I resolved a critical crash where the embedding vectors (size 3072) didn't fit the database index (size 768) by strictly enforcing the `text-embedding-004` model standard.

### Phase 10: Production Deployment (CI/CD)

**Challenge:** Moving from "it works on my machine" to "it works for everyone" required a robust deployment pipeline. I needed a way to update the code without manually logging into a server to install libraries or restart processes.

**Solution:** I established a Continuous Deployment pipeline using **Render** linked to **GitHub**.
* **Dependency Locking:** I used `uv export` to generate a hashed `requirements.txt`. This ensures the server installs the *exact* same library versions as my local machine, preventing "it works locally but breaks in prod" bugs.
* **Secret Management:** Instead of hardcoding keys (which is dangerous), I injected sensitive data (API Keys, Passwords) via Render's "Environment Variables" dashboard.
* **Automated Builds:** Now, whenever I `git push` to the main branch, Render automatically detects the change, builds a new Docker container, and swaps it with the old one with zero downtime.


## 🔮 Future Roadmap

- [ ] Save the Conversations Locally.
- [ ] Work with Local LLMs by the likes of Ollama, LMStudio, Docker Desktop Models etc.
- [ ] Connect with Obsidian?
    - [ ] Implement "Watch Mode" to auto-ingest notes when they change.
    - [ ] Perform FileOps in the Local Vault, by tool-calling & function-calling.
- [ ] Add a GUI (Streamlit or Gradio).
    - [ ] Also have some advanced files & conversations management.
- [ ] Share/Export conversations (as link & file or as compressed-zip if its a group)
- [ ] Add support for image recognition within notes.
