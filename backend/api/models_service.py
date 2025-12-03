import requests
import os
from typing import List, Dict, Optional
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
CACHE_KEY = "openrouter_models"
CACHE_TTL = 3600  # 1 hour

# Fallback models list in case API fails
DEFAULT_MODELS = [
    {
        "id": "google/gemini-2.0-flash-exp:free",
        "name": "Gemini 2.0 Flash",
        "description": "Fast and efficient model from Google (free tier)",
        "context_length": 1000000,
        "capabilities": {
            "vision": True,
            "fast": True,
            "code": True,
            "free": True
        }
    },
    {
        "id": "openai/gpt-4-turbo",
        "name": "GPT-4 Turbo",
        "description": "OpenAI's most capable model with advanced reasoning",
        "context_length": 128000,
        "capabilities": {
            "vision": True,
            "fast": False,
            "code": True,
            "free": False
        }
    },
    {
        "id": "anthropic/claude-3.5-sonnet",
        "name": "Claude 3.5 Sonnet",
        "description": "Anthropic's most capable model for complex tasks",
        "context_length": 200000,
        "capabilities": {
            "vision": True,
            "fast": False,
            "code": True,
            "free": False
        }
    },
    {
        "id": "qwen/qwen-turbo",
        "name": "Qwen Turbo",
        "description": "Fast and efficient model",
        "context_length": 8000,
        "capabilities": {
            "vision": False,
            "fast": True,
            "code": True,
            "free": False
        }
    },
    {
        "id": "deepseek/deepseek-chat",
        "name": "DeepSeek Chat",
        "description": "DeepSeek chat model",
        "context_length": 64000,
        "capabilities": {
            "vision": False,
            "fast": False,
            "code": True,
            "free": False
        }
    }
]


def detect_capabilities(model_data: Dict) -> Dict[str, bool]:
    """Detect model capabilities from OpenRouter data."""
    capabilities = {
        "vision": False,
        "fast": False,
        "code": False,
        "free": False
    }
    
    model_id = model_data.get("id", "").lower()
    model_name = model_data.get("name", "").lower()
    description = model_data.get("description", "").lower()
    architecture = model_data.get("architecture", {})
    
    # Detect vision capability
    modality = architecture.get("modality", "")
    if "vision" in modality or "image" in modality or "multimodal" in modality:
        capabilities["vision"] = True
    if any(keyword in model_id or keyword in model_name for keyword in ["vision", "grok", "gemini", "gpt-4", "claude-3"]):
        capabilities["vision"] = True
    
    # Detect fast models (flash, turbo, etc.)
    if any(keyword in model_id or keyword in model_name for keyword in ["flash", "turbo", "fast", "instant"]):
        capabilities["fast"] = True
    
    # Detect code capability (most modern models support code)
    if any(keyword in model_id or keyword in model_name or keyword in description 
           for keyword in ["code", "deepseek", "claude", "gpt", "gemini"]):
        capabilities["code"] = True
    
    # Detect free tier
    if ":free" in model_id or "free" in model_name or "(free)" in model_name.lower():
        capabilities["free"] = True
    
    return capabilities


def format_model_data(model: Dict) -> Dict:
    """Format model data for frontend consumption."""
    return {
        "id": model.get("id"),
        "name": model.get("name"),
        "description": model.get("description", ""),
        "context_length": model.get("context_length", 0),
        "capabilities": detect_capabilities(model),
        "pricing": model.get("pricing", {})
    }


def get_openrouter_models(use_cache: bool = True) -> Optional[List[Dict]]:
    """
    Fetch available models from OpenRouter API.
    Returns None if API fails, allowing caller to use fallback.
    """
    # Check cache first
    if use_cache:
        cached_models = cache.get(CACHE_KEY)
        if cached_models:
            logger.info("Returning cached OpenRouter models")
            return cached_models
    
    # Fetch from API
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        
        logger.info("Fetching models from OpenRouter API")
        response = requests.get(OPENROUTER_MODELS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        models_data = data.get("data", [])
        
        # Format models
        formatted_models = [format_model_data(model) for model in models_data]
        
        # Filter out models without proper ID or name
        formatted_models = [m for m in formatted_models if m.get("id") and m.get("name")]
        
        # Cache the results
        cache.set(CACHE_KEY, formatted_models, CACHE_TTL)
        
        logger.info(f"Successfully fetched {len(formatted_models)} models from OpenRouter")
        return formatted_models
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch OpenRouter models: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching OpenRouter models: {str(e)}")
        return None


def get_models_with_fallback() -> tuple[List[Dict], Optional[str]]:
    """
    Get models from OpenRouter with fallback to default list.
    Returns (models_list, error_message).
    If error_message is not None, it means fallback was used.
    """
    models = get_openrouter_models()
    
    if models is None:
        logger.warning("Using fallback model list")
        error_msg = "Failed to fetch latest models from OpenRouter. Using cached model list."
        return DEFAULT_MODELS, error_msg
    
    return models, None
