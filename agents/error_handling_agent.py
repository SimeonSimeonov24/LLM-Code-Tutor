from gradio_llm import query_gradio_client


class ErrorHandlingAgent:
    def __init__(self, tool):
        self.tool = tool
        self.name = "ErrorHandlingAgent"

    def create_plan(self, code):
        """Create a plan for analyzing the code's error handling."""
        plan_prompt = f"""
        You are an error handling analysis expert. Create a simple step-by-step plan of max 5 steps to evaluate the error handling practices in the provided code.
        Ensure your plan covers all possible aspects of error handling, including try/except blocks, specific error messages, and graceful failure.

        Do not analyze or improve/revise the code.

        Code:
        {code}
        """
        return query_gradio_client(plan_prompt)

    def analyze_error_handling(self, code):
        """Run the error handling tool and return its output."""
        return self.tool.func(code)

    def generate_report(self, plan, tool_feedback, code):
        """Generate a final report based on the plan, tool feedback, and code."""
        report_prompt = f"""
        You are an error handling analysis expert. Based on the following:
        - Analysis Plan: {plan}
        - Tool Feedback: {tool_feedback}
        - Code: {code}

        Generate a short report summarizing all error handling issues within the code.
        Do not improve/revise the code.

        Ensure that your response is logically consistent.
        """
        return query_gradio_client(report_prompt)

    def check_analysis(self, analysis):
        """Check if there are error handling issues based on the report."""
        error_handling_validation_prompt = f"""
        You are an error handling analysis expert. Based on the following error handling analysis, determine if the code has any error handling issues.
        Analysis: {analysis}
        Answer only 'yes' if there are issues or 'no' if the code is fine.
        """
        has_issues = query_gradio_client(error_handling_validation_prompt).strip().lower() == "yes"
        return not has_issues  # Returns True if code is fine, False otherwise.

    def run(self, code):
        """Execute the error handling checking workflow."""
        plan = self.create_plan(code)
        tool_analysis = self.analyze_error_handling(code)
        report = self.generate_report(plan, tool_analysis, code)

        is_valid = self.check_analysis(report)  # Check based on report, not just tool feedback

        return report, is_valid
