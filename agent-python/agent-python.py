import os
import requests
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent

load_dotenv()

JAVA_API_URL = os.getenv("JAVA_API_URL", "http://localhost:8080/api") # Default fallback
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1")

@tool
def check_inventory(product_name: str):
    """
    Searches the warehouse inventory for a product by name.
    Use this BEFORE placing an order to check stock and get the correct Product ID.
    Returns: JSON list of products with Name, Price, Stock, and ID.
    """
    try:
        print(f"   [System] Searching inventory for: '{product_name}'...")
        # Use the variable instead of hardcoded URL
        response = requests.get(f"{JAVA_API_URL}/products", params={"query": product_name})
        
        if response.status_code == 200:
            data = response.json()
            if not data:
                return "No products found with that name."
            return str(data) 
        else:
            return f"Error: API returned status code {response.status_code}"
    except Exception as e:
        return f"Connection Error: {e}"

@tool
def place_order(product_id: str, quantity: int):
    """
    Places a confirmed order for a product.
    Requires the exact 'id' (e.g., 'COKE_001') found via check_inventory.
    Returns: Success or Failure message.
    """
    try:
        print(f"   [System] Placing order: ID={product_id}, Qty={quantity}...")
        # Use the variable instead of hardcoded URL
        response = requests.post(f"{JAVA_API_URL}/order", params={"productId": product_id, "quantity": quantity})
        return response.text
    except Exception as e:
        return f"Connection Error: {e}"

# --- 2. SETUP THE BRAIN (Ollama) ---

tools = [check_inventory, place_order]

# Initialize LLM using the env variable
llm = ChatOllama(model=LLM_MODEL, temperature=0)

# --- 3. DEFINE THE PERSONALITY ---

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are 'SCAI', an expert B2B Sales Agent for Salescode.
    
    YOUR RESPONSIBILITIES:
    1. Help store owners verify stock and place orders.
    2. ALWAYS use 'check_inventory' first to find the Product ID and available Stock.
    3. NEVER invent Product IDs. Only use IDs returned by the tool.
    4. If stock is low (less than 20), warn the user.
    5. If an item is Out of Stock, suggest a similar item from the inventory search results.
    
    Keep responses professional, concise, and helpful."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# --- 4. CREATE THE AGENT RUNTIME ---

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

# --- 5. RUN THE CHAT LOOP ---

if __name__ == "__main__":
    print(f"🤖 SCAI Agent is Online (Powered by {LLM_MODEL})")
    print(f"🔌 Connected to Backend: {JAVA_API_URL}")
    print("Type 'quit' to exit.\n")

    while True:
        user_input = input("Retailer (You): ")
        if user_input.lower() in ["quit", "exit"]:
            print("SCAI: Goodbye! Happy Selling.")
            break
        
        try:
            response = agent_executor.invoke({"input": user_input})
            print(f"SCAI: {response['output']}\n")
        except Exception as e:
            print(f"Error: {e}. (Make sure Ollama is running!)\n")