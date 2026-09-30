import sys
import os
import gc

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.planner_agent import plan_workflow
from agents.nl2sql_agent import run_nl2sql
from agents.bi_agent import run_bi_analytics
from agents.rag_agent import run_rag_search
from agents.forecasting_agent import run_forecasting
from agents.communication_agent import draft_communication
from agents.scheduling_agent import schedule_meeting
from agents.reporting_agent import generate_pdf_report
from agents.visualization_agent import generate_visualizations

def run_workflow(user_intent: str) -> list:
    """
    Orchestrates the end-to-end multi-agent execution pipeline.
    Takes user input, generates a dynamic plan, and delegates tasks to specialist agents.
    Passes structured insight context (latest_insight_context) between agents and flushes memory via gc.collect().
    """
    # Step 1: Generate Execution Plan via Planner Node
    planner_res = plan_workflow(user_intent)
    if isinstance(planner_res, dict):
        plan = planner_res.get("plan", [])
        reasoning = planner_res.get("reasoning", "")
    else:
        plan = planner_res
        reasoning = ""
    
    print("\n[Execution Node] Routing tasks...")
    results = []
    latest_insight_context = None
    
    # Step 2: Sequentially Execute Planned Tasks
    for step in plan:
        agent_type = step.get("agent")
        task_desc = step.get("task")
        
        res = None
        if agent_type == "nl2sql":
            print(f" -> Routing to NL2SQL Agent for: {task_desc}")
            res = run_nl2sql(task_desc)
            latest_insight_context = res
            results.append({"agent": "nl2sql", "task": task_desc, "result": res})
            
        elif agent_type in ["bi", "analytics"]:
            print(f" -> Routing to BI Agent for: {task_desc}")
            res = run_bi_analytics(task_desc, context_df=latest_insight_context)
            if isinstance(res, dict) and "insights" in res:
                latest_insight_context = res["insights"]
            else:
                latest_insight_context = res
            results.append({"agent": "bi", "task": task_desc, "result": res})
            
        elif agent_type == "rag":
            print(f" -> Routing to RAG Agent for: {task_desc}")
            res = run_rag_search(task_desc)
            results.append({"agent": "rag", "task": task_desc, "result": res})
            
        elif agent_type == "forecasting":
            print(f" -> Routing to Forecasting Agent for: {task_desc}")
            res = run_forecasting(task_desc)
            results.append({"agent": "forecasting", "task": task_desc, "result": res})
            
        elif agent_type == "visualization":
            print(f" -> Routing to Visualization Agent for: {task_desc}")
            res = generate_visualizations(task_desc, context_data=results)
            results.append({"agent": "visualization", "task": task_desc, "result": res})
            
        elif agent_type == "communication":
            print(f" -> Routing to Communication Agent for: {task_desc}")
            res = draft_communication(task_desc, context_data=results)
            results.append({"agent": "communication", "task": task_desc, "result": res})
            
        elif agent_type == "scheduling":
            print(f" -> Routing to Scheduling Agent for: {task_desc}")
            res = schedule_meeting(task_desc)
            results.append({"agent": "scheduling", "task": task_desc, "result": res})
            
        elif agent_type == "reporting":
            print(f" -> Routing to Reporting Agent for: {task_desc}")
            res = generate_pdf_report(task_desc, context_data=results)
            results.append({"agent": "reporting", "task": task_desc, "result": res})

        else:
            print(f" -> Warning: Unrecognized agent type '{agent_type}' for task: {task_desc}")
            
        # Flush memory after each agent execution step
        gc.collect()
            
    return {
        "user_intent": user_intent,
        "reasoning": reasoning,
        "steps": results
    }

if __name__ == "__main__":
    print("Testing Full EAIOS Orchestrator Pipeline...")
    test_intent = "Forecast next month's sales and draft an email to the regional manager."
    final_output = run_workflow(test_intent)
    print("\nWorkflow Execution Complete.")