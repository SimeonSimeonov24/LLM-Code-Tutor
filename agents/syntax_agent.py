from gradio_llm import query_gradio_client

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