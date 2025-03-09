from gradio_llm import query_gradio_client

class CodeStructureAgent:
    def __init__(self, tool):
        self.tool = tool
        self.name = "CodeStructureAgent"

    def create_plan(self, code):
        """Create a plan for analyzing the modularity and structure of the code."""
        plan_prompt = f"""
        You are a software architecture expert. Create a simple step-by-step plan of max 5 steps to analyze the modularity
        and structure of the provided code.
        Ensure your plan covers aspects such as function/class structure, cyclomatic complexity, maintainability, and coupling.
        Do not analyze or improve/revise the code yet.
        Ignore comments and focus only on issues found by the tool.

        This is your Code Structure Analysis tool: {self.tool.description}

        Code:
        {code}
        """
        return query_gradio_client(plan_prompt)

    def analyze_structure(self, code):
        """Run the code structure analysis tool and return its output."""
        return self.tool.func(code)

    def generate_report(self, plan, tool_feedback, code):
        """Generate a final report based on the plan, tool feedback, and code."""
        report_prompt = f"""
        You are a software architecture expert. Based on the following:
        - Analysis Plan: {plan}
        - Tool Feedback: {tool_feedback}
        - Code: {code}

        Generate a short report summarizing all modularity and structural issues and suggesting improvements.
        Focus only on issues detected by the tool and ignore any comments in the code.
        If the issues are only minor and minor improvements are required, then do not say that those issues were detected or suggest improvements.
        Do not improve/revise the code.
        """
        return query_gradio_client(report_prompt)

    def check_report(self, report):
        """Check if there are structural/modularity issues based on the report."""
        structure_validation_prompt = f"""
        You are a software architecture expert. Based on the following modularity and structure report, determine if the code has any issues.
        Ignore comments and focus only on tool-detected issues.
        Report: {report}
        Answer only 'yes' if there are issues or 'no' if the code is fine.
        """
        has_issues = query_gradio_client(structure_validation_prompt).strip().lower() == "yes"
        return not has_issues  # Returns True if code is fine, False otherwise.

    def run(self, code):
        """Execute the code structure checking workflow."""
        plan = self.create_plan(code)
        tool_analysis = self.analyze_structure(code)
        report = self.generate_report(plan, tool_analysis, code)
        is_valid = self.check_report(report)
        return report, is_valid
