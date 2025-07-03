import requests
from typing import List, Dict
import time
from ..config.constants import MODEL_STATUS_ACTIVE, ERROR_MESSAGES, DEFAULT_MODEL

# Cache for API models
_model_cache: Dict[str, any] = {
    "models": [],
    "last_updated": 0
}
CACHE_DURATION = 300  # Cache duration in seconds (5 minutes)

class SlackBotError(Exception):
    """Base exception class for SlackBot errors"""
    def __init__(self, message: str, user_message: str, error_code: str = None):
        self.message = message
        self.user_message = user_message
        self.error_code = error_code
        super().__init__(self.message)


class ModelNotAvailableError(SlackBotError):
    """Raised when the requested model is not available or deprecated"""
    def __init__(self, message: str, model_name: str, available_models: List[str], error_type: str = "model_not_found"):
        error_code = "MODEL_ERROR"
        error_details = {
            "model_requested": model_name,
            "available_models": available_models
        }
        
        # Format user-friendly message
        user_message = ERROR_MESSAGES[error_type].format(
            model=model_name,
            models=", ".join(available_models)
        )
        
        full_message = f"Error Code: {error_code}\nMessage: {message}\nDetails: {error_details}\nUser Message: {user_message}"
        super().__init__(full_message, user_message, error_code)


class APIError(SlackBotError):
    """Raised when there's an error communicating with the API"""
    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        error_code = "API_ERROR"
        error_details = {
            "status_code": status_code,
            "response_body": response_body
        }
        user_message = ERROR_MESSAGES["api_error"]
        full_message = f"Error Code: {error_code}\nMessage: {message}\nDetails: {error_details}\nUser Message: {user_message}"
        super().__init__(full_message, user_message, error_code)


def get_model_list(use_cache: bool = True) -> List[str]:
    """
    Get the list of available models from the SambaNova API.
    Args:
        use_cache: Whether to use cached model list (default: True)
    Returns:
        List of model IDs available in the API
    Raises:
        APIError: If there's an error communicating with the API
    """
    current_time = time.time()
    
    # Return cached models if they're still valid
    if use_cache and _model_cache["models"] and (current_time - _model_cache["last_updated"]) < CACHE_DURATION:
        return _model_cache["models"]
    
    url = "https://api.sambanova.ai/v1/models"
    try:
        response = requests.get(url)
        response.raise_for_status()
        models = response.json()["data"]
        model_list = [model["id"] for model in models]
        
        # Update cache
        _model_cache["models"] = model_list
        _model_cache["last_updated"] = current_time
        
        return model_list
    except requests.exceptions.RequestException as e:
        raise APIError(
            message="Failed to fetch models from API",
            status_code=getattr(e.response, 'status_code', None),
            response_body=getattr(e.response, 'text', str(e))
        )


def validate_model(model_name: str, use_cache: bool = True) -> bool:
    """
    Validate if the model is available in the API.
    Args:
        model_name: Name of the model to validate
        use_cache: Whether to use cached model list (default: True)
    Returns:
        True if model is valid
    Raises:
        ModelNotAvailableError: If the model is not available
        APIError: If there's an error communicating with the API
    """
    try:
        api_models = get_model_list(use_cache=use_cache)
        
        if model_name not in api_models:
            raise ModelNotAvailableError(
                message=f"Model {model_name} not found in API models",
                model_name=model_name,
                available_models=api_models,
                error_type="model_not_found"
            )
        
        return True
        
    except APIError:
        # If we can't reach the API but have cached models, use them
        if use_cache and _model_cache["models"]:
            if model_name in _model_cache["models"]:
                return True
            raise ModelNotAvailableError(
                message="Model not found in cached models",
                model_name=model_name,
                available_models=_model_cache["models"],
                error_type="model_not_found"
            )
        raise


# Validate default model on module import
try:
    validate_model(DEFAULT_MODEL)
except (ModelNotAvailableError, APIError) as e:
    print(f"Warning: Default model validation failed: {e.message}") 