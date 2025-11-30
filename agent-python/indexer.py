import os
import requests
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter;
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

load_dotenv()
JAVA_API_URL = os.getenv("JAVA_API_URL", "http://localhost:8080/api")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1")
CHROMA_PATH = "./chroma_db"  # Folder where vector data will be saved

def index_products_data():
    """
    retrieves all the data from products table and
    creates vector database 
    """
    try:
        print(f"   [System] Retrieving products data from Java API...")
        response = requests.get("http://localhost:8080/api/all-products")
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: API returned status code {response.status_code}")
            return []
    except Exception as e:
        print(f"Connection Error: {e}")
        return []

def index_five_recent_orders_data():
    """
    retrieves all the data from orders table and
    creates vector database 
    """
    try:
        print(f"   [System] Retrieving orders data from Java API...")
        response = requests.get("http://localhost:8080/api/recent-orders")
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: API returned status code {response.status_code}")
            return []
    except Exception as e:
        print(f"Connection Error: {e}")
        return []
    
if __name__ == "__main__":
    products_data = index_products_data()
    
    orders_data = index_five_recent_orders_data()
    all_data = products_data + orders_data

    print(f"   [System] Processing {len(all_data)} items...")

    documents = [str(item) for item in all_data]
    
    text_splitter= RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks= text_splitter.create_documents(documents)
    
    embedding_func= OllamaEmbeddings(model=LLM_MODEL)

    vector_store = Chroma(
        collection_name="inventory_data",
        embedding_function=embedding_func,
        persist_directory=CHROMA_PATH
    )
    vector_store.add_documents(documents=chunks)

    print("🎉 Success! Inventory has been vectorized and saved.")
    
    