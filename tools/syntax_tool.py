from langchain.agents import Tool

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
