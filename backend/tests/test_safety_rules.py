import pytest
from app.services.safety_rules import check_emergency_escalation


def test_chest_pain_triggers_er():
    result = check_emergency_escalation("I have severe chest pain and can't breathe")
    assert result is not None
    assert result["urgency_level"] == "er"
    assert result["confidence_score"] == 1.0
    assert result["bypassed_ai"] is True


def test_stroke_keywords():
    for text in ["face drooping on one side", "sudden arm weakness", "having trouble with speech difficulty"]:
        result = check_emergency_escalation(text)
        assert result is not None, f"Expected ER escalation for: {text}"
        assert result["urgency_level"] == "er"


def test_suicidal_ideation():
    result = check_emergency_escalation("I feel suicidal and don't want to go on")
    assert result is not None
    assert result["urgency_level"] == "er"


def test_overdose():
    result = check_emergency_escalation("I think I overdose on my medication")
    assert result is not None
    assert result["urgency_level"] == "er"


def test_benign_symptoms_not_escalated():
    for text in [
        "I have a mild headache for two days",
        "runny nose and sore throat since yesterday",
        "I twisted my ankle playing basketball",
    ]:
        result = check_emergency_escalation(text)
        assert result is None, f"Expected no escalation for: {text}"


def test_case_insensitive():
    result = check_emergency_escalation("CHEST PAIN radiating to my left arm")
    assert result is not None
    assert result["urgency_level"] == "er"


def test_escalation_includes_recommended_actions():
    result = check_emergency_escalation("I have an allergic reaction, throat closing")
    assert result is not None
    assert len(result["recommended_actions"]) > 0
    assert any("911" in a for a in result["recommended_actions"])
