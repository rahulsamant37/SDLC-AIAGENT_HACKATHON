"""
Requirement analysis node for SDLC Agent.
"""
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from src.LLMS.groq_llm import get_llm

def create_requirement_analysis_prompt(requirements: str) -> str:
    """
    Create a prompt for requirement analysis.
    
    Args:
        requirements (str): The user requirements.
        
    Returns:
        str: The prompt for requirement analysis.
    """
    return f"""
    You are an expert software requirements analyst. Analyze the following requirements
    and provide a structured analysis with categories, priorities, and stakeholders.
    
    Requirements:
    {requirements}
    
    Your analysis should include:
    1. A summary of the core requirements
    2. Categorized requirements (functional, non-functional, etc.)
    3. Priority assignments (high, medium, low)
    4. Identified stakeholders
    5. Potential risks or challenges
    6. Suggested clarification questions
    
    Format your response using Markdown with clear sections.
    """

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

def requirement_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze requirements and update state.
    
    Args:
        state (Dict[str, Any]): The current state.
        
    Returns:
        Dict[str, Any]: The updated state.
    """
    # Extract requirements from state
    requirements = state.get("requirements", "")
    if not requirements:
        return {
            "requirements_analysis": "No requirements provided.",
            "current_stage": "REQUIREMENTS"
        }
    
    # Create prompt for requirement analysis
    prompt = create_requirement_analysis_prompt(requirements)
    
    # Generate analysis
    analysis = generate_with_langchain(prompt, temperature=0.5)
    
    # Extract important elements from analysis for complexity assessment
    complexity_prompt = f"""
    Based on the following requirements and analysis, assess the project complexity.
    
    Requirements:
    {requirements}
    
    Analysis:
    {analysis}
    
    Please provide a JSON object with the following attributes:
    {{
        "complexity": "low"|"medium"|"high",
        "security_critical": true|false,
        "performance_critical": true|false,
        "data_intensive": true|false,
        "user_interface_focused": true|false,
        "integration_heavy": true|false,
        "estimated_effort_days": <number>,
        "primary_technical_challenges": ["challenge1", "challenge2", ...],
        "recommended_team_size": <number>,
        "recommended_technology_stack": ["tech1", "tech2", ...]
    }}
    
    Provide only the JSON object, no other text.
    """
    
    # Get complexity assessment
    complexity_assessment_str = generate_with_langchain(complexity_prompt, temperature=0.2)
    
    # Try to parse JSON, use default if parsing fails
    try:
        # Extract JSON if it's wrapped in markdown code blocks
        if "```json" in complexity_assessment_str:
            json_start = complexity_assessment_str.find("```json") + 7
            json_end = complexity_assessment_str.find("```", json_start)
            complexity_assessment_str = complexity_assessment_str[json_start:json_end].strip()
        elif "```" in complexity_assessment_str:
            json_start = complexity_assessment_str.find("```") + 3
            json_end = complexity_assessment_str.find("```", json_start)
            complexity_assessment_str = complexity_assessment_str[json_start:json_end].strip()
        
        complexity_assessment = json.loads(complexity_assessment_str)
    except (json.JSONDecodeError, ValueError):
        # Default values if parsing fails
        complexity_assessment = {
            "complexity": "medium",
            "security_critical": True,
            "performance_critical": False,
            "data_intensive": False,
            "user_interface_focused": True,
            "integration_heavy": False,
            "estimated_effort_days": 30,
            "primary_technical_challenges": ["Requirement clarity", "Technical feasibility"],
            "recommended_team_size": 3,
            "recommended_technology_stack": ["Python", "JavaScript", "SQL"]
        }
    
    # Update state with analysis
    return {
        "requirements_analysis": analysis,
        "complexity_analysis": complexity_assessment,
        "current_stage": "USER_STORIES",
        "last_updated": datetime.now().isoformat()
    }