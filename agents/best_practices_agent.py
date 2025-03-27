from gradio_llm import query_gradio_client

class BestPracticesAgent:
    def __init__(self, tool):
        self.tool = tool
        self.name = "BestPracticesAgent"

    def create_plan(self, code):
        """Create a plan for analyzing best practices in the code."""
        plan_prompt = f"""
        You are an expert in software engineering best practices. Create a simple step-by-step plan of max 5 steps to analyze
        the provided code for adherence to best practices.
        Ensure your plan covers:
        - Magic number detection
        - Consistent variable naming and usage
        - Proper use of constants
        - Maintainability issues (excluding documentation)
        - Any other relevant best practice violations
        
        Do not analyze or improve/revise the code yet.
        
        This is your Best Practices Analysis tool: {self.tool.description}

        Code:
        {code}
        """
        try:
            return query_gradio_client(plan_prompt)
        except Exception as e:
            return f"Error generating best practices analysis plan: {str(e)}"

    def analyze_best_practices(self, code):
        """Runs the best practices analysis tool and gets all issues."""
        try:
            return self.tool.func(code)
        except Exception as e:
            return f"Error running best practices analysis: {str(e)}"
    
    def analyze_magic_numbers(self, code):
        """Sends a prompt to the LLM to check for magic numbers while avoiding false positives from defined constants."""
        prompt = f"""
        You are an expert in software engineering best practices. Your task is to analyze Python code **only for magic numbers** and flag **only numbers that are directly used in expressions without being defined as constants first**.

        ### **Rules:**
        - **IGNORE** numbers **0, 1, -1**, as they are commonly accepted as non-magic numbers.
        - **DO NOT** flag a number if it has already been assigned to a **constant variable** before usage.
        - **ONLY flag a number** if it is directly used in an expression **without being assigned to a constant** beforehand.
        - If a number appears in a `range()` function, **DO NOT flag it** if it is constructed using a pre-defined constant.
        - Provide a **structured list** of flagged numbers, including:
            - **Line number**
            - **The problematic number**
            - **A brief reason why it is a magic number**
        - If no violations exist, return **only**: "No magic numbers found."

        ### Now analyze the following code:
        {code}

        **Provide your analysis below:**
        """
        try:
            return query_gradio_client(prompt).strip()
        except Exception as e:
            return f"Error analyzing magic numbers: {str(e)}"

    def generate_report(self, tool_feedback, magic_numbers_analysis, code):
        """Generates a clear and actionable best practices report."""
        report_prompt = f"""
        You are an expert in software engineering best practices. 
        Based on the tool's feedback and the given code, generate a FINAL and COMPLETE report.

        - List **all** best practice violations in the code, **excluding** documentation, error handling, code structure, or efficiency-related issues.
        - Ensure that the report is actionable so that fixing the listed issues will make the code fully compliant.
        - Do **not** flag issues where a constant is already properly defined and used consistently.
        - **Do NOT flag an issue if it was already addressed using a constant.**
        - **Do NOT suggest unnecessary constants for 0, 1, -1, or pre-defined variables.**
        - Provide a **structured, detailed list** of problems, ensuring that each reported issue is genuinely a violation.
        - DO NOT CORRECT THE CODE!

        Tool Feedback: {tool_feedback}
        Magic Numbers Analysis: {magic_numbers_analysis}
        Code: {code}
        """
        try:
            return query_gradio_client(report_prompt).strip()
        except Exception as e:
            return f"Error generating best practices report: {str(e)}"

    def check_analysis(self, analysis):
        """Determines if the code fully follows best practices."""
        validation_prompt = f"""
        You are a software best practices expert. Based on the following analysis, does the code still contain **ANY** best practices violations?
        Analysis: {analysis}
        Answer **only** 'yes' if there are issues or 'no' if the code is fully correct.
        """
        try:
            has_issues = query_gradio_client(validation_prompt).strip().lower() == "yes"
            return not has_issues  # Returns True if code follows best practices, False otherwise.
        except Exception as e:
            return f"Error validating best practices analysis: {str(e)}"

    def run(self, code):
        """Runs the best practices checking workflow."""
        try:
            plan = self.create_plan(code)
            tool_analysis = self.analyze_best_practices(code)
            magic_numbers_analysis = self.analyze_magic_numbers(code)
            report = self.generate_report(tool_analysis, magic_numbers_analysis, code)
            is_valid = self.check_analysis(report)
            return report, is_valid
        except Exception as e:
            return f"Error during best practices analysis workflow: {str(e)}", False