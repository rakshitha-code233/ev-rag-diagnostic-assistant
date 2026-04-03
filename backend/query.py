import os
from huggingface_hub import InferenceClient

def get_answer(query):
    try:
        token = os.getenv("HF_TOKEN")

        client = InferenceClient(
            model="HuggingFaceH4/zephyr-7b-beta",   # ✅ FREE WORKING MODEL
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