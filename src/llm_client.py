
from ollama import Client

MODEL_NAME = "qwen3:4b"


def get_llm_client():
    """Connect to the local Ollama server."""
    return Client(host="http://localhost:11434")


def check_model(client):
    """Check whether the required model is available."""
    models = client.list()

    installed = [
        model.model
        for model in models.models
    ]

    if MODEL_NAME not in installed:
        raise RuntimeError(
            f"Model {MODEL_NAME} is not installed. "
            f"Run: ollama pull {MODEL_NAME}"
        )

    return True
