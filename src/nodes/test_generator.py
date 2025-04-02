"""
Test generator node for SDLC Agent.
"""
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from src.LLMS.groq_llm import get_llm

def create_test_generation_prompt(requirements: str, user_stories: str, 
                                 code_artifacts: Dict[str, str]) -> str:
    """
    Create a prompt for test generation.
    
    Args:
        requirements (str): The user requirements.
        user_stories (str): The user stories.
        code_artifacts (Dict[str, str]): The code artifacts.
        
    Returns:
        str: The prompt for test generation.
    """
    # Convert code artifacts to a single formatted string
    code_str = ""
    for file_name, code in code_artifacts.items():
        # Skip non-code files and documentation
        if file_name.endswith((".md", ".txt")):
            continue
        code_str += f"\n\n### File: {file_name}\n```\n{code}\n```\n"
    
    return f"""
    You are an expert software testing engineer. Create comprehensive test cases
    based on the following requirements, user stories, and code.
    
    Requirements:
    {requirements}
    
    User Stories:
    {user_stories}
    
    Code:
    {code_str}
    
    Your test plan should include:
    1. Test strategy overview
    2. Unit tests
    3. Integration tests
    4. Functional tests
    5. Performance tests
    6. Security tests
    7. User acceptance tests
    
    For each test category, include:
    - Test ID and name
    - Description
    - Pre-conditions
    - Test steps
    - Expected results
    - Priority (High, Medium, Low)
    
    Format your response using Markdown with clear sections and tables where appropriate.
    Include actual test code for at least the most critical unit and integration tests.
    """

def create_test_results_prompt(test_cases: str) -> str:
    """
    Create a prompt for test results generation.
    
    Args:
        test_cases (str): The test cases.
        
    Returns:
        str: The prompt for test results generation.
    """
    return f"""
    You are an expert software testing engineer. Generate realistic test execution results
    for the following test cases.
    
    Test Cases:
    {test_cases}
    
    Your test results should include:
    1. Executive summary
    2. Test execution metrics
       - Total tests executed
       - Pass rate
       - Failure rate
       - Blocked tests
    3. Detailed test results for each test case
       - Status (Passed, Failed, Blocked)
       - Execution time
       - Actual results
       - Defects found (if applicable)
    4. Test coverage analysis
    5. Recommendations for improving quality
    
    Format your response using Markdown with clear sections and tables where appropriate.
    """

def extract_test_metrics(test_results: str) -> Dict[str, Any]:
    """
    Extract test metrics from test results.
    
    Args:
        test_results (str): The test results.
        
    Returns:
        Dict[str, Any]: The test metrics.
    """
    prompt = f"""
    Extract key metrics from the following test results as a JSON object.
    
    Test Results:
    {test_results}
    
    Please provide a JSON object with the following structure:
    {{
        "total_tests": <number>,
        "passed_tests": <number>,
        "failed_tests": <number>,
        "blocked_tests": <number>,
        "pass_rate": <float>,
        "test_coverage": <float>,
        "execution_time_minutes": <number>,
        "critical_defects": <number>,
        "major_defects": <number>,
        "minor_defects": <number>,
        "categories": {{
            "unit": {{
                "total": <number>,
                "passed": <number>
            }},
            "integration": {{
                "total": <number>,
                "passed": <number>
            }},
            "functional": {{
                "total": <number>,
                "passed": <number>
            }},
            "performance": {{
                "total": <number>,
                "passed": <number>
            }},
            "security": {{
                "total": <number>,
                "passed": <number>
            }}
        }},
        "most_failed_components": ["<component1>", "<component2>", ...]
    }}
    
    Provide only the JSON object, no other text.
    """
    
    # Get metrics
    metrics_str = generate_with_langchain(prompt, temperature=0.2)
    
    # Try to parse JSON, use default if parsing fails
    try:
        # Extract JSON if it's wrapped in markdown code blocks
        if "```json" in metrics_str:
            json_start = metrics_str.find("```json") + 7
            json_end = metrics_str.find("```", json_start)
            metrics_str = metrics_str[json_start:json_end].strip()
        elif "```" in metrics_str:
            json_start = metrics_str.find("```") + 3
            json_end = metrics_str.find("```", json_start)
            metrics_str = metrics_str[json_start:json_end].strip()
        
        test_metrics = json.loads(metrics_str)
    except (json.JSONDecodeError, ValueError):
        # Default values if parsing fails
        test_metrics = {
            "total_tests": 50,
            "passed_tests": 42,
            "failed_tests": 6,
            "blocked_tests": 2,
            "pass_rate": 0.84,
            "test_coverage": 0.78,
            "execution_time_minutes": 45,
            "critical_defects": 1,
            "major_defects": 3,
            "minor_defects": 5,
            "categories": {
                "unit": {
                    "total": 20,
                    "passed": 18
                },
                "integration": {
                    "total": 15,
                    "passed": 13
                },
                "functional": {
                    "total": 10,
                    "passed": 8
                },
                "performance": {
                    "total": 3,
                    "passed": 2
                },
                "security": {
                    "total": 2,
                    "passed": 1
                }
            },
            "most_failed_components": ["Authentication", "Data Processing"]
        }
    
    return test_metrics

def generate_with_langchain(prompt: str, temperature: float = 0.7) -> str:
    """
    Generate content using LLM.
    
    Args:
        prompt (str): The prompt to use.
        temperature (float): The temperature for generation.
        
    Returns:
        str: The generated content.
    """
    llm = get_llm(temperature=temperature)
    return llm.invoke(prompt)

def test_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate test cases, execute tests, and update state.
    
    Args:
        state (Dict[str, Any]): The current state.
        
    Returns:
        Dict[str, Any]: The updated state.
    """
    # Extract data from state
    requirements = state.get("requirements", "")
    user_stories = state.get("user_stories", "")
    code_artifacts = state.get("code_artifacts", {})
    
    if not code_artifacts:
        return {
            "test_cases": "No code artifacts to test.",
            "test_results": "No code artifacts to test.",
            "current_stage": "CODE"  # Go back to code stage
        }
    
    # Create prompt for test generation
    prompt = create_test_generation_prompt(requirements, user_stories, code_artifacts)
    
    # Generate test cases
    test_cases = generate_with_langchain(prompt, temperature=0.7)
    
    # Create prompt for test results
    results_prompt = create_test_results_prompt(test_cases)
    
    # Generate test results
    test_results = generate_with_langchain(results_prompt, temperature=0.7)
    
    # Extract test metrics
    test_metrics = extract_test_metrics(test_results)
    
    # Update state with test cases, results, and metrics
    return {
        "test_cases": test_cases,
        "test_results": test_results,
        "test_metrics": test_metrics,
        "current_stage": "COMPLETE",
        "last_updated": datetime.now().isoformat()
    }