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
        try:
            return query_gradio_client(plan_prompt)
        except Exception as e:
            return f"Error generating code efficiency analysis plan: {str(e)}"

    def analyze_efficiency(self, code):
        """Run the code efficiency analysis tool and return its output."""
        try:
            return self.tool.func(code)
        except Exception as e:
            return f"Error running code efficiency analysis: {str(e)}"
        
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
        try:
            return query_gradio_client(report_prompt)
        except Exception as e:
            return f"Error generating code efficiency report: {str(e)}"

    def check_analysis(self, report):
        """Ensure code is not marked valid if critical issues exist and prevent over-reporting minor issues."""
        efficiency_validation_prompt = f"""
        You are a software optimization expert. Based on the following efficiency report, determine if the code is efficient.
        
        Make sure you really focus on checking for critical issues first and answer "No" if there are any.
        If there are no critical issues then answer "Yes"

        Report:
        {report}
        """
        try:
            has_issues = query_gradio_client(efficiency_validation_prompt).strip().lower() == "yes"
            return not has_issues
        except Exception as e:
            return f"Error checking error handling report: {str(e)}"

    def run(self, code):
        """Execute the code efficiency checking workflow."""
        try:
            plan = self.create_plan(code)
            tool_analysis = self.analyze_efficiency(code)
            report = self.generate_report(plan, tool_analysis, code)
            is_valid = self.check_analysis(report)
            return report, is_valid
        except Exception as e:
            return f"Error running code efficiency analysis: {str(e)}", False
