"""
LLM-based content generation utilities using Groq API.
"""
import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import traceback

# Initialize Groq client with API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_llm(temperature=0.7):
    """
    Get a Groq LLM instance.
    
    Args:
        temperature (float): The temperature for generation.
        
    Returns:
        ChatGroq: The LLM instance.
    """
    # Initialize Groq client for code generation
    return ChatGroq(
        model="qwen-2.5-32b",  # Using Llama 3 model
        api_key=GROQ_API_KEY,
        temperature=temperature,
    )

def generate_content(prompt_template, input_variables):
    """
    Generate content using Groq LLM with improved error handling and retry logic.
    
    Args:
        prompt_template (str): The prompt template.
        input_variables (dict): The input variables for the prompt.
        
    Returns:
        str: The generated content.
    """
    # Maximum retry attempts
    max_retries = 3
    retry_count = 0
    backoff_time = 2  # seconds
    
    while retry_count < max_retries:
        try:
            llm = get_llm()
            
            # Create prompt
            prompt = PromptTemplate(
                input_variables=list(input_variables.keys()),
                template=prompt_template
            )
            
            # Format prompt
            formatted_prompt = prompt.format(**input_variables)
            
            # Generate content
            response = llm.invoke(formatted_prompt)
            
            return response.content
        except Exception as e:
            error_msg = str(e)
            retry_count += 1
            error_trace = traceback.format_exc()
            
            print(f"Error generating content (attempt {retry_count}/{max_retries}): {error_msg}\n{error_trace}")
            
            # If this is a service unavailable error, retry after backoff
            if "503" in error_msg or "Service Unavailable" in error_msg:
                if retry_count < max_retries:
                    import time
                    wait_time = backoff_time * retry_count
                    print(f"Service unavailable, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
            
            # If we've reached max retries or it's not a 503 error
            if retry_count >= max_retries:
                return f"""# Service Currently Unavailable

The Groq API service is experiencing issues after {max_retries} retry attempts.

This might be a temporary issue with the service. Please try the following:
1. Wait a few moments and try again
2. Check your Groq API key is valid and properly configured
3. If the problem persists, consider switching to an alternative model or service

Error details: {error_msg}
"""
            elif retry_count < max_retries and not ("503" in error_msg or "Service Unavailable" in error_msg):
                # For non-503 errors, we'll break out of the retry loop
                break
    
    # This will be reached for non-503 errors or if all retries fail
    return f"""# Error Generating Content

An error occurred while generating content. 

Error details: {error_msg}

Please try again later.
"""

def generate_user_stories(requirements):
    """
    Generate user stories based on requirements.
    
    Args:
        requirements (str): The user requirements.
        
    Returns:
        str: The generated user stories.
    """
    prompt_template = """
You are an expert in Agile development and user story creation. Given the following requirements, create a comprehensive set of user stories.

Requirements:
{requirements}

Please create well-formed user stories using the format "As a [role], I want [feature/action], so that [benefit]".
Organize the user stories into categories based on the functionality they describe.
Each user story should be specific, measurable, achievable, relevant, and time-bound (SMART).
Include a mixture of core functionality, secondary features, and admin/maintenance features if appropriate.

For each user story, include:
1. A unique identifier (e.g., US-001)
2. A clear role (who wants the feature)
3. A specific action or feature
4. The benefit or value to the user
5. Acceptance criteria (2-3 bullet points per story)

Organize your response using Markdown formatting with headers for categories and sections.
"""
    
    return generate_content(prompt_template, {"requirements": requirements})

def generate_functional_design(requirements, user_stories):
    """
    Generate functional design based on requirements and user stories.
    
    Args:
        requirements (str): The user requirements.
        user_stories (str): The user stories.
        
    Returns:
        str: The generated functional design.
    """
    prompt_template = """
You are an expert software architect. Create a detailed functional design document based on the following requirements and user stories.

Requirements:
{requirements}

User Stories:
{user_stories}

Create a comprehensive functional design document that includes:

1. Introduction
   - Purpose and scope
   - Target audience
   - System overview

2. System Architecture
   - High-level architecture diagram (described in text)
   - Component breakdown
   - Data flow

3. Functional Components
   - Detailed description of each component
   - Interfaces and dependencies
   - Business logic

4. User Interface Design
   - Description of key screens/pages
   - User interactions
   - Navigation flow

5. Data Model
   - Entity relationship descriptions
   - Data structures
   - Data validation rules

6. API Specifications
   - Endpoints
   - Request/response formats
   - Authentication and authorization

7. Integration Points
   - External systems
   - Third-party services
   - Integration protocols

Format your response using Markdown with appropriate headers, bullet points, and code blocks where needed.
"""
    
    return generate_content(prompt_template, {
        "requirements": requirements,
        "user_stories": user_stories
    })

def generate_non_functional_design(requirements, user_stories):
    """
    Generate non-functional design based on requirements and user stories.
    
    Args:
        requirements (str): The user requirements.
        user_stories (str): The user stories.
        
    Returns:
        str: The generated non-functional design.
    """
    prompt_template = """
You are an expert software architect. Create a detailed non-functional design document based on the following requirements and user stories.

Requirements:
{requirements}

User Stories:
{user_stories}

Create a comprehensive non-functional design document that includes:

1. Performance Requirements
   - Response time expectations
   - Throughput requirements
   - Scalability considerations

2. Security Requirements
   - Authentication and authorization
   - Data protection
   - Compliance requirements

3. Reliability and Availability
   - Uptime requirements
   - Fault tolerance
   - Disaster recovery

4. Maintainability
   - Code organization
   - Documentation requirements
   - Testing strategy

5. Usability
   - Accessibility requirements
   - User experience guidelines
   - Internationalization/localization

6. Deployment Considerations
   - Environment requirements
   - Deployment strategy
   - Monitoring and logging

7. Constraints and Limitations
   - Technical constraints
   - Business constraints
   - Assumptions

Format your response using Markdown with appropriate headers, bullet points, and code blocks where needed.
"""
    
    return generate_content(prompt_template, {
        "requirements": requirements,
        "user_stories": user_stories
    })

def generate_code_artifacts(requirements, functional_design, non_functional_design):
    """
    Generate code artifacts based on design documents.
    
    Args:
        requirements (str): The user requirements.
        functional_design (str): The functional design document.
        non_functional_design (str): The non-functional design document.
        
    Returns:
        dict: The generated code artifacts.
    """
    prompt_template = """
You are an expert software developer. Based on the requirements and design documents, generate the main code artifacts for this project.

Requirements:
{requirements}

Functional Design:
{functional_design}

Non-Functional Design:
{non_functional_design}

Please generate code for the following components:
1. The main application file
2. Core business logic module
3. API endpoints
4. Data model definitions

For each file, include:
- Appropriate imports
- Class/function definitions
- Docstrings and comments
- Error handling
- Example usage (where appropriate)

Use modern best practices and patterns appropriate for the type of application.
Format your response as a JSON object with file names as keys and code as values.
Structure the response as:
{{
  "main.py": "# Code content here",
  "models.py": "# Code content here",
  "api.py": "# Code content here",
  "utils.py": "# Code content here"
}}

The code should be complete, functional and ready to execute.
"""
    
    # Generate code with lower temperature for more predictable output
    llm = get_llm(temperature=0.2)
    
    prompt = PromptTemplate(
        input_variables=["requirements", "functional_design", "non_functional_design"],
        template=prompt_template
    )
    
    # Format prompt
    formatted_prompt = prompt.format(
        requirements=requirements, 
        functional_design=functional_design, 
        non_functional_design=non_functional_design
    )
    
    # Generate content
    try:
        response = llm.invoke(formatted_prompt)
        content = response.content
        
        # Extract JSON content if it's embedded in a code block
        import re
        import json
        
        # First try to extract JSON from code blocks
        if "```json" in content or "```" in content:
            # Look for ```json blocks first
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            # Then try any ``` code blocks
            else:
                json_match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
        
        # Clean up the content - remove any trailing commas in JSON which can cause parse errors
        content = re.sub(r',\s*}', '}', content)
        content = re.sub(r',\s*]', ']', content)
        
        # Try to parse JSON
        try:
            code_artifacts = json.loads(content)
        except json.JSONDecodeError:
            # If parsing fails, try to create a structured dictionary from the text
            # This is a fallback for when the LLM doesn't return proper JSON
            print(f"JSON parsing failed, attempting to structure response manually")
            artifacts = {}
            
            # Look for patterns like "filename.py": "content"
            file_matches = re.finditer(r'["\']([\w\d_\-\.]+)["\']:\s*["\']', content)
            for match in file_matches:
                filename = match.group(1)
                start_idx = match.end()
                
                # Find the closing quote, accounting for escaped quotes
                in_escape = False
                quote_char = content[start_idx-1]  # Get the quote character used
                end_idx = start_idx
                
                for i in range(start_idx, len(content)):
                    char = content[i]
                    if char == '\\' and not in_escape:
                        in_escape = True
                    elif char == quote_char and not in_escape:
                        end_idx = i
                        break
                    elif in_escape:
                        in_escape = False
                
                if end_idx > start_idx:
                    file_content = content[start_idx:end_idx]
                    artifacts[filename] = file_content
            
            # If we found files, use them
            if artifacts:
                code_artifacts = artifacts
            else:
                # Last resort - just return the raw content as a single file
                code_artifacts = {"main.py": content}
        
        return code_artifacts
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error generating code artifacts: {str(e)}\n{error_trace}")
        return {
            "error.py": f"# Error generating code artifacts\n# {str(e)}"
        }

def generate_security_findings(code_artifacts):
    """
    Generate security findings for the code artifacts.
    
    Args:
        code_artifacts (dict): The code artifacts.
        
    Returns:
        str: The generated security findings.
    """
    # Combine all code into a single string for analysis
    code_combined = "\n\n".join([f"### {filename}\n```python\n{code}\n```" for filename, code in code_artifacts.items()])
    
    prompt_template = """
You are an expert security auditor. Conduct a security review of the following code artifacts and provide your findings.

Code Artifacts:
{code_artifacts}

Perform a comprehensive security review and provide your findings in the following format:

# Security Review Findings

## Overview
[Brief summary of the review and overall assessment]

## Findings Summary
[Summary of the number of issues found by severity]

## High Severity Issues
[List of high severity issues with descriptions and remediation steps]

## Medium Severity Issues
[List of medium severity issues with descriptions and remediation steps]

## Low Severity Issues
[List of low severity issues with descriptions and remediation steps]

## Recommendations
[General recommendations for improving security]

Use Markdown formatting for your response.
"""
    
    return generate_content(prompt_template, {"code_artifacts": code_combined})

def generate_test_cases(requirements, user_stories, code_artifacts):
    """
    Generate test cases based on requirements, user stories, and code artifacts.
    
    Args:
        requirements (str): The user requirements.
        user_stories (str): The user stories.
        code_artifacts (dict): The code artifacts.
        
    Returns:
        str: The generated test cases.
    """
    # Combine all code into a single string for analysis
    code_combined = "\n\n".join([f"### {filename}\n```python\n{code}\n```" for filename, code in code_artifacts.items()])
    
    prompt_template = """
You are an expert in software testing. Create comprehensive test cases for the application based on the following requirements, user stories, and code artifacts.

Requirements:
{requirements}

User Stories:
{user_stories}

Code Artifacts:
{code_artifacts}

Create detailed test cases covering the following categories:
1. Functional Tests
2. Integration Tests
3. Edge Case Tests
4. Performance Tests
5. Security Tests

For each test case, include:
- Test ID and title
- Test description
- Preconditions
- Test steps
- Expected results
- Postconditions (if applicable)

Format your response using Markdown with appropriate headers and sections.
"""
    
    return generate_content(prompt_template, {
        "requirements": requirements,
        "user_stories": user_stories,
        "code_artifacts": code_combined
    })

def generate_test_results(test_cases):
    """
    Generate test results based on test cases.
    
    Args:
        test_cases (str): The test cases.
        
    Returns:
        str: The generated test results.
    """
    prompt_template = """
You are an expert in software testing. Given the following test cases, simulate test execution and generate test results.

Test Cases:
{test_cases}

Generate comprehensive test results including:
1. Overall summary (tests passed, failed, skipped)
2. Detailed results for each test case
3. Failure details for any failed tests
4. Performance metrics where applicable
5. Recommendations for fixing failed tests and improving test coverage

Format your response using Markdown with appropriate headers, bullet points, and formatting.
"""
    
    return generate_content(prompt_template, {"test_cases": test_cases})

def process_feedback(original_content, feedback, content_type):
    """
    Process feedback and update content accordingly.
    
    Args:
        original_content (str): The original content.
        feedback (str): The feedback to process.
        content_type (str): The type of content (e.g., "user_stories", "design").
        
    Returns:
        str: The updated content.
    """
    prompt_template = """
You are an expert in software development. A user has provided feedback on the following content.
Your task is to update the content based on this feedback.

Original Content:
{original_content}

User Feedback:
{feedback}

Content Type: {content_type}

Please provide an updated version of the content that incorporates the feedback.
Maintain the same format and structure as the original content where possible,
but make substantive changes to address the user's feedback.

Make sure to highlight what changes you've made by adding a section at the end titled
"## Changes Made Based on Feedback" that concisely lists the modifications.
"""
    
    return generate_content(prompt_template, {
        "original_content": original_content,
        "feedback": feedback,
        "content_type": content_type
    })