"""
Utilities for file operations.
"""
import os
from typing import Dict, Any, List, Optional, Union
import json
import zipfile
import io
import base64
from datetime import datetime

def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that a directory exists.
    
    Args:
        directory_path (str): The directory path.
    """
    os.makedirs(directory_path, exist_ok=True)

def read_file(file_path: str) -> str:
    """
    Read a file.
    
    Args:
        file_path (str): The file path.
        
    Returns:
        str: The file content.
    """
    with open(file_path, "r") as f:
        return f.read()

def write_file(file_path: str, content: str) -> None:
    """
    Write content to a file.
    
    Args:
        file_path (str): The file path.
        content (str): The content to write.
    """
    # Ensure directory exists
    directory = os.path.dirname(file_path)
    if directory:
        ensure_directory_exists(directory)
    
    # Write file
    with open(file_path, "w") as f:
        f.write(content)

def create_zip_file(files: Dict[str, str]) -> bytes:
    """
    Create a ZIP file in memory.
    
    Args:
        files (Dict[str, str]): A dictionary of {filename: content}.
        
    Returns:
        bytes: The ZIP file as bytes.
    """
    # Create a zip file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, content in files.items():
            zf.writestr(filename, content)
    
    # Reset buffer position
    zip_buffer.seek(0)
    
    return zip_buffer.getvalue()

def create_download_link(content: str, filename: str, mimetype: str = "text/plain") -> str:
    """
    Create a download link for file content.
    
    Args:
        content (str): The file content.
        filename (str): The filename for the download.
        mimetype (str): The MIME type of the file.
        
    Returns:
        str: A HTML link for downloading the file.
    """
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:{mimetype};base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

def generate_timestamp() -> str:
    """
    Generate a timestamp string.
    
    Returns:
        str: The timestamp string.
    """
    return datetime.now().isoformat()

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to ensure it's valid.
    
    Args:
        filename (str): The filename to sanitize.
        
    Returns:
        str: The sanitized filename.
    """
    # Replace invalid characters with underscore
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    return filename

def write_json_file(file_path: str, data: Any) -> None:
    """
    Write data to a JSON file.
    
    Args:
        file_path (str): The file path.
        data (Any): The data to write.
    """
    # Ensure directory exists
    directory = os.path.dirname(file_path)
    if directory:
        ensure_directory_exists(directory)
    
    # Write file
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def read_json_file(file_path: str) -> Any:
    """
    Read data from a JSON file.
    
    Args:
        file_path (str): The file path.
        
    Returns:
        Any: The data from the file.
    """
    with open(file_path, "r") as f:
        return json.load(f)

def list_files(directory_path: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    List files in a directory.
    
    Args:
        directory_path (str): The directory path.
        extensions (Optional[List[str]]): Optional list of file extensions to filter by.
        
    Returns:
        List[str]: List of file paths.
    """
    files = []
    
    for root, _, filenames in os.walk(directory_path):
        for filename in filenames:
            if extensions is None or any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    
    return files