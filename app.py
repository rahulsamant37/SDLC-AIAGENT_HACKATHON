"""
Streamlit frontend for the SDLC Agent with a mock backend.
"""
import os
import json
import time
import requests
import base64
from datetime import datetime
import uuid

import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="SDLC Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS and JavaScript for enhanced UI and functionality
st.markdown("""
<style>
    /* General styling improvements */
    .stApp {
        background-color: #F5F7FA;
    }
    
    .stMarkdown {
        color: #2C3E50;
    }
    
    .stTextArea > div {
        border-radius: 0.5rem;
    }
    
    .stTextArea > label {
        color: #1976D2;
        font-weight: 500;
    }
    
    .stExpander {
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Headers */
    .main-header {
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
        color: #1565C0;
        text-align: center;
        font-weight: 700;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    .sub-header {
        font-size: 1.8rem;
        margin-top: 2rem;
        margin-bottom: 1.2rem;
        color: #0D47A1;
        border-bottom: 3px solid #1976D2;
        padding-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .section-header {
        font-size: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        color: #1565C0;
        font-weight: 600;
    }
    
    .info-box {
        background-color: #BBDEFB;
        padding: 1.2rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1565C0;
        margin-bottom: 1rem;
        color: #0D47A1;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .success-box {
        background-color: #C8E6C9;
        padding: 1.2rem;
        border-radius: 0.5rem;
        border-left: 5px solid #2E7D32;
        margin-bottom: 1rem;
        color: #1B5E20;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .warning-box {
        background-color: #FFECB3;
        padding: 1.2rem;
        border-radius: 0.5rem;
        border-left: 5px solid #F57F17;
        margin-bottom: 1rem;
        color: #E65100;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .error-box {
        background-color: #FFCDD2;
        padding: 1.2rem;
        border-radius: 0.5rem;
        border-left: 5px solid #C62828;
        margin-bottom: 1rem;
        color: #B71C1C;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .feedback-card {
        background-color: #E8EAF6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.16);
        margin-bottom: 1.5rem;
        border: 1px solid #C5CAE9;
    }
    
    .code-box {
        background-color: #263238;
        color: #ECEFF1;
        padding: 1.2rem;
        border-radius: 0.5rem;
        border: 1px solid #455A64;
        overflow-x: auto;
        font-family: 'Courier New', monospace;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
    
    .stage-indicator {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    
    .stage {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 4rem;
    }
    
    .stage-circle {
        width: 3rem;
        height: 3rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.5rem;
        background-color: #E0E0E0;
        color: #616161;
        font-weight: bold;
    }
    
    .stage-active {
        background-color: #1E88E5;
        color: white;
    }
    
    .stage-completed {
        background-color: #43A047;
        color: white;
    }
    
    .stage-text {
        font-size: 0.8rem;
        text-align: center;
        color: #616161;
    }
    
    /* Improved button styling */
    div.stButton > button {
        background-color: #1976D2;
        color: white;
        border: none;
        border-radius: 0.3rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    div.stButton > button:hover {
        background-color: #1565C0;
    }
    
    /* Button variants */
    .primary-btn {
        background-color: #1976D2 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 0.3rem !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    
    .primary-btn:hover {
        background-color: #1565C0 !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
    }
    
    .success-btn {
        background-color: #43A047 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 0.3rem !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    
    .success-btn:hover {
        background-color: #388E3C !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
    }
    
    .warning-btn {
        background-color: #FB8C00 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 0.3rem !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    
    .warning-btn:hover {
        background-color: #F57C00 !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
    }
    
    .danger-btn {
        background-color: #E53935 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 0.3rem !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    
    .danger-btn:hover {
        background-color: #D32F2F !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Button group styles */
    .button-group {
        display: flex;
        gap: 10px;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    
    .button-group-item {
        flex: 1;
    }
    
    /* Custom checkbox for approval */
    .approval-checkbox {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding: 1rem 1.5rem;
        background-color: #C8E6C9;
        border: 1px solid #66BB6A;
        border-radius: 0.5rem;
        cursor: pointer;
        color: #1B5E20;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Tabbed interface */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        background-color: #F5F7FA;
        border-radius: 8px 8px 0 0;
        gap: 1rem;
        padding: 10px 15px;
        font-weight: 500;
        color: #37474F;
        border: 1px solid #CFD8DC;
        border-bottom: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #BBDEFB;
        border-radius: 8px 8px 0 0;
        border-right: 1px solid #1976D2;
        border-left: 1px solid #1976D2;
        border-top: 3px solid #1565C0;
        color: #0D47A1;
        font-weight: 600;
    }
    
    /* Style for the tab content area */
    .stTabs [data-baseweb="tab-panel"] {
        background-color: white;
        border: 1px solid #CFD8DC;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 20px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    
    /* Example tabs styling */
    .example-tab {
        background-color: #EFF7FF;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #BBDEFB;
        margin-bottom: 15px;
    }
    
    .example-tab h4 {
        color: #0D47A1;
        margin-top: 0;
        margin-bottom: 10px;
        border-bottom: 2px solid #90CAF9;
        padding-bottom: 5px;
    }
    
    .example-tab p {
        color: #263238;
        line-height: 1.5;
    }
    
    /* Style for the use example button */
    .use-example-btn {
        background-color: #90CAF9;
        color: #0D47A1;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: 500;
        margin-top: 10px;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
    }
    
    .use-example-btn:hover {
        background-color: #42A5F5;
        color: white;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
</style>

<script>
// Function to set text in the requirements textarea
function setRequirementsText(text) {
    // Find the requirements textarea
    const textareas = document.querySelectorAll('textarea');
    const requirementsTextarea = textareas[0]; // First textarea on the page should be requirements
    
    if (requirementsTextarea) {
        // Set value
        requirementsTextarea.value = text;
        
        // Create and dispatch an input event to trigger Streamlit's state update
        const event = new Event('input', { bubbles: true });
        requirementsTextarea.dispatchEvent(event);
    }
}

// Add event listeners when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initial setup - may not work due to Streamlit's component loading
    setupExampleButtons();
    
    // Use MutationObserver to detect when Streamlit components are fully loaded
    const observer = new MutationObserver(function(mutations) {
        setupExampleButtons();
    });
    
    // Start observing document body for changes
    observer.observe(document.body, { childList: true, subtree: true });
});

function setupExampleButtons() {
    // Web app example
    const webAppButton = document.getElementById('web-app-example-btn');
    const webAppText = document.getElementById('web-app-example-text');
    if (webAppButton && webAppText && !webAppButton.hasListener) {
        webAppButton.addEventListener('click', function() {
            setRequirementsText(webAppText.textContent);
        });
        webAppButton.hasListener = true;
    }
    
    // Mobile app example
    const mobileAppButton = document.getElementById('mobile-app-example-btn');
    const mobileAppText = document.getElementById('mobile-app-example-text');
    if (mobileAppButton && mobileAppText && !mobileAppButton.hasListener) {
        mobileAppButton.addEventListener('click', function() {
            setRequirementsText(mobileAppText.textContent);
        });
        mobileAppButton.hasListener = true;
    }
    
    // API service example
    const apiServiceButton = document.getElementById('api-service-example-btn');
    const apiServiceText = document.getElementById('api-service-example-text');
    if (apiServiceButton && apiServiceText && !apiServiceButton.hasListener) {
        apiServiceButton.addEventListener('click', function() {
            setRequirementsText(apiServiceText.textContent);
        });
        apiServiceButton.hasListener = true;
    }
    
    // Data analysis example
    const dataAnalysisButton = document.getElementById('data-analysis-example-btn');
    const dataAnalysisText = document.getElementById('data-analysis-example-text');
    if (dataAnalysisButton && dataAnalysisText && !dataAnalysisButton.hasListener) {
        dataAnalysisButton.addEventListener('click', function() {
            setRequirementsText(dataAnalysisText.textContent);
        });
        dataAnalysisButton.hasListener = true;
    }
}
</script>
""", unsafe_allow_html=True)

# Session variables
if 'sessions' not in st.session_state:
    st.session_state.sessions = {}

# Define SDLC stages
class SDLCStage:
    REQUIREMENTS = "REQUIREMENTS"
    USER_STORIES = "USER_STORIES"
    DESIGN = "DESIGN"
    CODE = "CODE"
    SECURITY = "SECURITY"
    TESTING = "TESTING"
    COMPLETE = "COMPLETE"

# Define programming languages for code generation
PROGRAMMING_LANGUAGES = {
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "java": "Java",
    "csharp": "C#",
    "cpp": "C++",
    "go": "Go",
    "rust": "Rust"
}

# Helper functions
def generate_session_id():
    return f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"

def create_new_session(requirements):
    session_id = generate_session_id()
    st.session_state.sessions[session_id] = {
        "state": {
            "current_stage": SDLCStage.USER_STORIES,
            "requirements": requirements,
            "requirement_analysis": f"Analysis of the requirements:\n\n{requirements}\n\nThis project aims to solve the specified problem with the given constraints.",
            "user_stories": generate_mock_user_stories(requirements),
            "functional_design": "",
            "non_functional_design": "",
            "code_artifacts": {},
            "security_findings": "",
            "test_cases": "",
            "test_results": "",
        },
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    return session_id

def advance_stage(session_id, current_stage, feedback=None):
    """Advance to the next stage based on current stage and feedback"""
    if current_stage == SDLCStage.REQUIREMENTS:
        return SDLCStage.USER_STORIES
    elif current_stage == SDLCStage.USER_STORIES:
        # Generate design documents
        session = st.session_state.sessions[session_id]
        session["state"]["functional_design"] = generate_mock_functional_design(session["state"]["requirements"])
        session["state"]["non_functional_design"] = generate_mock_non_functional_design(session["state"]["requirements"])
        return SDLCStage.DESIGN
    elif current_stage == SDLCStage.DESIGN:
        # Generate code
        session = st.session_state.sessions[session_id]
        session["state"]["code_artifacts"] = generate_mock_code(session["state"]["requirements"])
        return SDLCStage.CODE
    elif current_stage == SDLCStage.CODE:
        # Generate security findings
        session = st.session_state.sessions[session_id]
        session["state"]["security_findings"] = generate_mock_security_findings(session["state"]["requirements"])
        return SDLCStage.SECURITY
    elif current_stage == SDLCStage.SECURITY:
        # Generate test cases
        session = st.session_state.sessions[session_id]
        session["state"]["test_cases"] = generate_mock_test_cases(session["state"]["requirements"])
        session["state"]["test_results"] = generate_mock_test_results()
        return SDLCStage.TESTING
    elif current_stage == SDLCStage.TESTING:
        return SDLCStage.COMPLETE
    else:
        return current_stage

# Mock data generators
def generate_mock_user_stories(requirements):
    """
    Generate user stories based on the requirements using LLM.
    """
    try:
        from src.utils.llm_generator import generate_user_stories
        return generate_user_stories(requirements)
    except Exception as e:
        print(f"Error using LLM to generate user stories: {str(e)}")
        # Fallback to simple generation method if there's an error with the LLM
        user_stories = ["# User Stories Based on Your Requirements\n"]
        user_stories.append("## Core User Stories\n")
        user_stories.append("### User Story 1\nAs a user, I want to have a clear and intuitive interface, so that I can easily navigate the application.")
        user_stories.append("### User Story 2\nAs a user, I want to interact with features specific to my requirements, so that I can accomplish my tasks efficiently.")
        user_stories.append("### User Story 3\nAs a stakeholder, I want to provide feedback on generated artifacts, so that I can ensure they meet my requirements.")
        return "\n\n".join(user_stories)

def generate_mock_functional_design(requirements):
    """
    Generate functional design document based on requirements using LLM.
    
    Args:
        requirements (str): The user requirements.
        
    Returns:
        str: The generated functional design document.
    """
    try:
        # Try to get user stories first
        session_id = st.session_state.session_id
        if session_id in st.session_state.sessions:
            session = st.session_state.sessions[session_id]
            user_stories = session["state"].get("user_stories", "")
            
            # Use LLM to generate functional design
            from src.utils.llm_generator import generate_functional_design
            return generate_functional_design(requirements, user_stories)
    except Exception as e:
        print(f"Error using LLM to generate functional design: {str(e)}")
    
    # Fallback to simple generation method if there's an error with the LLM
    return f"""# Functional Design Document

## 1. Introduction
This document outlines the functional design for the system based on the requirements.

## 2. System Overview
The system will automate the software development lifecycle with human feedback at each stage.

## 3. Feature Descriptions
- Requirements input and analysis
- User story generation
- Design document creation
- Code generation
- Security review
- Test case generation and execution

## 4. User Interface
The system will have a web-based interface built with Streamlit for user interactions.

## 5. API Specifications
RESTful API endpoints will be provided for programmatic access to the system.

Generated based on requirements: {requirements[:100]}...
"""

def generate_mock_non_functional_design(requirements):
    """
    Generate non-functional design document based on requirements using LLM.
    
    Args:
        requirements (str): The user requirements.
        
    Returns:
        str: The generated non-functional design document.
    """
    try:
        # Try to get user stories first
        session_id = st.session_state.session_id
        if session_id in st.session_state.sessions:
            session = st.session_state.sessions[session_id]
            user_stories = session["state"].get("user_stories", "")
            
            # Use LLM to generate non-functional design
            from src.utils.llm_generator import generate_non_functional_design
            return generate_non_functional_design(requirements, user_stories)
    except Exception as e:
        print(f"Error using LLM to generate non-functional design: {str(e)}")
    
    # Fallback to simple generation method if there's an error with the LLM
    return f"""# Non-Functional Design Document

## 1. Performance Requirements
- The system should respond to user interactions within 2 seconds
- LLM generation tasks may take up to 30 seconds

## 2. Security Requirements
- User data will be stored securely
- API keys will be managed through environment variables

## 3. Scalability
- The system should handle multiple concurrent sessions
- Stateless design for horizontal scaling

## 4. Reliability
- Error handling for all user inputs and API calls
- Graceful degradation if LLM services are unavailable

## 5. Maintainability
- Modular design with separation of concerns
- Comprehensive documentation for all components

Generated based on requirements: {requirements[:100]}...
"""

def generate_mock_code(requirements):
    """
    Generate code artifacts based on requirements and design documents using LLM.
    
    Args:
        requirements (str): The user requirements.
        
    Returns:
        dict: The generated code artifacts.
    """
    try:
        # Try to get user stories and design docs
        session_id = st.session_state.session_id
        if session_id in st.session_state.sessions:
            session = st.session_state.sessions[session_id]
            state = session["state"]
            
            functional_design = state.get("functional_design", "")
            non_functional_design = state.get("non_functional_design", "")
            
            # Use LLM to generate code artifacts
            from src.utils.llm_generator import generate_code_artifacts
            code_artifacts = generate_code_artifacts(requirements, functional_design, non_functional_design)
            
            if code_artifacts:
                return code_artifacts
    except Exception as e:
        print(f"Error using LLM to generate code artifacts: {str(e)}")
    
    # Fallback to simple generation method if there's an error with the LLM
    code_artifacts = {
        "main": """import streamlit as st
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

def main():
    st.title("SDLC Agent")
    st.write("Input your requirements below to start the SDLC process.")
    
    requirements = st.text_area("Requirements", height=200)
    
    if st.button("Submit", key="submit_button"):
        if requirements:
            with st.spinner("Processing requirements..."):
                # Process requirements using LLM
                result = process_requirements(requirements)
                st.success("Processing complete!")
                st.write(result)
        else:
            st.error("Please enter requirements.")

def process_requirements(requirements):
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(google_api_key="YOUR_API_KEY", model="gemini-2.0-flash")
    
    # Create prompt
    prompt = PromptTemplate(
        input_variables=["requirements"],
        template="Analyze these requirements and provide insights:\\n{requirements}"
    )
    
    # Create chain
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Run chain
    return chain.run(requirements=requirements)

if __name__ == "__main__":
    main()
""",
        "api": """from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
from datetime import datetime

app = FastAPI()

# Model definitions
class RequirementInput(BaseModel):
    text: str

class Session(BaseModel):
    id: str
    stage: str
    created_at: str
    artifacts: Dict[str, Any]

# Store sessions
sessions = {}

@app.post("/requirements", response_model=Session)
async def create_session(input: RequirementInput):
    session_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    sessions[session_id] = {
        "id": session_id,
        "stage": "REQUIREMENTS",
        "created_at": now,
        "artifacts": {
            "requirements": input.text
        }
    }
    
    return sessions[session_id]

@app.get("/sessions/{session_id}", response_model=Session)
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return sessions[session_id]
""",
        "graph": """from langchain.graphs import StateGraph
from langchain.schema import Document

def create_sdlc_graph(llm, vectorstore):
    # Create the graph
    graph = StateGraph(name="SDLC Process")
    
    # Add nodes
    graph.add_node("requirements_analyzer", requirements_analyzer)
    graph.add_node("user_story_generator", user_story_generator)
    graph.add_node("design_document_generator", design_document_generator)
    graph.add_node("code_generator", code_generator)
    graph.add_node("security_reviewer", security_reviewer)
    graph.add_node("test_case_generator", test_case_generator)
    
    # Add edges
    graph.add_edge("requirements_analyzer", "user_story_generator")
    graph.add_edge("user_story_generator", "design_document_generator")
    graph.add_edge("design_document_generator", "code_generator")
    graph.add_edge("code_generator", "security_reviewer")
    graph.add_edge("security_reviewer", "test_case_generator")
    
    # Compile the graph
    return graph.compile()
"""
    }
    return code_artifacts

def generate_mock_security_findings(requirements):
    """
    Generate security findings based on code artifacts using LLM.
    
    Args:
        requirements (str): The user requirements.
        
    Returns:
        str: The generated security findings.
    """
    try:
        # Try to get code artifacts
        session_id = st.session_state.session_id
        if session_id in st.session_state.sessions:
            session = st.session_state.sessions[session_id]
            code_artifacts = session["state"].get("code_artifacts", {})
            
            if code_artifacts:
                # Use LLM to generate security findings
                from src.utils.llm_generator import generate_security_findings
                return generate_security_findings(code_artifacts)
    except Exception as e:
        print(f"Error using LLM to generate security findings: {str(e)}")
    
    # Fallback to simple generation method if there's an error with the LLM
    return f"""# Security Review Findings

## Overview
This report presents the findings of the security review conducted on the generated code.

## Findings Summary
- 2 High severity issues
- 3 Medium severity issues
- 4 Low severity issues

## High Severity Issues
1. **API Key Exposure**: Hard-coded API key in the main.py file
   - **Fix**: Store the API key in environment variables

2. **Input Validation Missing**: No validation of user input
   - **Fix**: Add proper input validation routines

## Medium Severity Issues
1. **Error Handling**: Insufficient error handling in API endpoints
2. **Session Management**: Weak session ID generation mechanism
3. **Dependency Issues**: Using outdated libraries with known vulnerabilities

## Low Severity Issues
1. **Logging**: Inadequate logging for security events
2. **Documentation**: Missing security considerations in documentation
3. **Configuration**: Default configurations may not be secure
4. **Exception Handling**: Exceptions could reveal sensitive information

Generated based on requirements: {requirements[:100]}...
"""

def generate_mock_test_cases(requirements):
    """
    Generate test cases based on requirements, user stories, and code artifacts using LLM.
    
    Args:
        requirements (str): The user requirements.
        
    Returns:
        str: The generated test cases.
    """
    try:
        # Try to get user stories and code artifacts
        session_id = st.session_state.session_id
        if session_id in st.session_state.sessions:
            session = st.session_state.sessions[session_id]
            state = session["state"]
            
            user_stories = state.get("user_stories", "")
            code_artifacts = state.get("code_artifacts", {})
            
            if user_stories and code_artifacts:
                # Use LLM to generate test cases
                from src.utils.llm_generator import generate_test_cases
                return generate_test_cases(requirements, user_stories, code_artifacts)
    except Exception as e:
        print(f"Error using LLM to generate test cases: {str(e)}")
    
    # Fallback to simple generation method if there's an error with the LLM
    return f"""# Test Cases

## Functional Tests

### Test Case 1: Requirement Submission
- **Description**: Test the submission of requirements
- **Steps**:
  1. Navigate to the home page
  2. Enter requirements in the text field
  3. Click the Submit button
- **Expected Result**: Requirements are accepted and a session is created

### Test Case 2: User Story Generation
- **Description**: Test the generation of user stories
- **Steps**:
  1. Submit requirements
  2. Wait for user story generation
  3. Verify user stories are displayed
- **Expected Result**: User stories are generated based on requirements

### Test Case 3: Design Document Review
- **Description**: Test the review of design documents
- **Steps**:
  1. Navigate to design document review page
  2. View the functional and non-functional designs
  3. Submit approval feedback
- **Expected Result**: System advances to the next stage

## Integration Tests

### Test Case 4: End-to-End Process
- **Description**: Test the complete SDLC process
- **Steps**:
  1. Submit requirements
  2. Review and approve user stories
  3. Review and approve design documents
  4. Review and approve generated code
  5. Review and approve security findings
  6. Review and approve test cases
- **Expected Result**: All artifacts are generated and the process completes successfully

Generated based on requirements: {requirements[:100]}...
"""

def generate_mock_test_results():
    """
    Generate test results based on test cases using LLM.
    
    Returns:
        str: The generated test results.
    """
    try:
        # Try to get test cases
        session_id = st.session_state.session_id
        if session_id in st.session_state.sessions:
            session = st.session_state.sessions[session_id]
            test_cases = session["state"].get("test_cases", "")
            
            if test_cases:
                # Use LLM to generate test results
                from src.utils.llm_generator import generate_test_results
                return generate_test_results(test_cases)
    except Exception as e:
        print(f"Error using LLM to generate test results: {str(e)}")
    
    # Fallback to simple generation method if there's an error with the LLM
    return """# Test Execution Results

## Summary
- **Total Tests**: 8
- **Passed**: 7
- **Failed**: 1
- **Skipped**: 0

## Detailed Results

### Functional Tests
- ✅ Test Case 1: Requirement Submission - PASSED
- ✅ Test Case 2: User Story Generation - PASSED
- ✅ Test Case 3: Design Document Review - PASSED

### Integration Tests
- ❌ Test Case 4: End-to-End Process - FAILED
  - **Reason**: Timeout waiting for code generation
  - **Fix**: Increased timeout limit and optimized code generation process

### Performance Tests
- ✅ Test Case 5: Response Time - PASSED
- ✅ Test Case 6: Concurrent Users - PASSED

### Security Tests
- ✅ Test Case 7: Input Validation - PASSED
- ✅ Test Case 8: API Security - PASSED

## Recommendations
- Optimize the code generation process to reduce processing time
- Add more comprehensive error handling for edge cases
- Implement caching for frequently accessed data
"""

# Application title with dark color
st.markdown('<h1 style="color: #0A1929; margin-bottom: 0px;">🤖 SDLC Agent</h1>', unsafe_allow_html=True)
st.markdown("""
This application automates the Software Development Life Cycle (SDLC) with human feedback at each stage.
Input your requirements and the agent will guide you through the entire process, from user stories 
to test execution.
""")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "current_stage" not in st.session_state:
    st.session_state.current_stage = None
if "feedback_provided" not in st.session_state:
    st.session_state.feedback_provided = False
if "processing" not in st.session_state:
    st.session_state.processing = False
if "trigger_rerun" not in st.session_state:
    st.session_state.trigger_rerun = False

def create_download_button(content, filename):
    """
    Create a download button for text content.
    
    Args:
        content (str): The text content to download.
        filename (str): The filename for the download.
    """
    # Generate a unique key based on the filename
    key = f"download_{filename.replace('.', '_')}"
    
    st.download_button(
        label=f"Download {filename}",
        data=content,
        file_name=filename,
        mime="text/plain",
        key=key
    )

def submit_requirements():
    """Submit user requirements to start a new SDLC process."""
    requirements = st.session_state.requirements
    
    # Create a new session
    try:
        session_id = create_new_session(requirements)
        st.session_state.session_id = session_id
        st.session_state.current_stage = st.session_state.sessions[session_id]["state"]["current_stage"]
        st.session_state.processing = False
        st.success("Requirements submitted successfully!")
        st.session_state.trigger_rerun = True
    except Exception as e:
        st.error(f"Error submitting requirements: {str(e)}")

def submit_feedback(stage, approved, comments):
    """
    Submit feedback for a specific stage.
    
    Args:
        stage (str): The SDLC stage.
        approved (bool): Whether the stage is approved.
        comments (str): Feedback comments.
    """
    # Process feedback
    try:
        session_id = st.session_state.session_id
        if session_id in st.session_state.sessions:
            session = st.session_state.sessions[session_id]
            
            # Add feedback to session
            current_stage = session["state"]["current_stage"]
            
            # Store feedback in session
            if "feedback" not in session:
                session["feedback"] = {}
            
            session["feedback"][current_stage] = {
                "approved": approved,
                "comments": comments,
                "timestamp": datetime.now().isoformat()
            }
            
            # If not approved, update the content based on feedback
            if not approved and comments.strip():
                # Update content based on stage
                if current_stage == SDLCStage.USER_STORIES:
                    # Process user story feedback and update
                    session["state"]["user_stories"] = process_feedback_content(
                        session["state"]["user_stories"], 
                        comments
                    )
                elif current_stage == SDLCStage.DESIGN:
                    # Process design feedback
                    session["state"]["functional_design"] = process_feedback_content(
                        session["state"]["functional_design"], 
                        comments
                    )
                    session["state"]["non_functional_design"] = process_feedback_content(
                        session["state"]["non_functional_design"], 
                        comments
                    )
                elif current_stage == SDLCStage.CODE:
                    # Process code feedback
                    for artifact_name, artifact_content in session["state"]["code_artifacts"].items():
                        session["state"]["code_artifacts"][artifact_name] = process_feedback_content(
                            artifact_content, 
                            comments
                        )
                elif current_stage == SDLCStage.SECURITY:
                    # Process security feedback
                    session["state"]["security_findings"] = process_feedback_content(
                        session["state"]["security_findings"], 
                        comments
                    )
                elif current_stage == SDLCStage.TESTING:
                    # Process testing feedback
                    session["state"]["test_cases"] = process_feedback_content(
                        session["state"]["test_cases"], 
                        comments
                    )
            
            # If approved, advance to next stage
            if approved:
                next_stage = advance_stage(session_id, current_stage)
                session["state"]["current_stage"] = next_stage
                st.session_state.current_stage = next_stage
            
            # Update session
            session["last_updated"] = datetime.now().isoformat()
            st.session_state.sessions[session_id] = session
            
            st.session_state.feedback_provided = True
            st.success("Feedback submitted successfully!")
            st.session_state.trigger_rerun = True
        else:
            st.error("Session not found")
    except Exception as e:
        st.error(f"Error submitting feedback: {str(e)}")

def regenerate_content(stage):
    """
    Regenerate content for a specific stage without using feedback.
    
    Args:
        stage (str): The SDLC stage to regenerate content for.
    """
    try:
        session_id = st.session_state.session_id
        if session_id in st.session_state.sessions:
            session = st.session_state.sessions[session_id]
            requirements = session["state"]["requirements"]
            
            # Regenerate content based on stage
            with st.spinner(f"Regenerating {stage.replace('_', ' ').title()}..."):
                if stage == SDLCStage.USER_STORIES:
                    session["state"]["user_stories"] = generate_mock_user_stories(requirements)
                elif stage == SDLCStage.DESIGN:
                    session["state"]["functional_design"] = generate_mock_functional_design(requirements)
                    session["state"]["non_functional_design"] = generate_mock_non_functional_design(requirements)
                elif stage == SDLCStage.CODE:
                    session["state"]["code_artifacts"] = generate_mock_code(requirements)
                elif stage == SDLCStage.SECURITY:
                    session["state"]["security_findings"] = generate_mock_security_findings(requirements)
                elif stage == SDLCStage.TESTING:
                    session["state"]["test_cases"] = generate_mock_test_cases(requirements)
                    session["state"]["test_results"] = generate_mock_test_results()
            
            # Update session
            session["last_updated"] = datetime.now().isoformat()
            st.session_state.sessions[session_id] = session
            
            st.success(f"{stage.replace('_', ' ').title()} regenerated successfully!")
            st.session_state.trigger_rerun = True
        else:
            st.error("Session not found")
    except Exception as e:
        st.error(f"Error regenerating content: {str(e)}")

def process_feedback_content(original_content, feedback, content_type="general"):
    """
    Process feedback and modify content accordingly using LLM.
    
    Args:
        original_content (str): The original content.
        feedback (str): The feedback to apply.
        content_type (str): The type of content (used for LLM processing).
        
    Returns:
        str: Updated content with feedback applied.
    """
    try:
        # Use LLM to process feedback
        from src.utils.llm_generator import process_feedback
        return process_feedback(original_content, feedback, content_type)
    except Exception as e:
        print(f"Error using LLM to process feedback: {str(e)}")
        # Fallback to simple feedback incorporation if there's an error with the LLM
        feedback_lines = feedback.strip().split('\n')
        feedback_text = "\n".join([f"* {line}" for line in feedback_lines])
        
        updated_content = f"{original_content}\n\n## Applied Feedback\n{feedback_text}\n"
        return updated_content

def get_session_data():
    """
    Get data for the current session.
    
    Returns:
        dict: Session data or None if error.
    """
    if not st.session_state.session_id:
        return None
    
    try:
        session_id = st.session_state.session_id
        if session_id in st.session_state.sessions:
            return st.session_state.sessions[session_id]
        return None
    except Exception as e:
        st.error(f"Error getting session data: {str(e)}")
        return None

def render_requirements_input():
    """Render the requirements input form."""
    st.markdown('<h1 class="main-header">🤖 SDLC Agent</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3>Welcome to the AI-Powered Software Development Lifecycle Agent</h3>
        <p>This intelligent agent will guide you through the entire software development process:</p>
        <ul>
            <li>Analyze your requirements</li>
            <li>Generate detailed user stories</li>
            <li>Create technical design documents</li>
            <li>Produce code artifacts</li>
            <li>Perform security reviews</li>
            <li>Generate comprehensive test cases</li>
        </ul>
        <p>You'll have the opportunity to provide feedback at each stage of the process.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="sub-header">📝 Enter Your Requirements</h2>', unsafe_allow_html=True)
    
    # Show examples as expandable section with better styling
    with st.expander("💡 Need inspiration? Click to see example requirements"):
        example_tabs = st.tabs(["Web App", "Mobile App", "API Service", "Data Analysis"])
        
        with example_tabs[0]:
            st.markdown("""
            <div class="example-tab">
                <h4>Web Application Example</h4>
                <p>
                I need a web application that allows users to upload CSV files, visualize the data as charts, and download reports. 
                The application should have user authentication and the ability to save previous visualizations. 
                It should support at least 3 types of charts (bar, line, pie) and allow users to customize colors and labels.
                </p>
                <button class="use-example-btn" id="web-app-example-btn">Use this example</button>
                <div style="display: none;" id="web-app-example-text">I need a web application that allows users to upload CSV files, visualize the data as charts, and download reports. The application should have user authentication and the ability to save previous visualizations. It should support at least 3 types of charts (bar, line, pie) and allow users to customize colors and labels.</div>
            </div>
            """, unsafe_allow_html=True)
            
        with example_tabs[1]:
            st.markdown("""
            <div class="example-tab">
                <h4>Mobile App Example</h4>
                <p>
                I want a mobile app for tracking daily fitness goals. Users should be able to set goals for steps, calories, 
                and exercise duration. The app should integrate with phone sensors to track steps automatically 
                and allow manual entry for other activities. It should provide weekly and monthly progress reports.
                </p>
                <button class="use-example-btn" id="mobile-app-example-btn">Use this example</button>
                <div style="display: none;" id="mobile-app-example-text">I want a mobile app for tracking daily fitness goals. Users should be able to set goals for steps, calories, and exercise duration. The app should integrate with phone sensors to track steps automatically and allow manual entry for other activities. It should provide weekly and monthly progress reports.</div>
            </div>
            """, unsafe_allow_html=True)
            
        with example_tabs[2]:
            st.markdown("""
            <div class="example-tab">
                <h4>API Service Example</h4>
                <p>
                I need a RESTful API for a product inventory system. It should support CRUD operations for products, 
                categories, and suppliers. Each product should have a name, description, price, quantity, category, 
                and supplier. The API should include authentication, rate limiting, and detailed documentation.
                </p>
                <button class="use-example-btn" id="api-service-example-btn">Use this example</button>
                <div style="display: none;" id="api-service-example-text">I need a RESTful API for a product inventory system. It should support CRUD operations for products, categories, and suppliers. Each product should have a name, description, price, quantity, category, and supplier. The API should include authentication, rate limiting, and detailed documentation.</div>
            </div>
            """, unsafe_allow_html=True)
            
        with example_tabs[3]:
            st.markdown("""
            <div class="example-tab">
                <h4>Data Analysis Example</h4>
                <p>
                I need a data analysis tool that can process customer transaction data to identify purchasing patterns. 
                The tool should import data from CSV or database sources, clean the data, perform clustering analysis, 
                and generate visualizations of customer segments based on purchasing behavior.
                </p>
                <button class="use-example-btn" id="data-analysis-example-btn">Use this example</button>
                <div style="display: none;" id="data-analysis-example-text">I need a data analysis tool that can process customer transaction data to identify purchasing patterns. The tool should import data from CSV or database sources, clean the data, perform clustering analysis, and generate visualizations of customer segments based on purchasing behavior.</div>
            </div>
            """, unsafe_allow_html=True)
    
    requirements = st.text_area(
        "Requirements",
        height=250,
        placeholder="Describe your software requirements here. Be as detailed as possible about features, user interactions, technical considerations, and any specific constraints.",
        key="requirements",
        help="Provide comprehensive details for better results. Include functional requirements, technical constraints, and any specific technologies you prefer."
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        submit_button = st.button(
            "🚀 Submit Requirements", 
            on_click=submit_requirements, 
            key="submit_requirements_button", 
            use_container_width=True
        )

def render_user_stories_review(session_data):
    """
    Render the user stories review section.
    
    Args:
        session_data (dict): Session data.
    """
    # Display the progress indicator
    render_progress_indicator(SDLCStage.USER_STORIES)
    
    st.markdown('<h2 class="sub-header">📚 User Stories Review</h2>', unsafe_allow_html=True)
    
    if "state" in session_data and "user_stories" in session_data["state"]:
        user_stories = session_data["state"]["user_stories"]
        
        # Show the user stories in an expandable section with a nice UI
        with st.expander("Generated User Stories", expanded=True):
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown(user_stories)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add download button
            col1, col2 = st.columns([5, 1])
            with col2:
                create_download_button(user_stories, "user_stories.md")
        
        # Add feedback form in a nice card layout
        st.markdown('<div class="feedback-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">Provide Feedback</h3>', unsafe_allow_html=True)
        st.markdown('<p>Please review the generated user stories and provide your feedback. Your input helps improve the quality of the deliverables.</p>', unsafe_allow_html=True)
        
        feedback_tabs = st.tabs(["Feedback Form", "Feedback Guidelines"])
        
        with feedback_tabs[0]:
            comments = st.text_area(
                "Feedback Comments",
                placeholder="Let us know how to improve these user stories. Be specific about additions, modifications, or clarifications needed.",
                key="user_stories_comments",
                height=150
            )
            
            # Action buttons with better styling
            st.markdown('<div class="button-group">', unsafe_allow_html=True)
            
            # Create three columns for buttons
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                # Regenerate button
                st.markdown('<div class="button-group-item">', unsafe_allow_html=True)
                regenerate_button = st.button(
                    "🔄 Regenerate Stories",
                    key="user_stories_regenerate_button",
                    on_click=regenerate_content,
                    args=(SDLCStage.USER_STORIES,),
                    type="secondary",
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with action_col2:
                # Submit Feedback button
                st.markdown('<div class="button-group-item">', unsafe_allow_html=True)
                submit_feedback_button = st.button(
                    "✏️ Submit Feedback",
                    key="user_stories_feedback_button",
                    on_click=submit_feedback,
                    args=(SDLCStage.USER_STORIES, False, comments),
                    type="primary",
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with action_col3:
                # Approve and Continue button
                st.markdown('<div class="button-group-item">', unsafe_allow_html=True)
                approve_button = st.button(
                    "✅ Approve & Continue",
                    key="user_stories_approve_button",
                    on_click=submit_feedback,
                    args=(SDLCStage.USER_STORIES, True, comments),
                    type="primary",
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with feedback_tabs[1]:
            st.markdown("""
            ### Effective Feedback Guidelines
            
            **Focus on specificity:**
            - Mention specific user stories that need revision
            - Provide concrete examples rather than general comments
                
            **Be constructive:**
            - Suggest improvements rather than just pointing out issues
            - Consider both what works well and what needs improvement
                
            **Consider completeness:**
            - Are all key user personas represented?
            - Do the stories cover all essential functionality?
            - Are acceptance criteria clear and testable?
            
            **Ensure clarity:**
            - Each story should follow the "As a [role], I want [goal], so that [benefit]" format
            - Stories should be independent, negotiable, valuable, estimable, small, and testable
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("No user stories available. Please submit requirements first.")
        
def render_progress_indicator(current_stage):
    """
    Render a progress indicator for the SDLC stages.
    
    Args:
        current_stage (str): The current SDLC stage.
    """
    # Define all stages and their icons
    stages = [
        {"id": SDLCStage.REQUIREMENTS, "name": "Requirements", "icon": "📝"},
        {"id": SDLCStage.USER_STORIES, "name": "User Stories", "icon": "📚"},
        {"id": SDLCStage.DESIGN, "name": "Design", "icon": "🏗️"},
        {"id": SDLCStage.CODE, "name": "Code", "icon": "💻"},
        {"id": SDLCStage.SECURITY, "name": "Security", "icon": "🔒"},
        {"id": SDLCStage.TESTING, "name": "Testing", "icon": "🧪"},
        {"id": SDLCStage.COMPLETE, "name": "Complete", "icon": "🎉"}
    ]
    
    # Get the index of the current stage
    current_index = next((i for i, s in enumerate(stages) if s["id"] == current_stage), 0)
    
    # Create the HTML for the progress indicator
    html = '<div class="stage-indicator">'
    
    for i, stage in enumerate(stages):
        # Determine the stage status
        if i < current_index:
            status_class = "stage-completed"
        elif i == current_index:
            status_class = "stage-active"
        else:
            status_class = ""
        
        html += f'''
        <div class="stage">
            <div class="stage-circle {status_class}">{stage["icon"]}</div>
            <div class="stage-text">{stage["name"]}</div>
        </div>
        '''
        
        # Add connecting line between stages if not the last stage
        if i < len(stages) - 1:
            html += '<div style="flex-grow: 1; height: 2px; background-color: #E0E0E0; margin-top: 1.5rem;"></div>'
    
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)

def render_design_review(session_data):
    """
    Render the design documents review section.
    
    Args:
        session_data (dict): Session data.
    """
    st.header("🏗️ Design Documents Review")
    
    if "state" in session_data:
        state = session_data["state"]
        
        # Functional Design
        if "functional_design" in state and state["functional_design"]:
            st.markdown("### Functional Design")
            st.markdown(state["functional_design"])
            
            # Add download button
            create_download_button(state["functional_design"], "functional_design.md")
        
        # Non-Functional Design
        if "non_functional_design" in state and state["non_functional_design"]:
            st.markdown("### Non-Functional Design")
            st.markdown(state["non_functional_design"])
            
            # Add download button
            create_download_button(state["non_functional_design"], "non_functional_design.md")
        
        # Add feedback form in a nice card layout
        st.markdown('<div class="feedback-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">Provide Feedback</h3>', unsafe_allow_html=True)
        st.markdown('<p>Please review the design documents and provide your feedback. Your input helps improve the quality of the deliverables.</p>', unsafe_allow_html=True)
        
        feedback_tabs = st.tabs(["Feedback Form", "Feedback Guidelines"])
        
        with feedback_tabs[0]:
            comments = st.text_area(
                "Feedback Comments",
                placeholder="Provide any suggestions or feedback about the design documents...",
                key="design_comments",
                height=150
            )
            
            # Action buttons with better styling
            st.markdown('<div class="button-group">', unsafe_allow_html=True)
            
            # Create three columns for buttons
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                # Regenerate button
                st.markdown('<div class="button-group-item">', unsafe_allow_html=True)
                regenerate_button = st.button(
                    "🔄 Regenerate Design",
                    key="design_regenerate_button",
                    on_click=regenerate_content,
                    args=(SDLCStage.DESIGN,),
                    type="secondary",
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with action_col2:
                # Submit Feedback button
                st.markdown('<div class="button-group-item">', unsafe_allow_html=True)
                submit_feedback_button = st.button(
                    "✏️ Submit Feedback",
                    key="design_feedback_button",
                    on_click=submit_feedback,
                    args=(SDLCStage.DESIGN, False, comments),
                    type="primary",
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with action_col3:
                # Approve and Continue button
                st.markdown('<div class="button-group-item">', unsafe_allow_html=True)
                approve_button = st.button(
                    "✅ Approve & Continue",
                    key="design_approve_button",
                    on_click=submit_feedback,
                    args=(SDLCStage.DESIGN, True, comments),
                    type="primary",
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        with feedback_tabs[1]:
            st.markdown("""
            ### Effective Feedback Guidelines
            
            **Focus on specificity:**
            - Mention specific design elements that need revision
            - Provide concrete examples rather than general comments
                
            **Be constructive:**
            - Suggest improvements rather than just pointing out issues
            - Consider both what works well and what needs improvement
                
            **Consider completeness:**
            - Are all functional requirements addressed?
            - Are the non-functional requirements realistic?
            - Is the design testable and implementable?
            
            **Ensure clarity:**
            - Is the design easy to understand?
            - Are there any ambiguities that need clarification?
            - Are all components and their interactions clearly defined?
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("No design documents available. Please wait for the design phase to complete.")

def render_code_review(session_data):
    """
    Render the code review section.
    
    Args:
        session_data (dict): Session data.
    """
    st.header("💻 Code Review")
    
    if "state" in session_data and "code_artifacts" in session_data["state"]:
        code_artifacts = session_data["state"]["code_artifacts"]
        
        if code_artifacts:
            # Multi-language code generation
            st.markdown("### Multi-Language Support")
            st.markdown("View or convert the code in different programming languages.")
            
            # Language selection
            selected_language = st.selectbox(
                "Select Programming Language",
                options=list(PROGRAMMING_LANGUAGES.keys()),
                format_func=lambda x: PROGRAMMING_LANGUAGES[x],
                index=0,
                key="selected_language"
            )
            
            # Display code with syntax highlighting and real-time collaboration features
            st.markdown("### Code Artifacts with Real-Time Collaboration")
            st.markdown("Review the generated code with syntax highlighting. Code updates can be seen in real-time when feedback is applied.")
            
            # Tabs for different code artifacts
            artifact_tabs = st.tabs([name for name in code_artifacts.keys()])
            
            for i, (name, code) in enumerate(code_artifacts.items()):
                with artifact_tabs[i]:
                    # Display the code with proper syntax highlighting
                    extension = ".py" if selected_language == "python" else get_file_extension(selected_language)
                    
                    # In a real implementation, we would translate the code to the selected language
                    # For now, we'll just display a message if it's not Python
                    if selected_language != "python":
                        st.info(f"Generated {PROGRAMMING_LANGUAGES[selected_language]} code would appear here.")
                        converted_code = f"// Code converted to {PROGRAMMING_LANGUAGES[selected_language]}\n// Original Python code:\n\n{code}"
                    else:
                        converted_code = code
                    
                    st.code(converted_code, language=selected_language)
                    
                    # Add download button for each artifact
                    create_download_button(converted_code, f"{name}{extension}")
                    
                    # Add a button to copy code to clipboard
                    st.button(
                        "📋 Copy to Clipboard",
                        key=f"copy_{name}_{selected_language}"
                    )
            
            # Add feedback form in a nice card layout
            st.markdown('<div class="feedback-card">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-header">Provide Feedback</h3>', unsafe_allow_html=True)
            st.markdown('<p>Please review the generated code and provide your feedback. Your input helps improve the quality of the code.</p>', unsafe_allow_html=True)
            
            feedback_tabs = st.tabs(["Feedback Form", "Feedback Guidelines"])
            
            with feedback_tabs[0]:
                comments = st.text_area(
                    "Feedback Comments",
                    placeholder="Provide any suggestions or feedback about the code...",
                    key="code_comments",
                    height=150
                )
                
                # Action buttons with better styling
                st.markdown('<div class="button-group">', unsafe_allow_html=True)
                
                # Create three columns for buttons
                action_col1, action_col2, action_col3 = st.columns(3)
                
                with action_col1:
                    # Regenerate button
                    st.markdown('<div class="button-group-item">', unsafe_allow_html=True)
                    regenerate_button = st.button(
                        "🔄 Regenerate Code",
                        key="code_regenerate_button",
                        on_click=regenerate_content,
                        args=(SDLCStage.CODE,),
                        type="secondary",
                        use_container_width=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with action_col2:
                    # Submit Feedback button
                    st.markdown('<div class="button-group-item">', unsafe_allow_html=True)
                    submit_feedback_button = st.button(
                        "✏️ Submit Feedback",
                        key="code_feedback_button",
                        on_click=submit_feedback,
                        args=(SDLCStage.CODE, False, comments),
                        type="primary",
                        use_container_width=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with action_col3:
                    # Approve and Continue button
                    st.markdown('<div class="button-group-item">', unsafe_allow_html=True)
                    approve_button = st.button(
                        "✅ Approve & Continue",
                        key="code_approve_button",
                        on_click=submit_feedback,
                        args=(SDLCStage.CODE, True, comments),
                        type="primary",
                        use_container_width=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            with feedback_tabs[1]:
                st.markdown("""
                ### Effective Code Feedback Guidelines
                
                **Focus on specificity:**
                - Mention specific functions or code blocks that need revision
                - Provide concrete examples rather than general comments
                    
                **Be constructive:**
                - Suggest improvements rather than just pointing out issues
                - Consider both what works well and what needs improvement
                    
                **Consider completeness:**
                - Does the code fulfill all the requirements?
                - Are there any edge cases not handled?
                - Is the code optimally structured?
                
                **Ensure quality:**
                - Is the code readable and maintainable?
                - Does it follow best practices for the language?
                - Are there potential security or performance concerns?
                """)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No code artifacts available yet. Please wait for the code generation to complete.")
    else:
        st.warning("No code artifacts available yet. Please wait for the code generation to complete.")

def get_file_extension(language):
    """Get file extension for a programming language."""
    extensions = {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "java": ".java",
        "csharp": ".cs",
        "cpp": ".cpp",
        "go": ".go",
        "rust": ".rs"
    }
    return extensions.get(language, ".txt")

def render_security_review(session_data):
    """
    Render the security review section.
    
    Args:
        session_data (dict): Session data.
    """
    st.header("🔒 Security Review")
    
    if "state" in session_data and "security_findings" in session_data["state"]:
        security_findings = session_data["state"]["security_findings"]
        
        if security_findings:
            st.markdown("### Security Findings")
            st.markdown(security_findings)
            
            # Add download button
            create_download_button(security_findings, "security_findings.md")
            
            # Add feedback form in a nice card layout
            st.markdown('<div class="feedback-card">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-header">Provide Feedback</h3>', unsafe_allow_html=True)
            st.markdown('<p>Please review the security findings and provide your feedback. Your input helps improve the security of the application.</p>', unsafe_allow_html=True)
            
            feedback_tabs = st.tabs(["Feedback Form", "Feedback Guidelines"])
            
            with feedback_tabs[0]:
                comments = st.text_area(
                    "Feedback Comments",
                    placeholder="Provide any suggestions or feedback about the security findings...",
                    key="security_comments",
                    height=150
                )
                
                # Action buttons with better styling
                st.markdown('<div class="button-group">', unsafe_allow_html=True)
                
                # Create three columns for buttons
                action_col1, action_col2, action_col3 = st.columns(3)
                
                with action_col1:
                    # Regenerate button
                    st.markdown('<div class="button-group-item">', unsafe_allow_html=True)
                    regenerate_button = st.button(
                        "🔄 Regenerate Security Report",
                        key="security_regenerate_button",
                        on_click=regenerate_content,
                        args=(SDLCStage.SECURITY,),
                        type="secondary",
                        use_container_width=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with action_col2:
                    # Submit Feedback button
                    st.markdown('<div class="button-group-item">', unsafe_allow_html=True)
                    submit_feedback_button = st.button(
                        "✏️ Submit Feedback",
                        key="security_feedback_button",
                        on_click=submit_feedback,
                        args=(SDLCStage.SECURITY, False, comments),
                        type="primary",
                        use_container_width=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with action_col3:
                    # Approve and Continue button
                    st.markdown('<div class="button-group-item">', unsafe_allow_html=True)
                    approve_button = st.button(
                        "✅ Approve & Continue",
                        key="security_approve_button",
                        on_click=submit_feedback,
                        args=(SDLCStage.SECURITY, True, comments),
                        type="primary",
                        use_container_width=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            with feedback_tabs[1]:
                st.markdown("""
                ### Effective Security Feedback Guidelines
                
                **Focus on specificity:**
                - Mention specific security issues that are missing or incorrectly assessed
                - Provide concrete examples of security risks or vulnerabilities
                    
                **Be constructive:**
                - Suggest security improvements rather than just pointing out issues
                - Prioritize security concerns by their potential impact
                    
                **Consider completeness:**
                - Are all security aspects addressed (authentication, authorization, data validation, etc.)?
                - Are there any security best practices missing?
                - Are the security findings actionable?
                
                **Ensure real-world applicability:**
                - Are the security concerns realistic for your application context?
                - Do the proposed mitigations make sense for your project?
                - Are there any compliance requirements that should be addressed?
                """)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No security findings available yet. Please wait for the security review to complete.")
    else:
        st.warning("No security findings available yet. Please wait for the security review to complete.")

def render_testing_review(session_data):
    """
    Render the testing review section.
    
    Args:
        session_data (dict): Session data.
    """
    st.header("🧪 Testing Review")
    
    if "state" in session_data:
        state = session_data["state"]
        
        # Test Cases
        if "test_cases" in state and state["test_cases"]:
            st.markdown("### Test Cases")
            st.markdown(state["test_cases"])
            
            # Add download button
            create_download_button(state["test_cases"], "test_cases.md")
        
        # Test Results
        if "test_results" in state and state["test_results"]:
            st.markdown("### Test Results")
            st.markdown(state["test_results"])
            
            # Add download button
            create_download_button(state["test_results"], "test_results.md")
        
        # Add feedback form in a nice card layout
        st.markdown('<div class="feedback-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">Provide Feedback</h3>', unsafe_allow_html=True)
        st.markdown('<p>Please review the test cases and results, then provide your feedback. Your input helps ensure comprehensive test coverage.</p>', unsafe_allow_html=True)
        
        feedback_tabs = st.tabs(["Feedback Form", "Feedback Guidelines"])
        
        with feedback_tabs[0]:
            comments = st.text_area(
                "Feedback Comments",
                placeholder="Provide any suggestions or feedback about the test cases and results...",
                key="testing_comments",
                height=150
            )
            
            # Action buttons with better styling
            st.markdown('<div class="button-group">', unsafe_allow_html=True)
            
            # Create three columns for buttons
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                # Regenerate button
                st.markdown('<div class="button-group-item">', unsafe_allow_html=True)
                regenerate_button = st.button(
                    "🔄 Regenerate Tests",
                    key="testing_regenerate_button",
                    on_click=regenerate_content,
                    args=(SDLCStage.TESTING,),
                    type="secondary",
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with action_col2:
                # Submit Feedback button
                st.markdown('<div class="button-group-item">', unsafe_allow_html=True)
                submit_feedback_button = st.button(
                    "✏️ Submit Feedback",
                    key="testing_feedback_button",
                    on_click=submit_feedback,
                    args=(SDLCStage.TESTING, False, comments),
                    type="primary",
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with action_col3:
                # Approve and Continue button
                st.markdown('<div class="button-group-item">', unsafe_allow_html=True)
                approve_button = st.button(
                    "✅ Approve & Complete",
                    key="testing_approve_button",
                    on_click=submit_feedback,
                    args=(SDLCStage.TESTING, True, comments),
                    type="primary",
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        with feedback_tabs[1]:
            st.markdown("""
            ### Effective Testing Feedback Guidelines
            
            **Focus on specificity:**
            - Mention specific test cases that need revision or are missing
            - Provide concrete examples of scenarios that should be tested
                
            **Be constructive:**
            - Suggest testing improvements rather than just pointing out issues
            - Consider both positive and negative test cases
                
            **Consider completeness:**
            - Do the tests cover all functional requirements?
            - Are edge cases and error scenarios tested?
            - Is there a good balance of unit, integration, and end-to-end tests?
            
            **Ensure quality:**
            - Are the test cases clear and easily understandable?
            - Do test cases have clear pass/fail criteria?
            - Are the test results thorough and properly documented?
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("No test cases or results available yet. Please wait for the testing phase to complete.")

def create_github_repository(github_token, github_username, repo_name, state):
    """
    Create a new GitHub repository and push code artifacts.
    
    Args:
        github_token (str): GitHub personal access token.
        github_username (str): GitHub username.
        repo_name (str): Repository name.
        state (dict): The session state with all artifacts.
        
    Returns:
        tuple: (success, message, repo_url)
    """
    try:
        # GitHub API endpoint for creating a new repository
        api_url = "https://api.github.com/user/repos"
        
        # Headers with authentication
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Repository configuration
        repo_data = {
            "name": repo_name,
            "description": "Generated by SDLC Agent",
            "private": False,
            "auto_init": True  # Initialize with a README
        }
        
        repo_url = None
        is_new_repo = True
        
        # Try to create repository
        response = requests.post(api_url, headers=headers, json=repo_data)
        
        if response.status_code == 201:  # Created successfully
            repo_info = response.json()
            repo_url = repo_info["html_url"]
            time.sleep(2)  # Give GitHub a moment to fully initialize the repo
        elif response.status_code == 422 and "already exists" in response.json().get("message", ""):
            # Repository already exists
            get_repo_url = f"https://api.github.com/repos/{github_username}/{repo_name}"
            repo_response = requests.get(get_repo_url, headers=headers)
            
            if repo_response.status_code == 200:
                repo_url = repo_response.json()["html_url"]
                is_new_repo = False
            else:
                return False, f"Repository '{repo_name}' already exists but could not access it.", None
        else:
            try:
                # Get detailed error information
                error_response = response.json()
                error_message = error_response.get("message", "Unknown error")
                error_details = ""
                
                # Try to extract more specific error information
                if "errors" in error_response and len(error_response["errors"]) > 0:
                    error_details = f" Details: {', '.join([err.get('message', str(err)) for err in error_response['errors']])}"
                
                # Log full error for debugging
                print(f"GitHub API Error: {response.status_code} - {error_message}")
                print(f"Full response: {error_response}")
                
                # Return user-friendly error message
                return False, f"Failed to create repository: {error_message}{error_details}", None
            except Exception as e:
                # If we can't parse the JSON response
                return False, f"Failed to create repository: {str(e)}", None
        
        # Now upload the code files
        success, upload_message = upload_files_to_github(github_token, github_username, repo_name, state, is_new_repo)
        
        if success:
            if is_new_repo:
                return True, "Repository created successfully!", repo_url
            else:
                return False, f"Repository already exists. Files have been updated.", repo_url
        else:
            if is_new_repo:
                return True, f"Repository created, but some files could not be uploaded: {upload_message}", repo_url
            else:
                return False, f"Repository exists, but files could not be updated: {upload_message}", repo_url
            
    except Exception as e:
        return False, f"Error working with GitHub repository: {str(e)}", None

def upload_files_to_github(github_token, github_username, repo_name, state, is_new_repo=True):
    """
    Upload files to a GitHub repository.
    
    Args:
        github_token (str): GitHub personal access token.
        github_username (str): GitHub username.
        repo_name (str): Repository name.
        state (dict): The session state with all artifacts.
        is_new_repo (bool): Whether this is a new repository or existing one.
        
    Returns:
        tuple: (success, message)
    """
    # Headers with authentication
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    files_uploaded = 0
    files_failed = 0
    error_messages = []
    
    # Upload code artifacts first - these are the most important
    if "code_artifacts" in state and state["code_artifacts"]:
        for component, code in state["code_artifacts"].items():
            # Check if the component already has a file extension
            filename = component if "." in component else f"{component}.py"
            
            # API endpoint to create or update a file
            url = f"https://api.github.com/repos/{github_username}/{repo_name}/contents/{filename}"
            
            # File content must be base64 encoded
            content = base64.b64encode(code.encode("utf-8")).decode("utf-8")
            
            # Check if file already exists
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                # File exists, need to update it
                sha = response.json()["sha"]
                data = {
                    "message": f"Update {filename}",
                    "content": content,
                    "sha": sha
                }
            else:
                # New file
                data = {
                    "message": f"Add {filename}",
                    "content": content
                }
            
            # Put the file
            response = requests.put(url, headers=headers, json=data)
            
            if response.status_code in (200, 201):
                files_uploaded += 1
            else:
                files_failed += 1
                error_messages.append(f"Failed to upload {filename}: {response.json().get('message', 'Unknown error')}")
    
    # Create a requirements.txt file
    url = f"https://api.github.com/repos/{github_username}/{repo_name}/contents/requirements.txt"
    requirements = """# Generated by SDLC Agent
fastapi
pydantic
langchain
langchain-google-genai
langchain-community
langgraph
uvicorn
python-dotenv
requests
"""
    content = base64.b64encode(requirements.encode("utf-8")).decode("utf-8")
    
    # Check if requirements.txt already exists
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # File exists, need to update it
        sha = response.json()["sha"]
        data = {
            "message": "Update requirements.txt",
            "content": content,
            "sha": sha
        }
    else:
        # New file
        data = {
            "message": "Add requirements.txt",
            "content": content
        }
    
    # Put the file
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code in (200, 201):
        files_uploaded += 1
    else:
        files_failed += 1
        error_messages.append(f"Failed to upload requirements.txt: {response.json().get('message', 'Unknown error')}")
    
    # Create a README.md file if not already initialized
    if "requirements" in state and is_new_repo:
        url = f"https://api.github.com/repos/{github_username}/{repo_name}/contents/README.md"
        readme_content = f"""# {repo_name}

Generated by SDLC Agent

## Project Requirements

{state.get('requirements', 'No requirements specified.')}

## Getting Started

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`
"""
        content = base64.b64encode(readme_content.encode("utf-8")).decode("utf-8")
        
        # Check if README.md already exists
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # File exists, need to update it
            sha = response.json()["sha"]
            data = {
                "message": "Update README.md",
                "content": content,
                "sha": sha
            }
        else:
            # New file
            data = {
                "message": "Add README.md",
                "content": content
            }
        
        # Put the file
        response = requests.put(url, headers=headers, json=data)
        
        if response.status_code in (200, 201):
            files_uploaded += 1
        else:
            files_failed += 1
            error_messages.append(f"Failed to upload README.md: {response.json().get('message', 'Unknown error')}")
    
    if files_failed == 0:
        return True, f"Successfully uploaded {files_uploaded} files."
    else:
        return False, f"Uploaded {files_uploaded} files, but {files_failed} failed: {', '.join(error_messages)}"

def create_download_all_button(state):
    """
    Create a download all button for all artifacts.
    
    Args:
        state (dict): The session state with all artifacts.
    """
    import zipfile
    import io
    
    # Create a zip file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Requirements and analysis
        if "requirements" in state:
            zf.writestr("requirements.md", state["requirements"])
        
        if "requirement_analysis" in state:
            zf.writestr("requirement_analysis.md", state["requirement_analysis"])
        
        # User stories
        if "user_stories" in state:
            zf.writestr("user_stories.md", state["user_stories"])
        
        # Design documents
        if "functional_design" in state:
            zf.writestr("functional_design.md", state["functional_design"])
        
        if "non_functional_design" in state:
            zf.writestr("non_functional_design.md", state["non_functional_design"])
        
        # Code artifacts
        if "code_artifacts" in state and state["code_artifacts"]:
            for component, code in state["code_artifacts"].items():
                zf.writestr(f"{component}.py", code)
        
        # Security findings
        if "security_findings" in state:
            zf.writestr("security_findings.md", state["security_findings"])
        
        # Test cases and results
        if "test_cases" in state:
            zf.writestr("test_cases.md", state["test_cases"])
        
        if "test_results" in state:
            zf.writestr("test_results.md", state["test_results"])
    
    # Reset buffer position
    zip_buffer.seek(0)
    
    # Create download button
    st.download_button(
        label="📦 Download All Artifacts (ZIP)",
        data=zip_buffer,
        file_name="sdlc_artifacts.zip",
        mime="application/zip",
        key="download_all_artifacts"
    )

def render_completion(session_data):
    """
    Render the completion section.
    
    Args:
        session_data (dict): Session data.
    """
    st.header("🎉 SDLC Process Completed")
    
    st.markdown("""
    Congratulations! The SDLC process has been completed successfully.
    All artifacts have been generated and reviewed.
    
    You can download individual artifacts or download everything as a ZIP file.
    """)
    
    # Get state data from the session
    if "state" in session_data:
        state = session_data["state"]
        
        # Add download all button at the top
        create_download_all_button(state)
        
        # Artifact summary section
        st.markdown("### 📌 Project Artifacts Summary")
        st.markdown('<div style="color: #333333; font-weight: 500;">Here\'s a summary of all the generated artifacts for your project.</div>', unsafe_allow_html=True)
        
        if "requirements" in state:
            # Create a summary of the artifacts
            summary_container = st.container()
            
            with summary_container:
                # Create a table to summarize all artifacts
                summary_data = []
                
                if "requirements" in state:
                    summary_data.append(["Requirements", "✅ Complete"])
                
                if "user_stories" in state:
                    summary_data.append(["User Stories", "✅ Complete"])
                
                if "functional_design" in state:
                    summary_data.append(["Functional Design", "✅ Complete"])
                
                if "non_functional_design" in state:
                    summary_data.append(["Non-Functional Design", "✅ Complete"])
                
                if "code_artifacts" in state and state["code_artifacts"]:
                    summary_data.append(["Code Artifacts", f"✅ {len(state['code_artifacts'])} files generated"])
                
                if "security_findings" in state:
                    summary_data.append(["Security Review", "✅ Complete"])
                
                if "test_cases" in state:
                    summary_data.append(["Test Cases", "✅ Complete"])
                
                if "test_results" in state:
                    summary_data.append(["Test Results", "✅ Complete"])
                
                # Display the summary table with custom styling for dark text
                table_html = '<div style="color: #333333;">'
                table_html += '<table style="width:100%; border-collapse: collapse;">'
                table_html += '<thead><tr><th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Artifact</th><th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Status</th></tr></thead>'
                table_html += '<tbody>'
                
                for i, row in enumerate(summary_data):
                    bg_color = "#f2f2f2" if i % 2 == 0 else "#ffffff"
                    table_html += f'<tr style="background-color: {bg_color};">'
                    table_html += f'<td style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd; color: #333333;">{row[0]}</td>'
                    table_html += f'<td style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd; color: #333333;">{row[1]}</td>'
                    table_html += '</tr>'
                
                table_html += '</tbody></table></div>'
                st.markdown(table_html, unsafe_allow_html=True)
        
        # Multi-agent conversation capabilities
        st.markdown("### 🤖 Multi-Agent Conversation")
        st.markdown('<div style="color: #333333; font-weight: 500;">Use multiple specialized AI agents to analyze and refine your project requirements.</div>', unsafe_allow_html=True)
        
        if st.button("Start Multi-Agent Analysis", key="multi_agent_button"):
            st.info("Multi-agent conversation feature would be available here. This would enable deeper requirements analysis with different specialized AI personas.")
        
        # Export to GitHub section
        st.markdown("### 🚀 Export to GitHub")
        st.markdown('<div style="color: #333333; font-weight: 500;">Push your generated code artifacts to a new GitHub repository.</div>', unsafe_allow_html=True)
        
        # GitHub integration section
        st.markdown('<div style="color: #333333; font-weight: 500; background-color: #FFECB3; padding: 10px; border-radius: 5px; border-left: 5px solid #F57F17;">To export your project to GitHub, you need to provide a GitHub Personal Access Token.</div>', unsafe_allow_html=True)
        
        # Initialize the github variables in session state if they don't exist
        if "github_token" not in st.session_state:
            st.session_state.github_token = ""
        
        if "github_username" not in st.session_state:
            st.session_state.github_username = ""    
            
        # Use temp_repo_name instead of github_repo_name
        if "temp_repo_name" not in st.session_state:
            st.session_state.temp_repo_name = "sdlc-agent-project"
        
        # Get token from input
        github_token = st.text_input(
            "GitHub Personal Access Token",
            type="password",
            value=st.session_state.github_token,
            help="Create a token at https://github.com/settings/tokens with 'repo' scope",
            key="github_token_input"
        )
        
        # Get GitHub username
        github_username = st.text_input(
            "GitHub Username",
            value=st.session_state.github_username,
            help="Your GitHub username (required for repository creation)",
            key="github_username_input"
        )
        
        # Get repo name from input - using the existing temp_repo_name in session state
        # Important: Do not store the input value directly back into session state
        # as it will cause a StreamlitAPIException
        repo_name = st.text_input(
            "Repository Name",
            value=st.session_state.temp_repo_name,
            key="github_repo_name_input"
        )
        
        # Use callbacks to update session state securely
        # This approach avoids trying to modify session_state variables after widgets use them
        if "save_github_settings" not in st.session_state:
            st.session_state.save_github_settings = False
            
        def save_github_settings_callback():
            # This callback will run before the widget renders
            st.session_state.save_github_settings = True
            
        # Save button
        if st.button("Save GitHub Settings", key="save_github_settings_button", on_click=save_github_settings_callback):
            pass  # The actual logic happens after button press via the callback

        # Process the save after button press
        if st.session_state.save_github_settings:
            # Update temporary values
            st.session_state.github_token = github_token
            st.session_state.github_username = github_username
            st.session_state.temp_repo_name = repo_name  # Store in a temporary variable
            st.success("GitHub settings saved!")
            # Reset flag
            st.session_state.save_github_settings = False
        
        # Only show export button if token and username are provided
        if st.session_state.github_token and st.session_state.github_username:
            
            if st.button("Export to GitHub", key="github_export_button"):
                with st.spinner("Creating GitHub repository and pushing code..."):
                    # Use the actual GitHub API to create a repository
                    github_token = st.session_state.github_token
                    github_username = st.session_state.github_username
                    repo_name = st.session_state.temp_repo_name
                    
                    # Call our repository creation function
                    success, message, repo_url = create_github_repository(
                        github_token, 
                        github_username, 
                        repo_name, 
                        state
                    )
                    
                    if success:
                        st.markdown(f'<div style="color: #333333; font-weight: 500; background-color: #C8E6C9; padding: 10px; border-radius: 5px; border-left: 5px solid #388E3C;">Successfully created repository: {message}</div>', unsafe_allow_html=True)
                        st.markdown(f"[View Repository on GitHub]({repo_url})")
                    else:
                        if repo_url:  # Repository exists but we got its URL
                            st.markdown(f'<div style="color: #333333; font-weight: 500; background-color: #FFECB3; padding: 10px; border-radius: 5px; border-left: 5px solid #F57F17;">{message}</div>', unsafe_allow_html=True)
                            st.markdown(f"[View Existing Repository on GitHub]({repo_url})")
                        else:  # Failed to create
                            st.markdown(f'<div style="color: #333333; font-weight: 500; background-color: #FFCDD2; padding: 10px; border-radius: 5px; border-left: 5px solid #D32F2F;">{message}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### Individual Artifacts")
        
        # Requirements and analysis
        if "requirements" in state:
            create_download_button(state["requirements"], "requirements.md")
        
        if "requirement_analysis" in state:
            create_download_button(state["requirement_analysis"], "requirement_analysis.md")
        
        # User stories
        if "user_stories" in state:
            create_download_button(state["user_stories"], "user_stories.md")
        
        # Design documents
        if "functional_design" in state:
            create_download_button(state["functional_design"], "functional_design.md")
        
        if "non_functional_design" in state:
            create_download_button(state["non_functional_design"], "non_functional_design.md")
        
        # Code artifacts
        if "code_artifacts" in state and state["code_artifacts"]:
            for component, code in state["code_artifacts"].items():
                # Check if the component name already has a file extension to avoid double extensions
                if "." in component:
                    create_download_button(code, component)
                else:
                    create_download_button(code, f"{component}.py")
        
        # Security findings
        if "security_findings" in state:
            create_download_button(state["security_findings"], "security_findings.md")
        
        # Test cases and results
        if "test_cases" in state:
            create_download_button(state["test_cases"], "test_cases.md")
        
        if "test_results" in state:
            create_download_button(state["test_results"], "test_results.md")
    
    # Use a unique key for the button in completion section
    st.button("Start New Project", on_click=reset_session, key="complete_new_project_button")

def reset_session():
    """Reset the session state to start a new project."""
    st.session_state.session_id = None
    st.session_state.current_stage = None
    st.session_state.feedback_provided = False
    st.session_state.processing = False
    # Instead of calling st.rerun() here, we'll set a flag to trigger rerun in the main flow
    st.session_state.trigger_rerun = True

def main():
    """Main application function."""
    # Create sidebar
    with st.sidebar:
        st.header("Session Information")
        
        if st.session_state.session_id:
            session_data = get_session_data()
            if session_data:
                st.success(f"Active Session: {st.session_state.session_id}")
                st.info(f"Current Stage: {st.session_state.current_stage}")
                st.info(f"Created: {session_data.get('created_at', 'Unknown')}")
                st.info(f"Last Updated: {session_data.get('last_updated', 'Unknown')}")
                
                # Add refresh button
                if st.button("Refresh Status", key="sidebar_refresh_button"):
                    st.session_state.trigger_rerun = True
                
                # Add reset button
                if st.button("Start New Project", key="sidebar_new_project_button"):
                    reset_session()
            else:
                st.warning("No active session")
        else:
            st.warning("No active session")
    
    # Main content
    if st.session_state.trigger_rerun:
        st.session_state.trigger_rerun = False
        st.rerun()
    
    # Display content based on current stage
    if not st.session_state.session_id:
        # No active session, show requirements input
        render_requirements_input()
    else:
        # Active session, show current stage
        session_data = get_session_data()
        
        if not session_data:
            st.error("Session data not found")
            return
        
        # Display content based on current stage
        current_stage = st.session_state.current_stage
        
        if current_stage == SDLCStage.USER_STORIES:
            render_user_stories_review(session_data)
        elif current_stage == SDLCStage.DESIGN:
            render_design_review(session_data)
        elif current_stage == SDLCStage.CODE:
            render_code_review(session_data)
        elif current_stage == SDLCStage.SECURITY:
            render_security_review(session_data)
        elif current_stage == SDLCStage.TESTING:
            render_testing_review(session_data)
        elif current_stage == SDLCStage.COMPLETE:
            render_completion(session_data)
            
            # Auto-refresh if processing
            if st.session_state.processing:
                time.sleep(5)
                st.session_state.trigger_rerun = True

if __name__ == "__main__":
    main()