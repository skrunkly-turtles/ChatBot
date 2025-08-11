from dotenv import load_dotenv, dotenv_values
import os
load_dotenv()
from openai import OpenAI
client = OpenAI(api_key = os.getenv("API_KEY"))

def chat_with_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = [{"role": "user", "content": prompt}],
        max_tokens=50
    )
    return response.choices[0].message.content.strip()

if __name__== "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            break
        response = chat_with_gpt(user_input)
        print("ChatBot: ", response)