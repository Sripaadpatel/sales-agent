import os
import requests
import datetime
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_chroma import Chroma

load_dotenv()

# ==========================================
# CONFIGURATION
# ==========================================
JAVA_API_URL = os.getenv("JAVA_API_URL", "http://localhost:8080/api")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1")
CHROMA_PATH = "./chroma_db"

# ⚠️ IMPORTANT: Matches the model you used for indexing!
EMBEDDING_MODEL_NAME = "llama3.1" 

print(f"⏳ Connecting to Knowledge Base using {EMBEDDING_MODEL_NAME}...")

# Initialize Vector DB
embedding_function = OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)
vector_store = Chroma(
    collection_name="inventory_data",
    embedding_function=embedding_function,
    persist_directory=CHROMA_PATH
)

# ==========================================
# 1. DEFINE TOOLS (The Agent's Hands)
# ==========================================

@tool
def check_inventory(item_name: str) -> str:
    """
    Useful to search for a product's price, stock, and ID.
    ALWAYS use this before calculating discounts or placing orders.
    Returns: JSON list of matching products.
    """
    print(f"   [Tool] Checking inventory for '{item_name}'...")
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    results = retriever.invoke(item_name)
    # DEBUG: Print what the agent actually found to the console
    if results:
        print(f"   [Debug] Found: {[doc.metadata.get('name', 'Unknown') for doc in results]}")
    else:
        print("   [Debug] No results found.")
        return "No products found. Ask user to check spelling."
        
    return results

@tool
def calculate_discount(current_price: float, quantity: int):
    """
    Useful to calculate savings for bulk orders. 
    Use this when a user orders less than 20 items to show them the math.
    Bulk Logic: If Quantity >= 20, apply 5% Discount.
    """
    standard_total = current_price * quantity
    
    if quantity >= 20:
        # User is already buying bulk - show them the savings they are getting
        discounted_total = standard_total * 0.95
        savings = standard_total - discounted_total
        return f"MATH PROOF: Standard Price: {standard_total:.2f}. BULK PRICE: {discounted_total:.2f}. YOU SAVE: {savings:.2f}! 💰"
    else:
        # User is buying small - show them what they COULD save if they bought 20
        upsell_qty = 20
        standard_upsell_total = current_price * upsell_qty
        discounted_upsell_total = standard_upsell_total * 0.95
        potential_savings = standard_upsell_total - discounted_upsell_total
        
        return (f"ANALYSIS: Buying {quantity} costs {standard_total:.2f} (No Discount). "
                f"OPPORTUNITY: If you buy {upsell_qty} units instead... "
                f"Normal Price: {standard_upsell_total:.2f}. "
                f"Your Price (5% OFF): {discounted_upsell_total:.2f}. "
                f"Total Savings: {potential_savings:.2f}! 🔥")
                
@tool
def recommend_cross_sell(product_name: str):
    """
    Useful to find related items to recommend AFTER a user places an order.
    Searches the database for items similar to the one purchased.
    """
    print(f"   [Tool] Recommending cross-sell items for '{product_name}'...")
    results = vector_store.similarity_search(product_name, k=5)
    # Filter out the exact same item if possible, but returning top 5 is usually fine
    return [doc.page_content for doc in results]

@tool
def place_order(product_id: str, product_name: str, quantity: int, unit_price: float = 0.0):
    """
    Places a FINAL confirmed order.
    Requires the exact 'product_id' found via check_inventory.
    """
    try:
        print(f"   [Tool] Placing order: ID={product_id}, Qty={quantity}...")
        # 1. Calculate Real Totals
        total_price = unit_price * quantity
        if quantity >= 20:
            total_price = total_price * 0.95 # Apply bulk discount
        # 2. Call API
        response = requests.post(
            f"{JAVA_API_URL}/orders",
            json={"product_id": product_id, "quantity": quantity}
        )
        if response.status_code == 200:
            order_data = response.json()
            real_order_id = order_data.get('order_id', 'PENDING')
            
            # We return a formatted block. The Agent MUST output this exactly.
            return (f"\n✅ ORDER PLACED SUCCESSFULLY!\n"
                    f"----------------------------\n"
                    f"Order ID:  #{real_order_id}\n"
                    f"Date:      {datetime.date.today()}\n"
                    f"Product:   {product_name}\n"
                    f"ID:        {product_id}\n"
                    f"Qty:       {quantity}\n"
                    f"Total:     ${total_price:.2f}\n"
                    f"----------------------------\n"
                    f"(Receipt generated by SalesSystem v1.0)")
        else:
            return f"❌ Failed to place order. API Response: {response.text}"
    except Exception as e:
        return f"❌ Error placing order: {str(e)}"
# ==========================================
tools = [check_inventory, calculate_discount, recommend_cross_sell, place_order]

# ==========================================
# 2. THE BRAIN (LLM and promt)
# ==========================================

llm = ChatOllama(model=LLM_MODEL, temperature=0.1)

system_prompt = f"""
You are 'SCAI', a High-Energy B2B Sales Agent. 
TODAY'S DATE: {datetime.date.today()}

**YOUR BEHAVIOR PROTOCOL:**
1. **Aggressive Upsell:** If a user orders small (<20 items), PUSH for bulk (20+).
2. **Smart Cross-Sell:** After EVERY confirmed order, immediately suggest a related item.
3. **Inventory First:** Always check stock using 'check_inventory' before promising anything.
4. **Negotiation:** If they hesitate on price, remind them of the profit margin or bulk savings.

**CRITICAL RULES FOR ORDER CONFIRMATION:**
- When the user confirms an order, you MUST call the 'place_order' tool.
- The 'place_order' tool will return a receipt text.
- **YOU MUST OUTPUT THAT RECEIPT EXACTLY AS IS.** - **DO NOT** rewrite the receipt. 
- **DO NOT** change the product name. 
- **DO NOT** invent a new format.
"""
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# ==========================================
# 3. RUNTIME
# ==========================================

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

if __name__ == "__main__":
    print(f"\n🚀 SCAI Sales Agent is READY! (Model: {LLM_MODEL})")
    print("---------------------------------------------------")
    
    chat_history = []
    while True:
        user_input = input("\nRetailer (You): ")
        if user_input.lower() in ["quit", "exit"]:
            print("SCAI: Closing the deal! Have a profitable day! 💼")
            break
        try:
            response = agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history
            })
            output = response['output']
            print(f"SCAI: {output}")
            chat_history.append(("human", user_input))
            chat_history.append(("ai", output))
        except Exception as e:
            print(f"SCAI: Oops! Something went wrong: {str(e)}")