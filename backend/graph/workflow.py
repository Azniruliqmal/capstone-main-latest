from langgraph.graph import StateGraph, START, END
from graph.states import OptimizedWorkflowState
from graph.nodes import analyst_agent_node, human_feedback_node

# # Auto human_feedback
# def should_continue_or_end(state: OptimizedWorkflowState):
#     """Simplified routing logic"""
#     feedback_required = state.get('feedback_required', False)
    
#     if feedback_required:
#         return "unified_analysis"
    
#     return "END"

# def create_workflow():
#     """Create simplified workflow with single analysis node"""
#     workflow = StateGraph(OptimizedWorkflowState)
    
#     # Add nodes - only 2 nodes now!
#     workflow.add_node("analyst_agent", analyst_agent_node)
#     workflow.add_node("human_feedback", human_feedback_node)
    
#     # Simple sequential flow
#     workflow.set_entry_point("analyst_agent")
#     workflow.add_edge("analyst_agent", "human_feedback")
    
#     workflow.add_conditional_edges(
#         "human_feedback",
#         should_continue_or_end,
#         {
#             "END": END,
#             "analyst_agent": "analyst_agent"
#         }
#     )
    
#     return workflow.compile()

# Manual human-in-the-loop
def should_continue_or_end(state: OptimizedWorkflowState):
    """Enhanced routing logic with feedback support"""
    feedback_required = state.get('feedback_required', False)
    status = state.get('status', '')
    
    # If feedback is required and not yet provided
    if feedback_required and not state.get('human_feedback_provided', False):
        return "WAIT_FOR_FEEDBACK"  # This would pause the workflow
    
    # If feedback was provided and indicates need for revision
    if state.get('status') == 'analysis_needs_revision':
        return "analyst_agent"  # Re-run analysis
    
    return "END"

def create_workflow():
    """Create workflow with feedback support"""
    workflow = StateGraph(OptimizedWorkflowState)
    
    # Add nodes
    workflow.add_node("analyst_agent", analyst_agent_node)
    workflow.add_node("human_feedback", human_feedback_node)
    
    # Flow
    workflow.set_entry_point("analyst_agent")
    workflow.add_edge("analyst_agent", "human_feedback")
    
    workflow.add_conditional_edges(
        "human_feedback",
        should_continue_or_end,
        {
            "END": END,
            "analyst_agent": "analyst_agent",  # Allow re-analysis
            "WAIT_FOR_FEEDBACK": END  # End workflow, wait for external feedback
        }
    )
    
    return workflow.compile()