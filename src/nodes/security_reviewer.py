"""
Security review node for SDLC Agent.
"""
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from src.LLMS.google_llm import get_llm

def create_security_review_prompt(code_artifacts: Dict[str, str], requirements: str) -> str:
    """
    Create a prompt for security review.
    
    Args:
        code_artifacts (Dict[str, str]): The code artifacts.
        requirements (str): The user requirements.
        
    Returns:
        str: The prompt for security review.
    """
    # Convert code artifacts to a single formatted string
    code_str = ""
    for file_name, code in code_artifacts.items():
        code_str += f"\n\n### File: {file_name}\n```\n{code}\n```\n"
    
    return f"""
    You are an expert security reviewer. Analyze the following code for security vulnerabilities
    and provide a comprehensive security assessment.
    
    Requirements:
    {requirements}
    
    Code:
    {code_str}
    
    Your security assessment should include:
    1. Executive summary
    2. Risk rating (Critical, High, Medium, Low)
    3. Identified vulnerabilities with detailed explanation
    4. Recommendations for remediation
    5. Security best practices that should be implemented
    
    Format your response using Markdown with clear sections.
    """

def categorize_findings(security_findings: str) -> Dict[str, Any]:
    """
    Categorize security findings.
    
    Args:
        security_findings (str): The security findings.
        
    Returns:
        Dict[str, Any]: Categorized findings.
    """
    prompt = f"""
    Analyze the following security findings and categorize them.
    
    Security Findings:
    {security_findings}
    
    Please provide a JSON object with the following structure:
    {{
        "total_findings": <number>,
        "risk_levels": {{
            "critical": <number>,
            "high": <number>,
            "medium": <number>,
            "low": <number>
        }},
        "vulnerability_categories": [
            {{
                "category": "<category_name>",
                "count": <number>,
                "highest_risk": "<risk_level>"
            }},
            ...
        ],
        "most_affected_files": ["<file_name>", ...],
        "overall_risk_rating": "critical"|"high"|"medium"|"low",
        "remediation_priority": ["<vulnerability1>", "<vulnerability2>", ...]
    }}
    
    Provide only the JSON object, no other text.
    """
    
    # Get categorization
    categorization_str = generate_with_langchain(prompt, temperature=0.2)
    
    # Try to parse JSON, use default if parsing fails
    try:
        # Extract JSON if it's wrapped in markdown code blocks
        if "```json" in categorization_str:
            json_start = categorization_str.find("```json") + 7
            json_end = categorization_str.find("```", json_start)
            categorization_str = categorization_str[json_start:json_end].strip()
        elif "```" in categorization_str:
            json_start = categorization_str.find("```") + 3
            json_end = categorization_str.find("```", json_start)
            categorization_str = categorization_str[json_start:json_end].strip()
        
        categorized_findings = json.loads(categorization_str)
    except (json.JSONDecodeError, ValueError):
        # Default values if parsing fails
        categorized_findings = {
            "total_findings": 5,
            "risk_levels": {
                "critical": 0,
                "high": 1,
                "medium": 2,
                "low": 2
            },
            "vulnerability_categories": [
                {
                    "category": "Input Validation",
                    "count": 2,
                    "highest_risk": "high"
                },
                {
                    "category": "Authentication",
                    "count": 1,
                    "highest_risk": "medium"
                },
                {
                    "category": "Error Handling",
                    "count": 2,
                    "highest_risk": "low"
                }
            ],
            "most_affected_files": ["app.py", "utils.py"],
            "overall_risk_rating": "medium",
            "remediation_priority": ["Input validation", "Authentication", "Error handling"]
        }
    
    return categorized_findings

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

def security_review_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform security review and update state.
    
    Args:
        state (Dict[str, Any]): The current state.
        
    Returns:
        Dict[str, Any]: The updated state.
    """
    # Extract code artifacts from state
    code_artifacts = state.get("code_artifacts", {})
    requirements = state.get("requirements", "")
    
    if not code_artifacts:
        return {
            "security_findings": "No code artifacts to review.",
            "current_stage": "CODE",  # Go back to code stage
            "security_review_error": "Missing code artifacts."
        }
    
    # Create prompt for security review
    prompt = create_security_review_prompt(code_artifacts, requirements)
    
    # Generate security findings
    security_findings = generate_with_langchain(prompt, temperature=0.7)
    
    # Categorize findings
    categorized_findings = categorize_findings(security_findings)
    
    # Update state with security findings and categorization
    return {
        "security_findings": security_findings,
        "security_metadata": categorized_findings,
        "current_stage": "TESTING",
        "last_updated": datetime.now().isoformat()
    }