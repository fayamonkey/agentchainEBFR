from laboratory import AgentLaboratory
import os
import traceback
import time
import json
from updater import GitHubUpdater

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Configuration file not found. Please run setup.bat first.")
        input("Press Enter to exit...")
        exit(1)

def check_for_updates():
    """Check for updates and prompt user to update if available."""
    print("Checking for updates...")
    updater = GitHubUpdater()
    updates_available, commit_msg = updater.check_for_updates()
    
    if updates_available:
        print("\nA new version is available!")
        if commit_msg:
            print(f"Latest update: {commit_msg}")
        
        response = input("\nWould you like to update now? (y/n): ").lower().strip()
        if response == 'y':
            success, message = updater.update()
            if success:
                print("\nUpdate successful! Please restart the application.")
                input("Press Enter to exit...")
                exit(0)
            else:
                print(f"\nUpdate failed: {message}")
                input("Press Enter to continue with current version...")
    else:
        print("You are running the latest version.")

def main():
    try:
        # Check for updates at startup
        check_for_updates()
        
        print("Starting Agent Laboratory...")
        print("Initializing with gpt-4o model...\n")
        
        # Load configuration
        config = load_config()
        api_key = config.get('api_key')
        
        if not api_key:
            print("API key not found. Please run setup.bat first.")
            input("Press Enter to exit...")
            return
        
        # Initialize the laboratory with gpt-4o
        lab = AgentLaboratory(api_key=api_key, model_name="gpt-4o")
        print("Laboratory initialized successfully!\n")
        
        # Define research topic and any additional notes
        print("Please provide the following information:")
        research_topic = input("Enter your research topic: ").strip()
        if not research_topic:
            raise ValueError("Research topic cannot be empty")
            
        focus_areas = input("Enter focus areas (comma-separated): ").strip()
        if not focus_areas:
            raise ValueError("Focus areas cannot be empty")
            
        task_notes = {
            "focus_areas": [area.strip() for area in focus_areas.split(",")],
            "experiment_preferences": {
                "dataset_size": "small",
                "model_complexity": "medium",
                "evaluation_metrics": ["accuracy", "perplexity"]
            }
        }
        
        print("\nStarting research process...")
        print("This may take several minutes depending on the complexity of the topic.\n")
        
        # Conduct research
        results = lab.conduct_research(research_topic, task_notes)
        
        # Print research status
        print("\nResearch Status:")
        status = lab.get_research_status()
        for phase, complete in status.items():
            print(f"{phase}: {'Complete' if complete else 'Incomplete'}")
        
        # Print final report
        print("\nFinal Report:")
        print("=" * 80)
        print(results["final_report"])
        print("=" * 80)
        
        print("\nResearch complete! Press Enter to exit...")
        input()
        
    except Exception as e:
        print("\nAn error occurred:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nFull error traceback:")
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()

if __name__ == "__main__":
    main() 