import os
from huggingface_hub import InferenceClient

api_key = os.getenv("HF_API_KEY")

def get_answer(query):
    if not api_key:
        return "Error: API key not found"

    try:
        client = InferenceClient(api_key=api_key)

        response = client.text_generation(
            model="google/flan-t5-small",  # lighter model
            prompt=query,
            max_new_tokens=100
        )

        return response.strip() if response else "No response from model"

    except Exception as e:
        return f"Error: {str(e)}"