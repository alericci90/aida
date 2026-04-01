# new_azure_llm.py
import os
import streamlit as st
from openai import AzureOpenAI

# ✅ Leggi i secrets (Streamlit Cloud) o environment variables (Codespaces)
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or st.secrets["AZURE_OPENAI_ENDPOINT"]
api_key = os.getenv("AZURE_OPENAI_API_KEY") or st.secrets["AZURE_OPENAI_API_KEY"]
api_version = os.getenv("AZURE_OPENAI_API_VERSION") or st.secrets["AZURE_OPENAI_API_VERSION"]

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version=api_version
)

def call_azure_llm(system_prompt: str, messages: list) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            *messages
        ],
        max_tokens=4096,
        temperature=0.2,
        top_p=1.0
    )
    return response.choices[0].message.content
