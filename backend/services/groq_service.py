"""
Groq service layer.

Handles note generation from a transcript using the Groq API.
"""

import json
import os

from groq import Groq


def generate_notes_from_transcript(transcript_text: str) -> dict:
    """
    Generate structured notes from a transcript using Groq.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You convert lecture transcripts into structured study notes."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Return valid JSON only with this exact shape:\n"
                    "{\n"
                    '  "summary": "string",\n'
                    '  "topics": ["string"],\n'
                    '  "action_items": ["string"]\n'
                    "}\n\n"
                    f"Transcript:\n{transcript_text}"
                ),
            },
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content
    return json.loads(content)
