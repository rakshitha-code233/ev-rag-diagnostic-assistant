from groq import Groq

client = Groq(api_key="YOUR_GROQ_API_KEY")

def ask_ai(question):
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are an EV diagnostic assistant."},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content
    except:
        return "⚠️ AI not working. Check API key."