import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("API_KEY"),
)

# История сообщений
messages = [
    {"role": "system", "content": "Ты помощник по юридическим делам, отвечай кратко и по делу"},
    {"role": "user", "content": "Привет!"},
    {"role": "assistant", "content": "Привет! Рад помочь."},
    {"role": "user", "content": "Кто  ты?"}
]

completion = client.chat.completions.create(
    model="openai/gpt-oss-20b:free",
    messages=messages
)

print(completion.choices[0].message.content.split("assistantfinal")[-1].strip())