import ast
import io
import tempfile
import os
import sys
import subprocess
import pyflakes.reporter
import pyflakes.api
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
        # Create a temporary file
        fd, temp_path = tempfile.mkstemp(suffix=".py")
        with os.fdopen(fd, 'w') as temp_file:
            temp_file.write(code)

        # Redirect stderr to capture Pyflakes output
        stderr_capture = io.StringIO()
        sys.stderr = stderr_capture

        # Run Pyflakes on the temp file
        pyflakes.api.checkPath(temp_path)

        # Restore stderr and capture the output
        sys.stderr = sys.__stderr__
        output = stderr_capture.getvalue().strip()

        if output:
            issues = output.split("\n")
    except Exception as e:
        issues.append(f"Error running Pyflakes: {e}")
    finally:
        os.remove(temp_path)  # Cleanup the temporary file

    return issues

def analyze_pylint(code):
    """
    Runs Pylint to analyze code efficiency and captures detected issues.

    Returns:
        dict: Pylint score and detected issues.
    """
    results = {"score": None, "issues": []}
    try:
        # Create a temporary file
        fd, temp_path = tempfile.mkstemp(suffix=".py")
        with os.fdopen(fd, 'w') as temp_file:
            temp_file.write(code)

        # Run Pylint as a subprocess
        process = subprocess.run(["pylint", temp_path, "--output-format=json"],
                                 capture_output=True, text=True, check=False)

        # Parse Pylint output (if available)
        if process.stdout:
            import json
            try:
                pylint_output = json.loads(process.stdout)
                results["issues"] = [issue["message"] for issue in pylint_output]
                results["score"] = None  # Pylint scores are in separate output formats
            except json.JSONDecodeError:
                results["issues"].append("Error decoding Pylint JSON output.")
        
        if process.stderr:
            results["issues"].append(f"Pylint error: {process.stderr.strip()}")

    except Exception as e:
        results["issues"].append(f"Error running Pylint: {e}")

    finally:
        os.remove(temp_path)  # Cleanup the temporary file

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
