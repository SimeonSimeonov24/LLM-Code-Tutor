from gradio_llm import query_gradio_client

class OrchestratorAgent:
    def __init__(self, agents):
        self.name = "Orchestrator"
        self.agents = agents
        self.execution_plan = []

    def create_plan_with_llm(self, code):
        plan_prompt = f"""
        You are an assistant coordinating a code analysis process. The available agents are:
        {', '.join(agent.name for agent in self.agents)}.
        Based on the code below, create an analysis plan. Indicate the order in which agents should run with a very short explanation of what the agents do.
        Keep it very simple, only a few lines. Make sure to use Syntax and Semantic Agents first, since they are important.
        Do not add two explanations of the agents, only within the plan.

        Code:
        {code}
        
        Example:
        ***
        ### Analysis Plan

        1. **SyntaxAgent**: Checks for syntax errors and ensures the code is syntactically correct.
        2. **SemanticsAgent**: Evaluates the logical structure and meaning of the code to ensure it behaves as intended.
        ***
        """
        
        response = query_gradio_client(plan_prompt)
        self.execution_plan = self.parse_plan(response)
        if not self.execution_plan:
            print("Warning: Execution plan is empty. Check the LLM response and parsed agent names.")
        return response

    def parse_plan(self, plan):
        parse_plan_prompt = f"""
        You have the task to parse the necessary agents from the given plan:
        {plan}
        Make sure you only answer with the names of the agents.
        Example:
        ["SyntaxAgent", "SemanticsAgent"]
        """
        parsed_plan = query_gradio_client(parse_plan_prompt)
        try:
            agent_names = eval(parsed_plan)
            if not isinstance(agent_names, list) or not all(isinstance(name, str) for name in agent_names):
                raise ValueError("Parsed plan is not a valid list of agent names.")
        except Exception as e:
            print(f"Error parsing agent names: {e}")
            agent_names = []

        agent_dict = {agent.name: agent for agent in self.agents}

        matched_agents = [agent_dict[name] for name in agent_names if name in agent_dict]

        return matched_agents

    def adjust_plan_with_llm(self, initial_plan, user_feedback):
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
        - 'run' to execute the plan.
        - 'adjust' to adjust the plan.
        - 'exit' to end the workflow.

        Return only the action as a single word: 'run', 'adjust', or 'exit'.
        """
        return query_gradio_client(decision_prompt).strip().lower()

    def execute(self, code):
        #feedback_list = []
        code_list = []
        for agent in self.execution_plan:
            code = agent.run(code)
            code_list.append(f"{agent.name} Improved Code:\n{code}")
            #feedback = agent.run(code)
            #feedback_list.append(f"{agent.name} Feedback:\n{feedback}")
        return "\n\n".join(code_list)

    def run_workflow(self, code):
        initial_plan = self.create_plan_with_llm(code)
        print("Initial Plan:")
        print(initial_plan)
        last_feedback = ""
        while True:
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
                initial_plan = adjusted_plan
            elif next_action == "exit":
                print("Exiting the workflow. Goodbye!")
                break
            else:
                print("Unexpected response from the LLM. Ending the workflow.")
                break
