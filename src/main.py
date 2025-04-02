"""
Main application entry point for SDLC Agent.
"""
import os
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import uuid
import asyncio
from functools import wraps
import logging

from dotenv import load_dotenv
from langchain.chains import ConversationChain

from src.LLMS.groq_llm import get_llm
from src.state.sdlc_state import SDLCState, SDLCStage
from src.graph.dynamic_graph_builder import build_sdlc_graph, get_dynamic_graph_description, analyze_project_complexity
from src.monitoring.workflow_monitor import monitor_workflow_progress, get_monitoring_summary

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global state storage
sessions = {}

async def initialize_agent():
    """
    Initialize the SDLC Agent.
    
    Returns:
        tuple: (llm, sdlc_graph)
    """
    # Initialize LLM
    llm = get_llm()
    
    # Initialize graph (will be built dynamically for each request)
    sdlc_graph = None
    
    return llm, sdlc_graph

async def process_requirements(requirements: str, session_id: Optional[str] = None):
    """
    Process user requirements to start a new SDLC process.
    
    Args:
        requirements (str): The user requirements.
        session_id (Optional[str]): The session ID.
        
    Returns:
        SDLCState: The SDLC state.
    """
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Initialize LLM
    llm, _ = await initialize_agent()
    
    # Create initial state
    state = SDLCState(
        session_id=session_id,
        current_stage=SDLCStage.REQUIREMENTS,
        requirements=requirements
    )
    
    # Analyze complexity to determine dynamic workflow
    complexity_analysis = analyze_project_complexity(requirements)
    
    # Build dynamic graph based on requirements
    sdlc_graph = build_sdlc_graph(requirements)
    
    # Add complexity analysis to state
    state.complexity_analysis = complexity_analysis
    
    # Record state
    sessions[session_id] = {
        "state": state,
        "graph": sdlc_graph,
        "graph_description": get_dynamic_graph_description(requirements)
    }
    
    # Run the first step (requirements analysis)
    result = sdlc_graph.invoke({
        "session_id": session_id,
        "current_stage": SDLCStage.REQUIREMENTS,
        "requirements": requirements
    })
    
    # Update state with result
    for key, value in result.items():
        if hasattr(state, key):
            setattr(state, key, value)
    
    # Apply monitoring
    monitoring_result = monitor_workflow_progress(state.dict())
    state.monitoring = monitoring_result.get("monitoring")
    
    # Update state in sessions
    sessions[session_id]["state"] = state
    
    return state

async def process_feedback(session_id: str, stage: str, approved: bool, comments: str):
    """
    Process user feedback for a specific stage.
    
    Args:
        session_id (str): The session ID.
        stage (str): The SDLC stage.
        approved (bool): Whether the stage is approved.
        comments (str): Feedback comments.
        
    Returns:
        SDLCState: The updated SDLC state.
    """
    # Get session
    session = sessions.get(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found.")
    
    # Get state and graph
    state = session["state"]
    sdlc_graph = session["graph"]
    
    # Add feedback to state
    state.add_feedback(stage, comments)
    
    if approved:
        # If approved, move to next stage
        next_stage = state.get_next_stage()
        state.update_stage(next_stage)
        
        # Run the next step
        current_state = state.dict()
        result = sdlc_graph.invoke(current_state)
        
        # Update state with result
        for key, value in result.items():
            if hasattr(state, key):
                setattr(state, key, value)
    else:
        # If not approved, regenerate the current stage with feedback
        current_state = state.dict()
        current_state["feedback"] = {stage: state.feedback.get(stage, [])}
        
        # Determine which node to rerun based on stage
        stage_node_mapping = {
            SDLCStage.REQUIREMENTS: "requirements",
            SDLCStage.USER_STORIES: "user_stories",
            SDLCStage.DESIGN: "design",
            SDLCStage.CODE: "code", 
            SDLCStage.SECURITY: "security",
            SDLCStage.TESTING: "test"
        }
        
        node_name = stage_node_mapping.get(stage)
        if node_name:
            # Rerun the specific node with feedback
            result = sdlc_graph.invoke(current_state, {"target_node": node_name})
            
            # Update state with result
            for key, value in result.items():
                if hasattr(state, key):
                    setattr(state, key, value)
    
    # Apply monitoring
    monitoring_result = monitor_workflow_progress(state.dict())
    state.monitoring = monitoring_result.get("monitoring")
    
    # Update state in sessions
    sessions[session_id]["state"] = state
    
    return state

async def get_session(session_id: str):
    """
    Get information about a specific session.
    
    Args:
        session_id (str): The session ID.
        
    Returns:
        SDLCState: The SDLC state.
    """
    # Get session
    session = sessions.get(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found.")
    
    # Get state
    state = session["state"]
    
    # Apply monitoring
    monitoring_result = monitor_workflow_progress(state.dict())
    state.monitoring = monitoring_result.get("monitoring")
    
    # Update state in sessions
    sessions[session_id]["state"] = state
    
    return state

async def get_all_sessions():
    """
    Get a list of all active sessions.
    
    Returns:
        list: List of SDLCState objects.
    """
    return [session["state"] for session in sessions.values()]

async def get_monitoring_information(session_id: str):
    """
    Get detailed monitoring information for a session.
    
    Args:
        session_id (str): The session ID.
        
    Returns:
        str: Markdown formatted monitoring summary.
    """
    # Get session
    session = sessions.get(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found.")
    
    # Get state
    state = session["state"]
    
    # Apply monitoring
    monitoring_result = monitor_workflow_progress(state.dict())
    state.monitoring = monitoring_result.get("monitoring")
    
    # Update state in sessions
    sessions[session_id]["state"] = state
    
    # Get monitoring summary
    summary = get_monitoring_summary(state.dict())
    
    return summary

async def test_agent():
    """
    Test the SDLC Agent with a sample project.
    """
    requirements = """
    We need to build a task management system with the following features:
    1. User authentication (sign up, log in, log out)
    2. Task creation, update, and deletion
    3. Task assignment to users
    4. Task categorization and tagging
    5. Due date setting and reminder notifications
    6. Task priority levels
    7. Task status tracking (to-do, in progress, completed)
    8. User dashboard showing task summary
    9. Admin dashboard for user management
    10. Search and filter functionality
    11. Mobile-responsive design
    """
    
    # Process requirements
    state = await process_requirements(requirements)
    logger.info(f"Initial state: {state.current_stage}")
    
    # Approve and move through stages
    for stage in [
        SDLCStage.REQUIREMENTS,
        SDLCStage.USER_STORIES,
        SDLCStage.DESIGN,
        SDLCStage.CODE,
        SDLCStage.SECURITY,
        SDLCStage.TESTING
    ]:
        state = await process_feedback(
            state.session_id,
            stage,
            approved=True,
            comments="Looks good!"
        )
        logger.info(f"Advanced to stage: {state.current_stage}")
    
    # Get monitoring information
    monitoring_info = await get_monitoring_information(state.session_id)
    logger.info(f"Monitoring information: {monitoring_info}")
    
    return state

if __name__ == "__main__":
    asyncio.run(test_agent())