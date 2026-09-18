from openai import OpenAI

from app.clients.base import BaseAdapter
from app.models.llm import ApplicationRequest, ApplicationResult

client = OpenAI(api_key="YOUR_API_KEY", base_url="https://api.openai.com/v1")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! Can you help me with a question?"},
    ],
)

content = response.choices[0].message.content


class DeepSeekAdapter(BaseAdapter):
    api_key: str
    model: str

    def send(self, request: ApplicationRequest) -> ApplicationResult:
        pass
