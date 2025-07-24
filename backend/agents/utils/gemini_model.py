from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def get_model():
    """Get configured Gemini model with proper error handling"""
    try:
        model_name = os.getenv('MODEL_CHOICE', 'gemini-2.0-flash')
        api_key = os.getenv('GEMINI_KEY')
        
        if not api_key:
            raise ValueError("GEMINI_KEY not found in environment variables")
        
        if not model_name:
            raise ValueError("MODEL_CHOICE not found in environment variables")
        
        logger.info(f"Initializing Gemini model: {model_name}")
        
        # Initialize the provider with the API key
        provider = GoogleGLAProvider(api_key=api_key)
        
        # Create GeminiModel with the provider
        model = GeminiModel(model_name, provider=provider)
        
        logger.info(f"Successfully initialized Gemini model: {model_name}")
        return model
        
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model: {e}")
        
        # Fallback to a simple model configuration
        logger.info("Attempting fallback model configuration...")
        try:
            from pydantic_ai.models import openai
            # You can add OpenAI as fallback if you have the key
            # return openai.OpenAIModel('gpt-3.5-turbo')
            raise e  # Re-raise the original error for now
        except:
            raise e