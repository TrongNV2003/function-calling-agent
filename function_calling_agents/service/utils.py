import re
import json
from typing import Dict
from loguru import logger


def parse_response(text: str) -> Dict:
    """Parse response with JSON format from LLM
    
    Args:
        text: JSON format response
        
    Returns: 
        Dict: parsed data
    """
    pattern_think = r"<think>\n(.*?)</think>"
    match = re.search(pattern_think, text, re.DOTALL)
    if match:
        json_text = match.group(1)
        return json.loads(json_text)

    pattern_output = r"<output>\n(.*?)</output>"
    match = re.search(pattern_output, text, re.DOTALL)
    if match:
        json_text = match.group(1)
        return json.loads(json_text)

    pattern_action = r"<action>\n(.*?)</action>"
    match = re.search(pattern_action, text, re.DOTALL)
    if match:
        json_text = match.group(1)
        return json.loads(json_text)

    pattern_observe = r"<observe>\n(.*?)</observe>"
    match = re.search(pattern_observe, text, re.DOTALL)
    if match:
        json_text = match.group(1)
        return json.loads(json_text)

    logger.error(f"=== Lỗi: Response: {text} ===")
    raise ValueError("Response không hợp lệ từ LLM")

