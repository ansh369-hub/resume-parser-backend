import json
import re

def extract_json(text: str) -> str:
    """
    Extract the largest JSON object from a string.
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in response")
    return match.group(0)

def repair_json(json_str: str) -> str:
    """
    Repair common LLM JSON issues.
    """
    # Remove trailing commas
    json_str = re.sub(r",\s*([}\]])", r"\1", json_str)

    # Replace smart quotes
    json_str = json_str.replace("“", "\"").replace("”", "\"")

    return json_str

def safe_json_loads(text: str) -> dict:
    extracted = extract_json(text)
    repaired = repair_json(extracted)
    return json.loads(repaired)
