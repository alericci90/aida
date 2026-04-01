# new_azure_llm.py
import os
import openai

# 1. ELIMINA qualsiasi OPENAI_API_KEY messa da Codespaces/Streamlit
if "OPENAI_API_KEY" in os.environ:
    del os.environ["OPENAI_API_KEY"]

model_name = "gpt-4o-mini"
deployment = "gpt-4o-mini"

# 2. Rimuoviamo slash finale (bug noto)
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT").rstrip("/")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

# 3. Configurazione corretta per Cognitive Services
openai.api_type = "azure"
openai.api_base = endpoint
openai.api_key = subscription_key
openai.api_version = "2023-05-15"

def call_azure_llm(system_prompt: str, messages: list) -> str:
    response = openai.ChatCompletion.create(
        engine=deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            *messages
        ],
        max_tokens=4096,
        temperature=0.2,
        top_p=1.0
    )
    return response["choices"][0]["message"]["content"]
