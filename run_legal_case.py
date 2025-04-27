from legal_agents import LegalAgentLaboratory
import json
from dotenv import load_dotenv
import os
from datetime import datetime

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        return
    
    # Initialize the legal agent laboratory
    lab = LegalAgentLaboratory(api_key=api_key)
    
    # Get case description from user
    print("\nWelcome to the Legal Case Processor!")
    print("Please describe your legal case. Include all relevant details.\n")
    case_description = input("Case description: ")
    
    # Process the case
    try:
        results = lab.process_case(case_description)
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"legal_case_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults have been saved to {filename}")
        
        # Display results summary
        print("\nCase Processing Summary:")
        print("------------------------")
        print("1. Initial Analysis Complete")
        print("2. Legal Research Complete")
        print("3. Document Draft Complete")
        print("4. Review & Optimization Complete")
        print("5. Strategy Development Complete")
        
        # Ask if user wants to see full results
        show_results = input("\nWould you like to see the full results? (y/n): ")
        if show_results.lower() == 'y':
            print("\nFull Results:")
            print("-------------")
            for key, value in results.items():
                if key != "case_description":  # Skip the original case description
                    print(f"\n{key.replace('_', ' ').title()}:")
                    print("-" * (len(key) + 1))
                    print(value)
                    print()
    
    except Exception as e:
        print(f"\nError processing case: {e}")

if __name__ == "__main__":
    main() 