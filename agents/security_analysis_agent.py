from gradio_llm import query_gradio_client

class SecurityAnalysisAgent:
    def __init__(self, tool):
        self.tool = tool
        self.name = "SecurityAnalysisAgent"

    def create_plan(self, code):
        """Create a plan for analyzing the security of the code."""
        plan_prompt = f"""
        You are a cybersecurity expert. Create a simple step-by-step plan of max 5 steps to analyze the security of the provided code.
        Ensure your plan covers aspects such as:
        - Input validation (to prevent injection attacks)
        - Hardcoded credentials/secrets
        - Insecure function usage (e.g., eval, exec)
        - Weak cryptographic practices
        - Dependency security (unsafe imports)
        
        Do not analyze or improve/revise the code yet.
        
        This is your Security Analysis tool: {self.tool.description}

        Code:
        {code}
        """
        try:
            return query_gradio_client(plan_prompt)
        except Exception as e:
            return f"Error generating security analysis plan: {str(e)}"

    def analyze_security(self, code):
        """Run the security analysis tool and return its output."""
        try:
            return self.tool.func(code)
        except Exception as e:
            return f"Error running security analysis: {str(e)}"

    def generate_report(self, plan, tool_feedback, code):
        """Generate a final security report based on the plan, tool feedback, and code."""
        report_prompt = f"""
        You are a cybersecurity expert. Based on the following:
        - Security Analysis Plan: {plan}
        - Tool Feedback: {tool_feedback}
        - Code: {code}

        Generate a short report summarizing all security vulnerabilities and suggesting improvements.
        Focus only on issues detected by the tool.
        If no major security issues are found, state that the code appears secure.
        If only 1-2 LOW severity issues are found, state that the code appears mostly secure but still suggest improvements.
        However, state that the issues are not severe and do not require immediate action.

        Do not improve/revise the code.
        """
        try:
            return query_gradio_client(report_prompt)
        except Exception as e:
            return f"Error generating security report: {str(e)}"
    
    def check_report(self, report, tool_feedback):
        """Check if there are security issues based on the report."""
        security_validation_prompt = f"""
        You are a cybersecurity expert. Based on the following security report, determine if the code has any security vulnerabilities.

        Report: {report}
        Tool Feedback: {tool_feedback}
        Answer only 'yes' if there are vulnerabilities such as anything over MEDIUM severity.
        Answer only 'no' if the code is secure or only contains 1-2 LOW severity issues.
        """
        try:
            has_issues = query_gradio_client(security_validation_prompt).strip().lower() == "yes"
            return not has_issues  # Returns True if code is secure, False otherwise.
        except Exception as e:
            return f"Error checking security report: {str(e)}"

    def run(self, code):
        """Execute the security checking workflow."""
        try:
            plan = self.create_plan(code)
            tool_analysis = self.analyze_security(code)
            report = self.generate_report(plan, tool_analysis, code)
            is_valid = self.check_report(report, tool_analysis)
            return report, is_valid
        except Exception as e:
            return f"Error during security analysis workflow: {str(e)}", False