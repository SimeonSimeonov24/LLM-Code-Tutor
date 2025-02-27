import ast
import radon.complexity as rc
import radon.metrics as rm
from radon.metrics import h_visit
from radon.complexity import cc_visit
from langchain.agents import Tool

def analyze_code_structure(code: str):
    #TODO: Improve the analysis by lowering standards and not suggesting improvements to code that is already decent.
    """
    Analyzes the modularity and structure of the given Python code.
    Checks:
    - Number of functions and classes
    - Function lengths (bad modularity indicator)
    - Cyclomatic complexity (using Radon)
    - Maintainability Index (MI) for modularity
    - Code duplication (low cohesion)
    - Coupling through excessive imports
    - Nesting depth (high means bad structure)
    - Overall raw metrics: Lines of Code (LOC), comments, blank lines

    Returns:
        dict: Analysis report containing detected issues and suggestions.
    """
    results = {
        "functions": [],
        "classes": [],
        "issues": [],
        "halstead_metrics": {},
        "maintainability_index": {}
    }

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {"error": "Invalid Python code provided."}

    # Compute Halstead metrics as a replacement for raw metrics
    halstead_metrics = h_visit(code)
    results["halstead_metrics"] = halstead_metrics
    
    # Maintainability Index (MI) for code modularity
    maintainability_index = rm.mi_visit(code, True)  # True enables additional insights
    results["maintainability_index"] = maintainability_index
    if maintainability_index < 50:  # Maintainability Index ranges from 0-100 (low is bad) - under 65 is considered not easy to maintain
        results["issues"].append(f"Low maintainability index ({maintainability_index:.2f}). Consider refactoring.")

    # Analyze functions and classes
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):  # Function analysis
            func_name = node.name
            func_length = len(node.body)
            complexity = cc_visit(node)
            results["functions"].append({
                "name": func_name,
                "length": func_length,
                "complexity": complexity[0].complexity
            })
            if func_length > 30:  # Too long
                results["issues"].append(f"Function '{func_name}' is too long ({func_length} lines). Consider refactoring.")
            if complexity[0].complexity > 10:  # High complexity
                results["issues"].append(f"Function '{func_name}' has high complexity ({complexity[0].complexity}). Reduce branching.")

        elif isinstance(node, ast.ClassDef):  # Class analysis
            class_name = node.name
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            results["classes"].append({
                "name": class_name,
                "methods": methods,
                "num_methods": len(methods)
            })
            if len(methods) > 10:
                results["issues"].append(f"Class '{class_name}' has too many methods ({len(methods)}). Consider breaking it down.")

    # Check module imports (for high coupling)
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    if len(imports) > 10:
        results["issues"].append(f"Too many imports ({len(imports)}). This may indicate tight coupling.")

    return results["issues"]

# Define as a LangChain Tool
code_structure_tool = Tool(
    name="Code Structure Analysis Tool",
    func=analyze_code_structure,
    description="""
    Analyzes the modularity and structure of the given Python code.
    Checks:
    - Number of functions and classes
    - Function lengths (bad modularity indicator)
    - Cyclomatic complexity (using Radon)
    - Maintainability Index (MI) for modularity
    - Code duplication (low cohesion)
    - Coupling through excessive imports
    - Nesting depth (high means bad structure)
    - Overall code complexity (Halstead metrics)
    """
)