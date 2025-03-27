import io
from bandit.core import config, manager, test_set
from langchain.agents import Tool

def analyze_code_security(code: str):
    """
    Scans the provided Python code for security vulnerabilities using Bandit's Python API.
    
    Checks:
    - Insecure imports (e.g., pickle, os.system, eval, exec)
    - Hardcoded secrets (passwords, API keys)
    - Input validation issues (risk of injection attacks)
    - Weak cryptographic functions
    - Usage of outdated or dangerous libraries

    Returns:
        list: Detected security issues.
    """
    results = []
    
    try:
        # Initialize Bandit configuration
        bandit_conf = config.BanditConfig()
        
        # Create Bandit Manager
        bandit_mgr = manager.BanditManager(bandit_conf, "json")
        
        # Load test set
        bandit_mgr.b_ts = test_set.BanditTestSet(config=bandit_conf)

        # Create a temporary file to hold the code
        temp_filename = "temp_code.py"
        with open(temp_filename, "w") as temp_file:
            temp_file.write(code)

        bandit_mgr.discover_files([temp_filename])

        # Run security tests
        bandit_mgr.run_tests()
        
        # Process Bandit results
        for issue in bandit_mgr.get_issue_list():
            results.append({
                "severity": issue.severity,
                "confidence": issue.confidence,
                "message": issue.text,
                "line_number": issue.lineno
            })
    
    except Exception as e:
        return [f"Error during security analysis: {str(e)}"]
    
    return results if results else ["No security issues detected."]

# Define as a LangChain Tool
security_analysis_tool = Tool(
    name="Security Analysis Tool",
    func=analyze_code_security,
    description="""
    Scans Python code for security vulnerabilities using Bandit's Python API.
    Checks:
    - Insecure imports (e.g., pickle, os.system, eval, exec)
    - Hardcoded secrets (passwords, API keys)
    - Input validation issues (risk of injection attacks)
    - Weak cryptographic functions
    - Usage of outdated or dangerous libraries
    """
)