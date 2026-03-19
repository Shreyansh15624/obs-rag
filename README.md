## 🧠 Obsidian RAG: Decoupled Second Brain API
A production-ready, microservices-based Retrieval-Augmented Generation (RAG) system that transforms static Obsidian markdown vaults into an interactive, context-aware API powered by Google Gemini 2.5 and serverless vector databases.

*(Link: [https://github.com/Shreyansh15624/obs-rag/raw/main/video/obs-rag.mp4](https://github.com/Shreyansh15624/obs-rag/raw/main/video/obs-rag.mp4))*

### Motivation
I built this system to supercharge my personal knowledge management workflow while demonstrating a robust, cloud-native backend architecture. As a Python backend developer, transitioning this from a simple local script to a resilient, deployable service utilizing FastAPI, asynchronous concurrency, and stateless compute patterns was a primary goal. It bridges the gap between simple static file storage and intelligent, scalable retrieval.

### Quick Start
**1. Local Environment Setup**
Utilize `uv` for lightning-fast dependency resolution to eliminate environment mismatches.
```bash
git clone [https://github.com/Shreyansh15624/obs-rag](https://github.com/Shreyansh15624/obs-rag)
cd obs-rag
uv sync
```

**2. Environment Variables**
Create a `.env` file at the root. Do not use quotation marks around values to ensure cross-platform Docker compatibility:
```env
GOOGLE_API_KEY=your_gemini_key
VAULT_PATH=/path/to/your/obsidian/vault
API_GATEWAY_KEY=your_custom_security_password
```

**3. Data Ingestion & Execution**
```bash
# Ingest local markdown into the Vector DB
./embed.sh

# Spin up the asynchronous FastAPI server
uv run server.py
```

### Usage
The backend cleanly isolates the API to port `8080` (or `8000` locally). All incoming requests are protected by a middleware authentication layer and must pass strict `X-API-Key` validation before the LangChain agent is initialized.

**1. Querying the Vault (`POST /chat`)**
This is the core generative endpoint. It expects a JSON payload containing your question and an optional `top_k` parameter. 
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your_custom_security_password" \
     -d '{"question": "What is my latest project?", "top_k": 3}'
```
*Trick for deep dives:* You can maintain conversation context across multiple turns by passing an optional `history` list (containing message objects) within the JSON request body!

**2. Saving Context (`POST /api/notes/save`)**
You can seamlessly write AI interactions or generated summaries back into your local storage by hitting the save endpoint with a JSON payload containing the `filename`, `content`, and target `folder`.

### Contributing
Contributions are highly welcome, especially as this transitions further into a production cloud environment! 

**Where help is needed most:**
* **Reflex UI Framework:** The local client UI is built with Reflex, but UI development is not the primary focus of this project. Any optimizations, structural improvements, or enhancements to the Reflex codebase are greatly appreciated.
* **Render Deployment Connections:** While the backend deployment pipeline via Docker and `uv export` is functional, successfully connecting the deployed Reflex frontend client to the FastAPI backend on Render is currently pending. PRs addressing this service connection are a top priority.

**How to contribute:**
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/Optimization`).
3. Commit your changes (`git commit -m 'Add Optimization'`).
4. Push to the branch (`git push origin feature/Optimization`).
5. Open a Pull Request.
```
