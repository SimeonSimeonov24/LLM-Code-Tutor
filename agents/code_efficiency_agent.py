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
        """Generate a final report summarizing all efficiency issues and suggesting improvements."""
        report_prompt = f"""
        You are a software optimization expert. Based on the following:
        - Analysis Plan: {plan}
        - Tool Feedback: {tool_feedback}
        - Code: {code}

        Generate a short and precise report summarizing efficiency issues and suggest improvements.
        - **Critical Issues (must fix):** Only include inefficiencies that significantly impact performance.
        - **Minor Issues (Optional):** Only include very minor inefficiencies that do not impact performance.
        - If an inefficiency is **only relevant for massive datasets**, mention it but **do not flag it as an issue**.

        Format:
        - **Critical Issues:** [List significant performance-impacting problems]
        - **Minor Issues (Optional):** [List only if truly minor and not affecting performance]
        """
        return query_gradio_client(report_prompt)

    def check_report(self, report):
        """Ensure code is not marked valid if critical issues exist and prevent over-reporting minor issues."""
        efficiency_validation_prompt = f"""
        You are a software optimization expert. Based on the following efficiency report, determine if the code is efficient.
        
        Make sure you really focus on checking for critical issues first and answer "No" if there are any.
        If there are no critical issues then answer "Yes"

        Report:
        {report}
        """
        response = query_gradio_client(efficiency_validation_prompt).strip().lower()

        if response == "no":
            return False  # Code is inefficient due to critical issues.
        return True  # Code is valid if no critical issues exist.

    def run(self, code):
        """Execute the code efficiency checking workflow."""
        plan = self.create_plan(code)
        tool_analysis = self.analyze_efficiency(code)
        report = self.generate_report(plan, tool_analysis, code)
        is_valid = self.check_report(report)
        return report, is_valid
