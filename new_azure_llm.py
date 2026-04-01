# new_azure_llm.py
import os
import openai

model_name = "gpt-4o-mini"
deployment = "gpt-4o-mini"

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

openai.api_type = "azure"
openai.api_base = endpoint  # Endpoint cognitive-services
openai.api_key = subscription_key
openai.api_version = "2023-05-15"  # versione compatibile

def call_azure_llm(system_prompt: str, messages: list) -> str:
    response = openai.ChatCompletion.create(
        engine=deployment,      # per cognitive services
        messages=[
            {"role": "system", "content": system_prompt},
            *messages
        ],
        max_tokens=4096,
        temperature=0.2,
        top_p=1.0
    )
    return response["choices"][0]["message"]["content"]