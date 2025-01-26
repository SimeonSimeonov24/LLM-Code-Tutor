from gradio_client import Client
from langchain.prompts import PromptTemplate
from langchain.agents import Tool

# Gradio Client Setup
client = Client("Krass/Qwen-Qwen2.5-Coder-32B-Instruct")


# Helper function for querying Gradio Client
def query_gradio_client(prompt):
    """Query the Gradio API endpoint."""
    result = client.predict(
        message=prompt,
        # system_message="",
        # max_tokens=8196,
        # temperature=0.0,
        # top_p=0.95,
        api_name="/chat"
    )
    return result


def syntax_analysis(code):
    """Analyze the code for syntax errors using Parso."""
    import parso
    try:
        # Load the grammar for the current Python version
        grammar = parso.load_grammar()
        # Parse the code
        module = grammar.parse(code)
        # Iterate over syntax errors
        errors = [{"line": error.start_pos[0], "message": error.message} for error in grammar.iter_errors(module)]
        return "No syntax issues found." if not errors else errors
    except Exception as e:
        # Handle unexpected parsing errors
        return [{"line": 0, "message": f"Error during parsing: {str(e)}"}]


syntax_tool = Tool(
    name="Syntax Analysis Tool",
    func=syntax_analysis,
    description="Analyzes the code for syntax errors."
)


# Define Semantics Analysis Tool
def semantics_analysis(code):
    """Analyze the code for semantic issues."""
    import ast
    try:
        tree = ast.parse(code)
        return tree  # Return the AST for further analysis
    except SyntaxError as e:
        return [{"line": e.lineno, "message": e.msg}]


semantics_tool = Tool(
    name="Semantics Analysis Tool",
    func=semantics_analysis,
    description="Analyzes the code for semantic issues and returns the AST if valid."
)


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

    def run(self, code):
        """Execute the agent workflow."""
        plan = self.create_plan(code)
        print(f"Syntax Agent Plan: {plan}")
        tool_feedback = self.analyze_syntax(code)
        return self.generate_report(plan, tool_feedback, code)


# Semantics Agent
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
        Generate a simple report summarizing all semantic issues within the code.
        Do not improve/revise the code.

        """
        return query_gradio_client(report_prompt)

    def run(self, code):
        """Execute the agent workflow."""
        plan = self.create_plan(code)
        print(f"Semantics Agent Plan: {plan}")
        tool_feedback = self.analyze_semantics(code)
        return self.generate_report(plan, tool_feedback, code)

class OrchestratorAgent:
    def __init__(self, agents):
        self.name = "Orchestrator"
        self.agents = agents
        self.execution_plan = []

    def create_plan_with_llm(self, code):
        """Use the LLM to generate a dynamic execution plan."""
        # Step 1: Generate the initial plan with LLM
        plan_prompt = f"""
        You are an assistant coordinating a code analysis process. The available agents are:
        {', '.join(agent.name for agent in self.agents)}.
        Based on the code below, create an analysis plan. Indicate the order in which agents should run with a very short explanation of what the agents do.
        Keep it very simple, only a few lines.

        Code:
        {code}
        """
        response = query_gradio_client(plan_prompt)

        self.execution_plan = self.parse_plan(response)

        if not self.execution_plan:
            print("Warning: Execution plan is empty. Check the LLM response and parsed agent names.")

        return response

    def parse_plan(self, plan):        
        
        self.execution_plan = []
        # Step 2: Parse the agent names from the plan using an additional LLM prompt
        parse_plan_prompt = f"""
        You have the task to parse the necessary agents from the given plan:
        {plan}
        Make sure you only answer with the names of the agents.
        Example:
        ["SyntaxAgent", "SemanticsAgent"]
        """
        parsed_plan = query_gradio_client(parse_plan_prompt)
        print(f"Parsed Agent Names:\n{parsed_plan}")  # Debugging: Log the parsed agent names

        # Step 3: Convert parsed plan into Python list
        try:
            agent_names = eval(parsed_plan)  # Safely evaluate the parsed plan (expecting a list of strings)
            if not isinstance(agent_names, list) or not all(isinstance(name, str) for name in agent_names):
                raise ValueError("Parsed plan is not a valid list of agent names.")
        except Exception as e:
            print(f"Error parsing agent names: {e}")
            agent_names = []

        # Step 3: Match the parsed agent names to the corresponding agent objects
        matched_agents = []
        unmatched_agents = []
        for name in agent_names:
            found_agent = next((agent for agent in self.agents if agent.name == name), None)
            if found_agent:
                matched_agents.append(found_agent)
            else:
                unmatched_agents.append(name)

        # Handle unmatched agents
        if unmatched_agents:
            print(f"Warning: The following agents were not found: {unmatched_agents}")

        # Step 4: Return the matched agents as the execution plan
        return matched_agents

    def adjust_plan_with_llm(self, initial_plan, user_feedback):
        """Use the LLM to adjust the execution plan based on user input."""
        adjust_prompt = f"""
        The user has requested adjustments to the plan:
        {initial_plan}

        User Feedback: {user_feedback}

        Provide an updated execution plan based on the user's instructions. Clearly list the agents to be run and their order.
        """
        response = query_gradio_client(adjust_prompt)

        self.execution_plan = self.parse_plan(response)

        return response

    def decide_next_action(self, last_feedback=""):
        """Prompt the user and use their input to determine the next step."""
        print(f"Current Plan: {[agent.name for agent in self.execution_plan]}")
        if last_feedback:
            print(f"Last Feedback:\n{last_feedback}")

        user_input = input(
            "\nWhat would you like to do next? Options:\n"
            "- 'Run' to execute the plan.\n"
            "- 'Adjust' to modify the plan.\n"
            "- 'Exit' to finish the workflow.\n"
            "Your choice: "
        ).strip().lower()

        decision_prompt = f"""
        You are an assistant managing a workflow for analyzing code. 
        The current plan is:
        {[agent.name for agent in self.execution_plan]}

        The last feedback was:
        {last_feedback}

        The user has input the following: "{user_input}".

        Based on this input, determine the next step. Choose one of the following actions:
        - 'run' to execute the plan. If the user has said to execute or run.
        - 'adjust' to adjust the plan. If the user said "adjust" or has asked for adjustments.
        - 'exit' to end the workflow. If the user wants to cancel or exit.

        Return only the action as a single word: 'run', 'adjust', or 'exit'.
        """
        return query_gradio_client(decision_prompt).strip().lower()

    def execute(self, code):
        """Execute the analysis workflow based on the adjusted plan."""
        feedback_list = []
        for agent in self.execution_plan:
            feedback = agent.run(code)
            feedback_list.append(f"{agent.name} Feedback:\n{feedback}")
        return "\n\n".join(feedback_list)

    def run_workflow(self, code):
        """Run the orchestrator workflow, allowing LLM-driven decisions."""
        # Step 1: Create the initial plan
        print("Creating Initial Plan...")
        initial_plan = self.create_plan_with_llm(code)
        print("Initial Plan:")
        print(initial_plan)

        last_feedback = ""
        while True:
            # Prompt the user and let the LLM process their input
            next_action = self.decide_next_action(last_feedback)

            if next_action == "run":
                print("Executing the analysis...")
                last_feedback = self.execute(code)
                print("Analysis Feedback:")
                print(last_feedback)
            elif next_action == "adjust":
                user_feedback = input("Provide adjustments to the plan: ")
                adjusted_plan = self.adjust_plan_with_llm(initial_plan, user_feedback)
                print("Adjusted Plan:")
                print(adjusted_plan)
                initial_plan = adjusted_plan  # Update the plan for future adjustments
            elif next_action == "exit":
                print("Exiting the workflow. Goodbye!")
                break
            else:
                print("Unexpected response from the LLM. Ending the workflow.")
                break
# Example Usage
if __name__ == "__main__":
    # Initialize Agents
    syntax_agent = SyntaxAgent(syntax_tool)
    semantics_agent = SemanticsAgent(semantics_tool)
    orchestrator = OrchestratorAgent(agents=[syntax_agent, semantics_agent])

    # Example Code to Analyze
    code_snippet = """
def calculate_sum(a, b
    return a + b

def find_maximum(numbers):
    max_num = 0
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

result = calculate_sum(5, "10")  
max_value = find_maximum("not_a_list") 
print(result)
print(max_value)
    """

    # Run the orchestrator workflow
    orchestrator.run_workflow(code_snippet)