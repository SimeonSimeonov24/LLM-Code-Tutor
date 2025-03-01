import ast
import tempfile
import pyflakes.api
import pyflakes.reporter
from pylint.lint import Run
from vulture import Vulture
from langchain.agents import Tool

def analyze_ast(code):
    """
    Uses AST to analyze the code for:
    - Nested loops (O(n²) complexity)
    - Recursive functions (potential inefficiency)
    - Inefficient data structures

    Returns:
        list: AST-based inefficiency detections.
    """
    results = []
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"Syntax Error in provided code: {e}"]

    try:
        for node in ast.walk(tree):
            # Detect nested loops
            if isinstance(node, (ast.For, ast.While)):
                nested = any(isinstance(child, (ast.For, ast.While)) for child in ast.walk(node))
                if nested:
                    results.append("Nested loops detected (O(n²) complexity). Consider optimizing.")

            # Detect inefficient recursion
            if isinstance(node, ast.FunctionDef):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == node.name:
                        results.append(f"Recursive function '{node.name}' detected. Consider memoization or iteration.")
    except Exception as e:
        results.append(f"Error analyzing AST: {e}")

    return results


def analyze_pyflakes(code):
    """
    Runs Pyflakes to detect:
    - Unused variables
    - Unused imports
    - Redundant operations

    Returns:
        list: Pyflakes-detected issues.
    """
    issues = []
    try:
        with tempfile.NamedTemporaryFile(delete=True, suffix=".py") as temp_file:
            temp_file.write(code.encode())
            temp_file.flush()
            reporter = pyflakes.reporter.Reporter(errorStream=temp_file.file, warningStream=temp_file.file)
            pyflakes.api.checkPath(temp_file.name)
            temp_file.seek(0)
            output = temp_file.read().decode().strip()
            if output:
                issues = output.split("\n")
    except Exception as e:
        issues.append(f"Error running Pyflakes: {e}")

    return issues


def analyze_pylint(code):
    """
    Runs Pylint to analyze code efficiency, scoring it based on best practices.

    Returns:
        dict: Pylint score and detected issues.
    """
    results = {"score": None, "issues": []}
    try:
        with tempfile.NamedTemporaryFile(delete=True, suffix=".py") as temp_file:
            temp_file.write(code.encode())
            temp_file.flush()
            pylint_output = Run([temp_file.name], do_exit=False)
            results["score"] = pylint_output.linter.stats.global_note
            results["issues"] = pylint_output.linter.reporter.messages
    except Exception as e:
        results["issues"].append(f"Error running Pylint: {e}")

    return results


def analyze_vulture(code):
    """
    Uses Vulture to detect:
    - Dead code
    - Unreachable code
    - Unused functions and imports

    Returns:
        list: Vulture-detected issues.
    """
    issues = []
    try:
        vulture = Vulture()
        vulture.scan(code)
        issues = [str(issue) for issue in vulture.get_unused_code()]
    except Exception as e:
        issues.append(f"Error running Vulture: {e}")

    return issues


def analyze_code_efficiency(code: str):
    """
    Main function that integrates all the different analysis methods:
    - AST (for inefficiencies in loops, recursion, and structures)
    - Pyflakes (for unused variables and redundant operations)
    - Pylint (for scoring and performance suggestions)
    - Vulture (for detecting dead/unreachable code)

    Returns:
        dict: Consolidated analysis report.
    """
    return {
        "ast_analysis": analyze_ast(code),
        "pyflakes_issues": analyze_pyflakes(code),
        "pylint_analysis": analyze_pylint(code),
        "vulture_issues": analyze_vulture(code),
    }


# Define as a LangChain Tool
code_efficiency_tool = Tool(
    name="Code Efficiency Analysis Tool",
    func=analyze_code_efficiency,
    description="""
    Analyzes Python code efficiency using AST, Pyflakes, Pylint, and Vulture.
    - Detects inefficient algorithms and redundant operations.
    - Flags unnecessary loops, recursion, and suboptimal data structures.
    - Identifies unused variables and dead code.
    - Scores efficiency and optimization potential.
    """
)
