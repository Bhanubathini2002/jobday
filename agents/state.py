from typing import Annotated, TypedDict, List, Dict, Any
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    The state of the agentic workflow.
    """
    # Messages for chat-like interaction
    messages: Annotated[List, add_messages]
    
    # User profile data (raw input)
    user_data: Dict[str, Any]
    
    # Generated LaTeX sections
    # Key: section name (e.g., 'education', 'experience')
    # Value: generated LaTeX string
    resume_sections: Dict[str, str]
    
    # Final compiled LaTeX document
    final_latex: str
    
    # Current section being processed
    current_section: str
    
    # Generation preferences
    # e.g., {"max_points": 8, "max_words": 200, "max_lines": 10}
    preferences: Dict[str, Any]
