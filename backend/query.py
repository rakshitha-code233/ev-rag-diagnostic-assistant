import os
import requests

def get_answer(query):
    try:
        API_URL = "https://router.huggingface.co/hf-inference/models/google/flan-t5-base"

        headers = {
            "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": query
        }

        response = requests.post(API_URL, headers=headers, json=payload)

        # 🔥 IMPORTANT DEBUG
        if response.status_code != 200:
            return f"Error: {response.text}"

        result = response.json()

        if isinstance(result, list):
            return result[0].get("generated_text", "No response")

        return str(result)

    except Exception as e:
        return f"Error: {str(e)}"