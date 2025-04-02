"""
Multi-modal node processor for handling text and images in design reviews.
"""
import base64
import os
from typing import Dict, List, Any, Optional
import io
from datetime import datetime
from PIL import Image

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from src.LLMS.groq_llm import get_llm

def extract_diagrams_from_design(design_document: str) -> List[str]:
    """
    Extract diagram descriptions from design document and convert to image.
    This is a mock implementation - in a real scenario you would:
    1. Parse the design document for diagram descriptions
    2. Use a text-to-diagram tool to generate actual diagrams
    3. Return these as base64 encoded images
    
    Args:
        design_document (str): The design document text
        
    Returns:
        List[str]: List of base64 encoded diagram images
    """
    # Create a diagram folder if it doesn't exist
    diagrams_dir = os.path.join(os.path.dirname(__file__), "..", "..", "diagrams")
    os.makedirs(diagrams_dir, exist_ok=True)
    
    # Extract diagram sections - in a real implementation this would be more sophisticated
    diagram_sections = []
    lines = design_document.split("\n")
    current_section = []
    in_diagram_section = False
    
    for line in lines:
        if "## Diagram:" in line or "### Diagram:" in line:
            in_diagram_section = True
            if current_section:
                diagram_sections.append("\n".join(current_section))
                current_section = []
        elif in_diagram_section and line.strip() and "##" in line and not "Diagram" in line:
            in_diagram_section = False
            if current_section:
                diagram_sections.append("\n".join(current_section))
                current_section = []
        
        if in_diagram_section and line.strip():
            current_section.append(line)
    
    # Add the last section if needed
    if current_section:
        diagram_sections.append("\n".join(current_section))
    
    # Generate simple placeholder images for diagrams
    base64_images = []
    for i, section in enumerate(diagram_sections):
        # Create a simple image with text
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        
        # Save the image
        img_path = os.path.join(diagrams_dir, f"diagram_{i}.png")
        image.save(img_path)
        
        # Convert to base64
        with open(img_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')
            base64_images.append(base64_image)
    
    return base64_images

def get_multimodal_llm():
    """
    Get an LLM that supports multimodal inputs.
    In a real implementation, this would use a model that supports images.
    
    Returns:
        LLM: A language model supporting multimodal inputs
    """
    # In a real implementation, use a multimodal model
    # For now, we'll use the standard LLM with a special prompt
    return get_llm()

def process_design_with_image(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process design documents with accompanying diagrams.
    
    Args:
        state (Dict[str, Any]): The current state
        
    Returns:
        Dict[str, Any]: Updated state with design review
    """
    # Extract design document from state
    design_document = state.get("functional_design", "")
    if not design_document:
        return {"design_review": "No design document available for review."}
    
    # Extract diagrams from design
    diagrams = extract_diagrams_from_design(design_document)
    
    # Prepare design review prompt
    diagram_descriptions = [f"[Diagram {i+1}]" for i in range(len(diagrams))]
    review_prompt = f"""
    You are an expert software architect reviewing a design document with associated diagrams.
    
    Design Document:
    {design_document}
    
    Diagrams:
    {chr(10).join(diagram_descriptions)}
    
    Please provide a comprehensive review of this design focusing on:
    1. Architectural soundness
    2. Component relationships
    3. Data flow
    4. Potential issues or improvements
    5. Alignment with requirements
    
    Format your response using Markdown with clear sections.
    """
    
    # Get LLM response
    llm = get_multimodal_llm()
    response = llm.invoke(review_prompt)
    
    # In a true multimodal implementation, we would pass the images directly
    # For this implementation, we're using text descriptions
    
    return {"design_review": response}

async def process_design_with_image_async(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Asynchronous version of process_design_with_image.
    
    Args:
        state (Dict[str, Any]): The current state
        
    Returns:
        Dict[str, Any]: Updated state with design review
    """
    # This would be implemented with async calls to the LLM
    # For now, we'll use the synchronous version
    return process_design_with_image(state)