# AIDA · Leasys Financial Index — mock-up

Dashboard Streamlit di presentazione: risultato del modello LFI (Run O, nucleo fisso) su 10 pratiche d'esempio e chat con l'AI Analyst.

    pip install -r requirements.txt
    streamlit run app.py

Per l'AI Analyst servono `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_API_VERSION`, letti da `new_azure_llm.py` (identico alla versione precedente) dalle variabili d'ambiente o da `st.secrets`. Le credenziali non sono nel codice: vanno configurate nell'ambiente in cui gira l'app (secrets dell'app su Streamlit Cloud, secrets del repository su Codespaces, `.streamlit/secrets.toml` in locale). Il modo piu' semplice e' copiare questi file nella cartella o nel repository dove la versione precedente funziona.

| File | Contenuto |
|---|---|
| `app.py` | Stesso template della versione precedente: Data Input, Customer Data, Financial Statement Indicators, Integrated Score (LFI), Indicator Results (10 indicatori), Radar, SHAP, AI Analyst, PDF |
| `objects.py` | Metadati: **scala delle classi (`LFI_CLASS_CUTS`)**, override, aree, indicatori, scheda del modello |
| `lfi_engine.py` | Lettura dei casi, classe di rischio, eta' del bilancio. Punto di innesto del motore di produzione |
| `functions.py` | Formattazione dei numeri, grafici, PDF |
| `funzione_ai_azure_eng.py` | Prompt di sistema, blocco dati del caso, analisi iniziale e chat |
| `style.py` | Tema (invariato) + stili dei componenti LFI in fondo |
| `repository_lfi/` | `cases.json` (10 casi), `portfolio.json` |
| `payline/` | Dati cliente per "Customer Data" (anagrafica, rapporti con Leasys, flotta): un `<case_id>.json` per caso, campi in `objects.CUSTOMER_FIELDS`. **Simulati** |
| `tools/build_cases.py` | Estrazione dei casi dal df_out: `python tools/build_cases.py <df_out.parquet> repository_lfi` |

Scala delle classi: 6 classi, tagli ufficiali sulla PD calibrata in `LFI_CLASS_CUTS` (`objects.py`). Dopo un cambio dei tagli rilanciare `tools/build_cases.py`, che sceglie i casi per classe.

## Dati reali e dati simulati
- **Dal parquet del modello (reali)**: voci di bilancio, 11 indicatori, PD calibrata e banda, sottoindici di famiglia, driver (SHAP), confronti con il segmento e con il portafoglio, settore, dimensione, eta' dell'azienda.
- **Simulati da `tools/build_cases.py` (realistici, non reali; seed fisso)**: nome, partita IVA (codice ufficio 999, inesistente) e id_bp (prefisso SIM); rapporti con Leasys e flotta, coerenti con la classe LFI, il tipo di cliente e l'eta' dell'azienda; PD dell'LFI sui due bilanci precedenti solo dove manca il dato reale.
- **Trend a 3 anni dello score integrato**: la PD sui bilanci precedenti e' quella del modello sulle pratiche precedenti della stessa azienda (stesso codice fiscale): reale per 28 punti su 30; i 2 mancanti (LFI-04 nel 2022, LFI-08 nel 2021) sono simulati. I casi sono scelti dando priorita' alle aziende con storico reale.
