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
        return query_gradio_client(plan_prompt)

    def analyze_semantics(self, code):
        """Run the semantics tool and return its output."""
        return self.tool.func(code)

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
        return query_gradio_client(report_prompt)
    
    def check_report(self, report):
        """Check if there are semantic issues based on the report."""
        semantics_validation_prompt = f"""
        You are a semantics analysis expert. Based on the following semantic analysis report, determine if the code has any semantic issues.
        Report: {report}
        Answer only 'yes' if there are issues or 'no' if the code is fine.
        """
        has_issues = query_gradio_client(semantics_validation_prompt).strip().lower() == "yes"
        return not has_issues  # Returns True if code is fine, False otherwise.

    def run(self, code):
        """Execute the semantics checking workflow with user interaction for fixing errors."""
        plan = self.create_plan(code)
        print(f"Semantics Agent Plan: {plan}")
        while True:
            tool_analysis = self.analyze_semantics(code)
            report = self.generate_report(plan, tool_analysis, code)

            print("Semantics Analysis Report:")
            print(report)

            # Check if the semantics are valid
            is_valid = self.check_report(report)
            if is_valid:
                print("No semantic issues found. Proceeding with the workflow.")
                return code  # Return the last valid version of the code

            # If semantic issues are found, ask the user to fix them
            print("Semantic issues detected! Please provide the corrected code.")
            # code = input("Enter the corrected code:\n")
            code = """
def calculate_sum(a, b): 
    return a + b

def find_maximum(numbers):
    if not numbers:  # Handling empty list
        return None
    max_num = numbers[0]  # Start with the first element
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

result = calculate_sum(5, 10)   
max_value = find_maximum([3,6,1,9])  
print(result)
print(max_value)
            """
            print(f"Corrected Code: {code}")
            if not code.strip():
                print("No input received. Keeping the previous code.")
