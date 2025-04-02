"""
State management for SDLC Agent workflow.
"""
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class SDLCStage:
    """SDLC stages enumeration."""
    REQUIREMENTS = "REQUIREMENTS"
    USER_STORIES = "USER_STORIES"
    DESIGN = "DESIGN"
    CODE = "CODE"
    SECURITY = "SECURITY"
    TESTING = "TESTING"
    COMPLETE = "COMPLETE"

class SDLCState(BaseModel):
    """State for SDLC Agent workflow."""
    
    # Core state attributes
    session_id: str = Field(..., description="Unique session identifier")
    current_stage: str = Field(SDLCStage.REQUIREMENTS, description="Current SDLC stage")
    requirements: Optional[str] = Field(None, description="Project requirements")
    
    # Artifacts
    user_stories: Optional[str] = Field(None, description="Generated user stories")
    functional_design: Optional[str] = Field(None, description="Functional design document")
    non_functional_design: Optional[str] = Field(None, description="Non-functional design document")
    code_artifacts: Optional[Dict[str, str]] = Field(None, description="Generated code artifacts")
    security_findings: Optional[str] = Field(None, description="Security analysis findings")
    test_cases: Optional[str] = Field(None, description="Generated test cases")
    test_results: Optional[str] = Field(None, description="Test execution results")
    
    # Feedback
    feedback: Dict[str, List[str]] = Field(default_factory=dict, description="User feedback by stage")
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Last update timestamp")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="State history for monitoring")
    
    # Advanced attributes
    monitoring: Optional[Dict[str, Any]] = Field(None, description="Workflow monitoring data")
    complexity_analysis: Optional[Dict[str, Any]] = Field(None, description="Requirements complexity analysis")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return self.dict()
    
    def update_stage(self, new_stage: str):
        """
        Update current stage and record in history.
        
        Args:
            new_stage (str): The new stage.
        """
        # Record current state in history
        self.history.append({
            "stage": self.current_stage,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update stage
        self.current_stage = new_stage
        self.last_updated = datetime.now().isoformat()
    
    def add_feedback(self, stage: str, feedback_text: str):
        """
        Add feedback for a specific stage.
        
        Args:
            stage (str): The SDLC stage.
            feedback_text (str): The feedback text.
        """
        if stage not in self.feedback:
            self.feedback[stage] = []
        
        self.feedback[stage].append(feedback_text)
        self.last_updated = datetime.now().isoformat()
    
    def get_next_stage(self) -> str:
        """
        Get the next stage in the SDLC process.
        
        Returns:
            str: The next stage.
        """
        stages = [
            SDLCStage.REQUIREMENTS,
            SDLCStage.USER_STORIES,
            SDLCStage.DESIGN,
            SDLCStage.CODE,
            SDLCStage.SECURITY,
            SDLCStage.TESTING,
            SDLCStage.COMPLETE
        ]
        
        try:
            current_index = stages.index(self.current_stage)
            if current_index < len(stages) - 1:
                return stages[current_index + 1]
            return SDLCStage.COMPLETE
        except ValueError:
            return SDLCStage.REQUIREMENTS
    
    def get_all_artifacts(self) -> Dict[str, Any]:
        """
        Get all artifacts in the state.
        
        Returns:
            Dict[str, Any]: All artifacts.
        """
        return {
            "requirements": self.requirements,
            "user_stories": self.user_stories,
            "functional_design": self.functional_design,
            "non_functional_design": self.non_functional_design,
            "code_artifacts": self.code_artifacts,
            "security_findings": self.security_findings,
            "test_cases": self.test_cases,
            "test_results": self.test_results
        }