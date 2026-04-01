# new_azure_llm.py
import os
import openai

# 1. RIMUOVI qualsiasi OPENAI_API_KEY creata da Codespaces/Streamlit
#    (questa è LA causa del tuo errore)
if "OPENAI_API_KEY" in os.environ:
    print("⚠️  Rimozione OPENAI_API_KEY trovata nell'ambiente!")
    del os.environ["OPENAI_API_KEY"]

model_name = "gpt-4o-mini"
deployment = "gpt-4o-mini"

# 2. Endpoint e chiave (li hai verificati e sono ok)
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

# 3. Configurazione COMPATIBILE con Cognitive Services (openai==0.28.1)
openai.api_type = "azure"
openai.api_base = endpoint.rstrip("/")  # rimuove slash finale per sicurezza
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
