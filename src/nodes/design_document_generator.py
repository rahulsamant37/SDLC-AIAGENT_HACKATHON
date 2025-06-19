"""
Design document generator node for SDLC Agent.
"""
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from src.LLMS.google_llm import get_llm

def create_design_document_prompt(requirements: str, user_stories: str, is_functional: bool = True) -> str:
    """
    Create a prompt for design document generation.
    
    Args:
        requirements (str): The user requirements.
        user_stories (str): The user stories.
        is_functional (bool): Whether to generate functional or non-functional design.
        
    Returns:
        str: The prompt for design document generation.
    """
    if is_functional:
        return f"""
        You are an expert software architect. Create a comprehensive functional design document
        based on the following requirements and user stories.
        
        Requirements:
        {requirements}
        
        User Stories:
        {user_stories}
        
        Your functional design document should include:
        1. Introduction and purpose
        2. System overview and architecture
        3. Data models and database schema
        4. API specifications
        5. User interface design
        6. Process flows
        7. Integration points
        8. Sequence diagrams (describe them textually)
        9. Error handling
        
        For each diagram or visual element, provide a detailed textual description.
        Format your response using Markdown with clear sections and code snippets where appropriate.
        Include placeholders for diagrams that would be helpful.
        """
    else:
        return f"""
        You are an expert software architect. Create a comprehensive non-functional design document
        based on the following requirements and user stories.
        
        Requirements:
        {requirements}
        
        User Stories:
        {user_stories}
        
        Your non-functional design document should include:
        1. Performance requirements
        2. Scalability considerations
        3. Security requirements and approaches
        4. Reliability and fault tolerance
        5. Maintainability
        6. Deployment strategy
        7. Monitoring and observability
        8. Configuration management
        9. Documentation requirements
        
        Format your response using Markdown with clear sections and code snippets where appropriate.
        """

def design_document_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate design documents and update state.
    
    Args:
        state (Dict[str, Any]): The current state.
        
    Returns:
        Dict[str, Any]: The updated state.
    """
    # Extract requirements and user stories from state
    requirements = state.get("requirements", "")
    user_stories = state.get("user_stories", "")
    
    if not requirements or not user_stories:
        return {
            "functional_design": "Missing requirements or user stories.",
            "non_functional_design": "Missing requirements or user stories.",
            "current_stage": "USER_STORIES" if not user_stories else "REQUIREMENTS"
        }
    
    # Create prompts for design document generation
    functional_prompt = create_design_document_prompt(requirements, user_stories, is_functional=True)
    non_functional_prompt = create_design_document_prompt(requirements, user_stories, is_functional=False)
    
    # Generate design documents
    functional_design = generate_with_langchain(functional_prompt, temperature=0.7)
    non_functional_design = generate_with_langchain(non_functional_prompt, temperature=0.7)
    
    # Generate design metadata
    metadata_prompt = f"""
    Analyze the following functional and non-functional design documents and extract key metadata.
    
    Functional Design:
    {functional_design}
    
    Non-Functional Design:
    {non_functional_design}
    
    Please provide a JSON object with the following structure:
    {{
        "architecture_type": "<architecture_pattern>",
        "key_components": ["component1", "component2", ...],
        "external_dependencies": ["dependency1", "dependency2", ...],
        "database_type": "<database_type>",
        "api_count": <number>,
        "ui_screens": <number>,
        "security_measures": ["measure1", "measure2", ...],
        "scalability_approaches": ["approach1", "approach2", ...],
        "estimated_implementation_complexity": "low"|"medium"|"high",
        "recommended_team_structure": ["role1", "role2", ...]
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
        
        design_metadata = json.loads(metadata_str)
    except (json.JSONDecodeError, ValueError):
        # Default values if parsing fails
        design_metadata = {
            "architecture_type": "Microservices",
            "key_components": ["API Gateway", "User Service", "Data Service"],
            "external_dependencies": ["Database", "Authentication Service"],
            "database_type": "Relational",
            "api_count": 15,
            "ui_screens": 8,
            "security_measures": ["Authentication", "Authorization", "Input Validation"],
            "scalability_approaches": ["Horizontal Scaling", "Caching", "Load Balancing"],
            "estimated_implementation_complexity": "medium",
            "recommended_team_structure": ["Backend Developer", "Frontend Developer", "QA Engineer", "DevOps"]
        }
    
    # Update state with design documents and metadata
    return {
        "functional_design": functional_design,
        "non_functional_design": non_functional_design,
        "design_metadata": design_metadata,
        "current_stage": "CODE",
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