from gradio_llm import query_gradio_client


class CodeStyleAgent:
    def __init__(self, tool):
        self.tool = tool
        self.name = "CodeStyleAgent"

    def create_plan(self, code):
        """Create a plan for analyzing the code's style."""
        plan_prompt = f"""
        You are a coding style expert. Create a simple step-by-step plan of max 5 steps to identify style issues in the provided code.
        Ensure your plan covers aspects such as indentation, naming conventions, and overall readability.
        Do not analyze or improve/revise the code yet.
        Ignore comments and focus only on issues found by autopep8.
        This is your Autopep8 tool: {self.tool.description}

        Code:
        {code}
        """
        try:
            return query_gradio_client(plan_prompt)
        except Exception as e:
            return f"Error generating code style analysis plan: {str(e)}"

    def analyze_style(self, code):
        """Run the coding style tool and return its output."""
        try:
            return self.tool.func(code)
        except Exception as e:
            return f"Error running code style analysis: {str(e)}"

    def generate_report(self, plan, tool_feedback, code):
        """Generate a final report based on the plan, tool feedback, and code."""
        report_prompt = f"""
        You are a coding style expert. Based on the following:
        - Analysis Plan: {plan}
        - Tool Feedback: {tool_feedback}
        - Code: {code}

        Generate a short report summarizing all coding style issues and suggesting improvements.
        Focus only on issues detected by black and ignore any comments in the code.
        Do not improve/revise the code.
        """
        try:
            return query_gradio_client(report_prompt)
        except Exception as e:
            return f"Error generating code style report: {str(e)}"
        
    def check_report(self, report):
        """Check if there are coding style issues based on the report."""
        style_validation_prompt = f"""
        You are a coding style expert. Based on the following coding style report, determine if the code has any style issues.
        Ignore comments and focus only on black-detected issues.
        Report: {report}
        Answer only 'yes' if there are issues or 'no' if the code is fine.
        """
        try:
            has_issues = query_gradio_client(style_validation_prompt).strip().lower() == "yes"
            return not has_issues
        except Exception as e:
            return f"Error checking code style report: {str(e)}"

    def run(self, code):
        """Execute the coding style checking workflow."""
        try:  
            plan = self.create_plan(code)
            tool_analysis = self.analyze_style(code)
            report = self.generate_report(plan, tool_analysis, code)
            is_valid = self.check_report(report)
            
            return report, is_valid
        except Exception as e:
            return f"Error running code style analysis: {str(e)}", False
    
