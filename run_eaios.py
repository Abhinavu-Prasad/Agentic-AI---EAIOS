import sys
import os

# Ensure Python can find local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.orchestrator import run_workflow

def main():
    print("==================================================")
    print("  Enterprise AI Operating System (EAIOS) - Interactive CLI")
    print("==================================================")
    print("Type any natural language request (e.g., 'What is the total sales for HOBBIES?')")
    print("Type 'exit' or 'quit' to close.\n")
    
    while True:
        try:
            user_intent = input("\n[User Intent] > ").strip()
            
            if not user_intent:
                continue
            if user_intent.lower() in ["exit", "quit"]:
                print("Shutting down EAIOS CLI. Goodbye!")
                break
            
            print(f"\n[EAIOS] Dispatching workflow for: '{user_intent}'...")
            
            # Execute the full LangGraph multi-agent pipeline dynamically
            response = run_workflow(user_intent)
            steps = response.get("steps", []) if isinstance(response, dict) else response
            
            print("\n[Execution Summary]:")
            for step in steps:
                print(f" -> Agent Executed: {step.get('agent')}")
                
            print("\n[Status]: Success! Check 'data/reports/Autonomous_Executive_Report.pdf' for output.")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\n[Error Encountered]: {str(e)}")

if __name__ == "__main__":
    main()