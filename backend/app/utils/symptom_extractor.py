import json
import re
import anthropic
from app.config import settings

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


async def extract_structured_symptoms(raw_text: str) -> dict:
    """Convert free-text symptoms into a structured JSON object using Claude."""
    prompt = f"""Extract structured medical information from this patient symptom description.
Return ONLY valid JSON, no other text.

Patient description: {raw_text}

Return this exact structure:
{{
    "primary_symptoms": ["list of main symptoms"],
    "duration": "how long symptoms have lasted",
    "severity": "mild/moderate/severe",
    "location": "body location if mentioned",
    "associated_symptoms": ["secondary symptoms"],
    "onset": "sudden/gradual",
    "aggravating_factors": ["what makes it worse"],
    "relieving_factors": ["what makes it better"],
    "relevant_history": "any mentioned medical history"
}}"""

    response = await _get_client().messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())
