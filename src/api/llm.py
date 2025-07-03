from openai import OpenAI
import os
from ..config.constants import DEFAULT_MODEL
from ..utils.model_validator import validate_model, APIError

def get_api_client():
    """
    Get the OpenAI API client with proper configuration.
    Raises:
        APIError: If required environment variables are missing
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise APIError(
            message="OPENAI_API_KEY environment variable is not set",
            status_code=None,
            response_body="Missing API key configuration"
        )
    
    return OpenAI(
        api_key=api_key,
        base_url="https://api.sambanova.ai/v1",
    )

def chat(query: str, model_name: str = DEFAULT_MODEL):
    """
    Send a chat query to the specified model.
    Args:
        query: The user's query
        model_name: Name of the model to use (defaults to DEFAULT_MODEL from config)
    Returns:
        The model's response
    Raises:
        ModelNotAvailableError: If the model is not available or deprecated
        APIError: If there's an error communicating with the API
    """
    # Validate model before making the API call
    validate_model(model_name)
    
    # Get API client
    client = get_api_client()
    
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": query}
        ]
    )

    return response.choices[0].message.content 