# new_azure_llm.py
# Stessa connessione della versione originale (stesso modello e stessi parametri). Cambia solo DOVE si cercano le
# credenziali: oltre a variabili d'ambiente e st.secrets, anche i file .streamlit/secrets.toml della cartella
# dell'app, delle cartelle superiori e della cartella da cui si lancia streamlit. Cosi' l'app funziona anche se e'
# estratta in una cartella diversa da quella che contiene secrets.toml.
import os
import tomllib
from pathlib import Path

import streamlit as st
from openai import AzureOpenAI

_KEYS = ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_API_VERSION")


def _secrets_files() -> list[Path]:
    """File secrets.toml candidati: cartella dell'app e superiori, cartella di lancio, home."""
    here = Path(__file__).resolve().parent
    dirs = [here, *here.parents, Path.cwd(), *Path.cwd().parents, Path.home()]
    seen, out = set(), []
    for d in dirs:
        p = d / ".streamlit" / "secrets.toml"
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _find(data: dict, name: str):
    """Chiave al primo livello o dentro una sezione del toml."""
    if name in data:
        return data[name]
    for v in data.values():
        if isinstance(v, dict) and name in v:
            return v[name]
    return None


def _setting(name: str) -> str:
    # 1. variabile d'ambiente (Codespaces)
    v = os.getenv(name)
    if v:
        return v
    # 2. st.secrets (Streamlit Cloud, o secrets.toml nella cartella di lancio)
    try:
        v = st.secrets[name]
        if v:
            return v
    except Exception:
        pass
    # 3. secrets.toml in una delle cartelle candidate
    for p in _secrets_files():
        if p.exists():
            try:
                with open(p, "rb") as f:
                    v = _find(tomllib.load(f), name)
                if v:
                    return v
            except Exception:
                continue
    raise KeyError(f"{name} not found (environment variables, st.secrets, .streamlit/secrets.toml in the app "
                   f"folder, its parent folders, the launch folder and the home folder)")


endpoint = _setting("AZURE_OPENAI_ENDPOINT")
api_key = _setting("AZURE_OPENAI_API_KEY")
api_version = _setting("AZURE_OPENAI_API_VERSION")

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
