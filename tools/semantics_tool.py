from langchain.agents import Tool
import ast

# Define Semantics Analysis Tool
def semantics_analysis(code):
    """Analyze the code for semantic issues."""
    try:
        # Parse the code to generate the Abstract Syntax Tree (AST)
        tree = ast.parse(code)
        return "No semantic issues found."  # If parsing is successful, there are no semantic issues
    except SyntaxError as e:
        # Return details about the syntax error
        return [{"line": e.lineno, "message": e.msg}]


semantics_tool = Tool(
    name="Semantics Analysis Tool",
    func=semantics_analysis,
    description="Analyzes the code for semantic issues and returns the AST if valid."
)