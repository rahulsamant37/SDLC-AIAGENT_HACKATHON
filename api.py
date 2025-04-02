"""
FastAPI backend for the SDLC Agent.
"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from src.main import process_requirements, process_feedback, get_session, get_all_sessions, get_monitoring_information
from src.state.sdlc_state import SDLCStage

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="SDLC Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequirementsInput(BaseModel):
    """Requirements input model."""
    requirements: str

class FeedbackInput(BaseModel):
    """Feedback input model."""
    session_id: str
    stage: str
    approved: bool
    comments: str

class SessionInfo(BaseModel):
    """Session information model."""
    session_id: str
    current_stage: str
    created_at: str
    last_updated: str

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "SDLC Agent API"}

@app.post("/api/requirements")
async def submit_requirements(requirements_input: RequirementsInput, background_tasks: BackgroundTasks):
    """
    Submit user requirements to start a new SDLC process.
    
    Args:
        requirements_input (RequirementsInput): The requirements input.
        background_tasks (BackgroundTasks): Background tasks.
        
    Returns:
        dict: Session information.
    """
    # Process requirements in the background
    background_tasks.add_task(
        process_requirements_async, 
        requirements_input.requirements
    )
    
    # Generate a temporary session ID
    session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "session_id": session_id,
        "current_stage": SDLCStage.REQUIREMENTS,
        "message": "Requirements submitted successfully. Processing has started."
    }

async def process_requirements_async(requirements: str):
    """
    Process requirements asynchronously.
    
    Args:
        requirements (str): The requirements to process.
    """
    try:
        await process_requirements(requirements)
    except Exception as e:
        print(f"Error processing requirements: {str(e)}")
        import traceback
        traceback.print_exc()

@app.post("/api/feedback")
async def submit_feedback(feedback_input: FeedbackInput, background_tasks: BackgroundTasks):
    """
    Submit user feedback for a specific stage.
    
    Args:
        feedback_input (FeedbackInput): The feedback input.
        background_tasks (BackgroundTasks): Background tasks.
        
    Returns:
        dict: Updated session information.
    """
    # Process feedback in the background
    background_tasks.add_task(
        process_feedback_async,
        feedback_input.session_id,
        feedback_input.stage,
        feedback_input.approved,
        feedback_input.comments
    )
    
    return {
        "session_id": feedback_input.session_id,
        "message": "Feedback submitted successfully. Processing has started."
    }

async def process_feedback_async(session_id: str, stage: str, approved: bool, comments: str):
    """
    Process feedback asynchronously.
    
    Args:
        session_id (str): The session ID.
        stage (str): The SDLC stage.
        approved (bool): Whether the stage is approved.
        comments (str): Feedback comments.
    """
    try:
        await process_feedback(session_id, stage, approved, comments)
    except Exception as e:
        print(f"Error processing feedback for session {session_id}: {str(e)}")
        import traceback
        traceback.print_exc()

@app.get("/api/sessions")
async def get_all_sessions_endpoint():
    """
    Get a list of all active sessions.
    
    Returns:
        list: List of session information.
    """
    try:
        sessions = await get_all_sessions()
        session_info = []
        for state in sessions:
            session_info.append({
                "session_id": state.session_id,
                "current_stage": state.current_stage,
                "created_at": state.created_at,
                "last_updated": state.last_updated
            })
        return session_info
    except Exception as e:
        print(f"Error getting sessions: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

@app.get("/api/sessions/{session_id}")
async def get_session_endpoint(session_id: str):
    """
    Get information about a specific session.
    
    Args:
        session_id (str): The session ID.
        
    Returns:
        dict: Session information.
    """
    try:
        state = await get_session(session_id)
        return {
            "session_id": state.session_id,
            "state": state.to_dict(),
            "created_at": state.created_at,
            "last_updated": state.last_updated
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        print(f"Error getting session {session_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting session: {str(e)}")

@app.get("/api/sessions/{session_id}/download")
async def get_download_links(session_id: str):
    """
    Get download links for all artifacts in a session.
    
    Args:
        session_id (str): The session ID.
        
    Returns:
        dict: Download links.
    """
    try:
        state = await get_session(session_id)
        state_dict = state.to_dict()
        
        # Prepare list of available artifacts
        available_artifacts = []
        if state_dict.get("requirements"):
            available_artifacts.append({"filename": "requirements.md"})
        if state_dict.get("user_stories"):
            available_artifacts.append({"filename": "user_stories.md"})
        if state_dict.get("functional_design"):
            available_artifacts.append({"filename": "functional_design.md"})
        if state_dict.get("non_functional_design"):
            available_artifacts.append({"filename": "non_functional_design.md"})
        if state_dict.get("security_findings"):
            available_artifacts.append({"filename": "security_findings.md"})
        if state_dict.get("test_cases"):
            available_artifacts.append({"filename": "test_cases.md"})
        if state_dict.get("test_results"):
            available_artifacts.append({"filename": "test_results.md"})
        
        # Add code artifacts
        code_artifacts = state_dict.get("code_artifacts", {})
        for filename in code_artifacts.keys():
            available_artifacts.append({"filename": filename})
        
        return {
            "session_id": session_id,
            "files": available_artifacts
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        print(f"Error getting download links for session {session_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting download links: {str(e)}")

@app.get("/api/sessions/{session_id}/artifacts/{artifact_name}")
async def get_artifact(session_id: str, artifact_name: str):
    """
    Get a specific artifact from a session.
    
    Args:
        session_id (str): The session ID.
        artifact_name (str): The artifact name.
        
    Returns:
        dict: Artifact content.
    """
    try:
        state = await get_session(session_id)
        state_dict = state.to_dict()
        
        # Map artifact name to state field
        artifact_map = {
            "requirements.md": "requirements",
            "requirements_analysis.md": "requirements_analysis",
            "user_stories.md": "user_stories",
            "functional_design.md": "functional_design",
            "non_functional_design.md": "non_functional_design",
            "security_findings.md": "security_findings",
            "test_cases.md": "test_cases",
            "test_results.md": "test_results"
        }
        
        if artifact_name in artifact_map and artifact_map[artifact_name] in state_dict:
            return {
                "content": state_dict[artifact_map[artifact_name]]
            }
        elif "code_artifacts" in state_dict and artifact_name in state_dict["code_artifacts"]:
            return {
                "content": state_dict["code_artifacts"][artifact_name]
            }
        
        raise HTTPException(status_code=404, detail="Artifact not found")
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        print(f"Error getting artifact {artifact_name} for session {session_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting artifact: {str(e)}")

@app.get("/api/sessions/{session_id}/monitor")
async def get_monitoring_information_endpoint(session_id: str):
    """
    Get detailed monitoring information for a session.
    
    Args:
        session_id (str): The session ID.
        
    Returns:
        dict: Monitoring information.
    """
    try:
        monitoring_info = await get_monitoring_information(session_id)
        return {
            "session_id": session_id,
            "monitoring_info": monitoring_info
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        print(f"Error getting monitoring information for session {session_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting monitoring information: {str(e)}")

# Run the app with uvicorn
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run("api:app", host=host, port=port, reload=True)
