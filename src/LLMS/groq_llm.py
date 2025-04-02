"""
Groq LLM integration with streaming support.
"""
import os
from typing import Dict, Any, List, Optional, Callable
from langchain_groq import ChatGroq
from langchain.schema.runnable import RunnableConfig
from langchain.callbacks.base import BaseCallbackHandler

class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming LLM responses."""
    
    def __init__(self, streaming_callback: Callable[[str], None]):
        """Initialize with a callback function."""
        self.streaming_callback = streaming_callback
        self.buffer = ""
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Handle new token received from LLM."""
        self.buffer += token
        # Call the callback with the token
        self.streaming_callback(token)
        
    def get_buffer(self) -> str:
        """Get the current buffer contents."""
        return self.buffer

def get_llm(temperature=0.7, streaming=False, streaming_callback=None):
    """
    Get a Groq LLM instance.
    
    Args:
        temperature (float): The temperature for generation.
        streaming (bool): Whether to stream the response.
        streaming_callback (Callable[[str], None]): Callback function for streaming.
        
    Returns:
        ChatGroq: The LLM instance.
    """
    # Get API key from environment
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not found. Please make sure it's set.")
    
    # Initialized LLM with model
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama3-70b-8192",  # Use Llama 3 70B model for high quality results
        temperature=temperature,
        streaming=streaming,
        callbacks=[StreamingCallbackHandler(streaming_callback)] if streaming and streaming_callback else None,
    )
    
    return llm

def invoke_with_streaming(prompt: str, streaming_callback: Callable[[str], None], temperature=0.7):
    """
    Invoke LLM with streaming response.
    
    Args:
        prompt (str): The prompt to send to the LLM.
        streaming_callback (Callable[[str], None]): Callback function for streaming.
        temperature (float): The temperature for generation.
        
    Returns:
        str: The complete response.
    """
    callback_handler = StreamingCallbackHandler(streaming_callback)
    
    # Get LLM instance
    llm = get_llm(temperature=temperature, streaming=True)
    
    # Configure with callbacks
    config = RunnableConfig(callbacks=[callback_handler])
    
    # Invoke with streaming
    response = llm.invoke(prompt, config=config)
    
    # Return the complete response
    return response

def get_available_models() -> List[str]:
    """
    Get a list of available Groq models.
    
    Returns:
        List[str]: Available model names.
    """
    return [
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma-7b-it"
    ]