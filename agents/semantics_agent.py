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
        try:
            return query_gradio_client(plan_prompt)
        except Exception as e:
            return f"Error generating analysis plan: {str(e)}"

    def analyze_semantics(self, code):
        """Run the semantics tool and return its output."""
        try:
            return self.tool.func(code)
        except Exception as e:
            return f"Error running semantics analysis: {str(e)}"

    def generate_report(self, plan, tool_feedback, code):
        """Generate a final report based on the plan, tool feedback, and code."""
        report_prompt = f"""
        You are a semantics analysis expert. Based on the following:
        - Analysis Plan: {plan}
        - Tool Feedback: {tool_feedback}
        - Code: {code}

        Generate a short report summarizing all semantic issues within the code.
        Do not improve/revise the code.
        """
        try:
            return query_gradio_client(report_prompt)
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    def check_report(self, report):
        """Check if there are semantic issues based on the report."""
        semantics_validation_prompt = f"""
        You are a semantics analysis expert. Based on the following semantic analysis report, determine if the code has any semantic issues.
        Report: {report}
        Answer only 'yes' if there are issues or 'no' if the code is fine.
        """
        try:
            has_issues = query_gradio_client(semantics_validation_prompt).strip().lower() == "yes"
            return not has_issues  # Returns True if code is fine, False otherwise.
        except Exception as e:
            return f"Error checking report: {str(e)}"

    def run(self, code):
        """Execute the semantics checking workflow."""
        try:
            plan = self.create_plan(code)
            tool_analysis = self.analyze_semantics(code)
            report = self.generate_report(plan, tool_analysis, code)

            is_valid = self.check_report(report)

            return report, is_valid
        except Exception as e:
            return f"Error during syntax analysis workflow: {str(e)}", False
