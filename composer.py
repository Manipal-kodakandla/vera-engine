
import os
from google import genai

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def call_model(prompt):
    models = ["gemini-2.0-flash", "gemini-2.5-flash"]

    for model in models:
        try:
            print(f"Using model: {model}")
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response
        except Exception as e:
            print(f"Failed with {model}: {e}")

    return None


def extract_text(response):
    try:
        if response and response.text:
            return response.text
        return response.candidates[0].content.parts[0].text
    except:
        return None


def generate_message(prompt):
    response = call_model(prompt)

    if not response:
        return None

    output = extract_text(response)

    if not output:
        return None

    output = output.replace("```json", "").replace("```", "").strip()

    return output