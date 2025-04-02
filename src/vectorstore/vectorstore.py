"""
Module for initializing and configuring the vector store.
"""
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from typing import List, Dict, Any, Optional, Union

# Load environment variables
load_dotenv()

def initialize_embeddings(model_name: str = "all-MiniLM-L6-v2"):
    """
    Initialize the embeddings model.
    
    Args:
        model_name (str): The name of the model to use.
        
    Returns:
        HuggingFaceEmbeddings: The embeddings model.
    """
    # Check if HF token is available
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN not found in environment variables.")
    
    # Initialize embeddings model
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    
    return embeddings

def initialize_vectorstore(embeddings=None, persist_directory: str = "/tmp/sdlc_vectorstore"):
    """
    Initialize the vector store.
    
    Args:
        embeddings: The embeddings model to use.
        persist_directory (str): The directory to persist the vector store to.
        
    Returns:
        FAISS: The vector store.
    """
    # Create persist directory if it doesn't exist
    os.makedirs(persist_directory, exist_ok=True)
    
    # Initialize embeddings if not provided
    if embeddings is None:
        embeddings = initialize_embeddings()
    
    # Check if vectorstore exists
    if os.path.exists(os.path.join(persist_directory, "index.faiss")):
        # Load existing vectorstore
        vectorstore = FAISS.load_local(
            persist_directory,
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        # Create new vectorstore
        vectorstore = FAISS.from_texts(
            ["SDLC Agent Vectorstore"], 
            embeddings,
            metadatas=[{"source": "initialization"}]
        )
        # Persist vectorstore
        vectorstore.save_local(persist_directory)
    
    return vectorstore

def add_document_to_vectorstore(
    vectorstore: FAISS, 
    text: str, 
    metadata: Dict[str, Any],
    session_id: str,
    stage: str
) -> str:
    """
    Add a document to the vector store.
    
    Args:
        vectorstore (FAISS): The vector store.
        text (str): The document text.
        metadata (Dict[str, Any]): The document metadata.
        session_id (str): The session ID.
        stage (str): The SDLC stage.
        
    Returns:
        str: The document ID.
    """
    # Add session_id and stage to metadata
    metadata["session_id"] = session_id
    metadata["stage"] = stage
    
    # Create document
    document = Document(page_content=text, metadata=metadata)
    
    # Add document to vectorstore
    ids = vectorstore.add_documents([document])
    
    return ids[0]

def search_vectorstore(
    vectorstore: FAISS, 
    query: str, 
    filter: Optional[Dict[str, Any]] = None,
    k: int = 5
) -> List[Document]:
    """
    Search the vector store.
    
    Args:
        vectorstore (FAISS): The vector store.
        query (str): The search query.
        filter (Optional[Dict[str, Any]]): The search filter.
        k (int): The number of results to return.
        
    Returns:
        List[Document]: The search results.
    """
    # Search vectorstore
    results = vectorstore.similarity_search(
        query,
        k=k,
        filter=filter
    )
    
    return results

def get_documents_by_session(
    vectorstore: FAISS, 
    session_id: str,
    stage: Optional[str] = None
) -> List[Document]:
    """
    Get all documents for a session.
    
    Args:
        vectorstore (FAISS): The vector store.
        session_id (str): The session ID.
        stage (Optional[str]): The SDLC stage.
        
    Returns:
        List[Document]: The documents.
    """
    # Prepare filter
    filter = {"session_id": session_id}
    if stage:
        filter["stage"] = stage
    
    # Get documents with specified metadata
    results = vectorstore.get(
        where=filter
    )
    
    return results

def delete_documents_by_session(
    vectorstore: FAISS, 
    session_id: str,
    stage: Optional[str] = None,
    persist_directory: str = "/tmp/sdlc_vectorstore"
) -> None:
    """
    Delete all documents for a session.
    
    Args:
        vectorstore (FAISS): The vector store.
        session_id (str): The session ID.
        stage (Optional[str]): The SDLC stage.
        persist_directory (str): The directory to persist the vector store to.
    """
    # Prepare filter
    filter = {"session_id": session_id}
    if stage:
        filter["stage"] = stage
    
    # Delete documents with specified metadata
    vectorstore.delete(
        filter=filter
    )
    
    # Persist vectorstore
    vectorstore.save_local(persist_directory)

def get_document_by_id(
    vectorstore: FAISS, 
    document_id: str
) -> Optional[Document]:
    """
    Get a document by ID.
    
    Args:
        vectorstore (FAISS): The vector store.
        document_id (str): The document ID.
        
    Returns:
        Optional[Document]: The document or None if not found.
    """
    # Get document by ID
    try:
        document = vectorstore.get(
            ids=[document_id]
        )
        if document:
            return document[0]
        return None
    except:
        return None