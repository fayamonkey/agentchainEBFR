import os
from dotenv import load_dotenv
from agents.orchestrator import ProjectPlanningOrchestrator

def main():
    # Load environment variables
    load_dotenv()
    
    # Ensure API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        return
    
    # Initialize the orchestrator
    orchestrator = ProjectPlanningOrchestrator()
    
    # Example app idea
    app_idea = """
    I want to create a task management app where users can:
    - Create and organize tasks
    - Set priorities and deadlines
    - Share tasks with team members
    - Track progress with a dashboard
    The app should be web-based and mobile-responsive.
    """
    
    # Process the app idea through the agent chain
    try:
        results = orchestrator.process_app_idea(app_idea)
        
        # Print results
        print("\n📝 Initial Project Plan:")
        print("=" * 80)
        print(results["initial_plan"])
        
        print("\n📈 Optimized Plan:")
        print("=" * 80)
        print(results["optimized_plan"])
        
        print("\n📋 Final Plan with Prerequisites:")
        print("=" * 80)
        print(results["final_plan"])
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 