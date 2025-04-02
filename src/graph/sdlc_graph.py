"""
LangGraph implementation of the SDLC process.
"""
from typing import Dict, Any, List, Optional, Union, Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph import MessagesState
from langgraph.checkpoint import JsonCheckpoint
import os
import asyncio
import json

from src.nodes.requirement_analyzer import analyze_requirements
from src.nodes.user_story_generator import generate_user_stories, process_user_stories_feedback
from src.nodes.design_document_generator import generate_design_documents, process_design_feedback

# Define checkpoint directory
CHECKPOINT_DIR = "/tmp/sdlc_checkpoints"
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

def should_retry_operation(state: Dict[str, Any]) -> bool:
    """
    Check if an operation should be retried.
    
    Args:
        state (Dict[str, Any]): The current state.
        
    Returns:
        bool: Whether to retry the operation.
    """
    error = state.get("error")
    if not error:
        return False
    
    # Check retries
    operation = state.get("current_operation", "unknown")
    retries = state.get("retries", {}).get(operation, 0)
    
    # Allow up to 3 retries
    return retries < 3

def create_sdlc_graph(llm: Any, vectorstore: Any):
    """
    Create the SDLC graph.
    
    Args:
        llm (Any): The language model to use.
        vectorstore (Any): The vector store for document storage.
        
    Returns:
        StateGraph: The SDLC graph.
    """
    # Define state schema
    class SDLCGraphState(TypedDict):
        session_id: str
        current_stage: str
        current_operation: Optional[str]
        requirements: str
        requirement_analysis: Optional[str]
        domain_analysis: Optional[str]
        complexity: str
        user_stories: Optional[str]
        functional_design: Optional[str]
        non_functional_design: Optional[str]
        code_artifacts: Dict[str, str]
        security_findings: Optional[str]
        test_cases: Optional[str]
        test_results: Optional[str]
        feedback: Dict[str, Dict[str, Any]]
        history: List[Dict[str, Any]]
        created_at: str
        last_updated: str
        completed: bool
        error: Optional[str]
        retries: Dict[str, int]
    
    # Create graph
    graph = StateGraph(SDLCGraphState)
    
    # Add nodes
    
    # Requirements Analysis Node
    async def requirements_node(state: Dict[str, Any]) -> Dict[str, Any]:
        # Set current operation
        state["current_operation"] = "analyze_requirements"
        
        # If there's an error and we should retry, increment retry count
        if state.get("error") and should_retry_operation(state):
            retries = state.get("retries", {})
            current_retries = retries.get("analyze_requirements", 0)
            retries["analyze_requirements"] = current_retries + 1
            state["retries"] = retries
            state["error"] = None
        
        # Analyze requirements
        try:
            state = await analyze_requirements(state, llm)
            return state
        except Exception as e:
            state["error"] = f"Error in requirements analysis: {str(e)}"
            return state
    
    # User Stories Generation Node
    async def user_stories_node(state: Dict[str, Any]) -> Dict[str, Any]:
        # Set current operation
        state["current_operation"] = "generate_user_stories"
        
        # If there's an error and we should retry, increment retry count
        if state.get("error") and should_retry_operation(state):
            retries = state.get("retries", {})
            current_retries = retries.get("generate_user_stories", 0)
            retries["generate_user_stories"] = current_retries + 1
            state["retries"] = retries
            state["error"] = None
        
        # Generate user stories
        try:
            state = await generate_user_stories(state, llm, vectorstore)
            return state
        except Exception as e:
            state["error"] = f"Error in user stories generation: {str(e)}"
            return state
    
    # User Stories Feedback Node
    async def user_stories_feedback_node(state: Dict[str, Any]) -> Dict[str, Any]:
        # Set current operation
        state["current_operation"] = "process_user_stories_feedback"
        
        # If there's an error and we should retry, increment retry count
        if state.get("error") and should_retry_operation(state):
            retries = state.get("retries", {})
            current_retries = retries.get("process_user_stories_feedback", 0)
            retries["process_user_stories_feedback"] = current_retries + 1
            state["retries"] = retries
            state["error"] = None
        
        # Process user stories feedback
        try:
            state = await process_user_stories_feedback(state, llm, vectorstore)
            return state
        except Exception as e:
            state["error"] = f"Error in user stories feedback processing: {str(e)}"
            return state
    
    # Design Documents Generation Node
    async def design_node(state: Dict[str, Any]) -> Dict[str, Any]:
        # Set current operation
        state["current_operation"] = "generate_design_documents"
        
        # If there's an error and we should retry, increment retry count
        if state.get("error") and should_retry_operation(state):
            retries = state.get("retries", {})
            current_retries = retries.get("generate_design_documents", 0)
            retries["generate_design_documents"] = current_retries + 1
            state["retries"] = retries
            state["error"] = None
        
        # Generate design documents
        try:
            state = await generate_design_documents(state, llm, vectorstore)
            return state
        except Exception as e:
            state["error"] = f"Error in design document generation: {str(e)}"
            return state
    
    # Design Feedback Node
    async def design_feedback_node(state: Dict[str, Any]) -> Dict[str, Any]:
        # Set current operation
        state["current_operation"] = "process_design_feedback"
        
        # If there's an error and we should retry, increment retry count
        if state.get("error") and should_retry_operation(state):
            retries = state.get("retries", {})
            current_retries = retries.get("process_design_feedback", 0)
            retries["process_design_feedback"] = current_retries + 1
            state["retries"] = retries
            state["error"] = None
        
        # Process design feedback
        try:
            state = await process_design_feedback(state, llm, vectorstore)
            return state
        except Exception as e:
            state["error"] = f"Error in design feedback processing: {str(e)}"
            return state
    
    # Error Handler Node
    async def error_handler_node(state: Dict[str, Any]) -> Dict[str, Any]:
        # Get error
        error = state.get("error", "Unknown error")
        
        # Get current operation
        operation = state.get("current_operation", "unknown")
        
        # Get retries
        retries = state.get("retries", {}).get(operation, 0)
        
        # Log error
        print(f"Error in operation {operation} (retry {retries}): {error}")
        
        # If max retries exceeded, add error to history and continue
        if retries >= 3:
            history = state.get("history", [])
            history.append({
                "type": "error",
                "operation": operation,
                "error": error,
                "retries": retries
            })
            state["history"] = history
            state["error"] = None
        
        return state
    
    # Add nodes to graph
    graph.add_node("analyze_requirements", requirements_node)
    graph.add_node("generate_user_stories", user_stories_node)
    graph.add_node("process_user_stories_feedback", user_stories_feedback_node)
    graph.add_node("generate_design_documents", design_node)
    graph.add_node("process_design_feedback", design_feedback_node)
    graph.add_node("error_handler", error_handler_node)
    
    # Define conditional edges
    
    # Start with requirements analysis
    graph.set_entry_point("analyze_requirements")
    
    # Define edge conditions
    
    def has_error(state: Dict[str, Any]) -> str:
        """Check if state has an error."""
        if state.get("error"):
            return "error_handler"
        return None
    
    def next_after_requirements(state: Dict[str, Any]) -> str:
        """Determine next node after requirements analysis."""
        if state.get("error"):
            return "error_handler"
        return "generate_user_stories"
    
    def next_after_user_stories(state: Dict[str, Any]) -> str:
        """Determine next node after user stories generation."""
        if state.get("error"):
            return "error_handler"
        
        # Check if there's feedback for USER_STORIES stage
        feedback = state.get("feedback", {}).get("USER_STORIES")
        
        if feedback:
            # If not approved, process feedback
            if not feedback.get("approved", False):
                return "process_user_stories_feedback"
        
        # Move to design stage
        return "generate_design_documents"
    
    def next_after_user_stories_feedback(state: Dict[str, Any]) -> str:
        """Determine next node after user stories feedback processing."""
        if state.get("error"):
            return "error_handler"
        
        # Check if user stories feedback is approved
        feedback = state.get("feedback", {}).get("USER_STORIES")
        
        if feedback and feedback.get("approved", False):
            return "generate_design_documents"
        
        # Stay in user stories feedback
        return "process_user_stories_feedback"
    
    def next_after_design(state: Dict[str, Any]) -> str:
        """Determine next node after design document generation."""
        if state.get("error"):
            return "error_handler"
        
        # Check if there's feedback for DESIGN stage
        feedback = state.get("feedback", {}).get("DESIGN")
        
        if feedback:
            # If not approved, process feedback
            if not feedback.get("approved", False):
                return "process_design_feedback"
        
        # End for now (will add more nodes later)
        return END
    
    def next_after_design_feedback(state: Dict[str, Any]) -> str:
        """Determine next node after design feedback processing."""
        if state.get("error"):
            return "error_handler"
        
        # Check if design feedback is approved
        feedback = state.get("feedback", {}).get("DESIGN")
        
        if feedback and feedback.get("approved", False):
            return END
        
        # Stay in design feedback
        return "process_design_feedback"
    
    def next_after_error_handler(state: Dict[str, Any]) -> Union[str, None]:
        """Determine next node after error handling."""
        # If error is still present and should retry, return to current operation
        if state.get("error") and should_retry_operation(state):
            return state.get("current_operation", "analyze_requirements")
        
        # If no error or max retries exceeded, proceed based on current stage
        current_stage = state.get("current_stage", "REQUIREMENTS")
        
        if current_stage == "REQUIREMENTS":
            return "generate_user_stories"
        elif current_stage == "USER_STORIES":
            return "generate_design_documents"
        elif current_stage == "DESIGN":
            return END  # End for now (will add more nodes later)
        
        # Default: end
        return END
    
    # Add edges
    graph.add_conditional_edges(
        "analyze_requirements",
        next_after_requirements
    )
    
    graph.add_conditional_edges(
        "generate_user_stories",
        next_after_user_stories
    )
    
    graph.add_conditional_edges(
        "process_user_stories_feedback",
        next_after_user_stories_feedback
    )
    
    graph.add_conditional_edges(
        "generate_design_documents",
        next_after_design
    )
    
    graph.add_conditional_edges(
        "process_design_feedback",
        next_after_design_feedback
    )
    
    graph.add_conditional_edges(
        "error_handler",
        next_after_error_handler
    )
    
    # Create checkpoint directory for this graph
    session_checkpoint_dir = os.path.join(CHECKPOINT_DIR, "sdlc_graph")
    os.makedirs(session_checkpoint_dir, exist_ok=True)
    
    # Create and return checkpointed graph
    checkpointed_graph = graph.with_checkpointer(
        JsonCheckpoint(session_checkpoint_dir)
    )
    
    return checkpointed_graph