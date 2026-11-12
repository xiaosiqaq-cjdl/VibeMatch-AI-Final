
import os

import gradio as gr

from src.recommender import load_songs
from src.pipeline import run_ai_recommender

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SONGS = load_songs("data/songs_full.csv")


def recommend_music(user_request):
    if not user_request.strip():
        return "Please describe what music you want."

    try:
        result = run_ai_recommender(
            user_request,
            SONGS,
            defaults={}
        )

        if result.get("needs_clarification"):
            return (
                "### Could you tell me a little more?\n\n"
                "Are you looking for relaxing music to unwind, "
                "or energetic music to help you feel more awake?\n\n"
                "You can also tell me a genre you enjoy, "
                "like pop, jazz, or rock."
            )

        output = ["# Your VibeMatch Recommendations"]

        output.append("## Understood Preferences")

        for key, value in result["corrected_preferences"].items():
            if value is not None:
                output.append(f"- **{key}:** {value}")

        output.append("\n## Top 5 Songs")

        for index, song in enumerate(
            result["recommendations"], start=1
        ):
            output.append(
                f"### {index}. {song['title']}"
            )
            output.append(f"**Artist:** {song['artist']}")
            output.append(
                f"**Match Score:** {song['score']:.2f}/100"
            )

            reasons = song["reasons"]
            if isinstance(reasons, list):
                reasons = "; ".join(reasons)

            output.append(f"**Why:** {reasons}")
            output.append("---")

        return "\n\n".join(output)

    except Exception as exc:
        logger.exception("VibeMatch recommendation failed")
        return (
            "Unable to generate recommendations. "
            f"Error: {type(exc).__name__}. "
            "Please try a more specific music preference."
        )


demo = gr.Interface(
    fn=recommend_music,
    inputs=gr.Textbox(
        label="Describe your music preferences",
        placeholder="I want relaxing acoustic music for studying.",
        lines=2
    ),
    outputs=gr.Markdown(label="Recommendations"),
    title="VibeMatch AI",
    description=(
        "Discover music using a local LLM and "
        "an explainable recommendation algorithm."
    ),
    examples=[
        ["I want relaxing acoustic music."],
        ["Play energetic rock music."],
        ["Give me happy pop songs around 120 BPM."],
        ["I want calm jazz music."],
    ],
    concurrency_limit=1
)


if __name__ == "__main__":
    demo.launch(
        share=True,
        server_name="127.0.0.1",
        auth=(
            os.environ["VIBEMATCH_USER"],
            os.environ["VIBEMATCH_PASSWORD"]
        ),
        show_error=False
    )

