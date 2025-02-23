from gradio_llm import query_gradio_client

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