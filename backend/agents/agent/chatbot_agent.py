from pydantic_ai import Agent
from agents.utils.gemini_model import get_model
from agents.states.states import ComprehensiveAnalysis
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_script_analysis_context(analysis_data: Dict[str, Any]) -> str:
    """Helper function to format script analysis data"""
    if not analysis_data:
        return "No script analysis data available"
    
    # Extract key information for context
    context = []
    character_count = 0
    scene_count = 0
    
    # Scene count and character extraction
    scenes_data = None
    if "script_data" in analysis_data and "scenes" in analysis_data["script_data"]:
        scenes_data = analysis_data["script_data"]["scenes"]
    elif "scenes" in analysis_data:
        scenes_data = analysis_data["scenes"]
    
    if scenes_data:
        scene_count = len(scenes_data)
        context.append(f"Total scenes: {scene_count}")
        
        # Extract unique characters from scenes
        all_characters = set()
        for scene in scenes_data:
            characters = scene.get("characters_present", scene.get("characters", []))
            if isinstance(characters, list):
                all_characters.update(characters)
        
        character_count = len(all_characters)
        if character_count > 0:
            context.append(f"Total characters: {character_count}")
            context.append(f"Characters: {', '.join(sorted(list(all_characters)[:10]))}" + 
                         (f" and {character_count - 10} more" if character_count > 10 else ""))
        
        if scene_count > 0:
            context.append("Sample scenes:")
            for i, scene in enumerate(scenes_data[:3]):
                scene_num = scene.get("scene_number", scene.get("number", i+1))
                scene_header = scene.get("scene_header", scene.get("heading", "Unknown"))
                context.append(f"  - Scene {scene_num}: {scene_header}")
    
    # Cast breakdown info
    if "cast_breakdown" in analysis_data:
        cast_data = analysis_data["cast_breakdown"]
        if isinstance(cast_data, dict):
            if "characters" in cast_data:
                char_list = cast_data["characters"]
                if isinstance(char_list, list):
                    character_count = len(char_list)
                    context.append(f"Cast breakdown shows {character_count} characters")
            elif "main_characters" in cast_data:
                main_chars = cast_data["main_characters"]
                if isinstance(main_chars, list):
                    context.append(f"Main characters: {', '.join(main_chars[:5])}")
    
    # Budget info
    if "cost_breakdown" in analysis_data:
        context.append("Budget breakdown available")
        cost_data = analysis_data["cost_breakdown"]
        if isinstance(cost_data, dict):
            total_cost = sum(v for v in cost_data.values() if isinstance(v, (int, float)))
            if total_cost > 0:
                context.append(f"  - Estimated total cost: ${total_cost:,.2f}")
    
    # Location info
    if "location_breakdown" in analysis_data:
        context.append("Location breakdown available")
    
    return "\n".join(context) if context else "Script analysis data structure not recognized"

system_prompt = """
You are an expert film production assistant chatbot specializing in script analysis and film production guidance. You are conversational, helpful, and knowledgeable about all aspects of filmmaking.

IMPORTANT: You MUST respond to every user message. Never stay silent or fail to respond.

You will receive script analysis data in the conversation context. Use this data to provide detailed, specific answers about:
- Scene breakdowns and requirements
- Cast and character details  
- Budget estimates and cost breakdowns
- Location requirements
- Props and wardrobe needs
- Production insights and recommendations


Always:
- Be conversational and engaging
- Reference specific data from the analysis when relevant
- Provide actionable insights and recommendations
- Ask follow-up questions to better assist the user
- Maintain a professional but friendly tone
- Format responses clearly with bullet points or sections when appropriate
- ALWAYS respond with useful information, never refuse to answer

CRITICAL: When analyzing scenes for location and character combinations:
- Read through ALL scene data in the script analysis
- For each scene, note the location and exact character list
- When asked about "scenes with same location and same characters", find scenes that have BOTH the same location AND the exact same character list
- Compare scenes systematically to identify matches
- Provide specific scene numbers and details in your response
- DO NOT just count characters - analyze the actual question being asked

Example responses:
- "Based on the script analysis, there are X characters in this script..."
- "Looking at the scene breakdown, I can see there are X scenes..."
- "The budget analysis shows an estimated cost of $X..."
- "Analyzing scenes with same locations and characters, I found X scenes that share..."
"""

# Initialize the chatbot agent with error handling
def create_chatbot_agent():
    """Create chatbot agent with proper error handling"""
    try:
        model = get_model()
        logger.info(f"Initializing chatbot with model: {model}")
        
        agent = Agent(
            model=model,
            system_prompt=system_prompt,
            deps_type=dict  # Will receive script analysis data
        )
        logger.info("Chatbot agent initialized successfully")
        return agent
    except Exception as e:
        logger.error(f"Failed to initialize chatbot agent: {e}")
        raise

chatbot_agent = create_chatbot_agent()  