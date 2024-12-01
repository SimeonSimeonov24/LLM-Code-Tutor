from gradio_client import Client
from langchain.prompts import PromptTemplate
from langchain.agents import Tool

# Gradio Client Setup
client = Client("Nymbo/Qwen2.5-Coder-32B-Instruct-Serverless")


# Helper function for querying Gradio Client
def query_gradio_client(prompt):
    """Query the Gradio API endpoint."""
    result = client.predict(
        message=prompt,
        system_message="",
        max_tokens=8196,
        temperature=0.0,
        top_p=0.95,
        api_name="/chat"
    )
    return result


def syntax_analysis(code):
    """Analyze the code for syntax errors using Parso."""
    import parso
    try:
        # Load the grammar for the current Python version
        grammar = parso.load_grammar()
        # Parse the code
        module = grammar.parse(code)
        # Iterate over syntax errors
        errors = [{"line": error.start_pos[0], "message": error.message} for error in grammar.iter_errors(module)]
        return "No syntax issues found." if not errors else errors
    except Exception as e:
        # Handle unexpected parsing errors
        return [{"line": 0, "message": f"Error during parsing: {str(e)}"}]


syntax_tool = Tool(
    name="Syntax Analysis Tool",
    func=syntax_analysis,
    description="Analyzes the code for syntax errors."
)


# Define Semantics Analysis Tool
def semantics_analysis(code):
    """Analyze the code for semantic issues."""
    import ast
    try:
        tree = ast.parse(code)
        return tree  # Return the AST for further analysis
    except SyntaxError as e:
        return [{"line": e.lineno, "message": e.msg}]


semantics_tool = Tool(
    name="Semantics Analysis Tool",
    func=semantics_analysis,
    description="Analyzes the code for semantic issues and returns the AST if valid."
)


class SyntaxAgent:
    def __init__(self, tool):
        self.tool = tool
        self.name = "SyntaxAgent"

    def create_plan(self, code):
        """Create a plan for analyzing the code's syntax."""
        plan_prompt = f"""
        You are a syntax analysis expert. Create a simple step-by-step plan of max 5 simple steps to identify syntax issues in the provided code.
        Ensure your plan covers all possible aspects of syntax analysis.

        Do not analyse or improve/revise the code.
        
        Code:
        {code}
        """
        return query_gradio_client(plan_prompt)

    def analyze_syntax(self, code):
        """Run the syntax tool and return its output."""
        return self.tool.func(code)

    def generate_report(self, plan, tool_feedback, code):
        """Generate a final report based on the plan, tool feedback, and code."""
        report_prompt = f"""
        You are a syntax analysis expert. Based on the following:
        - Analysis Plan: {plan}
        - Tool Feedback: {tool_feedback}
        - Code: {code}
        
        Generate a short report summarizing all syntax issues within the code.
        Do not improve/revise the code.
        """
        return query_gradio_client(report_prompt)

    def run(self, code):
        """Execute the agent workflow."""
        plan = self.create_plan(code)
        print(f"Syntax Agent Plan: {plan}")
        tool_feedback = self.analyze_syntax(code)
        return self.generate_report(plan, tool_feedback, code)


# Semantics Agent
class SemanticsAgent:
    def __init__(self, tool):
        self.tool = tool
        self.name = "SemanticsAgent"

    def create_plan(self, code):
        """Create a plan for analyzing the code's semantics."""
        plan_prompt = f"""
        You are a semantics analysis expert. Create a simple step-by-step plan of max 5 simple steps to identify semantic issues in the provided code.
        Ensure your plan covers possible aspects of semantic analysis, including type checks, logic errors, and edge cases.
        Do not analyse or improve/revise the code yet. 
        
        Code:
        {code}
        """
        return query_gradio_client(plan_prompt)

    def analyze_semantics(self, code):
        """Run the semantics tool and return its output."""
        return self.tool.func(code)

    def generate_report(self, plan, tool_feedback, code):
        """Generate a final report based on the plan, tool feedback, and code."""
        report_prompt = f"""
        You are a semantics analysis expert. Based on the following:
        - Analysis Plan: {plan}
        - Tool Feedback: {tool_feedback}
        - Code: {code}
        Generate a simple report summarizing all semantic issues within the code.
        Do not improve/revise the code.

        """
        return query_gradio_client(report_prompt)

    def run(self, code):
        """Execute the agent workflow."""
        plan = self.create_plan(code)
        print(f"Semantics Agent Plan: {plan}")
        tool_feedback = self.analyze_semantics(code)
        return self.generate_report(plan, tool_feedback, code)



# Orchestrator Agent
class OrchestratorAgent:
    def __init__(self):
        self.name = "Orchestrator"
        self.summary_prompt_template = PromptTemplate(
            input_variables=["agent_feedback"],
            template="""You are an assistant summarizing the feedback from syntax and semantics analysis of the code. 
            Create a short summary of the feedback below and ensure it provides actionable insights to the user.
            If there are multiple faults with the code, make sure you summarize them all in your response. 
            If the syntax and semantic Agents both provided feedback to the same fault, do not list it twice. 

            Feedback from Agents:
            {agent_feedback}
            """
        )

    def summarize_feedback(self, feedback):
        """Summarize the feedback from all agents."""
        summary_prompt = self.summary_prompt_template.format(agent_feedback=feedback)
        return query_gradio_client(summary_prompt)

    def execute(self, code, agents):
        """Execute the analysis workflow."""
        feedback_list = []
        for agent in agents:
            feedback = agent.run(code)
            print(f"Feedback from Agent: {agent} is {feedback}")
            feedback_list.append(f"{agent.name} Feedback:\n{feedback}")
        combined_feedback = "\n\n".join(feedback_list)

        # Summarize the feedback
        summary = self.summarize_feedback(combined_feedback)
        return summary

# Example Usage
if __name__ == "__main__":
    # Initialize Agents
    syntax_agent = SyntaxAgent(syntax_tool)
    semantics_agent = SemanticsAgent(semantics_tool)
    orchestrator = OrchestratorAgent()

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

    # Execute Workflow
    summary = orchestrator.execute(code_snippet, agents=[syntax_agent, semantics_agent])
    print("Final Summary from Orchestrator:")
    print(summary)