"""
Dynamic workflow construction for SDLC Agent.
"""
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END

from src.state.sdlc_state import SDLCState
from src.nodes.requirement_analyzer import requirement_analysis_node
from src.nodes.user_story_generator import user_story_generator_node
from src.nodes.design_document_generator import design_document_generator_node
from src.nodes.code_generator import code_generator_node
from src.nodes.security_reviewer import security_review_node
from src.nodes.test_generator import test_generator_node
from src.nodes.multimodal_processor import process_design_with_image
from langchain_groq import ChatGroq
from src.LLMS.groq_llm import get_llm

def analyze_project_complexity(requirements: str) -> Dict[str, Any]:
    """
    Analyze requirements to determine project complexity and needs.
    
    Args:
        requirements (str): Project requirements
        
    Returns:
        Dict[str, Any]: Analysis results including complexity level, security needs, etc.
    """
    # Create a prompt for complexity analysis
    prompt = f"""
    You are an expert software project analyst. Analyze the following requirements 
    and determine the project complexity and special needs.
    
    Requirements:
    {requirements}
    
    Please provide an analysis with these specific attributes:
    1. complexity: "low", "medium", or "high"
    2. security_critical: true/false (does this project have specific security requirements?)
    3. performance_critical: true/false (does this project have specific performance requirements?)
    4. data_intensive: true/false (does this project involve handling large amounts of data?)
    5. user_interface_focused: true/false (is this primarily a UI/UX project?)
    6. integration_heavy: true/false (does this project require many external integrations?)
    
    Format your response as a valid JSON object with these attributes.
    """
    
    # Use LLM to analyze requirements
    llm = get_llm(temperature=0.1)  # Low temperature for more consistent results
    response = llm.invoke(prompt)
    
    # In a real implementation, parse the JSON response
    # For now, use default values
    default_analysis = {
        "complexity": "medium",
        "security_critical": True,
        "performance_critical": False,
        "data_intensive": False,
        "user_interface_focused": True,
        "integration_heavy": False
    }
    
    # TODO: Parse LLM response to extract the actual JSON
    # For now, return the default analysis
    return default_analysis

def build_sdlc_graph(requirements: str):
    """
    Dynamically build SDLC graph based on requirements analysis.
    
    Args:
        requirements (str): Project requirements
        
    Returns:
        Callable: Compiled LangGraph workflow
    """
    # Analyze requirements to determine needed nodes
    analysis = analyze_project_complexity(requirements)
    
    # Initialize state graph
    graph = StateGraph(SDLCState)
    
    # Add core nodes that every project needs
    graph.add_node("requirements", requirement_analysis_node)
    graph.add_node("user_stories", user_story_generator_node)
    graph.add_node("design", design_document_generator_node)
    graph.add_node("code", code_generator_node)
    graph.add_node("test", test_generator_node)
    
    # Always add these core edges
    graph.add_edge("requirements", "user_stories")
    graph.add_edge("user_stories", "design")
    
    # Add conditional nodes based on project complexity
    if analysis.get("complexity") == "high":
        # Add architectural review node for complex projects
        graph.add_node("architecture_review", process_design_with_image)
        # Modify the edges to include architectural review
        graph.add_edge("design", "architecture_review")
        graph.add_edge("architecture_review", "code")
    else:
        # Standard path
        graph.add_edge("design", "code")
    
    # Add security nodes if project is security critical
    if analysis.get("security_critical"):
        graph.add_node("security", security_review_node)
        
        # Add security review after code generation
        graph.add_edge("code", "security")
        graph.add_edge("security", "test")
    else:
        # Skip security review for non-security-critical projects
        graph.add_edge("code", "test")
    
    # Final edge to end
    graph.add_edge("test", END)
    
    # Compile graph
    return graph.compile()

def get_dynamic_graph_description(requirements: str) -> str:
    """
    Get a textual description of the dynamically built graph.
    
    Args:
        requirements (str): Project requirements
        
    Returns:
        str: Description of the graph structure
    """
    analysis = analyze_project_complexity(requirements)
    
    description = "SDLC Workflow:\n"
    description += "1. Requirements Analysis\n"
    description += "2. User Story Generation\n"
    description += "3. Design Document Creation\n"
    
    if analysis.get("complexity") == "high":
        description += "4. Architectural Review (added for high complexity)\n"
        description += "5. Code Generation\n"
    else:
        description += "4. Code Generation\n"
    
    if analysis.get("security_critical"):
        if analysis.get("complexity") == "high":
            description += "6. Security Review (added for security-critical project)\n"
            description += "7. Test Generation\n"
        else:
            description += "5. Security Review (added for security-critical project)\n"
            description += "6. Test Generation\n"
    else:
        if analysis.get("complexity") == "high":
            description += "6. Test Generation\n"
        else:
            description += "5. Test Generation\n"
    
    return description