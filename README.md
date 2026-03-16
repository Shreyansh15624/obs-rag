# 🧠 Obsidian RAG: Decoupled Second Brain API [IN-PROGRESS]

> A production-ready, microservices-based Retrieval-Augmented Generation (RAG) system. It transforms static Obsidian markdown vaults into an interactive, context-aware API powered by Google Gemini 2.5 and serverless vector databases.

*(Link: [https://github.com/Shreyansh15624/obs-rag/raw/main/video/obs-rag.mp4](https://github.com/Shreyansh15624/obs-rag/raw/main/video/obs-rag.mp4))*

## 🚀 System Overview

This project bypasses the limitations of standard static file search by implementing a full RAG pipeline. It ingests local markdown data, processes it into high-dimensional embeddings, and exposes a secure API for semantic querying.

Designed with cloud-native principles, the architecture cleanly decouples the compute layer from the storage layer, allowing for stateless deployments and scalable vector retrieval.

## 🏗️ Core Architecture & Tech Stack

- **Compute & API:** FastAPI, Python 3.11+, Uvicorn (Asynchronous ASGI)
- **AI & Orchestration:** LangChain (v0.3+), Google Gemini 2.5 Flash, `text-embedding-004`
- **Storage Layer (Vector DB):** Pinecone (Production Cloud) / ChromaDB (Local Dev)
- **DevOps & CI/CD:** Docker, Render, `uv` Package Manager, Git LFS
- **UI Microservice:** Reflex (Local Client)

## ⚙️ Architectural Decisions & System Design

To transition this from a local script to a resilient, deployable service, several key architectural patterns were implemented:

### 1. Decoupled Storage & Stateless Compute

Initial iterations utilized a local ChromaDB instance, which violated the stateless nature of ephemeral cloud containers (like those on Render).

- **The Solution:** Migrated the production storage layer to **Pinecone**. Engineered a dedicated, rate-limit-aware data pipeline (`seed_pinecone.py`) that batches document embeddings and handles API backoff automatically, completely separating the data ingestion logic from the live query server.

### 2. Asynchronous API & Microservices Pattern

To prevent API blocking during high-latency LLM generation, the core system was rebuilt using **FastAPI** with `async/await` concurrency and strict **Pydantic** data validation.

- **Service Isolation:** To avoid port conflicts and maintain separation of concerns, the backend API is strictly bound to port `8080`, while the local Reflex UI client operates independently on port `8000`.

### 3. Edge Security & API Gateway

Exposing the generative endpoint to the public web created a vulnerability regarding API quota hijacking.

- **The Solution:** Implemented a lightweight middleware authentication layer. All incoming requests must pass a strict `X-API-Key` header validation before the server allocates any compute resources or initializes the LangChain agent, immediately rejecting unauthorized traffic with a 403 status.

### 4. Deterministic CI/CD Pipeline

- Leveraged `uv export` to generate strict, hashed dependency locks, eliminating environment mismatches between local Windows development and the Linux Docker containers in production.
- Configured automated deployments via Render linked to the `main` branch, utilizing environment variables for secure secret injection without hardcoding keys into the repository.

## 📦 Quick Start & Installation

### 1. Local Environment Setup

```bash
git clone https://github.com/Shreyansh15624/obs-rag
cd obs-rag

# Utilize uv for lightning-fast dependency resolution
uv sync

```

### 2. Environment Variables

Create a `.env` file (do not use quotation marks around values to ensure cross-platform Docker compatibility):

```env
GOOGLE_API_KEY=your_gemini_key
VAULT_PATH=/path/to/your/obsidian/vault
API_GATEWAY_KEY=your_custom_security_password

```

### 3. Data Ingestion & Execution

```bash
# Ingest local markdown into the Vector DB
./embed.sh

# Spin up the asynchronous FastAPI server
uv run server.py

```

## 🔮 Roadmap

* **Continuous Ingestion:** Implement a filesystem watchdog to auto-ingest Obsidian notes upon modification.
* **Local LLM Support:** Abstract the LangChain generation layer to support local execution via Ollama or LMStudio.
* **Agentic File Operations:** Extend function-calling to allow the AI to perform secure CRUD operations directly within the local vault.
