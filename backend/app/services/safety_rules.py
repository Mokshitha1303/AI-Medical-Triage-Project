EMERGENCY_KEYWORDS = [
    "chest pain", "chest tightness", "heart attack",
    "can't breathe", "difficulty breathing", "shortness of breath",
    "stroke", "face drooping", "arm weakness", "speech difficulty",
    "unconscious", "unresponsive", "seizure",
    "suicidal", "want to die", "kill myself",
    "severe bleeding", "won't stop bleeding",
    "allergic reaction", "anaphylaxis", "throat closing",
    "overdose", "took too many pills",
]


def check_emergency_escalation(symptoms_text: str) -> dict | None:
    """
    Returns an escalation dict if any emergency keyword is detected.
    Runs BEFORE the AI pipeline — no LLM involved.
    """
    text_lower = symptoms_text.lower()
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text_lower:
            return {
                "urgency_level": "er",
                "trigger_keyword": keyword,
                "confidence_score": 1.0,
                "conditions_suggested": [],
                "reasoning": f"Emergency keyword detected: '{keyword}'",
                "recommended_actions": [
                    "Call 911 immediately",
                    "Go to the nearest emergency room",
                    "Do not drive yourself",
                ],
                "follow_up_questions": [],
                "disclaimer": "This is not a medical diagnosis. Call 911 or go to the ER immediately.",
                "bypassed_ai": True,
            }
    return None
