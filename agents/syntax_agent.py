from gradio_llm import query_gradio_client

class SyntaxAgent:
    def __init__(self, tool):
        self.tool = tool
        self.name = "SyntaxAgent"

    def create_plan(self, code):
        """Create a plan for analyzing the code's syntax."""
        plan_prompt = f"""
        You are a syntax analysis expert. Create a simple step-by-step plan of max 5 simple steps to identify syntax issues in the provided code.
        Ensure your plan covers all possible aspects of syntax analysis.

        Do not analyse or improve/revise the code.
        
        Code:
        {code}
        """
        return query_gradio_client(plan_prompt)

    def analyze_syntax(self, code):
        """Run the syntax tool and return its output."""
        return self.tool.func(code)

    def generate_report(self, plan, tool_feedback, code):
        """Generate a final report based on the plan, tool feedback, and code."""
        report_prompt = f"""
        You are a syntax analysis expert. Based on the following:
        - Analysis Plan: {plan}
        - Tool Feedback: {tool_feedback}
        - Code: {code}
        
        Generate a short report summarizing all syntax issues within the code.
        Do not improve/revise the code.
        """
        return query_gradio_client(report_prompt)
    
    def check_analysis(self, analysis):
        """Check if there are syntax issues based on the report."""
        syntax_validation_prompt = f"""
        You are a syntax analysis expert. Based on the following syntax analysis, determine if the code has any syntax issues.
        Analysis: {analysis}
        Answer only 'yes' if there are issues or 'no' if the code is fine.
        """
        has_issues = query_gradio_client(syntax_validation_prompt).strip().lower() == "yes"
        return not has_issues  # Returns True if code is fine, False otherwise.
        
    def run(self, code):
        """Execute the syntax checking workflow with user interaction for fixing errors."""
        while True:
            plan = self.create_plan(code)
            print(f"Syntax Agent Plan: {plan}")
            tool_analysis = self.analyze_syntax(code)
            report = self.generate_report(plan, tool_analysis, code)

            print("Syntax Analysis Report:")
            print(report)

            # Check if the syntax is valid
            is_valid = self.check_analysis(tool_analysis)
            if is_valid:
                print("No syntax issues found. Proceeding with the workflow.")
                return code  # Return the last valid version of the code

            # If syntax issues are found, ask the user to fix them
            print("Syntax issues detected! Please provide the corrected code.")
            #code = input("Enter the corrected code:\n")
            code = """
def calculate_sum(a, b): 
    return a + b

def find_maximum(numbers):
    max_num = 0
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

result = calculate_sum(5, 10)   
max_value = find_maximum([3,6,1,9])  
print(result)
print(max_value)
    """
            if not code.strip():
                print("No input received. Keeping the previous code.")