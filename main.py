from agents.orchestrator_agent import OrchestratorAgent
from agents.syntax_agent import SyntaxAgent
from agents.semantics_agent import SemanticsAgent
from tools.syntax_tool import syntax_tool
from tools.semantics_tool import semantics_tool

if __name__ == "__main__":
    # Initialize Agents
    syntax_agent = SyntaxAgent(syntax_tool)
    semantics_agent = SemanticsAgent(semantics_tool)
    orchestrator = OrchestratorAgent(agents=[syntax_agent, semantics_agent])

    # Example Code to Analyze
    code_snippet = """
def calculate_sum(a, b
    return a + b

def find_maximum(numbers):
    max_num = 0
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

result = calculate_sum(5, "10")  
max_value = find_maximum("not_a_list") 
print(result)
print(max_value)
    """

    # Run the orchestrator workflow
    orchestrator.run_workflow(code_snippet)
