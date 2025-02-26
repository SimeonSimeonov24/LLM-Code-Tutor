from langchain.agents import Tool
import autopep8
import re
from gradio_llm import query_gradio_client

# Define Coding Style Analysis Tool
def style_analysis(code):
    """Analyze the code style and suggest improvements."""
    # AutoPEP8 for basic style fixes
    formatted_code = autopep8.fix_code(code)

    # Check for PEP8 violations using regex
    issues = []
    if re.search(r"\t", code):
        issues.append({"line": "N/A", "message": "Tabs detected, use spaces instead."})
    if re.search(r"[^#]\s{2,}", code):
        issues.append({"line": "N/A", "message": "Extra spaces detected."})
    if re.search(r"[^\n]\n{2,}", code):
        issues.append({"line": "N/A", "message": "Multiple consecutive blank lines detected."})
    if re.search(r"[^#] {4,}", code):
        issues.append({"line": "N/A", "message": "Excessive spaces detected."})
    if re.search(r";", code):
        issues.append({"line": "N/A", "message": "Unnecessary semicolon detected."})
    if re.search(r"[^\S\n]{2,}$", code, re.MULTILINE):
        issues.append({"line": "N/A", "message": "Trailing whitespace detected."})
    if re.search(r"\s+$", code, re.MULTILINE):
        issues.append({"line": "N/A", "message": "Trailing spaces at the end of a line detected."})
    if re.search(r"^\s*\n", code, re.MULTILINE):
        issues.append({"line": "N/A", "message": "Unnecessary leading blank lines detected."})

    # Hugging Face Model for advanced style analysis
    prompt = f"""
    Analyze the following Python code for style and best practices:
    {code}
    """
    model_feedback = query_gradio_client(prompt)

    return {"autopep8_fix": formatted_code, "issues": issues, "model_feedback": model_feedback}

code_style_tool = Tool(
    name="Coding Style Analysis Tool",
    func=style_analysis,
    description="Analyzes the code for PEP8 compliance, best practices, and formatting issues."
)
