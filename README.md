# AIDA · Leasys Financial Index — mock-up

Dashboard Streamlit di presentazione: risultato del modello LFI (Run O, nucleo fisso) su 10 pratiche d'esempio e chat con l'AI Analyst.

    pip install -r requirements.txt
    streamlit run app.py

Per l'AI Analyst servono `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_API_VERSION`. `new_azure_llm.py` li cerca, nell'ordine, in: variabili d'ambiente, `st.secrets`, `.streamlit/secrets.toml` nella cartella dell'app, nelle cartelle superiori, nella cartella di lancio e nella home. Basta quindi il `secrets.toml` che usi gia' per la versione precedente, anche se sta in un'altra cartella del progetto. Senza credenziali la dashboard funziona e l'AI Analyst mostra quale chiave manca.

| File | Contenuto |
|---|---|
| `app.py` | Stesso template della versione precedente: Data Input, Customer Data, Financial Statement Indicators, Integrated Score (LFI), Indicator Results (10 indicatori), Radar, SHAP, AI Analyst, PDF |
| `objects.py` | Metadati: **scala delle classi (`LFI_CLASS_CUTS`)**, override, aree, indicatori, scheda del modello |
| `lfi_engine.py` | Lettura dei casi, classe di rischio, eta' del bilancio. Punto di innesto del motore di produzione |
| `functions.py` | Formattazione dei numeri, grafici, PDF |
| `funzione_ai_azure_eng.py` | Prompt di sistema, blocco dati del caso, analisi iniziale e chat |
| `style.py` | Tema (invariato) + stili dei componenti LFI in fondo |
| `repository_lfi/` | `cases.json` (10 casi), `portfolio.json` |
| `payline/` | Dati cliente per "Customer Data": un `<case_id>.json` per caso, formato del template. **Simulati** |
| `tools/build_cases.py` | Estrazione dei casi dal df_out: `python tools/build_cases.py <df_out.parquet> repository_lfi` |

Scala delle classi: 6 classi, tagli ufficiali sulla PD calibrata in `LFI_CLASS_CUTS` (`objects.py`). Dopo un cambio dei tagli rilanciare `tools/build_cases.py`, che sceglie i casi per classe.

## Dati reali e dati simulati
- **Dal parquet del modello (reali)**: voci di bilancio, 11 indicatori, PD calibrata e banda, sottoindici di famiglia, driver (SHAP), confronti con il segmento e con il portafoglio, settore, dimensione, eta' dell'azienda.
- **Simulati da `tools/build_cases.py` (realistici, non reali; seed fisso)**: nome e partita IVA (codice ufficio 999, inesistente), contratti attivi, outstanding e scaduto; PD dell'LFI sui due bilanci precedenti (trend a 3 anni dello score integrato).
