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

        response = client.chat_completion(
            messages=[
                {"role": "user", "content": query}
            ],
            max_tokens=150
        )

        return response.choices[0].message["content"]

    except Exception as e:
        return f"DEBUG: {str(e)}"