from gradio_llm import query_gradio_client


class DocumentationAgent:
    def __init__(self, tool):
        self.tool = tool
        self.name = "DocumentationAgent"

    def create_plan(self, code):
        """Create a plan for analyzing the documentation in the code."""
        plan_prompt = f"""
        You are a code documentation expert. Create a simple step-by-step plan of max 5 steps to evaluate the documentation quality in the provided code.
        Ensure your plan covers aspects like function/class docstrings, inline comments, and overall readability.

        Do not analyze or improve/revise the code.

        Code:
        {code}
        """
        try:
            return query_gradio_client(plan_prompt)
        except Exception as e:
            return f"Error generating documentation analysis plan: {str(e)}"

    def analyze_documentation(self, code):
        """Run the documentation analysis tool and return its output."""
        try:
            return self.tool.func(code)
        except Exception as e:
            return f"Error running documentation analysis: {str(e)}"
        
    def generate_report(self, plan, tool_feedback, code):
        """Generate a final report based on the plan, tool feedback, and code."""
        report_prompt = f"""
        You are a code documentation expert. Based on the following:
        - Analysis Plan: {plan}
        - Tool Feedback: {tool_feedback}
        - Code: {code}

        Generate a short report summarizing all documentation issues within the code.

        Do NOT add extra comments or suggestions if the documentation is already perfect.

        If there ARE issues, DO NOT say that all checks passed. Instead, provide clear feedback on what needs to be improved.
        """
        try:
            return query_gradio_client(report_prompt)
        except Exception as e:
            return f"Error generating documentation report: {str(e)}"

    def check_analysis(self, analysis):
        """Check if there are documentation issues based on the report."""
        documentation_validation_prompt = f"""
        You are a code documentation expert. Based on the following documentation analysis, determine if the code has any documentation issues.
        Analysis: {analysis}
        Answer only 'yes' if there are issues or 'no' if the documentation is fine.
        """
        try:
            has_issues = query_gradio_client(documentation_validation_prompt).strip().lower() == "yes"
            return not has_issues
        except Exception as e:
            return f"Error checking documentation report: {str(e)}"

    def run(self, code):
        """Execute the documentation checking workflow."""
        try:
            plan = self.create_plan(code)
            tool_analysis = self.analyze_documentation(code)
            report = self.generate_report(plan, tool_analysis, code)

            is_valid = self.check_analysis(report)

            return report, is_valid
        except Exception as e:
            return f"Error during documentation analysis workflow: {str(e)}", False            
