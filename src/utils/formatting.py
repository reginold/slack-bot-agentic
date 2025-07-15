import re

def format_slack_message(text: str) -> str:
    """
    Format text for Slack message display.
    Args:
        text: The text to format
    Returns:
        Formatted text suitable for Slack display
    """
    # Convert markdown links [text](url) to Slack format <url|text>
    # This pattern handles links with special characters in both text and URL
    text = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)', 
        lambda m: f'<{m.group(2).strip()}|{m.group(1).strip()}>',
        text
    )
    
    # Rest of your formatting rules
    text = re.sub(r'^###\s+(.*?)$', r'*\1*', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
    
    # Format primary level numbered lists (1.)
    text = re.sub(r'^\s*(\d+)\.\s+(.*?)$', r'\1. \2', text, flags=re.MULTILINE)
    
    # Format secondary level with letters (a.)
    text = re.sub(r'^\s*[-*]\s+(.*?)$', r'    a. \1', text, flags=re.MULTILINE)
    
    # Format tertiary level with roman numerals (i.)
    text = re.sub(r'^\s{4,}[-*]\s+(.*?)$', r'        i. \1', text, flags=re.MULTILINE)
    
    # Handle mentions (@username)
    text = re.sub(r'@(\w+)', r'@\1', text)
    
    # Ensure proper spacing between sections
    text = re.sub(r'\n\n+', '\n\n', text)
    
    return text.strip() 