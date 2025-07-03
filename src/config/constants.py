# Model status constants
MODEL_STATUS_ACTIVE = "active"
MODEL_STATUS_DEPRECATED = "deprecated"

# Default model to use (this will be validated against API models)
DEFAULT_MODEL = "Meta-Llama-3.3-70B-Instruct"

# User-friendly error messages
ERROR_MESSAGES = {
    "model_not_found": "Sorry, the model '{model}' is not available. Available models are: {models}",
    "model_deprecated": "The model '{model}' is no longer supported. Please use one of these active models: {models}",
    "model_api_unavailable": "The requested model '{model}' is not currently available. Available models: {models}",
    "api_error": "Sorry, I'm having trouble accessing the model API right now. Please try again later."
} 