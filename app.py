import streamlit as st
from agents.orchestrator_agent import OrchestratorAgent
from agents.syntax_agent import SyntaxAgent
from agents.semantics_agent import SemanticsAgent
from agents.code_style_agent import CodeStyleAgent
from agents.code_structure_agent import CodeStructureAgent
from agents.security_analysis_agent import SecurityAnalysisAgent
from agents.code_efficiency_agent import CodeEfficiencyAgent
from agents.documentation_agent import DocumentationAgent
from agents.error_handling_agent import ErrorHandlingAgent
from agents.best_practices_agent import BestPracticesAgent
from tools.syntax_tool import syntax_tool
from tools.semantics_tool import semantics_tool
from tools.code_style_tool import code_style_tool
from tools.code_structure_tool import code_structure_tool
from tools.security_analysis_tool import security_analysis_tool
from tools.code_efficiency_tool import code_efficiency_tool
from tools.documentation_tool import documentation_tool
from tools.error_handling_tool import error_handling_tool
from tools.best_practices_tool import best_practices_tool

# Initialize Agents
syntax_agent = SyntaxAgent(syntax_tool)
semantics_agent = SemanticsAgent(semantics_tool)
code_style_agent = CodeStyleAgent(code_style_tool)
documentation_agent = DocumentationAgent(documentation_tool)
code_structure_agent = CodeStructureAgent(code_structure_tool)
security_analysis_agent = SecurityAnalysisAgent(security_analysis_tool)
code_efficiency_agent = CodeEfficiencyAgent(code_efficiency_tool)
error_handling_agent = ErrorHandlingAgent(error_handling_tool)
best_practices_agent = BestPracticesAgent(best_practices_tool)
orchestrator = OrchestratorAgent(agents=[syntax_agent, semantics_agent, code_style_agent, code_structure_agent, security_analysis_agent, code_efficiency_agent, documentation_agent, error_handling_agent, best_practices_agent])

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
    st.session_state["last_checked_agent_index"] = 0
if "execution_plan" not in st.session_state:
    st.session_state["execution_plan"] = []
if "code_needs_fixing" not in st.session_state:
    st.session_state["code_needs_fixing"] = False
if "waiting_for_next" not in st.session_state:
    st.session_state["waiting_for_next"] = False

# User input for the code snippet
code_snippet = st.text_area("✍️ Enter your code for analysis:", st.session_state["code"], height=300)

if st.button("🛠️ Generate Execution Plan"):
    if not code_snippet.strip():
        st.warning("Please enter some code before analyzing.")
    else:
        st.session_state["code"] = code_snippet
        plan = orchestrator.create_plan_with_llm(code_snippet)
        st.session_state["plan"] = plan
        st.session_state["execution_plan"] = orchestrator.parse_plan(plan)
        st.session_state["last_checked_agent_index"] = 0
        st.session_state["code_needs_fixing"] = False
        st.session_state["waiting_for_next"] = False
        st.session_state["chat_history"] = []
        st.success("Execution plan created! You can adjust it before running analysis.")

# Show execution plan and allow user adjustments
if st.session_state["plan"]:
    st.subheader("📋 Execution Plan")
    st.markdown(st.session_state["plan"])
    user_feedback = st.text_area("✏️ You can provide adjustments to the plan here: ")
    if st.button("✅ Update Plan"):
        adjusted_plan = orchestrator.adjust_plan_with_llm(st.session_state["plan"], user_feedback)
        if adjusted_plan.strip():
            st.session_state["plan"] = adjusted_plan
            st.session_state["execution_plan"] = orchestrator.parse_plan(adjusted_plan)
            st.session_state["last_checked_agent_index"] = 0
            st.success("Execution plan updated! The new plan is shown above.")
            st.rerun()

# Run analysis
if st.session_state["plan"] and st.button("🚀 Run Analysis"):
    st.session_state["running_analysis"] = True
    st.session_state["code_needs_fixing"] = False
    st.session_state["last_checked_agent_index"] = 0
    st.session_state["waiting_for_next"] = False
    st.markdown(f"## 🚀 Running Analysis: {st.session_state['execution_plan'][st.session_state['last_checked_agent_index']].name}")
    st.rerun()

# Analysis Loop
if st.session_state["running_analysis"] and not st.session_state["waiting_for_next"]:
    if not st.session_state["execution_plan"]:
        st.error("Execution plan is empty! Please generate or adjust the plan.")
        st.session_state["running_analysis"] = False

    # Get the current agent
    agent_index = st.session_state["last_checked_agent_index"]

    if agent_index < len(st.session_state["execution_plan"]):
        agent = st.session_state["execution_plan"][agent_index]

        # Show running agent
        st.session_state["chat_history"].append(f"## 🚀 Running Analysis: {agent.name}")

        # Run the agent and get the report
        report, is_valid = agent.run(st.session_state["code"])

        # Display the agent's report
        st.session_state["chat_history"].append(report)

        if not is_valid:
            # If issues are found, stop and ask the user to correct them
            st.session_state["chat_history"].append("⚠️ **Issues detected! Please correct the code below and submit it.**")
            st.session_state["code_needs_fixing"] = True
            st.session_state["running_analysis"] = False

        else:
            # If code passes, confirm success
            st.session_state["chat_history"].append(f"✅ **{agent.name} has finished. No issues detected.**")
            st.session_state["last_checked_agent_index"] += 1

            # Check if another agent exists
            if st.session_state["last_checked_agent_index"] < len(st.session_state["execution_plan"]):
                next_agent = st.session_state["execution_plan"][st.session_state["last_checked_agent_index"]]
                st.session_state["chat_history"].append(f"### ⏭️ Next Agent: {next_agent.name}")

                # Pause and wait for user confirmation
                st.session_state["waiting_for_next"] = True
                st.rerun()

# Display chat history
for message in st.session_state["chat_history"]:
    st.markdown(message)

# Show "Run Next Agent" button when waiting for next agent
if st.session_state["waiting_for_next"]:
    next_agent = st.session_state["execution_plan"][st.session_state["last_checked_agent_index"]]
    if st.button(f"▶️ Run {next_agent.name} Analysis"):
        st.markdown(f"## 🚀 Running Analysis: {st.session_state['execution_plan'][st.session_state['last_checked_agent_index']].name}")
        st.session_state["waiting_for_next"] = False
        st.rerun()

# If the last agent detected issues, allow user to fix code
if st.session_state["code_needs_fixing"]:
    corrected_code = st.text_area("🛠️ Edit and Improve Your Code:", st.session_state["code"], height=300)
    if st.button("🔄 Submit Revised Code"):
        st.markdown(f"## 🚀 Running Analysis: {st.session_state['execution_plan'][st.session_state['last_checked_agent_index']].name}")
        st.session_state["code"] = corrected_code
        st.session_state["running_analysis"] = True
        st.session_state["code_needs_fixing"] = False
        st.session_state["waiting_for_next"] = False
        st.rerun()
