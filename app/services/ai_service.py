import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:latest"


def ask_ai(question: str) -> str:
    """Send a question to the local Ollama model."""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful Office AI Assistant. "
                    "Answer clearly and professionally."
                )
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=180
        )

        response.raise_for_status()

        result = response.json()

        return result["message"]["content"]

    except requests.exceptions.RequestException as error:
        return f"Ollama connection error: {error}"


if __name__ == "__main__":
    question = "Hello! Introduce yourself as an Office AI Assistant."

    answer = ask_ai(question)

    print("\nAI Response:")
    print(answer)
