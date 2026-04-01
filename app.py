# %% app_eng
# streamlit run D:\users\TA16669\PycharmProjects\PythonProject\dashboard\app_azure_eng.py
# ".\dashboard\logo.png"
import json
import numpy as np
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import tempfile

from functions import (
    commento_trend_intelligente_eng, genera_pdf_leasys, sparkline, classe_struttura, classe_liquidita, classe_leva,
    classe_cashflow, classe_profit, classe_cagr, badge, commento_score_integrato_eng, commento_cagr_ricavi_eng)
from funzione_ai_azure_eng import bilancio_ai_component_eng
from objects import (DESCRIZIONI_eng, DESCRIZIONE_INTEGRATO_eng, radar_labels_eng, colori_classi_radar,
                               descr_cagr_eng)

# %% dashboard
# CONFIG
st.set_page_config(page_title="Financial Index Dashboard", layout="wide")
LEASYS_BLUE = "#1F3556"


# CSS + FONT
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap');
html, body, [class*="css"] {{
    font-family: 'Lato', sans-serif;
    color: {LEASYS_BLUE};
}}
h1,h2,h3,h4 {{ color:{LEASYS_BLUE}; font-weight:700; }}
</style>
""", unsafe_allow_html=True)


# HEADER
# col_logo, col_title = st.columns([2, 4])

# with col_logo:
#     st.image(".\\dashboard\\logo_nuovo.png", use_container_width=True)

st.markdown(
    """
    <style>
    img {
        max-width: 850px !important;
        height: auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="center-logo">', unsafe_allow_html=True)
st.image("logo_nuovo.png", use_container_width=False)
st.markdown('</div>', unsafe_allow_html=True)


# st.markdown(
#     """
#     <h1 style="text-align: center; line-height: 1; font-size: 60px;">
#         Financial Index Dashboard
#     </h1>
#     """,
#     unsafe_allow_html=True
# )

st.divider()


# MODALITÀ INPUT
st.header("📥 Entering Financial Statement Data")

modalita = st.radio("Mode:", ["Companies DB", "Upload Excel", "Manual Entry"])

if "submitted" not in st.session_state:
    st.session_state.submitted = False


# INPUT MANUALE
if modalita == "Manual Entry":
    with st.form("manuale"):
        pn = st.number_input("Net worth")
        pn_1 = st.number_input("Net worth from 1 previous financial statement")
        pn_2 = st.number_input("Net worth from 2 previous financial statements")

        attivo = st.number_input("Total assets")
        attivo_1 = st.number_input("Total assets from 1 previous financial statement")
        attivo_2 = st.number_input("Total assets from 2 previous financial statements")

        att_breve = st.number_input("Current assets")
        att_breve_1 = st.number_input("Current assets from 1 previous financial statement")
        att_breve_2 = st.number_input("Current assets from 2 previous financial statements")

        pass_breve = st.number_input("Current liabilities")
        pass_breve_1 = st.number_input("Current liabilities from 1 previous financial statement")
        pass_breve_2 = st.number_input("Current liabilities from 2 previous financial statements")

        debiti = st.number_input("Total debts")
        debiti_1 = st.number_input("Total debts from 1 previous financial statement")
        debiti_2 = st.number_input("Total debts from 2 previous financial statements")

        liquidita = st.number_input("Liquidity")
        liquidita_1 = st.number_input("Liquidity from 1 previous financial statement")
        liquidita_2 = st.number_input("Liquidity from 2 previous financial statements")

        ebitda = st.number_input("EBITDA")
        ebitda_1 = st.number_input("EBITDA from 1 previous financial statement")
        ebitda_2 = st.number_input("EBITDA from 2 previous financial statements")

        cf = st.number_input("Cash flow")
        cf_1 = st.number_input("Cash flow from 1 previous financial statement")
        cf_2 = st.number_input("Cash flow from 2 previous financial statements")

        oneri = st.number_input("Financial payables")
        oneri_1 = st.number_input("Financial payables from 1 previous financial statement")
        oneri_2 = st.number_input("Financial payables from 2 previous financial statements")

        ricavi = st.number_input("Revenue")
        ricavi_1 = st.number_input("Revenue from 1 previous financial statement")
        ricavi_2 = st.number_input("Revenue from 2 previous financial statements")

        submitted = st.form_submit_button("Calculate the Score")


# INPUT FILE EXCEL
elif modalita == "Upload Excel":
    file = st.file_uploader(
        "Upload Excel file (.xlsx) – sheet: 'input CEE'",
        type=["xlsx"]
    )

    if file:
        try:
            df = pd.read_excel(
                file,
                sheet_name="input CEE",
                header=None
            )

            df = df.fillna(0)

            # LETTURA CELLE
            # ULTIMO ANNO
            anno_bil = df.iloc[0, 3]

            pn = df.iloc[2, 8]  # I3
            pn_1 = df.iloc[2, 7]
            pn_2 = df.iloc[2, 6]

            attivo = df.iloc[83, 3]  # D84
            attivo_1 = df.iloc[83, 2]
            attivo_2 = df.iloc[83, 1]

            att_breve = (
                    df.iloc[38, 3] + df.iloc[46, 3] + df.iloc[49, 3] + df.iloc[52, 3] + df.iloc[54, 3] +
                    df.iloc[56, 3] + df.iloc[59, 3] + df.iloc[62, 3] + df.iloc[64, 3] + df.iloc[73, 3]
            )
            att_breve_1 = (
                    df.iloc[38, 2] + df.iloc[46, 2] + df.iloc[49, 2] + df.iloc[52, 2] + df.iloc[54, 2] +
                    df.iloc[56, 2] + df.iloc[59, 2] + df.iloc[62, 2] + df.iloc[64, 2] + df.iloc[73, 2]
            )
            att_breve_2 = (
                    df.iloc[38, 1] + df.iloc[46, 1] + df.iloc[49, 1] + df.iloc[52, 1] + df.iloc[54, 1] +
                    df.iloc[56, 1] + df.iloc[59, 1] + df.iloc[62, 1] + df.iloc[64, 1] + df.iloc[73, 1]
            )

            pass_breve = (
                    df.iloc[36, 8] + df.iloc[39, 8] + df.iloc[42, 8] + df.iloc[45, 8] + df.iloc[48, 8] +
                    df.iloc[51, 8] + df.iloc[54, 8] + df.iloc[57, 8] + df.iloc[60, 8] + df.iloc[63, 8] +
                    df.iloc[66, 8] + df.iloc[69, 8]
            )
            pass_breve_1 = (
                    df.iloc[36, 7] + df.iloc[39, 7] + df.iloc[42, 7] + df.iloc[45, 7] + df.iloc[48, 7] +
                    df.iloc[51, 7] + df.iloc[54, 7] + df.iloc[57, 7] + df.iloc[60, 7] + df.iloc[63, 7] +
                    df.iloc[66, 7] + df.iloc[69, 7]
            )
            pass_breve_2 = (
                    df.iloc[36, 6] + df.iloc[39, 6] + df.iloc[42, 6] + df.iloc[45, 6] + df.iloc[48, 6] +
                    df.iloc[51, 6] + df.iloc[54, 6] + df.iloc[57, 6] + df.iloc[60, 6] + df.iloc[63, 6] +
                    df.iloc[66, 6] + df.iloc[69, 6]
            )

            debiti = df.iloc[34, 8]  # I35
            debiti_1 = df.iloc[34, 7]
            debiti_2 = df.iloc[34, 6]

            liquidita = (
                    df.iloc[73, 3] + df.iloc[46, 3] + df.iloc[49, 3] + df.iloc[52, 3] + df.iloc[54, 3] +
                    df.iloc[56, 3] + df.iloc[59, 3] + df.iloc[62, 3] + df.iloc[64, 3]
            )
            liquidita_1 = (
                    df.iloc[73, 2] + df.iloc[46, 2] + df.iloc[49, 2] + df.iloc[52, 2] + df.iloc[54, 2] +
                    df.iloc[56, 2] + df.iloc[59, 2] + df.iloc[62, 2] + df.iloc[64, 2]
            )
            liquidita_2 = (
                    df.iloc[73, 1] + df.iloc[46, 1] + df.iloc[49, 1] + df.iloc[52, 1] + df.iloc[54, 1] +
                    df.iloc[56, 1] + df.iloc[59, 1] + df.iloc[62, 1] + df.iloc[64, 1]
            )

            ebitda = (
                    df.iloc[92, 3] + df.iloc[93, 3] + df.iloc[94, 3] + df.iloc[95, 3] - df.iloc[113, 3] -
                    df.iloc[99, 3] + df.iloc[96, 3] - df.iloc[116, 3] -df.iloc[100, 3] - df.iloc[102, 3] -
                    df.iloc[101, 3]
            )
            ebitda_1 = (
                    df.iloc[92, 2] + df.iloc[93, 2] + df.iloc[94, 2] + df.iloc[95, 2] - df.iloc[113, 2] -
                    df.iloc[99, 2] + df.iloc[96, 2] - df.iloc[116, 2] -df.iloc[100, 2] - df.iloc[102, 2] -
                    df.iloc[101, 2]
            )
            ebitda_2 = (
                    df.iloc[92, 1] + df.iloc[93, 1] + df.iloc[94, 1] + df.iloc[95, 1] - df.iloc[113, 1] -
                    df.iloc[99, 1] + df.iloc[96, 1] - df.iloc[116, 1] -df.iloc[100, 1] - df.iloc[102, 1] -
                    df.iloc[101, 1]
            )

            cf = df.iloc[159, 3] + df.iloc[114, 3]  # D160 + D115
            cf_1 = df.iloc[159, 2] + df.iloc[114, 2]
            cf_2 = df.iloc[159, 1] + df.iloc[114, 1]

            oneri = (
                    df.iloc[35, 8] + df.iloc[38, 8] + df.iloc[41, 8] + df.iloc[44, 8] + df.iloc[59, 8]
            )
            oneri_1 = (
                    df.iloc[35, 7] + df.iloc[38, 7] + df.iloc[41, 7] + df.iloc[44, 7] + df.iloc[59, 7]
            )
            oneri_2 = (
                    df.iloc[35, 6] + df.iloc[38, 6] + df.iloc[41, 6] + df.iloc[44, 6] + df.iloc[59, 6]
            )

            ricavi = df.iloc[92, 3]  # D93
            ricavi_1 = df.iloc[92, 2]
            ricavi_2 = df.iloc[92, 1]

            st.session_state.submitted = True
            st.success("Excel File uploaded correctly")

        except Exception as e:
            st.error(f"Error in the file reading: {e}")


# INPUT AZIENDE SALVATE
elif modalita == "Companies DB":
    repo_path = Path("./repository_aziende")

    if not repo_path.exists():
        st.error("La cartella './repository_aziende' non esiste. Creala e inserisci i file Excel.")
    else:
        excel_files = list(repo_path.glob("*.xlsx"))

        if not excel_files:
            st.warning("Nessuna azienda trovata nella repository.")
        else:
            company_names = [f.stem for f in excel_files]

            # inizializza lo stato
            if "selected_company" not in st.session_state:
                st.session_state.selected_company = None    

            # selectbox sincronizzata allo stato
            selected_company = st.selectbox(
                "Select a company from repository:",
                company_names,
                index=company_names.index(st.session_state.selected_company)
                    if st.session_state.selected_company in company_names
                    else 0
            )

            # aggiorna sempre lo stato appena cambia selezione
            st.session_state.selected_company = selected_company

            # ✅ Form per evitare refresh UI violento
            with st.form("load_company_form"):
                submit_company = st.form_submit_button("Load Company Data")

            if submit_company:
                st.session_state.selected_company = selected_company

                file_path = repo_path / f"{selected_company}.xlsx"

                try:
                    df = pd.read_excel(file_path, sheet_name="input CEE", header=None)
                    df = df.fillna(0)


                    # LETTURA CELLE
                    # ULTIMO ANNO
                    st.session_state.anno_bil = df.iloc[0, 3]

                    st.session_state.pn = df.iloc[2, 8]  # I3
                    st.session_state.pn_1 = df.iloc[2, 7]
                    st.session_state.pn_2 = df.iloc[2, 6]

                    st.session_state.attivo = df.iloc[83, 3]  # D84
                    st.session_state.attivo_1 = df.iloc[83, 2]
                    st.session_state.attivo_2 = df.iloc[83, 1]

                    st.session_state.att_breve = (
                            df.iloc[38, 3] + df.iloc[46, 3] + df.iloc[49, 3] + df.iloc[52, 3] + df.iloc[54, 3] +
                            df.iloc[56, 3] + df.iloc[59, 3] + df.iloc[62, 3] + df.iloc[64, 3] + df.iloc[73, 3]
                    )
                    st.session_state.att_breve_1 = (
                            df.iloc[38, 2] + df.iloc[46, 2] + df.iloc[49, 2] + df.iloc[52, 2] + df.iloc[54, 2] +
                            df.iloc[56, 2] + df.iloc[59, 2] + df.iloc[62, 2] + df.iloc[64, 2] + df.iloc[73, 2]
                    )
                    st.session_state.att_breve_2 = (
                            df.iloc[38, 1] + df.iloc[46, 1] + df.iloc[49, 1] + df.iloc[52, 1] + df.iloc[54, 1] +
                            df.iloc[56, 1] + df.iloc[59, 1] + df.iloc[62, 1] + df.iloc[64, 1] + df.iloc[73, 1]
                    )

                    st.session_state.pass_breve = (
                            df.iloc[36, 8] + df.iloc[39, 8] + df.iloc[42, 8] + df.iloc[45, 8] + df.iloc[48, 8] +
                            df.iloc[51, 8] + df.iloc[54, 8] + df.iloc[57, 8] + df.iloc[60, 8] + df.iloc[63, 8] +
                            df.iloc[66, 8] + df.iloc[69, 8]
                    )
                    st.session_state.pass_breve_1 = (
                            df.iloc[36, 7] + df.iloc[39, 7] + df.iloc[42, 7] + df.iloc[45, 7] + df.iloc[48, 7] +
                            df.iloc[51, 7] + df.iloc[54, 7] + df.iloc[57, 7] + df.iloc[60, 7] + df.iloc[63, 7] +
                            df.iloc[66, 7] + df.iloc[69, 7]
                    )
                    st.session_state.pass_breve_2 = (
                            df.iloc[36, 6] + df.iloc[39, 6] + df.iloc[42, 6] + df.iloc[45, 6] + df.iloc[48, 6] +
                            df.iloc[51, 6] + df.iloc[54, 6] + df.iloc[57, 6] + df.iloc[60, 6] + df.iloc[63, 6] +
                            df.iloc[66, 6] + df.iloc[69, 6]
                    )

                    st.session_state.debiti = df.iloc[34, 8]  # I35
                    st.session_state.debiti_1 = df.iloc[34, 7]
                    st.session_state.debiti_2 = df.iloc[34, 6]

                    st.session_state.liquidita = (
                            df.iloc[73, 3] + df.iloc[46, 3] + df.iloc[49, 3] + df.iloc[52, 3] + df.iloc[54, 3] +
                            df.iloc[56, 3] + df.iloc[59, 3] + df.iloc[62, 3] + df.iloc[64, 3]
                    )
                    st.session_state.liquidita_1 = (
                            df.iloc[73, 2] + df.iloc[46, 2] + df.iloc[49, 2] + df.iloc[52, 2] + df.iloc[54, 2] +
                            df.iloc[56, 2] + df.iloc[59, 2] + df.iloc[62, 2] + df.iloc[64, 2]
                    )
                    st.session_state.liquidita_2 = (
                            df.iloc[73, 1] + df.iloc[46, 1] + df.iloc[49, 1] + df.iloc[52, 1] + df.iloc[54, 1] +
                            df.iloc[56, 1] + df.iloc[59, 1] + df.iloc[62, 1] + df.iloc[64, 1]
                    )

                    st.session_state.ebitda = (
                            df.iloc[92, 3] + df.iloc[93, 3] + df.iloc[94, 3] + df.iloc[95, 3] - df.iloc[113, 3] -
                            df.iloc[99, 3] + df.iloc[96, 3] - df.iloc[116, 3] -df.iloc[100, 3] - df.iloc[102, 3] -
                            df.iloc[101, 3]
                    )
                    st.session_state.ebitda_1 = (
                            df.iloc[92, 2] + df.iloc[93, 2] + df.iloc[94, 2] + df.iloc[95, 2] - df.iloc[113, 2] -
                            df.iloc[99, 2] + df.iloc[96, 2] - df.iloc[116, 2] -df.iloc[100, 2] - df.iloc[102, 2] -
                            df.iloc[101, 2]
                    )
                    st.session_state.ebitda_2 = (
                            df.iloc[92, 1] + df.iloc[93, 1] + df.iloc[94, 1] + df.iloc[95, 1] - df.iloc[113, 1] -
                            df.iloc[99, 1] + df.iloc[96, 1] - df.iloc[116, 1] -df.iloc[100, 1] - df.iloc[102, 1] -
                            df.iloc[101, 1]
                    )

                    st.session_state.cf = df.iloc[159, 3] + df.iloc[114, 3]  # D160 + D115
                    st.session_state.cf_1 = df.iloc[159, 2] + df.iloc[114, 2]
                    st.session_state.cf_2 = df.iloc[159, 1] + df.iloc[114, 1]

                    st.session_state.oneri = (
                            df.iloc[35, 8] + df.iloc[38, 8] + df.iloc[41, 8] + df.iloc[44, 8] + df.iloc[59, 8]
                    )
                    st.session_state.oneri_1 = (
                            df.iloc[35, 7] + df.iloc[38, 7] + df.iloc[41, 7] + df.iloc[44, 7] + df.iloc[59, 7]
                    )
                    st.session_state.oneri_2 = (
                            df.iloc[35, 6] + df.iloc[38, 6] + df.iloc[41, 6] + df.iloc[44, 6] + df.iloc[59, 6]
                    )

                    st.session_state.ricavi = df.iloc[92, 3]  # D93
                    st.session_state.ricavi_1 = df.iloc[92, 2]
                    st.session_state.ricavi_2 = df.iloc[92, 1]

                    st.session_state.submitted = True
                    st.success("Excel File uploaded correctly")
                    st.success(f"✅ Company '{selected_company}' loaded successfully!")

                except Exception as e:
                    st.error(f"Error loading saved company: {e}")


# ----- LETTURA JSON ASSOCIATO -----
json_repo = Path("./payline")
json_path = json_repo / f"{selected_company}.json"
json_data = None

if json_path.exists():
    try:
        import json
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # -----------------------------
        # ✅ ASSEGNAZIONE VARIABILI 1:1
        # -----------------------------

        # --- campi principali ---
        st.session_state.Name = json_data.get("Name")
        st.session_state.TaxCode = json_data.get("TaxCode")
        st.session_state.Active_Contracts = json_data.get("Active Contracts")

        # --- Outstanding ---
        Outstanding = json_data.get("Outstanding", {})

        st.session_state.Overall_Oustanding = Outstanding.get("Overall Oustanding")
        st.session_state.Rental_Remarketing_Total = Outstanding.get("Rental and Remarketing Total")      # il nome originale ha &amp; → Python non lo vuole
        st.session_state.Rental = Outstanding.get("Rental")
        st.session_state.Remarketing = Outstanding.get("Remarketing")
        st.session_state.Retail_Leasing_Total = Outstanding.get("Retail and Leasing Total")
        st.session_state.Retail = Outstanding.get("Retail")
        st.session_state.Leasing = Outstanding.get("Leasing")

        # --- Scaduto ---
        Scaduto = json_data.get("Scaduto", {})

        st.session_state.Overall_Past_due = Scaduto.get("Overall Past-due")
        st.session_state.Rental_fees_Past_due = Scaduto.get("Rental fees Past-due")
        st.session_state.Rental_extra_fees_Past_due = Scaduto.get("Rental extra-fees Past-due")

        # ✅ (opzionale) conferma interna
        st.success("JSON loaded and variables assigned.")

    except Exception as e:
        st.error(f"❌ Error reading JSON file: {e}")

else:
    st.warning(f"⚠️ No JSON found for company '{selected_company}'")

# CALCOLO + OUTPUT
if st.session_state.submitted:
    ind1 = st.session_state.pn / st.session_state.attivo
    ind2 = st.session_state.att_breve / st.session_state.pass_breve
    ind3 = (st.session_state.debiti - st.session_state.liquidita) / st.session_state.ebitda
    ind4 = st.session_state.cf / st.session_state.attivo
    ind5 = st.session_state.oneri / st.session_state.ricavi
    cagr_ricavi = (
        (st.session_state.ricavi / st.session_state.ricavi_2) ** 0.5 - 1
        if st.session_state.ricavi_2 > 0 else
        (st.session_state.ricavi / st.session_state.ricavi_1) - 1
        if st.session_state.ricavi_1 > 0 else
        np.nan
    )

    trend_ricavi = {'cagr_ricavi' : [st.session_state.ricavi_2, st.session_state.ricavi_1, st.session_state.ricavi]}

    ind1_1 = st.session_state.pn_1 / st.session_state.attivo_1
    ind2_1 = st.session_state.att_breve_1 / st.session_state.pass_breve_1
    ind3_1 = (st.session_state.debiti_1 - st.session_state.liquidita_1) / st.session_state.ebitda_1
    ind4_1 = st.session_state.cf_1 / st.session_state.attivo_1
    ind5_1 = st.session_state.oneri_1 / st.session_state.ricavi_1

    ind1_2 = st.session_state.pn_2 / st.session_state.attivo_2
    ind2_2 = st.session_state.att_breve_2 / st.session_state.pass_breve_2
    ind3_2 = (st.session_state.debiti_2 - st.session_state.liquidita_2) / st.session_state.ebitda_2
    ind4_2 = st.session_state.cf_2 / st.session_state.attivo_2
    ind5_2 = st.session_state.oneri_2 / st.session_state.ricavi_2

    # INDICATORI SINTETICI STORICI
    indicatori_storici = {
        "struttura": [ind1_2, ind1_1, ind1],
        "liquidita": [ind2_2, ind2_1, ind2],
        "leva": [ind3_2, ind3_1, ind3],
        "cashflow": [ind4_2, ind4_1, ind4],
        "profitability": [ind5_2, ind5_1, ind5]
    }

    bilancio_data = {
        "patrimonio_netto": {
            "t-2": st.session_state.pn_2,
            "t-1": st.session_state.pn_1,
            "t": st.session_state.pn
        },
        "attivo": {
            "t-2": st.session_state.attivo_2,
            "t-1": st.session_state.attivo_1,
            "t": st.session_state.attivo
        },
        "attivo_breve": {
            "t-2": st.session_state.att_breve_2,
            "t-1": st.session_state.att_breve_1,
            "t": st.session_state.att_breve
        },
        "passivo_breve": {
            "t-2": st.session_state.pass_breve_2,
            "t-1": st.session_state.pass_breve_1,
            "t": st.session_state.pass_breve
        },
        "debiti": {
            "t-2": st.session_state.debiti_2,
            "t-1": st.session_state.debiti_1,
            "t": st.session_state.debiti
        },
        "liquidita": {
            "t-2": st.session_state.liquidita_2,
            "t-1": st.session_state.liquidita_1,
            "t": st.session_state.liquidita
        },
        "ebitda": {
            "t-2": st.session_state.ebitda_2,
            "t-1": st.session_state.ebitda_1,
            "t": st.session_state.ebitda
        },
        "cashflow": {
            "t-2": st.session_state.cf_2,
            "t-1": st.session_state.cf_1,
            "t": st.session_state.cf
        },
        "oneri_finanziari": {
            "t-2": st.session_state.oneri_2,
            "t-1": st.session_state.oneri_1,
            "t": st.session_state.oneri
        },
        "ricavi": {
            "t-2": st.session_state.ricavi_2,
            "t-1": st.session_state.ricavi_1,
            "t": st.session_state.ricavi
        },

        # --- Indicatori ---
        "struttura_patrimoniale": {
            "t-2": ind1_2,
            "t-1": ind1_1,
            "t": ind1
        },
        "liquidita_indice": {
            "t-2": ind2_2,
            "t-1": ind2_1,
            "t": ind2
        },
        "leva": {
            "t-2": ind3_2,
            "t-1": ind3_1,
            "t": ind3
        },
        "cashflow_indice": {
            "t-2": ind4_2,
            "t-1": ind4_1,
            "t": ind4
        },
        "profitability": {
            "t-2": ind5_2,
            "t-1": ind5_1,
            "t": ind5
        },

        # --- Crescita ---
        "cagr_ricavi": {
            "periodo": "ultimi 2 anni",
            "valore": cagr_ricavi
        }
    }

    bilancio_data_new = {
        # --- Indicatori ---
        "struttura_patrimoniale": {
            "t-2": ind1_2,
            "t-1": ind1_1,
            "t": ind1
        },
        "liquidita_indice": {
            "t-2": ind2_2,
            "t-1": ind2_1,
            "t": ind2
        },
        "leva": {
            "t-2": ind3_2,
            "t-1": ind3_1,
            "t": ind3
        },
        "cashflow_indice": {
            "t-2": ind4_2,
            "t-1": ind4_1,
            "t": ind4
        },
        "profit": {
            "t-2": ind5_2,
            "t-1": ind5_1,
            "t": ind5
        },

        # --- Crescita ---
        "cagr_ricavi": {
            "periodo": "ultimi 2 anni",
            "valore": cagr_ricavi
        }
    }

    c1 = classe_struttura(ind1)
    c2 = classe_liquidita(ind2)
    c3 = classe_leva(ind3)
    c4 = classe_cashflow(ind4)
    c5 = classe_profit(ind5)
    c_cagr_ricavi = classe_cagr(cagr_ricavi)

    score_int = round((c1 + c2 + c3 + c4 + c5) / 5)

    c1_storico = [classe_struttura(x) for x in indicatori_storici["struttura"]]
    c2_storico = [classe_liquidita(x) for x in indicatori_storici["liquidita"]]
    c3_storico = [classe_leva(x) for x in indicatori_storici["leva"]]
    c4_storico = [classe_cashflow(x) for x in indicatori_storici["cashflow"]]
    c5_storico = [classe_profit(x) for x in indicatori_storici["profitability"]]

    score_int_storico = {'integrato': [
        round((c1_storico[i] + c2_storico[i] + c3_storico[i] + c4_storico[i] + c5_storico[i]) / 5)
        for i in range(3)
    ]}

    st.divider()
    st.header("👥 Customer Data")

    dati_cliente = {
        "Name": st.session_state.Name,
        "TaxCode": st.session_state.TaxCode,
        "Active Contracts": st.session_state.Active_Contracts,
        "Overall Outstanding": st.session_state.Overall_Oustanding,
        "Rental & RMKT Total": st.session_state.Rental_Remarketing_Total,
        "Rental": st.session_state.Rental,
        "Remarketing": st.session_state.Remarketing,
        "Retail & Leasing Total": st.session_state.Retail_Leasing_Total,
        "Retail": st.session_state.Retail,
        "Leasing": st.session_state.Leasing,
        "Overall Past-due": st.session_state.Overall_Past_due,
        "Rental fees Past-due": st.session_state.Rental_fees_Past_due,
        "Rental extra-fees Past-due": st.session_state.Rental_extra_fees_Past_due
    }

    col1, col2 = st.columns(2)

    items = list(dati_cliente.items())

    for i, (nome, valore) in enumerate(items):

        # --- primi 3 elementi → NO EURO ---
        if i < 3:
            col = col1 if i < len(items) / 2 else col2
            with col:
                st.markdown(f"""
                <div style="font-size:18px;">
                    <strong>{nome}</strong><br>
                    {valore}
                </div>
                """, unsafe_allow_html=True)
            continue

        # --- tutti gli altri → euro + separatore migliaia ---
        col = col1 if i < len(items) / 2 else col2
        with col:
            st.markdown(f"""
            <div style="font-size:18px;">
                <strong>{nome}</strong><br>
                € {valore:,.0f}
            </div>
            """, unsafe_allow_html=True)


    st.divider()
    st.header("📋 Financial Statement Indicators")

    dati_bilancio = {
        "Most recent Financial Year": st.session_state.anno_bil,
        "Net Worth": st.session_state.pn,
        "Total Assets": st.session_state.attivo,
        "Current Assets": st.session_state.att_breve,
        "Current Liabilities": st.session_state.pass_breve,
        "Total Debts": st.session_state.debiti,
        "Liquidity": st.session_state.liquidita,
        "EBITDA": st.session_state.ebitda,
        "Cash Flow": st.session_state.cf,
        "Financial Payables": st.session_state.oneri,
        "Revenues": st.session_state.ricavi
    }

    col1, col2 = st.columns(2)

    items = list(dati_bilancio.items())

    for i, (nome, valore) in enumerate(items):

        # Primo item → nessuna formattazione
        if i == 0:
            col = col1
            with col:
                st.markdown(f"""
                <div style="font-size:18px;">
                    <strong>{nome}</strong><br>
                    {int(valore)}
                </div>
                """, unsafe_allow_html=True)
            continue

        # Tutti gli altri → euro + separatore migliaia
        col = col1 if i < len(items) / 2 else col2
        with col:
            st.markdown(f"""
            <div style="font-size:18px;">
                <strong>{nome}</strong><br>
                € {valore:,.0f}
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.header("📊 Results")

    risultati = [
        ("Capital Structure", ind1, c1, "struttura", "Net Worth / Total Assets"),
        ("Current Liquidity", ind2, c2, "liquidita", "Current Assets / Current Liabilities"),
        ("Debt Sustainability", ind3, c3, "leva", "(Total Debts - Liquidity) / EBITDA"),
        ("Cash Flow", ind4, c4, "cashflow", "Cash Flow / Total Assets"),
        ("Profitability", ind5, c5, "profitability", "Financial Payables / Revenue"),
    ]

    for nome, valore, c, key, formula in risultati:
        # colA, colB = st.columns([1, 3])
        colA, colB, colC = st.columns([1, 3, 2.5])

        with colA:
            st.markdown(badge(c), unsafe_allow_html=True)

        with colB:
            st.markdown(f"""
            **{nome}**  
            *{formula}*  
            **Indicator value:** `{valore:.4f}`  

            {DESCRIZIONI_eng[key][c]}
            """)

        with colC:
            st.markdown(
                f"<div style='font-size:16px; font-weight:600; margin-bottom:2px;'>{nome}</div>",
                unsafe_allow_html=True
            )

            st.plotly_chart(
                sparkline(indicatori_storici[key], st.session_state.anno_bil),
                use_container_width=True
            )

            st.markdown(
                f"<div style='font-size:16px; color:#555;'>"
                f"{commento_trend_intelligente_eng(indicatori_storici[key], key)}"
                f"</div>",
                unsafe_allow_html=True
            )

        st.divider()

    risultati_cagr = [("Annual Growth", cagr_ricavi, c_cagr_ricavi, "cagr_ricavi", "Revenue CAGR")]
    colA, colB, colC = st.columns([1, 3, 2.5])

    for nome, valore, c, key, formula in risultati_cagr:
        with colA:
            st.markdown(badge(c), unsafe_allow_html=True)

        with colB:
            st.markdown(f"""
            **{nome}**  
            *{formula}*  
            **Indicator value:** `{valore:.4f}`  

            {DESCRIZIONI_eng[key][c]}
            """)

        with colC:
            st.markdown(
                f"<div style='font-size:16px; font-weight:600; margin-bottom:2px;'>{nome}</div>",
                unsafe_allow_html=True
            )


            st.plotly_chart(
                sparkline(trend_ricavi['cagr_ricavi'], st.session_state.anno_bil),
                use_container_width=True
            )

            st.markdown(
                f"<div style='font-size:16px; color:#555;'>"
                f"{commento_cagr_ricavi_eng(trend_ricavi['cagr_ricavi'], descr_cagr_eng)}"
                f"</div>",
                unsafe_allow_html=True
            )

    st.divider()

    st.header("🏁 LEASYS FINANCIAL INDEX – Integrated Score")
    # st.markdown(badge(score_int), unsafe_allow_html=True)
    # st.markdown(f""" <div style="font-size:18px; margin-top:8px;"> {DESCRIZIONE_INTEGRATO_eng[score_int]} </div> """,
    #             unsafe_allow_html=True)

    # colA, colB = st.columns([3, 2])
    colA, colB, colC = st.columns([1, 3, 2.5])

    with colA:
        st.markdown(badge(score_int), unsafe_allow_html=True)
        st.markdown(f""" <div style="font-size:18px; margin-top:8px;"> {DESCRIZIONE_INTEGRATO_eng[score_int]} </div> """,
                    unsafe_allow_html=True)

    nome_intg = "LEASYS FINANCIAL INDEX – Score Integrato"
    with colC:
        st.markdown(
            f"<div style='font-size:16px; font-weight:600; margin-bottom:2px;'>{nome_intg}</div>",
            unsafe_allow_html=True
        )

        st.plotly_chart(
            sparkline(score_int_storico['integrato'], st.session_state.anno_bil, score_intg=True),
            use_container_width=True
        )

        st.markdown(
            f"<div style='font-size:16px; color:#555;'>"
            f"{commento_score_integrato_eng(score_int_storico['integrato'])}"
            f"</div>",
            unsafe_allow_html=True
        )

    st.divider()


    # RADAR
    st.header("🕸️ Risk Profile – Radar")

    radar_classes = [c1, c2, c3, c4, c5]

    radar_values = radar_classes + [radar_classes[0]]
    radar_labels_closed = radar_labels_eng + [radar_labels_eng[0]]
    radar_colors = [colori_classi_radar[c] for c in radar_classes] + [colori_classi_radar[radar_classes[0]]]

    fig = go.Figure()

    # area radar (corporate)
    fig.add_trace(go.Scatterpolar(
        r=radar_values,
        theta=radar_labels_closed,
        fill='toself',
        fillcolor='rgba(0,70,122,0.25)',
        line=dict(color='#00467a', width=3),
        name="Risk Profile"
    ))

    # punti colorati per classe
    fig.add_trace(go.Scatterpolar(
        r=radar_values,
        theta=radar_labels_closed,
        mode='markers',
        marker=dict(
            size=14,
            color=radar_colors,
            line=dict(color="white", width=2)
        ),
        showlegend=False
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[1, 5],
                tickvals=[1, 2, 3, 4, 5],
                tickfont=dict(size=12, color="#00467a"),
                gridcolor="rgba(0,70,122,0.25)"
            ),
            angularaxis=dict(
                tickfont=dict(size=13, color="#00467a"),
                gridcolor="rgba(0,70,122,0.25)"
            )
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=520,
        margin=dict(t=40, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    col_logo_2, col_title_2 = st.columns([2, 4])
    with col_logo_2:
        st.image("aida.png", use_container_width=True)

    if st.session_state.anno_bil:
        bilancio_ai_component_eng(st.session_state.anno_bil, bilancio_data, dati_cliente

    # bilancio_ai_component_eng(st.session_state.anno_bil, bilancio_data, dati_cliente)

    st.divider()

    st.header("📄 Export PDF")

    if st.button("⬇️ Download Leasys PDF"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            genera_pdf_leasys(
                output_path=tmp.name,
                logo_path="./dashboard/logo.png",
                dati_bilancio={
                    "Patrimonio netto": pn,
                    "Attivo": attivo,
                    "Attivo a breve": att_breve,
                    "Passivo a breve": pass_breve,
                    "Debiti totali": debiti,
                    "Liquidità": liquidita,
                    "EBITDA": ebitda,
                    "Cash flow": cf,
                    "Oneri finanziari": oneri,
                    "Ricavi": ricavi
                },
                classi=risultati,
                descrizioni=DESCRIZIONI_eng,
                score_int=score_int,
                descrizione_int=DESCRIZIONE_INTEGRATO_eng[score_int],
                indicatori_calcolati={
                    "Struttura patrimoniale": ind1,
                    "Liquidità": ind2,
                    "Leva": ind3,
                    "Cash flow": ind4,
                    "Profitability": ind5,
                    "CAGR Ricavi": cagr_ricavi
                },
                grafici={
                    "Struttura": sparkline(indicatori_storici["struttura"], st.session_state.anno_bil),
                    "Liquidità": sparkline(indicatori_storici["liquidita"], st.session_state.anno_bil),
                    "Leva": sparkline(indicatori_storici["leva"], st.session_state.anno_bil),
                    "Cash Flow": sparkline(indicatori_storici["cashflow"], st.session_state.anno_bil),
                    "Profitability": sparkline(indicatori_storici["profitability"], st.session_state.anno_bil),
                    "Radar": fig
                }
            )

            with open(tmp.name, "rb") as f:
                st.download_button(
                    "📥 Download PDF",
                    f,
                    file_name="Scoring_Integrato_Leasys.pdf",
                    mime="application/pdf"
                )
