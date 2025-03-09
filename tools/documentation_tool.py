from langchain.agents import Tool
import ast

def documentation_analysis(code):
    """Analyze the code for missing or poor documentation (docstrings & comments)."""
    try:
        tree = ast.parse(code)
        issues = []

        # Check for missing or poor function/class docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    issues.append({
                        "line": node.lineno,
                        "message": f"Missing docstring in {'function' if isinstance(node, ast.FunctionDef) else 'class'} '{node.name}'."
                    })

        # Check for inline comments (basic check: at least one should exist)
        if "#" not in code:
            issues.append({"line": 0, "message": "No inline comments found in the code."})

        return "No documentation issues found." if not issues else issues
    except Exception as e:
        return [{"line": 0, "message": f"Error during analysis: {str(e)}"}]

documentation_tool = Tool(
    name="Documentation Analysis Tool",
    func=documentation_analysis,
    description="Analyzes the code for missing docstrings, poor comments, and documentation quality."
)
