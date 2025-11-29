SCAI - Autonomous B2B Sales Agent (v1.0)
A hybrid Agentic AI system designed to automate B2B retail ordering. This MVP version features a Python-based reasoning engine (LangChain + Llama 3.1) connected to a robust Spring Boot & MySQL enterprise backend.

🚀 Version 1 Features (MVP)
Hybrid Architecture: Python Brain + Java Body.

Autonomous Tool Usage: The Agent intelligently calls REST APIs to check stock and place orders.

Local AI: Powered by Ollama (Llama 3.1) for data privacy.

Enterprise Backend: Spring Boot application with MySQL persistence.

🛠️ Tech Stack
Brain: Python, LangChain, Ollama

Body: Java Spring Boot, REST APIs, JPA/Hibernate

Database: MySQL

⚡ How to Run
Start Backend: mvnw spring-boot:run (in backend-java)

Start Agent: python main.py (in agent-python)