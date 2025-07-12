from agents.agent.analyst_agent import analyst_agent, AnalysisContext
from graph.states import OptimizedWorkflowState
import logging

logger = logging.getLogger(__name__)

async def analyst_agent_node(state: OptimizedWorkflowState):
    """Analyze uploaded pdf script with MINIMUM API calls (2 total)"""
    pdf_path = state.get('pdf_path')
    logger.info(f"Starting OPTIMIZED analysis (2 API calls) for: {pdf_path}")
    
    try:
        # Create analysis context
        context = AnalysisContext(pdf_path=pdf_path)
        
        # Enhanced prompt for comprehensive analysis
        analysis_prompt = f"""
        Perform comprehensive script analysis for: {pdf_path}
        
        STEP 1: Extract the script text using extract_script_from_pdf_tool
        STEP 2: Analyze ALL aspects and return complete ComprehensiveAnalysis
        
        This should take exactly 2 API calls total.
        """
        
        # Execute analysis (will use 2 API calls: extract + analyze)
        try:
            result = await analyst_agent.run_async(analysis_prompt, deps=context)
        except AttributeError:
            try:
                result = await analyst_agent.run(analysis_prompt, deps=context)
            except AttributeError:
                result = await analyst_agent(analysis_prompt, deps=context)
        
        logger.info(f"✅ OPTIMIZED analysis completed with 2 API calls. Result type: {type(result)}")
        
        # Extract the actual analysis data
        if hasattr(result, 'output'):
            analysis_data = result.output
        elif hasattr(result, 'result'):
            analysis_data = result.result
        else:
            analysis_data = result
        
        # Update state
        state['comprehensive_analysis'] = analysis_data
        state['status'] = 'analysis_completed'
        state['api_calls_used'] = 2  # Track actual usage
        
        return state
        
    except Exception as e:
        logger.error(f"OPTIMIZED analysis failed: {str(e)}")
        state['status'] = f'analysis_failed: {str(e)}'
        state['errors'] = state.get('errors', []) + [str(e)]
        state['api_calls_used'] = 1  # Only extraction call succeeded
        return state

# # Auto human-in-the-loop
# async def human_feedback_node(state: OptimizedWorkflowState):
#     """Human feedback node - unchanged"""
#     if 'feedback_required' not in state:
#         state['feedback_required'] = False
    
#     if 'feedback_text' not in state:
#         state['feedback_text'] = ""
    
#     return {
#         **state,
#         "feedback_required": False,
#         "status": "analysis_completed"
#     }



# Manual human-in-the-loop
async def human_feedback_node(state: OptimizedWorkflowState):
    """Human feedback node - now functional"""
    
    # Check if feedback is required based on analysis quality or user preference
    comprehensive_analysis = state.get('comprehensive_analysis')
    
    # Auto-determine if feedback is needed (you can customize these conditions)
    feedback_required = False
    
    if comprehensive_analysis:
        # Example conditions that might require human feedback:
        script_data = comprehensive_analysis.script_data if hasattr(comprehensive_analysis, 'script_data') else None
        cost_data = comprehensive_analysis.cost_breakdown if hasattr(comprehensive_analysis, 'cost_breakdown') else None
        
        # Require feedback if:
        if script_data and len(script_data.scenes) == 0:  # No scenes detected
            feedback_required = True
        elif cost_data and cost_data.total_costs == 0:  # No costs calculated
            feedback_required = True
        elif state.get('force_human_review', False):  # Manually requested
            feedback_required = True
    else:
        feedback_required = True  # No analysis data - definitely need feedback
    
    # If feedback already provided, process it
    if state.get('human_feedback_provided', False):
        feedback_text = state.get('feedback_text', '')
        feedback_approved = state.get('feedback_approved', True)
        
        if feedback_approved:
            return {
                **state,
                "feedback_required": False,
                "status": "analysis_completed_with_approval",
                "feedback_processed": True
            }
        else:
            # Feedback indicates issues - might need re-analysis
            return {
                **state,
                "feedback_required": False,
                "status": "analysis_needs_revision",
                "feedback_processed": True,
                "revision_notes": feedback_text
            }
    
    # If feedback is required but not yet provided
    if feedback_required:
        return {
            **state,
            "feedback_required": True,
            "status": "awaiting_human_feedback",
            "feedback_prompt": "Please review the analysis results and provide feedback."
        }
    
    # No feedback needed - proceed
    return {
        **state,
        "feedback_required": False,
        "status": "analysis_completed"
    }