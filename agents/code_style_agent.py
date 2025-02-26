from gradio_llm import query_gradio_client


class CodeStyleAgent:
    def __init__(self, tool):
        self.tool = tool
        self.name = "CodeStyleAgent"

    def create_plan(self, code):
        """Create a plan for analyzing the code's style."""
        plan_prompt = f"""
        You are a coding style expert. Create a simple step-by-step plan of max 5 steps to identify style and best practices issues in the provided code.
        Ensure your plan covers aspects such as indentation, naming conventions, and overall readability.
        Do not analyze or improve/revise the code yet.
        Ignore comments and focus only on structural and formatting issues found by autopep8.

        Code:
        {code}
        """
        return query_gradio_client(plan_prompt)

    def analyze_style(self, code):
        """Run the coding style tool and return its output."""
        return self.tool.func(code)

    def generate_report(self, plan, tool_feedback, code):
        """Generate a final report based on the plan, tool feedback, and code."""
        report_prompt = f"""
        You are a coding style expert. Based on the following:
        - Analysis Plan: {plan}
        - Tool Feedback: {tool_feedback}
        - Code: {code}

        Generate a short report summarizing all coding style issues and suggesting improvements.
        Focus only on issues detected by autopep8 and ignore any comments in the code.
        Do not improve/revise the code.
        """
        return query_gradio_client(report_prompt)

    def check_report(self, report):
        """Check if there are coding style issues based on the report."""
        style_validation_prompt = f"""
        You are a coding style expert. Based on the following coding style report, determine if the code has any style issues.
        Ignore comments and focus only on autopep8-detected issues.
        Report: {report}
        Answer only 'yes' if there are issues or 'no' if the code is fine.
        """
        has_issues = query_gradio_client(style_validation_prompt).strip().lower() == "yes"
        return not has_issues  # Returns True if code is fine, False otherwise.

    def run(self, code):
        """Execute the coding style checking workflow."""
        plan = self.create_plan(code)
        tool_analysis = self.analyze_style(code)
        report = self.generate_report(plan, tool_analysis, code)

        is_valid = self.check_report(report)

        return report, is_valid
