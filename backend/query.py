import os
from groq import Groq

def get_answer(query):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # ✅ NEW MODEL
            messages=[
                {"role": "user", "content": query}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"