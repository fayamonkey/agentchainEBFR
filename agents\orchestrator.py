from typing import Dict, Any
from agents.specialized_agents import ProjectPlannerAgent, PlanOptimizerAgent, PrerequisiteAnalyzerAgent

class ProjectPlanningOrchestrator:
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize the orchestrator with all required agents."""
        self.planner = ProjectPlannerAgent(model_name)
        self.optimizer = PlanOptimizerAgent(model_name)
        self.prerequisite_analyzer = PrerequisiteAnalyzerAgent(model_name)
        
    def process_app_idea(self, app_idea: str) -> Dict[str, Any]:
        """Process the app idea through all agents in sequence."""
        print("🚀 Starting project planning process...")
        
        # Phase 1: Initial Project Planning
        print("\n📋 Phase 1: Creating initial project plan...")
        initial_result = self.planner.execute(app_idea)
        print("✅ Initial plan created")
        
        # Phase 2: Plan Optimization
        print("\n🔄 Phase 2: Optimizing project plan...")
        optimization_result = self.optimizer.execute(initial_result)
        print("✅ Plan optimized")
        
        # Phase 3: Prerequisites Analysis
        print("\n🔍 Phase 3: Analyzing prerequisites...")
        final_result = self.prerequisite_analyzer.execute(optimization_result)
        print("✅ Prerequisites analyzed")
        
        # Combine all results
        return {
            "initial_plan": initial_result["initial_plan"],
            "optimized_plan": optimization_result["optimized_plan"],
            "final_plan": final_result["final_plan"]
        } 