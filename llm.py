from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

def chat(query: str):
    response = client.chat.completions.create(
        model="Meta-Llama-3.3-70B-Instruct",
        messages=[{"role":"system","content":"You are a helpful assistant"},{"role":"user","content":query}]
    )

    return response.choices[0].message.content