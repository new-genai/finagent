from src.agents.router_agent import RouterAgent
from src.agents.workers import DynamicPandasWorker

class AgentCoordinator:
    def __init__(self, llm_call):
        self.router = RouterAgent(llm_call)
        # Khởi tạo True Agentic Worker
        self.worker = DynamicPandasWorker(llm_call)

    def plan_query(self, question: str) -> dict:
        plan = self.router.analyze(question)
        return plan.model_dump()

    def generate_code(self, question: str, plan_dict: dict, context_str: str) -> str:
        from src.agents.base import QueryPlan
        plan = QueryPlan(**plan_dict)
        
        # Bàn giao hoàn toàn quyền sinh mã cho Agentic Coder thay vì chia if-else
        return self.worker.generate_code(question, plan, context_str)