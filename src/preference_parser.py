
import json

from src.llm_client import get_llm_client, MODEL_NAME


# Define the output structure for the LLM
PREFERENCE_SCHEMA = {
    "type": "object",
    "properties": {
        "genre": {"type": ["string", "null"]},
        "mood": {"type": ["string", "null"]},
        "energy": {"type": ["number", "null"]},
        "tempo_bpm": {"type": ["number", "null"]},
        "valence": {"type": ["number", "null"]},
        "likes_acoustic": {"type": ["boolean", "null"]},
    },
    "required": [
        "genre", "mood", "energy",
        "tempo_bpm", "valence", "likes_acoustic"
    ],
    "additionalProperties": False,
}


def parse_user_preferences(user_request, client=None):
    """Extract structured preferences using a local LLM."""

    if not isinstance(user_request, str) or not user_request.strip():
        raise ValueError("User request cannot be empty.")

    if client is None:
        client = get_llm_client()

    
    system_prompt = """
    You are a strict music preference extractor.

    Your task is to convert a user's request into structured
    preferences for a music recommendation algorithm.

    IMPORTANT RULES:
    1. Extract every preference explicitly mentioned.
    2. Never invent preferences not supported by the request.
    3. If a preference is absent, return null.
    4. Do not recommend songs.
    5. Return only the required JSON object.



    SEMANTIC INTERPRETATION RULES:

    Distinguish between:
    1. The user's current emotional or physical state.
    2. The musical experience the user explicitly wants.
    3. A goal or desired effect expressed indirectly.

    You may infer a preference from a clear desired effect,
    even when no standard music adjective is used.

    Examples of desired effects:
    - Wanting to relax or decompress implies calm music.
    - Wanting to stay alert or become energized implies
      high-energy music.
    - Wanting to feel cheerful implies happy music.

    Do not infer a music preference from the user's
    current condition alone.

    Avoid adding unrelated attributes.
    For example, a desire for relaxing music does not
    automatically imply a specific genre or BPM.

    If the desired effect is clear, extract the corresponding
    preference. If the desired effect is ambiguous, use null.

    
    FIELD RULES:

    genre:
    - Extract any explicitly mentioned music genre.
    - Supported genres: pop, rock, jazz, classical,
      electronic, hip-hop, r-n-b, country, metal, ambient.
    - "acoustic" alone is NOT a genre.
    - If no supported genre is mentioned, return null.

    mood:
    - Allowed: happy, calm, intense, sad.
    - relaxing, peaceful, soothing -> calm
    - joyful, cheerful, upbeat -> happy
    - angry, aggressive -> intense
    - melancholic, depressing -> sad
    - "energetic" alone does NOT imply a mood.

    energy:
    - Extract the user's desired musical energy, not their current physical state.
    - High energy (0.8): energetic, powerful, exciting, uplifting,
        pump me up, give me energy, wake me up, lights me up,
        get me going, boost my energy.
    - Low energy (0.2): gentle, soft, low energy,
        mellow, wind down.
    - Understand natural paraphrases even when the exact
        keywords above are absent.
    - "I'm tired" alone does not specify desired music energy.
    - "I'm tired, play something to wake me up" implies
        high energy.
    - Do not infer energy from genre alone.
    - Return null if the desired energy is genuinely unclear.
```

    tempo_bpm:
    - Extract an explicitly stated numerical BPM.
    - Example: "around 120 BPM" -> 120
    - Never invent a BPM based on mood or activity.

    valence:
    - Extract only explicitly requested numerical valence.
    - Do not infer valence from mood or energy.

    likes_acoustic:
    - Explicitly wants acoustic -> true
    - Explicitly avoids acoustic -> false
    - Otherwise -> null
    - Do not infer acoustic preference from genre.

    EXAMPLES:

    Input: Play some happy pop music.
    Output:
    {"genre":"pop","mood":"happy","energy":null,
     "tempo_bpm":null,"valence":null,"likes_acoustic":null}

    Input: I want energetic rock music.
    Output:
    {"genre":"rock","mood":null,"energy":0.8,
     "tempo_bpm":null,"valence":null,"likes_acoustic":null}

    Input: Play music around 120 BPM.
    Output:
    {"genre":null,"mood":null,"energy":null,
     "tempo_bpm":120,"valence":null,"likes_acoustic":null}

    Input: Surprise me.
    Output:
    {"genre":null,"mood":null,"energy":null,
     "tempo_bpm":null,"valence":null,"likes_acoustic":null}
     Input: I'm looking for music that lights me up and gives me more energy.

    Output:
    {"genre":null,"mood":null,"energy":0.8,
    "tempo_bpm":null,"valence":null,"likes_acoustic":null}

    Input: I'm tired.
    Output:
    {"genre":null,"mood":null,"energy":null,
    "tempo_bpm":null,"valence":null,"likes_acoustic":null}
    """


    response = client.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_request},
        ],
        format=PREFERENCE_SCHEMA,
        think=True,
        options={"temperature": 0},
    )

    raw_output = response.message.content

    try:
        preferences = json.loads(raw_output)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError("LLM returned invalid JSON.") from exc

    if not isinstance(preferences, dict):
        raise ValueError("LLM must return a JSON object.")

    required_fields = set(PREFERENCE_SCHEMA["required"])

    if set(preferences) != required_fields:
        raise ValueError("LLM returned unexpected or missing fields.")

    allowed_moods = {"happy", "calm", "intense", "sad"}

    if preferences["mood"] is not None:
        if preferences["mood"] not in allowed_moods:
            raise ValueError("Unsupported mood.")

    for field in ("energy", "valence"):
        value = preferences[field]

        if value is not None:
            if type(value) not in (int, float) or not 0 <= value <= 1:
                raise ValueError(f"Invalid {field} value.")

    tempo = preferences["tempo_bpm"]
    if tempo is not None:
        if type(tempo) not in (int, float) or tempo <= 0:
            raise ValueError("Invalid tempo_bpm value.")

    if preferences["genre"] is not None:
        if not isinstance(preferences["genre"], str):
            raise ValueError("Invalid genre value.")

    acoustic = preferences["likes_acoustic"]
    if acoustic is not None and type(acoustic) is not bool:
        raise ValueError("Invalid likes_acoustic value.")

    return preferences
