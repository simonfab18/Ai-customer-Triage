from app.integrations.gemini.client import extract_gemini_output_text


def test_extract_gemini_output_text_from_output_text() -> None:
    assert extract_gemini_output_text({"output_text": "{}"}) == "{}"


def test_extract_gemini_output_text_from_model_output_step() -> None:
    raw_output = {
        "steps": [
            {"type": "other", "content": [{"text": "ignore me"}]},
            {"type": "model_output", "content": [{"type": "text", "text": '{"priority":"high"}'}]},
        ]
    }

    assert extract_gemini_output_text(raw_output) == '{"priority":"high"}'


def test_extract_gemini_output_text_returns_none_when_missing() -> None:
    assert extract_gemini_output_text({"steps": []}) is None
