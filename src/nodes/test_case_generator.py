"""
Node for generating and executing test cases.
"""
from typing import Any, Dict
from langchain.chains import LLMChain
from src.state.sdlc_state import SDLCStage
from src.vectorstore.vectorstore import add_to_vectorstore

def generate_test_cases(state: Dict[str, Any], llm: Any, vectorstore: Any) -> Dict[str, Any]:
    """
    Generate test cases for the implemented code.
    
    Args:
        state (Dict[str, Any]): The current state.
        llm (Any): The language model to use.
        vectorstore (Any): The vector store for document storage.
        
    Returns:
        Dict[str, Any]: The updated state.
    """
    # Check if code artifacts are present
    if not state.get("code_artifacts"):
        return {
            **state,
            "error": "Code not generated",
            "execution_order": state.get("execution_order", []) + ["generate_test_cases"]
        }
    
    # Generate test cases for each component
    test_cases = ""
    
    for component, code in state["code_artifacts"].items():
        template = """
        Generate comprehensive test cases for the following {component} component code:
        
        {code}
        
        Include the following types of tests where applicable:
        1. Unit tests
        2. Integration tests
        3. Functional tests
        4. Edge case tests
        
        For each test case, provide:
        - Test ID
        - Description
        - Preconditions
        - Test steps
        - Expected results
        - Actual code implementation of the test (in the appropriate testing framework)
        """
        
        prompt = {
            "input_variables": ["component", "code"],
            "template": template
        }
        
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Execute the chain
        component_test_cases = chain.run(
            component=component,
            code=code
        )
        
        test_cases += f"# Test Cases for {component}\n\n{component_test_cases}\n\n"
    
    # Add to vector store for future reference
    add_to_vectorstore(
        vectorstore,
        test_cases,
        metadata={
            "type": "test_cases",
            "stage": SDLCStage.TESTING.name
        }
    )
    
    # Update the state
    return {
        **state,
        "test_cases": test_cases,
        "current_stage": SDLCStage.TESTING.name,
        "execution_order": state.get("execution_order", []) + ["generate_test_cases"]
    }

def process_test_feedback(state: Dict[str, Any], llm: Any, vectorstore: Any) -> Dict[str, Any]:
    """
    Process user feedback on test cases.
    
    Args:
        state (Dict[str, Any]): The current state.
        llm (Any): The language model to use.
        vectorstore (Any): The vector store for document storage.
        
    Returns:
        Dict[str, Any]: The updated state.
    """
    # Check if test cases and feedback are present
    if not state.get("test_cases"):
        return {
            **state,
            "error": "Test cases not generated",
            "execution_order": state.get("execution_order", []) + ["process_test_feedback"]
        }
    
    if not state.get("testing_feedback"):
        return {
            **state,
            "error": "No feedback provided for test cases",
            "execution_order": state.get("execution_order", []) + ["process_test_feedback"]
        }
    
    feedback = state["testing_feedback"]
    
    # If feedback is approved, move to the next stage
    if feedback.get("approved", False):
        return {
            **state,
            "current_stage": SDLCStage.COMPLETE.name,
            "execution_order": state.get("execution_order", []) + ["process_test_feedback"]
        }
    
    # If feedback is not approved, update the test cases
    template = """
    You previously generated the following test cases:
    
    {test_cases}
    
    However, there was feedback that needs to be incorporated:
    
    {feedback}
    
    Please update the test cases, incorporating the feedback. Ensure your test cases are:
    1. Comprehensive
    2. Well-structured
    3. Address all the feedback points
    
    Provide the complete updated test cases.
    """
    
    prompt = {
        "input_variables": ["test_cases", "feedback"],
        "template": template
    }
    
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Execute the chain
    updated_test_cases = chain.run(
        test_cases=state["test_cases"],
        feedback=feedback.get("comments", "")
    )
    
    # Add to vector store for future reference
    add_to_vectorstore(
        vectorstore,
        updated_test_cases,
        metadata={
            "type": "test_cases_revised",
            "stage": SDLCStage.TESTING.name,
            "feedback": feedback.get("comments", "")
        }
    )
    
    # Update the state
    return {
        **state,
        "test_cases": updated_test_cases,
        "execution_order": state.get("execution_order", []) + ["process_test_feedback"]
    }

def execute_qa_testing(state: Dict[str, Any], llm: Any, vectorstore: Any) -> Dict[str, Any]:
    """
    Simulate the execution of QA testing.
    
    Args:
        state (Dict[str, Any]): The current state.
        llm (Any): The language model to use.
        vectorstore (Any): The vector store for document storage.
        
    Returns:
        Dict[str, Any]: The updated state.
    """
    # Check if test cases are present
    if not state.get("test_cases"):
        return {
            **state,
            "error": "Test cases not generated",
            "execution_order": state.get("execution_order", []) + ["execute_qa_testing"]
        }
    
    # Simulate test execution by analyzing the test cases and code
    template = """
    Simulate the execution of the following test cases against the code:
    
    Test Cases:
    {test_cases}
    
    Code:
    {code}
    
    Provide a detailed test execution report including:
    1. Test case ID
    2. Status (Passed/Failed)
    3. Execution details
    4. Issues found (if any)
    5. Recommendations for fixing failed tests
    
    Format the report in a clear, readable structure.
    """
    
    # Combine all code artifacts
    combined_code = ""
    for component, code in state["code_artifacts"].items():
        combined_code += f"# Component: {component}\n\n{code}\n\n"
    
    prompt = {
        "input_variables": ["test_cases", "code"],
        "template": template
    }
    
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Execute the chain
    test_results = chain.run(
        test_cases=state["test_cases"],
        code=combined_code
    )
    
    # Add to vector store for future reference
    add_to_vectorstore(
        vectorstore,
        test_results,
        metadata={
            "type": "test_results",
            "stage": SDLCStage.TESTING.name
        }
    )
    
    # Update the state
    return {
        **state,
        "test_results": test_results,
        "execution_order": state.get("execution_order", []) + ["execute_qa_testing"]
    }
