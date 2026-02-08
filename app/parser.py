import fitz
from pathlib import Path
from app.gemini_client import GeminiClient

from app.resume_schema import Resume
from app.json_utils import safe_json_loads
from app.json_normalizer import normalize_resume_json

SYSTEM_PROMPT = """
You are a deterministic resume parsing engine.

Your task is to convert raw resume text into a STRICTLY VALID JSON object
that EXACTLY follows the schema provided below.

========================
CRITICAL INSTRUCTIONS
========================

1. OUTPUT FORMAT
- Output MUST be a single JSON object.
- Do NOT include markdown, comments, explanations, or extra text.
- Do NOT wrap JSON in ``` or any other formatting.
- JSON MUST be syntactically valid (double quotes, no trailing commas).

2. SCHEMA COMPLIANCE (NON-NEGOTIABLE)
- The output JSON MUST contain ALL keys defined in the schema.
- If a value is missing in the resume, use an empty string "" or empty array [].
- NEVER omit a key.
- NEVER rename keys.
- NEVER change data types.

3. FACTUAL INTEGRITY
- Do NOT invent facts, numbers, companies, dates, or achievements.
- Only extract or lightly normalize what is present in the resume text.
- If information is unclear or absent, leave the field empty.

4. NORMALIZATION RULES
- Convert bullet points into clean, readable sentences.
- Remove symbols like •, –, |, emojis, and decorative characters.
- Normalize dates to readable strings (e.g., "Jan 2022 – Mar 2023").
- Technologies must be split into arrays (comma-separated → list).

5. FIELD-SPECIFIC RULES

- "name": Person’s full name only.
- "email": Valid email if present, else "".
- "phone": Phone number as text, else "".
- "linkedin": Full LinkedIn profile URL if present, else "".
- "github": Full GitHub profile URL if present, else "".
- "location": City/State/Country if present, else "".
- "work_experience": The total work experience of this candidate as a string
  (e.g., "2 years of experience in web development in this company at this post, etc"), else "".
- "job_roles": Infer likely job roles based on experience, skills, and projects
  (e.g., ["Software Engineer", "Backend Developer"]).
- "summary": 2–3 line professional summary extracted or lightly rewritten
  from the resume profile/objective section. Do NOT invent claims.
- "skills": Group skills into logical categories if possible
  (e.g., Languages, Frameworks, Tools). If unclear, use a single category "General".
- "experience": Each entry should represent a distinct role or internship.
- "projects": Each project MUST have:
  - name (string)
  - description (single string, NOT a list)
  - technologies (array of strings)
- "education": Each entry MUST include all schema fields, even if empty.
- "certifications": List of certifications, courses, or licenses.
- "achievements": Academic ranks, awards, scholarships, hackathon wins, etc.

6. ERROR PREVENTION
- NEVER output lists where a string is required.
- NEVER output strings where an array is required.
- NEVER nest objects incorrectly.
- If unsure, prefer empty values over guessing.

========================
SCHEMA (FIXED)
========================

{
  "name": "string",
  "email": "string",
  "phone": "string",
  "linkedin": "string",
  "github": "string",
  "location": "string",
  "work_experience": "string",
  "job_roles": [],
  "summary": "string",
  "skills": {},
  "experience": [],
  "projects": [
    {
      "name": "string",
      "description": "string",
      "technologies": []
    }
  ],
  "education": [
    {
      "degree": "string",
      "institution": "string",
      "start_date": "string",
      "end_date": "string",
      "cgpa": "string"
    }
  ],
  "certifications": [],
  "achievements": []
}

========================
INPUT
========================
You will now be given raw resume text.

Parse it carefully and produce the JSON output exactly as specified.

"""

USER_PROMPT_TEMPLATE = """
You are given raw resume text below.

Your task is to extract and structure the information strictly according to the provided schema and rules.

IMPORTANT:
- Use ONLY the information present in the resume text.
- If any field is missing or unclear, leave it empty ("") or as an empty array ([]).
- Do NOT invent or assume details.
- Follow the schema EXACTLY.
- Return ONLY a valid JSON object.

========================
RESUME TEXT
========================
{text}
"""


MAX_RETRIES = 3


def extract_text(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    return "\n".join(page.get_text() for page in doc)


def parse_resume_pdf(pdf_path: Path) -> dict:
    """
    Core resume parsing function.
    - Input: Path to PDF
    - Output: Parsed resume as dict
    """
    text = extract_text(pdf_path)
    client = GeminiClient()

    user_prompt = USER_PROMPT_TEMPLATE.format(text=text)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.generate_json(SYSTEM_PROMPT, user_prompt)
        except Exception as api_exc:
            if "RESOURCE_EXHAUSTED" in str(api_exc) or "429" in str(api_exc):
                raise RuntimeError(
                    "Gemini API quota exhausted. Please retry later."
                )
            continue

        try:
            raw = safe_json_loads(response)
            normalized = normalize_resume_json(raw)
            parsed = Resume.model_validate(normalized)
            return parsed.model_dump()

        except Exception as e:
          print("=" * 60)
          print(f"Parse attempt {attempt} failed")
          print("Error:", repr(e))
          print("Raw LLM output:")
          print(response)
          print("=" * 60)
