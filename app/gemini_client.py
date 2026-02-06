import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

class GeminiClient:
    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )
        self.model = "gemini-2.5-flash"

    def generate_json(self, system_prompt: str, user_prompt: str) -> str:
        prompt = f"""
{system_prompt}

USER INPUT:
{user_prompt}

RULES:
- Return ONLY valid JSON
- No markdown
- No explanations
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        )

        return response.text.strip()
