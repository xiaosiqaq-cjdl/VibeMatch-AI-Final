
from types import SimpleNamespace

import pytest

from src.preference_parser import parse_user_preferences


class FakeClient:
    """Simulate Ollama without calling a real model."""

    def __init__(self, response_text):
        self.response_text = response_text

    def chat(self, **kwargs):
        return SimpleNamespace(
            message=SimpleNamespace(content=self.response_text)
        )


VALID_RESPONSE = """
{
    "genre": null,
    "mood": "calm",
    "energy": null,
    "tempo_bpm": null,
    "valence": null,
    "likes_acoustic": true
}
"""


def test_valid_preferences():
    client = FakeClient(VALID_RESPONSE)

    result = parse_user_preferences(
        "I want relaxing acoustic music.",
        client=client
    )

    assert result["mood"] == "calm"
    assert result["likes_acoustic"] is True
    assert result["genre"] is None


def test_empty_request():
    with pytest.raises(ValueError, match="cannot be empty"):
        parse_user_preferences("")


def test_invalid_json():
    client = FakeClient("This is not JSON")

    with pytest.raises(ValueError, match="invalid JSON"):
        parse_user_preferences(
            "I want pop music.",
            client=client
        )


def test_unsupported_mood():
    response = VALID_RESPONSE.replace(
        '"calm"', '"excited"'
    )
    client = FakeClient(response)

    with pytest.raises(ValueError, match="Unsupported mood"):
        parse_user_preferences(
            "I want exciting music.",
            client=client
        )


def test_invalid_energy():
    response = VALID_RESPONSE.replace(
        '"energy": null', '"energy": 1.5'
    )
    client = FakeClient(response)

    with pytest.raises(ValueError, match="Invalid energy"):
        parse_user_preferences(
            "I want energetic music.",
            client=client
        )
