import os
from huggingface_hub import InferenceClient

def get_answer(query):
    try:
        token = os.getenv("HF_TOKEN")

        if not token:
            return "Error: API key not found"

        client = InferenceClient(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            token=token
        )

        response = client.text_generation(
            query,
            max_new_tokens=150
        )

        return response

    except Exception as e:
        return f"DEBUG: {str(e)}"