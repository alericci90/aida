import os
from openai import AzureOpenAI

endpoint = "https://aleri-mljnd89q-eastus2.cognitiveservices.azure.com/"
model_name = "gpt-4o-mini"
deployment = "gpt-4o-mini"

subscription_key = os.getenv("AZURE_OPENAI_KEY")
api_version = "2024-12-01-preview"

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
