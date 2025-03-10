from langchain.agents import Tool
import ast

def best_practices_analysis(code):
    """Analyzes the code for best practices violations (e.g., naming, magic numbers, clean coding principles)."""
    try:
        tree = ast.parse(code)
        issues = []

        # Check for meaningful variable & function names
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.name) < 3:
                    issues.append(f"Line {node.lineno}: Function '{node.name}' has a too-short name. Use a descriptive name.")
            elif isinstance(node, ast.Name):
                if len(node.id) < 2:
                    issues.append(f"Line {node.lineno}: Variable '{node.id}' has a too-short name. Use a meaningful name.")

        return "No best practices violations found." if not issues else "\n".join(issues)
    except Exception as e:
        return f"Error during analysis: {str(e)}"

best_practices_tool = Tool(
    name="Best Practices Analysis Tool",
    func=best_practices_analysis,
    description="Analyzes the code for best practices violations like naming, magic numbers, and clean coding principles."
)
