from langgraph.graph import StateGraph, START, END
from state import AgentState
from nodes import (
    objective_node,
    profile_summary_node,
    technical_skills_node,
    work_experience_1_node,
    work_experience_2_node,
    assembly_node,
)

def create_resume_graph():
    # Initialize the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("objective", objective_node)
    workflow.add_node("profile_summary", profile_summary_node)
    workflow.add_node("technical_skills", technical_skills_node)
    workflow.add_node("work_experience_1", work_experience_1_node)
    workflow.add_node("work_experience_2", work_experience_2_node)
    workflow.add_node("assembly", assembly_node)

    # Define edges
    # Linear flow: START -> objective -> profile_summary -> technical_skills -> exp1 -> exp2 -> assembly -> END
    workflow.add_edge(START, "objective")
    workflow.add_edge("objective", "profile_summary")
    workflow.add_edge("profile_summary", "technical_skills")
    workflow.add_edge("technical_skills", "work_experience_1")
    workflow.add_edge("work_experience_1", "work_experience_2")
    workflow.add_edge("work_experience_2", "assembly")
    workflow.add_edge("assembly", END)

    # Compile the graph
    return workflow.compile()

# Instantiate the graph
resume_graph = create_resume_graph()
