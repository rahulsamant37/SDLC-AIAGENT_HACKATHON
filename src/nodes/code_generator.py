"""
Code generator node for SDLC Agent.
"""
from typing import Dict, Any, List, Optional, Tuple
import json
from datetime import datetime
import re

from src.LLMS.google_llm import get_llm

def get_supported_languages() -> List[str]:
    """
    Get list of supported programming languages.
    
    Returns:
        List[str]: List of supported languages.
    """
    return [
        "Python",
        "JavaScript",
        "TypeScript",
        "Java",
        "Go",
        "Rust",
        "C#",
        "PHP"
    ]

def create_code_generation_prompt(requirements: str, functional_design: str, 
                               non_functional_design: str, file_name: str,
                               language: str) -> str:
    """
    Create a prompt for code generation.
    
    Args:
        requirements (str): The user requirements.
        functional_design (str): The functional design document.
        non_functional_design (str): The non-functional design document.
        file_name (str): The name of the file to generate.
        language (str): The programming language to use.
        
    Returns:
        str: The prompt for code generation.
    """
    return f"""
    You are an expert software developer. Generate production-quality code for the following file
    based on the provided requirements and design documents.
    
    Requirements:
    {requirements}
    
    Functional Design:
    {functional_design}
    
    Non-Functional Design:
    {non_functional_design}
    
    File to Generate: {file_name}
    Programming Language: {language}
    
    Generate complete, well-structured, and fully functional code for this file.
    Include comprehensive comments, proper error handling, and follow best practices for the language.
    The code should be ready for production use.
    
    Return ONLY the code without any additional explanations or markdown formatting.
    """

def extract_required_files(functional_design: str, non_functional_design: str) -> List[Dict[str, str]]:
    """
    Extract required files from design documents.
    
    Args:
        functional_design (str): The functional design document.
        non_functional_design (str): The non-functional design document.
        
    Returns:
        List[Dict[str, str]]: List of required files with their details.
    """
    # Create a prompt to extract required files
    prompt = f"""
    Analyze the following design documents and extract a list of all files that need to be created.
    
    Functional Design:
    {functional_design}
    
    Non-Functional Design:
    {non_functional_design}
    
    Please provide a JSON array of file objects with the following structure:
    [
        {{
            "file_name": "example.py",
            "description": "This file contains the main application logic",
            "language": "Python",
            "component": "Backend",
            "importance": "High"
        }},
        ...
    ]
    
    Include ALL necessary files for a complete implementation, including:
    - Application code
    - Configuration files
    - Database scripts
    - Frontend files
    - Test files
    - Documentation
    
    Provide only the JSON array, no other text.
    """
    
    # Get file list
    files_str = generate_with_langchain(prompt, temperature=0.2)
    
    # Try to parse JSON, use default if parsing fails
    try:
        # Extract JSON if it's wrapped in markdown code blocks
        if "```json" in files_str:
            json_start = files_str.find("```json") + 7
            json_end = files_str.find("```", json_start)
            files_str = files_str[json_start:json_end].strip()
        elif "```" in files_str:
            json_start = files_str.find("```") + 3
            json_end = files_str.find("```", json_start)
            files_str = files_str[json_start:json_end].strip()
        
        required_files = json.loads(files_str)
    except (json.JSONDecodeError, ValueError):
        # Default files if parsing fails
        required_files = [
            {
                "file_name": "app.py",
                "description": "Main application entry point",
                "language": "Python",
                "component": "Backend",
                "importance": "High"
            },
            {
                "file_name": "requirements.txt",
                "description": "Python dependencies",
                "language": "Text",
                "component": "Configuration",
                "importance": "Medium"
            },
            {
                "file_name": "README.md",
                "description": "Project documentation",
                "language": "Markdown",
                "component": "Documentation",
                "importance": "Medium"
            },
            {
                "file_name": "config.py",
                "description": "Application configuration",
                "language": "Python",
                "component": "Backend",
                "importance": "Medium"
            },
            {
                "file_name": "models.py",
                "description": "Data models",
                "language": "Python",
                "component": "Backend",
                "importance": "High"
            },
            {
                "file_name": "utils.py",
                "description": "Utility functions",
                "language": "Python",
                "component": "Backend",
                "importance": "Medium"
            },
            {
                "file_name": "tests.py",
                "description": "Test cases",
                "language": "Python", 
                "component": "Testing",
                "importance": "Medium"
            },
            {
                "file_name": "schema.sql",
                "description": "Database schema",
                "language": "SQL",
                "component": "Database",
                "importance": "High"
            }
        ]
    
    return required_files

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

def clean_code(code: str, language: str) -> str:
    """
    Clean generated code to remove any non-code elements.
    
    Args:
        code (str): The generated code.
        language (str): The programming language.
        
    Returns:
        str: The cleaned code.
    """
    # Remove markdown code blocks if present
    if "```" in code:
        # Extract language identifier if present
        language_pattern = r"```([a-zA-Z0-9#+]*)\n"
        match = re.search(language_pattern, code)
        if match:
            language_identifier = match.group(1)
            # Remove the opening code block with language
            code = re.sub(r"```" + language_identifier + r"\n", "", code, 1)
        else:
            # Remove the opening code block without language
            code = re.sub(r"```\n", "", code, 1)
        
        # Remove the closing code block
        code = re.sub(r"\n```", "", code)
    
    return code.strip()

def code_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate code artifacts and update state.
    
    Args:
        state (Dict[str, Any]): The current state.
        
    Returns:
        Dict[str, Any]: The updated state.
    """
    # Extract design documents from state
    requirements = state.get("requirements", "")
    functional_design = state.get("functional_design", "")
    non_functional_design = state.get("non_functional_design", "")
    
    if not functional_design or not non_functional_design:
        return {
            "code_artifacts": {},
            "current_stage": "DESIGN",  # Go back to design stage
            "code_generation_error": "Missing design documents."
        }
    
    # Extract required files
    required_files = extract_required_files(functional_design, non_functional_design)
    
    # Determine primary language
    languages = {}
    for file in required_files:
        lang = file.get("language", "")
        if lang in get_supported_languages():
            languages[lang] = languages.get(lang, 0) + 1
    
    primary_language = max(languages.items(), key=lambda x: x[1])[0] if languages else "Python"
    
    # Generate high-importance files first (limit to 5 to avoid hitting token limits)
    high_importance_files = [f for f in required_files if f.get("importance", "") == "High"]
    selected_files = high_importance_files[:5]
    
    # Generate code for each file
    code_artifacts = {}
    for file in selected_files:
        file_name = file.get("file_name", "")
        language = file.get("language", primary_language)
        
        # Skip non-code files
        if language.lower() in ["text", "markdown"]:
            continue
        
        # Generate code
        prompt = create_code_generation_prompt(
            requirements, 
            functional_design, 
            non_functional_design,
            file_name,
            language
        )
        
        code = generate_with_langchain(prompt, temperature=0.3)
        cleaned_code = clean_code(code, language)
        
        code_artifacts[file_name] = cleaned_code
    
    # Generate README.md
    readme_prompt = f"""
    Create a comprehensive README.md file for the project described in the following requirements and design documents.
    
    Requirements:
    {requirements}
    
    Functional Design:
    {functional_design}
    
    Non-Functional Design:
    {non_functional_design}
    
    The README should include:
    1. Project title and overview
    2. Installation instructions
    3. Usage examples
    4. Project structure
    5. Technologies used
    6. API documentation (if applicable)
    7. Contributing guidelines
    8. License information
    
    Format the README using proper Markdown syntax.
    """
    
    readme = generate_with_langchain(readme_prompt, temperature=0.7)
    code_artifacts["README.md"] = clean_code(readme, "Markdown")
    
    # Generate code metadata
    code_metadata = {
        "generated_files": list(code_artifacts.keys()),
        "primary_language": primary_language,
        "file_count": len(code_artifacts),
        "total_code_lines": sum(len(code.split("\n")) for code in code_artifacts.values()),
        "code_generation_timestamp": datetime.now().isoformat()
    }
    
    # Update state with code artifacts and metadata
    return {
        "code_artifacts": code_artifacts,
        "code_metadata": code_metadata,
        "current_stage": "SECURITY",
        "last_updated": datetime.now().isoformat()
    }