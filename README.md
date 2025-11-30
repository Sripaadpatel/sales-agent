SCAI: Salescode Artificial Intelligence Agent (v2.0)

SCAI is an autonomous B2B Sales Agent designed to maximize revenue for retail suppliers. Unlike traditional chatbots that simply answer questions, SCAI is engineered with a Sales Persona that actively upsells, calculates bulk discounts, and manages inventory in real-time.

🚀 Key Features

🧠 Intelligent Sales Brain: Powered by Llama 3.1 via Ollama, capable of maintaining context and negotiation.

💰 Aggressive Revenue Optimization: Automatically detects small orders and pitches bulk discounts using real-time math proofs.

🔄 Smart Cross-Selling: Uses Semantic Search (Vector DB) to recommend related products based on the current order context.

📦 Real-Time Inventory Management: Connects directly to a Java Spring Boot backend to verify stock levels before confirming orders.

🔒 Hallucination Prevention: Version 2.0 includes strict "Strict Mode" protocols to prevent fake receipts and invented product IDs.

🛠️ Technology Stack

AI & Logic Layer (Python)

Orchestration: LangChain (Tool Calling Agent)

LLM Engine: Ollama (Llama 3.1)

Vector Database: ChromaDB (for inventory embedding and semantic search)

Embeddings: Nomic-Embed-Text / Llama 3.1

Core Backend (Java)

Framework: Spring Boot 3.x

Database: MySQL

Persistence: Spring Data JPA (Hibernate)

API: RESTful endpoints for Product and Order management

📂 Project Structure

salescode-agent-project/
├── agent-python/           # AI Logic
│   ├── agent-python.py     # Main Agent Runtime (The "Brain")
│   ├── indexer.py          # Vector Database Generator
│   └── chroma_db/          # Local Vector Store
├── backend-java/           # Core Logic
│   ├── src/main/java/      # Spring Boot Controllers & Models
│   └── pom.xml             # Maven Dependencies
└── README.md


⚙️ Setup & Installation

Prerequisites

Java 17+ & Maven

Python 3.11+ (Anaconda recommended)

MySQL Database

Ollama installed locally

1. Backend Setup

Navigate to backend-java.

Configure your MySQL credentials in application.properties.

Run the application:

mvn spring-boot:run


Server will start on http://localhost:8080.

2. AI Environment Setup

Navigate to agent-python.

Install dependencies:

pip install langchain langchain-community langchain-ollama langchain-chroma requests python-dotenv


Start the Ollama server:

ollama serve


3. Data Indexing

Before running the agent, sync the vector database with the backend SQL data:

python indexer.py


4. Launch SCAI Agent

python agent-python.py


📡 API Reference (Internal)

Method

Endpoint

Description

GET

/api/all-products

Fetches full inventory for vectorization.

GET

/api/recent-orders

Fetches recent transaction history.

POST

/api/order

Places a confirmed order and updates stock.

🗺️ Roadmap (v3.0)

UI Integration: Developing a React/Streamlit frontend.

Bug Fixes: Enhanced error handling for "Unknown" product metadata parsing.

Multi-Agent System: Separating "Sales" and "Support" into distinct AI workers.

© 2025 Salescode Agent Project.