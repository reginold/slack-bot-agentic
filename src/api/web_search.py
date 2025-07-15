import os
import requests
from typing import Optional
from ..utils.model_validator import APIError

class WebSearchError(APIError):
    """Custom error class for web search failures"""
    def __init__(self, log_message: str, user_message: str = "Web search failed. Please try again later."):
        """
        Initialize the error with:
        - log_message: Detailed error for logging/debugging
        - user_message: Friendly message to show user
        """
        super().__init__(log_message, user_message)
        self.log_message = log_message
        self.user_message = user_message

def web_search(query: str, num_results: int = 3) -> str:
    """
    Perform web search using SerpAPI (or alternative)
    Returns formatted search results as markdown string
    """
    try:
        # Using SerpAPI (Google Search API) as example
        api_key = os.environ.get("SERPAPI_KEY")
        if not api_key:
            raise WebSearchError("API key missing", "Search service unavailable")
        
        params = {
            'q': query,
            'api_key': api_key,
            'num': num_results
        }
        
        response = requests.get('https://serpapi.com/search', params=params)
        response.raise_for_status()
        data = response.json()
        
        # Format results as markdown
        if 'organic_results' in data:
            results = []
            for idx, result in enumerate(data['organic_results'][:num_results], 1):
                title = result.get('title', 'No title')
                link = result.get('link', '#')
                snippet = result.get('snippet', 'No description available')
                results.append(f"{idx}. [{title}]({link})\n   {snippet}")
            
            return "\n\n".join(results)
        return "No results found for your query"
    
    except requests.exceptions.RequestException as e:
        raise WebSearchError(f"Network error: {str(e)}") 