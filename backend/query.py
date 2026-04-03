import os
from huggingface_hub import InferenceClient

def get_answer(query):
    try:
        token = os.getenv("HF_TOKEN")

        client = InferenceClient(
            model="google/flan-t5-base",   # ✅ WORKS FREE
            token=token
        )

        response = client.text_generation(
            query,
            max_new_tokens=100
        )

        return response

    except Exception as e:
        return f"DEBUG: {str(e)}"