import json
import re

import anthropic

import config

SYSTEM_PROMPT = """You are a precise meeting assistant.
Return ONLY valid JSON with this exact structure, and nothing else \
(no markdown fences, no commentary):

{
  "title": "short title <= 80 chars",
  "summary": "clean 1-2 paragraph summary",
  "key_decisions": ["decision 1", "decision 2"],
  "action_items": [
    {
      "owner": "Name or 'Unassigned'",
      "task": "clear actionable task",
      "due_date": "YYYY-MM-DD or null"
    }
  ]
}"""


def _extract_json(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return json.loads(cleaned)


def reason_over_transcript(transcript: str) -> dict:
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    message = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"TRANSCRIPT:\n{transcript}"}],
    )

    raw_text = message.content[0].text
    try:
        data = _extract_json(raw_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Claude did not return valid JSON. Raw response:\n{raw_text}"
        ) from exc

    data.setdefault("key_decisions", [])
    data.setdefault("action_items", [])

    print(f"[LLM] Generated {len(data['action_items'])} action item(s)")
    return data