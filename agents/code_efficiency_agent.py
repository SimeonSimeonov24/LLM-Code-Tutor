from gradio_llm import query_gradio_client

class CodeEfficiencyAgent:
    def __init__(self, tool):
        self.tool = tool
        self.name = "CodeEfficiencyAgent"

    def create_plan(self, code):
        """Create a plan for analyzing code efficiency."""
        plan_prompt = f"""
        You are a software optimization expert. Create a simple step-by-step plan of max 5 steps to analyze the efficiency
        of the provided code.
        Ensure your plan covers aspects such as algorithm complexity, redundant operations, suboptimal data structures, 
        and inefficient loops.
        Do not analyze or improve/revise the code yet.
        Ignore comments and focus only on issues found by the tool.

        This is your Code Efficiency Analysis tool: {self.tool.description}

        Code:
        {code}
        """
        return query_gradio_client(plan_prompt)

    def analyze_efficiency(self, code):
        """Run the code efficiency analysis tool and return its output."""
        return self.tool.func(code)

    def generate_report(self, plan, tool_feedback, code):
        """Generate a final report based on the plan, tool feedback, and code."""
        report_prompt = f"""
        You are a software optimization expert. Based on the following:
        - Analysis Plan: {plan}
        - Tool Feedback: {tool_feedback}
        - Code: {code}

        Generate a short report summarizing all efficiency issues and suggesting improvements.
        Focus only on issues detected by the tool and ignore any comments in the code.
        If the issues are only minor, then do not say that those issues were detected or suggest improvements.
        Do not improve/revise the code.
        """
        return query_gradio_client(report_prompt)

    def check_report(self, report):
        """Check if there are efficiency issues based on the report."""
        efficiency_validation_prompt = f"""
        You are a software optimization expert. Based on the following efficiency report, determine if the code has any issues.
        Ignore comments and focus only on tool-detected issues.
        Report: {report}
        Answer only 'yes' if there are issues or 'no' if the code is fine.
        """
        has_issues = query_gradio_client(efficiency_validation_prompt).strip().lower() == "yes"
        return not has_issues  # Returns True if code is efficient, False otherwise.

    def run(self, code):
        """Execute the code efficiency checking workflow."""
        plan = self.create_plan(code)
        tool_analysis = self.analyze_efficiency(code)
        report = self.generate_report(plan, tool_analysis, code)
        is_valid = self.check_report(report)
        return report, is_valid