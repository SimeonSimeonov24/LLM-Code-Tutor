from langchain.agents import Tool
import ast

def error_handling_analysis(code):
    """Analyze the code for error handling practices."""
    try:
        # Parse the code into an AST (Abstract Syntax Tree)
        tree = ast.parse(code)
        issues = []

        # Analyze the AST for try/except blocks
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                if not node.handlers:
                    issues.append({"line": node.lineno, "message": "Try block without except handlers."})
                for handler in node.handlers:
                    if handler.type is None:
                        issues.append({"line": handler.lineno, "message": "Bare except detected. Avoid catching all exceptions."})
            elif isinstance(node, ast.Raise) and not node.exc:
                issues.append({"line": node.lineno, "message": "Raise statement without exception specified."})

        return "No error handling issues found." if not issues else issues
    except Exception as e:
        # Handle unexpected parsing errors
        return [{"line": 0, "message": f"Error during error handling analysis: {str(e)}"}]


error_handling_tool = Tool(
    name="Error Handling Analysis Tool",
    func=error_handling_analysis,
    description="Analyzes the code for error handling practices and issues."
)

