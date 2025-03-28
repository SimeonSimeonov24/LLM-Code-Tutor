from gradio_llm import query_gradio_client

class SyntaxAgent:
    def __init__(self, tool):
        self.tool = tool
        self.name = "SyntaxAgent"

    def create_plan(self, code):
        """Create a plan for analyzing the code's syntax."""
        try:
            plan_prompt = f"""
            You are a syntax analysis expert. Create a simple step-by-step plan of max 5 simple steps to identify syntax issues in the provided code.
            Ensure your plan covers all possible aspects of syntax analysis.

            Do not analyse or improve/revise the code.
            
            Code:
            {code}
            """
            return query_gradio_client(plan_prompt)
        except Exception as e:
            return f"Error creating plan: {str(e)}"

    def analyze_syntax(self, code):
        """Run the syntax tool and return its output."""
        try:
            return self.tool.func(code)
        except Exception as e:
            return [{"line": 0, "message": f"Error during syntax analysis: {str(e)}"}]

    def generate_report(self, plan, tool_feedback, code):
        """Generate a final report based on the plan, tool feedback, and code."""
        try:
            report_prompt = f"""
            You are a syntax analysis expert. Based on the following:
            - Analysis Plan: {plan}
            - Tool Feedback: {tool_feedback}
            - Code: {code}
            
            Generate a short report summarizing all syntax issues within the code.
            Do not improve/revise the code.
            """
            return query_gradio_client(report_prompt)
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    def check_analysis(self, analysis):
        """Check if there are syntax issues based on the report."""
        try:
            syntax_validation_prompt = f"""
            You are a syntax analysis expert. Based on the following syntax analysis, determine if the code has any syntax issues.
            Analysis: {analysis}
            Answer only 'yes' if there are issues or 'no' if the code is fine.
            """
            has_issues = query_gradio_client(syntax_validation_prompt).strip().lower() == "yes"
            return not has_issues  # Returns True if code is fine, False otherwise.
        except Exception as e:
            return False  # Assume there are issues if error occurs during validation
        
    def run(self, code):
        """Execute the syntax checking workflow."""
        try:
            plan = self.create_plan(code)
            tool_analysis = self.analyze_syntax(code)
            report = self.generate_report(plan, tool_analysis, code)

            is_valid = self.check_analysis(tool_analysis)

            return report, is_valid
        except Exception as e:
            return f"Error during syntax analysis workflow: {str(e)}", False