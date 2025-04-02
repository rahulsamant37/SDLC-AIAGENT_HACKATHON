"""
User story generator node for SDLC Agent.
"""
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from src.LLMS.groq_llm import get_llm

def create_user_story_prompt(requirements: str, requirements_analysis: str) -> str:
    """
    Create a prompt for user story generation.
    
    Args:
        requirements (str): The user requirements.
        requirements_analysis (str): The requirements analysis.
        
    Returns:
        str: The prompt for user story generation.
    """
    return f"""
    You are an expert software business analyst. Create comprehensive user stories 
    based on the following requirements and analysis.
    
    Requirements:
    {requirements}
    
    Requirements Analysis:
    {requirements_analysis}
    
    Generate a comprehensive set of user stories that cover all the requirements.
    For each user story, include:
    1. A title
    2. User role (who)
    3. Action (what)
    4. Benefit (why)
    5. Acceptance criteria
    6. Priority (high, medium, low)
    7. Effort estimate (story points: 1, 2, 3, 5, 8, 13)
    
    Group the user stories into these categories:
    - Core Stories (essential functionality)
    - Feature-Specific Stories (important but not core)
    - SDLC Process Stories (related to development process, testing, documentation)
    
    Format your response using Markdown with clear sections and tables where appropriate.
    """

def user_story_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate user stories and update state.
    
    Args:
        state (Dict[str, Any]): The current state.
        
    Returns:
        Dict[str, Any]: The updated state.
    """
    # Extract requirements and analysis from state
    requirements = state.get("requirements", "")
    requirements_analysis = state.get("requirements_analysis", "")
    
    if not requirements:
        return {
            "user_stories": "No requirements provided.",
            "current_stage": "REQUIREMENTS"  # Stay in requirements stage
        }
    
    # Create prompt for user story generation
    prompt = create_user_story_prompt(requirements, requirements_analysis)
    
    # Generate user stories
    user_stories = generate_with_langchain(prompt, temperature=0.7)
    
    # Extract metadata for user stories
    metadata_prompt = f"""
    Based on the following user stories, extract metadata as a JSON object.
    
    User Stories:
    {user_stories}
    
    Please provide a JSON object with the following structure:
    {{
        "total_story_count": <number>,
        "high_priority_count": <number>,
        "medium_priority_count": <number>,
        "low_priority_count": <number>,
        "total_story_points": <number>,
        "categories": {{
            "core": <number>,
            "feature": <number>,
            "process": <number>
        }},
        "primary_user_roles": ["role1", "role2", ...],
        "most_complex_stories": ["story1", "story2", "story3"]
    }}
    
    Provide only the JSON object, no other text.
    """
    
    # Get metadata
    metadata_str = generate_with_langchain(metadata_prompt, temperature=0.2)
    
    # Try to parse JSON, use default if parsing fails
    try:
        # Extract JSON if it's wrapped in markdown code blocks
        if "```json" in metadata_str:
            json_start = metadata_str.find("```json") + 7
            json_end = metadata_str.find("```", json_start)
            metadata_str = metadata_str[json_start:json_end].strip()
        elif "```" in metadata_str:
            json_start = metadata_str.find("```") + 3
            json_end = metadata_str.find("```", json_start)
            metadata_str = metadata_str[json_start:json_end].strip()
        
        user_story_metadata = json.loads(metadata_str)
    except (json.JSONDecodeError, ValueError):
        # Default values if parsing fails
        user_story_metadata = {
            "total_story_count": 10,
            "high_priority_count": 4,
            "medium_priority_count": 4,
            "low_priority_count": 2,
            "total_story_points": 40,
            "categories": {
                "core": 5,
                "feature": 3,
                "process": 2
            },
            "primary_user_roles": ["User", "Admin", "System"],
            "most_complex_stories": ["Authentication", "Data Processing", "Reporting"]
        }
    
    # Update state with user stories and metadata
    return {
        "user_stories": user_stories,
        "user_story_metadata": user_story_metadata,
        "current_stage": "DESIGN",
        "last_updated": datetime.now().isoformat()
    }

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