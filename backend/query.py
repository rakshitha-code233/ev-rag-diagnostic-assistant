import os
import requests

def get_answer(query):
    try:
        API_URL = "https://router.huggingface.co/hf-inference/models/google/flan-t5-base"

        headers = {
            "Authorization": f"Bearer {os.getenv('HF_TOKEN')}"
        }

        payload = {
            "inputs": query
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()

        if isinstance(result, list):
            return result[0].get("generated_text", "No response")

        return str(result)

    except Exception as e:
        return f"Error: {str(e)}"