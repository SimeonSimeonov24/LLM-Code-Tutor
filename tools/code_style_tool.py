from langchain.agents import Tool
import black
import difflib

# Define Coding Style Analysis Tool using Black
def style_analysis(code):
    """Analyze the code style using Black."""
    try:
        # Use Black to format the code
        formatted_code = black.format_str(code, mode=black.Mode())
    except black.NothingChanged:
        formatted_code = code  # If no changes are made, return the original code
    except Exception as e:
        return {"error": f"Error analyzing code style: {str(e)}"}

    # Compare the original code with the formatted code to identify issues
    try:
        diff = difflib.unified_diff(code.splitlines(), formatted_code.splitlines())
        issues = []

        # Identify lines that need changes
        for line in diff:
            if line.startswith('- ') or line.startswith('+ '):
                issues.append({"line": line.strip(), "message": "Code needs formatting."})
    except Exception as e:
        return {"error": f"Error comparing code formatting: {str(e)}"}
    
    return {"black_analysis": formatted_code, "issues": issues}

# Create the Tool using Black formatting for analysis
code_style_tool = Tool(
    name="Coding Style Analysis Tool using Black",
    func=style_analysis,
    description="""Analyzes the code for formatting issues using Black.
    Compares the original code with the formatted code and identifies what needs to be changed."""
)