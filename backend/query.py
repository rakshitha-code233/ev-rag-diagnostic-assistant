import os
from huggingface_hub import InferenceClient

client = InferenceClient(api_key=os.getenv("HF_API_KEY"))

def get_answer(query):
    try:
        response = client.text_generation(
            model="google/flan-t5-base",
            prompt=query,
            max_new_tokens=100
        )
        return response
    except Exception as e:
        return str(e)