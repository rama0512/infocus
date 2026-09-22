from app.parser import parse_prediction


PREDICTION_TEXT = """
CHEATING_DETECTED: YES
CONFIDENCE: HIGH
PROBABILITY: 95%
VIOLATION: AI_ASSISTANT
REASON: AI assistant interface detected.
"""


def test_parses_key_value_block():
    result = parse_prediction(PREDICTION_TEXT)

    assert result == {
        "CHEATING_DETECTED": "YES",
        "CONFIDENCE": "HIGH",
        "PROBABILITY": "95%",
        "VIOLATION": "AI_ASSISTANT",
        "REASON": "AI assistant interface detected.",
    }


def test_none_and_empty_return_none():
    assert parse_prediction(None) is None
    assert parse_prediction("") is None


def test_lines_without_colon_are_skipped():
    result = parse_prediction("garbage line\nCONFIDENCE: LOW\n")

    assert result == {"CONFIDENCE": "LOW"}


def test_value_keeps_everything_after_first_colon():
    result = parse_prediction("REASON: seen at 12:00 on tab 2")

    assert result == {"REASON": "seen at 12:00 on tab 2"}
