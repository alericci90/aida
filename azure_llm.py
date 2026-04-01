import os
from openai import AzureOpenAI

model_name = "gpt-4o-mini"
deployment = "gpt-4o-mini"

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)


def call_azure_llm(system_prompt: str, messages: list) -> str:
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            *messages
        ],
        max_tokens=4096,
        temperature=0.2,
        top_p=1.0,
        model=deployment
    )

    return response.choices[0].message.content
