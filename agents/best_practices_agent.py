from gradio_llm import query_gradio_client

class BestPracticesAgent:
    def __init__(self, tool):
        self.tool = tool
        self.name = "BestPracticesAgent"

    def analyze_best_practices(self, code):
        """Runs the best practices analysis tool and gets all issues."""
        return self.tool.func(code)

    def generate_report(self, tool_feedback, code):
        """Generates a clear and actionable best practices report."""
        report_prompt = f"""
        You are an expert in software engineering best practices. 
        Based on the tool's feedback and the given code, generate a FINAL and COMPLETE report.

        - List **all** best practice violations in the code.
        - Ensure that the report is actionable so that fixing the listed issues will make the code fully compliant.
        - If there are **no issues**, return ONLY: "🎉 All checks passed! Your code follows best practices!"
        - If there ARE issues, **DO NOT** say all checks passed. Instead, provide a structured, detailed list of problems.

        Tool Feedback: {tool_feedback}
        Code: {code}
        """

        return query_gradio_client(report_prompt).strip()

    def check_analysis(self, analysis):
        """Determines if the code fully follows best practices."""
        validation_prompt = f"""
        You are a software best practices expert. Based on the following analysis, does the code still contain **ANY** best practices violations?
        Analysis: {analysis}
        Answer **only** 'yes' if there are issues or 'no' if the code is fully correct.
        """
        has_issues = query_gradio_client(validation_prompt).strip().lower() == "yes"
        return not has_issues  # Returns True if code follows best practices, False otherwise.

    def run(self, code):
        """Runs the best practices checking workflow."""
        tool_analysis = self.analyze_best_practices(code)
        report = self.generate_report(tool_analysis, code)
        is_valid = self.check_analysis(report)

        return report, is_valid
