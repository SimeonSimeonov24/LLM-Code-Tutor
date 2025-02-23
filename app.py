import streamlit as st
from agents.orchestrator_agent import OrchestratorAgent
from agents.syntax_agent import SyntaxAgent
from agents.semantics_agent import SemanticsAgent
from tools.syntax_tool import syntax_tool
from tools.semantics_tool import semantics_tool

# Initialize Agents
syntax_agent = SyntaxAgent(syntax_tool)
semantics_agent = SemanticsAgent(semantics_tool)
orchestrator = OrchestratorAgent(agents=[syntax_agent, semantics_agent])

st.title("💬 LLM Code Tutor Chatbot")
st.markdown("Analyze and improve your code with AI-driven syntax and semantic checks.")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "code" not in st.session_state:
    st.session_state["code"] = ""
if "plan" not in st.session_state:
    st.session_state["plan"] = ""
if "running_analysis" not in st.session_state:
    st.session_state["running_analysis"] = False
if "last_checked_agent_index" not in st.session_state:
    st.session_state["last_checked_agent_index"] = 0  # Track last agent
if "execution_plan" not in st.session_state:
    st.session_state["execution_plan"] = []  # Track agents in execution order
if "code_needs_fixing" not in st.session_state:
    st.session_state["code_needs_fixing"] = False  # Tracks if the user needs to correct the code
if "refresh" not in st.session_state:
    st.session_state["refresh"] = False

# User input for the code snippet
code_snippet = st.text_area("✍️ Enter your code for analysis:", st.session_state["code"], height=300)

if st.button("🛠️ Generate Execution Plan"):
    if not code_snippet.strip():
        st.warning("Please enter some code before analyzing.")
    else:
        st.session_state["code"] = code_snippet
        plan = orchestrator.create_plan_with_llm(code_snippet)
        st.session_state["plan"] = plan  # Store execution plan
        st.session_state["execution_plan"] = orchestrator.parse_plan(plan)  # Get agent order
        st.session_state["last_checked_agent_index"] = 0  # Reset agent index
        st.session_state["code_needs_fixing"] = False  # Reset fix status
        st.success("Execution plan created! You can adjust it before running analysis.")

# Show execution plan and allow user adjustments
if st.session_state["plan"]:
    st.subheader("📋 Execution Plan")
    st.text(st.session_state["plan"])  # Always show the latest plan
    user_feedback = st.text_area("✏️ You can provide adjustments to the plan here: ")
    if st.button("✅ Update Plan"):
        adjusted_plan = orchestrator.adjust_plan_with_llm(st.session_state["plan"], user_feedback)
        if adjusted_plan.strip():
            st.session_state["plan"] = adjusted_plan  # Store updated plan
            st.session_state["execution_plan"] = orchestrator.parse_plan(adjusted_plan)  # Get new agent order
            st.session_state["last_checked_agent_index"] = 0  # Restart from beginning
            st.session_state["refresh"] = True
            if st.session_state["refresh"]:
                st.rerun()
                st.session_state["refresh"] = False
            st.success("Execution plan updated! The new plan is shown above.")

# Run analysis (continues from the last agent)
if st.session_state["plan"] and st.button("🚀 Run Analysis"):
    st.session_state["running_analysis"] = True
    st.session_state["code_needs_fixing"] = False  # Reset before running analysis
    if st.session_state["last_checked_agent_index"] == 0:
        st.session_state["chat_history"] = []  # Clear history only on first run

# Chatbot-like analysis loop
if st.session_state["running_analysis"]:
    if not st.session_state["execution_plan"]:
        st.error("Execution plan is empty! Please generate or adjust the plan.")
        st.session_state["running_analysis"] = False

    for i in range(st.session_state["last_checked_agent_index"], len(st.session_state["execution_plan"])):
        agent = st.session_state["execution_plan"][i]
        report, is_valid = agent.run(st.session_state["code"])
        st.session_state["chat_history"].append(f"**{agent.name} Report:**\n{report}")

        # If issues are detected, stop and ask for user input
        if not is_valid:
            st.session_state["chat_history"].append("⚠️ Issues detected! Please correct the code below and submit it.")
            st.session_state["last_checked_agent_index"] = i  # Save progress at current agent
            st.session_state["code_needs_fixing"] = True  # Mark that user needs to fix code
            break  # Stop and wait for user input

    # If all agents validate the code, analysis is complete
    else:
        st.session_state["chat_history"].append("🎉 All checks passed! Your code is valid!")
        st.session_state["last_checked_agent_index"] = 0  # Reset for next run

    st.session_state["running_analysis"] = False  # Stop execution after reports

# Display chatbot conversation
for message in st.session_state["chat_history"]:
    st.markdown(message)

# User input for corrected code if the last agent found issues
if st.session_state["code_needs_fixing"]:
    corrected_code = st.text_area("🛠️ Edit and Improve Your Code:", st.session_state["code"], height=300)
    if st.button("🔄 Submit Revised Code"):
        st.session_state["code"] = corrected_code
        st.session_state["running_analysis"] = True  # Restart analysis
        st.session_state["code_needs_fixing"] = False  # Reset fix status
        st.session_state["chat_history"].append("✅ Code updated! Resuming analysis...")
        st.rerun()  # Refresh UI immediately
