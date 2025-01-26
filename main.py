from huggingface_hub import InferenceClient
from langchain.prompts import PromptTemplate
from langchain.agents import Tool

# Hugging Face Inference API Client
client = InferenceClient(api_key="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")


# Helper function for querying Hugging Face Inference API
def query_inference_api(prompt):
    messages = [{"role": "user", "content": prompt}]
    completion = client.chat_completion(
        model="Qwen/Qwen2.5-Coder-7B-Instruct",
        messages=messages,
        max_tokens=500
    )
    return completion.choices[0].message["content"]


# Define Syntax Analysis Tool
def syntax_analysis(code):
    """Analyze the code for syntax errors."""
    import parso
    tree = parso.parse(code)
    errors = [{"line": error.line, "message": error.message} for error in tree.errors]
    return "No syntax issues found." if not errors else errors


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
        ast.parse(code)
        return "No semantic issues found."
    except SyntaxError as e:
        return [{"line": e.lineno, "message": e.msg}]


semantics_tool = Tool(
    name="Semantics Analysis Tool",
    func=semantics_analysis,
    description="Analyzes the code for semantic issues."
)


# Syntax Agent
class SyntaxAgent:
    def __init__(self, tool):
        self.tool = tool
        self.name = "SyntaxAgent"
        self.prompt_template = PromptTemplate(
            input_variables=["tool_feedback"],
            template="""
            You are a syntax analysis expert. Based on the feedback below, provide a detailed report
            on syntax issues and suggest improvements for the code.

            Tool Feedback:
            {tool_feedback}
            """
        )

    def run(self, code):
        tool_feedback = self.tool.func(code)
        if isinstance(tool_feedback, list):
            tool_feedback = "\n".join([str(item) for item in tool_feedback])
        prompt = self.prompt_template.format(tool_feedback=tool_feedback)
        return query_inference_api(prompt)


# Semantics Agent
class SemanticsAgent:
    def __init__(self, tool):
        self.tool = tool
        self.name = "SemanticsAgent"
        self.prompt_template = PromptTemplate(
            input_variables=["tool_feedback"],
            template="""
            You are a semantics analysis expert. Based on the feedback below, provide a detailed report
            on semantic issues and suggest improvements for the code.

            Tool Feedback:
            {tool_feedback}
            """
        )

    def run(self, code):
        tool_feedback = self.tool.func(code)
        if isinstance(tool_feedback, list):
            tool_feedback = "\n".join([str(item) for item in tool_feedback])
        prompt = self.prompt_template.format(tool_feedback=tool_feedback)
        return query_inference_api(prompt)


# Orchestrator Agent
class OrchestratorAgent:
    def __init__(self):
        self.name = "Orchestrator"
        self.prompt_template = PromptTemplate(
            input_variables=["code"],
            template="""
            You are an expert programming assistant. Analyze the following code and create a step-by-step
            plan for analyzing its syntax and semantics. Specify the tools to be used.

            Code:
            {code}
            """
        )

    def create_plan(self, code):
        prompt = self.prompt_template.format(code=code)
        return query_inference_api(prompt)

    def execute(self, code, agents):
        plan = self.create_plan(code)
        print(f"Plan created by Orchestrator:\n{plan}")

        feedback_list = []
        for agent in agents:
            feedback = agent.run(code)
            feedback_list.append(f"{agent.name} Feedback:\n{feedback}")
        return "\n\n".join(feedback_list)


# Example Usage
if __name__ == "__main__":
    # Initialize Agents
    syntax_agent = SyntaxAgent(syntax_tool)
    semantics_agent = SemanticsAgent(semantics_tool)
    orchestrator = OrchestratorAgent()

    # Example Code to Analyze
    code_snippet = """
    def test_function(x):
        if x > 10
            return x
    """

    # Execute Workflow
    feedback = orchestrator.execute(code_snippet, agents=[syntax_agent, semantics_agent])
    print("Final Feedback from Multi-Agent System:")
    print(feedback)
