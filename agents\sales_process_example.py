import os
from dotenv import load_dotenv
from agents.sales_process_orchestrator import SalesProcessOrchestrator

def main():
    # Load environment variables
    load_dotenv()
    
    # Ensure API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        return
    
    # Initialize the orchestrator
    orchestrator = SalesProcessOrchestrator()
    
    # Example inquiry
    inquiry = """
    Customer: BikeWorld GmbH
    Products requested:
    - 30 Deluxe Touring Bikes in Black
    - 20 Professional Touring Bikes in Red
    Delivery: Needed within 4 weeks
    Special requirements: All bikes must include standard warranty
    """
    
    # Process the sales inquiry through the agent chain
    try:
        results = orchestrator.process_sales_inquiry(inquiry)
        
        print("\n✅ Process completed successfully!")
        print("You can now proceed with the next step in the workflow.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 