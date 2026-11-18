# %% app_eng
# streamlit run app.py
# ============================================================================
#  AIDA · LEASYS FINANCIAL INDEX — DASHBOARD (MOCK-UP PER LE PRESENTAZIONI)
# ----------------------------------------------------------------------------
#  STESSO TEMPLATE della versione precedente, sezione per sezione:
#    Data Input -> Customer Data -> Financial Statement Indicators
#    -> Leasys Financial Index – Integrated Score -> Indicator Results
#    -> Risk Profile – Radar -> AI Analyst -> Export PDF
#  Cambia il contenuto: lo score integrato e' l'LFI (Run O, nucleo fisso) e
#  gli indicatori sono i 10 indicatori di bilancio del nucleo (l'eta'
#  dell'azienda resta nel modello, non tra gli indicatori). Accanto al radar, la tabella sintetica dei
#  sottoindici di famiglia.
#
#  I risultati sono letti da lfi_engine (repository_lfi/cases.json): in questo
#  mock-up non c'e' il motore di scoring, quindi "Upload Excel" e "Manual
#  Entry" restano nel menu ma non calcolano.
# ============================================================================
import tempfile
from pathlib import Path

import importlib

import streamlit as st

st.set_page_config(page_title="Financial Index Dashboard", layout="wide")

# CONTROLLO DEI FILE: tutti i moduli del mock-up devono essere della stessa versione (MOCKUP_BUILD). Se un file non e'
# stato aggiornato la pagina dice quale, invece di fermarsi su un ImportError senza spiegazioni.
MOCKUP_BUILD = "2026-11-18.1340"
_outdated = []
for _m in ("objects", "style", "lfi_engine", "functions", "funzione_ai_azure_eng"):
    try:
        _ver = getattr(importlib.import_module(_m), "MOCKUP_BUILD", None)
    except Exception as _e:                                 # modulo vecchio che importa nomi che non esistono piu'
        _ver = f"error on import ({type(_e).__name__})"
    if _ver != MOCKUP_BUILD:
        _outdated.append(f"{_m}.py ({_ver or 'older version'})")
if _outdated:
    st.error("Some files of the mock-up are not up to date: " + ", ".join(_outdated) + ". Replace them with the "
             f"latest version (build {MOCKUP_BUILD}) together with app.py.")
    st.stop()

from functions import (class_badge, class_radar, class_scale, fmt_customer, fmt_eur, fmt_pct, fmt_value,
                       genera_pdf_lfi, indicator_summary_table, score_trend_comment, sparkline, subindex_description,
                       trend_comment)
from funzione_ai_azure_eng import lfi_ai_component
from lfi_engine import (case_label, indicator_class, lfi_class, load_cases, load_customer, load_portfolio,
                        statement_age_months)
from objects import (BAND_DESCRIPTIONS, CLUSTER_LABELS, CUSTOMER_FIELDS, DISPLAY_INDICATORS, FINANCIAL_CARDS, INDICATORS,
                     LFI_CLASSES_PROVISIONAL)
from style import inject_lfi_css, inject_theme, kpi_card, section_header

# %% dashboard
APP_DIR = Path(__file__).resolve().parent     # immagini lette dalla cartella dell'app, da qualunque cartella si lanci
# CONFIG
PLOT_CONFIG = {"displayModeBar": False}          # grafici senza la barra degli strumenti di plotly

# CSS + FONT (theme layer, solo estetica)
DARK_MODE = True   # <-- True = dark premium, False = light
inject_theme(dark=DARK_MODE)
inject_lfi_css()

st.markdown(
    """
    <style>
    [data-testid="stImage"] img { max-width: 300px !important; height: auto !important; }
    </style>
    """,
    unsafe_allow_html=True
)


def _cases() -> dict:
    return load_cases()          # nessuna cache: dopo un aggiornamento di cases.json i dati nuovi sono subito visibili


def _portfolio() -> dict:
    return load_portfolio()


# HEADER
st.markdown('<div class="center-logo">', unsafe_allow_html=True)
st.image(str(APP_DIR / "logo_nuovo.png"), width="content")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="aida-hero">
      <div class="brand">
        <div class="glyph">AI</div>
        <div class="txt">
          <div class="t">AIDA · Leasys Financial Index</div>
          <div class="s">Credit Analytics Dashboard</div>
        </div>
      </div>
      <div class="tag">Enterprise Credit Risk</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# MODALITÀ INPUT
st.markdown(section_header("Data Input", "Entering Financial Statement Data"), unsafe_allow_html=True)

modalita = st.radio("Mode:", ["Companies DB", "Upload Excel", "Manual Entry"], key="modalita")

if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "selected_company" not in st.session_state:
    st.session_state.selected_company = None

cases = _cases()
portfolio = _portfolio()

# controllo di versione dei dati: se repository_lfi/cases.json non e' aggiornato lo si dice, invece di andare in errore
REQUIRED_CASE_KEYS = ["lfi", "indicators", "financials_eur", "lfi_history", "indicator_history", "customer"]
_old = sorted({k for c in cases.values() for k in REQUIRED_CASE_KEYS if k not in c})
if _old:
    st.error(f"repository_lfi/cases.json is an older version (missing: {', '.join(_old)}). Replace it with the latest "
             f"file in the folder repository_lfi of the app ({APP_DIR / 'repository_lfi' / 'cases.json'}).")

if st.session_state.modalita != "Companies DB":
    st.session_state.submitted = False
    st.session_state.selected_company = None
    st.info("In this mock-up the Leasys Financial Index is available for the companies of the repository only: "
            "this mode will be enabled with the production scoring engine.")
else:
    selected_company = st.selectbox("Select a company from repository:", list(cases),
                                    format_func=lambda k: case_label(cases[k]))
    with st.form("load_company_form"):
        submit_company = st.form_submit_button("Load Company Data")
    if submit_company:
        st.session_state.selected_company = selected_company
        st.session_state.submitted = True

# CALCOLO + OUTPUT
if st.session_state.submitted and st.session_state.selected_company in cases:
    case_id = st.session_state.selected_company
    case = cases[case_id]
    lfi = case["lfi"]
    fin = case["financials_eur"]
    years = case["years"]
    cls = lfi_class(lfi["pd"], lfi["negative_equity"])
    customer = load_customer(case)
    if not customer:
        st.warning("Customer data not available for this company: repository_lfi/cases.json is an older version "
                   "(no 'customer' field). Replace it with the latest file.")

    # ----- CUSTOMER DATA (stesse card del template) -----
    st.divider()
    st.markdown(section_header("Counterparty", "Customer Data"), unsafe_allow_html=True)

    groups = {}
    for group, key, label, kind in CUSTOMER_FIELDS:
        groups.setdefault(group, []).append((key, label, kind))
    for group, fields in groups.items():
        st.markdown(f'<div class="aida-ind-fam" style="margin-top:.9rem;">{group}</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        for i, (key, label, kind) in enumerate(fields):
            testo = fmt_customer(customer.get(key), kind)
            if kind == "text" and len(testo) > 34:          # testi lunghi: carattere piu' piccolo
                testo = f"<span style='font-size:.98rem;line-height:1.3;display:block;'>{testo}</span>"
            sub = f"{case['sector']} · {case['size_class']} · {case['customer_type']}" if key == "name" else ""
            with (col1 if i < len(fields) / 2 else col2):
                st.markdown(kpi_card(label, testo, sub=sub), unsafe_allow_html=True)

    # ----- FINANCIAL STATEMENT INDICATORS (stesse card del template, voci usate dal modello) -----
    st.divider()
    st.markdown(section_header("Financials", "Financial Statement Indicators"), unsafe_allow_html=True)

    dati_bilancio = [("Most recent Financial Year", years[-1])] + [(lab, fin[key][-1]) for key, lab in FINANCIAL_CARDS]
    col1, col2 = st.columns(2)
    for i, (nome, valore) in enumerate(dati_bilancio):
        if i == 0:
            with col1:
                st.markdown(kpi_card(nome, f"{int(valore)}", sub="Reporting year", accent_ink=True),
                            unsafe_allow_html=True)
            continue
        col = col1 if i < len(dati_bilancio) / 2 else col2
        with col:
            st.markdown(kpi_card(nome, f"€ {valore:,.0f}"), unsafe_allow_html=True)

    # ----- LEASYS FINANCIAL INDEX – INTEGRATED SCORE -----
    st.divider()
    st.markdown(section_header("Composite", "Leasys Financial Index – Integrated Score"), unsafe_allow_html=True)

    colA, colB, colC = st.columns([1, 3, 2.5])

    with colA:
        st.markdown(class_badge(cls), unsafe_allow_html=True)
        descr = ("Class assigned by the negative-equity override, not by the PD." if cls["overridden"]
                 else BAND_DESCRIPTIONS[cls["band"]])
        st.markdown(f'<div class="aida-ind-desc" style="margin-top:10px;">{descr}</div>', unsafe_allow_html=True)

    with colB:
        ratio = lfi["pd"] / lfi["cluster_pd_mean"]
        versus = "below" if ratio < 0.95 else "above" if ratio > 1.05 else "in line with"
        st.markdown(
            f'<div class="aida-ind-fam">Probability of default · 12 months</div>'
            f'<div class="lfi-pd">{fmt_pct(lfi["pd"])}</div>'
            f'<div class="aida-ind-value" style="margin-top:.6rem;">90% credible band &nbsp; '
            f'<b>{fmt_pct(lfi["pd_low"])} – {fmt_pct(lfi["pd_high"])}</b></div><br>'
            f'<div class="aida-ind-value">Reference segment &nbsp; <b>{CLUSTER_LABELS[case["cluster"]]}</b>'
            f' &nbsp;·&nbsp; average PD <b>{fmt_pct(lfi["cluster_pd_mean"])}</b></div>'
            f'<div class="aida-ind-desc">The PD is {versus} the average of the reference segment ({ratio:.2f}×) and '
            f'higher than {lfi["pd_pct_cluster"]:.0f}% of the applications of the same segment '
            f'({lfi["pd_pct_portfolio"]:.0f}% of the whole portfolio).</div>',
            unsafe_allow_html=True
        )
        st.markdown(class_scale(cls), unsafe_allow_html=True)

    nome_intg = "LEASYS FINANCIAL INDEX – Score Integrato"
    with colC:
        hist = case["lfi_history"]
        classi_storico = [lfi_class(p, ne)["final"] for p, ne in zip(hist["pd"], hist["negative_equity"])]
        st.markdown(f"<div class='aida-spark-title'>{nome_intg} · 3Y trend</div>", unsafe_allow_html=True)
        seg_med_class = lfi_class(portfolio["cluster_pd_median"][case["cluster"]], False)["final"]
        st.plotly_chart(sparkline(classi_storico, years, "class", y_range=[0.7, cls["n"] + 0.3], reference=seg_med_class,
                                  reference_label=f"Segment median (class {seg_med_class})"),
                        width="stretch", key="spark_integrated_score", config=PLOT_CONFIG)
        st.markdown(f"<div class='aida-spark-note'>{score_trend_comment(classi_storico)}</div>",
                    unsafe_allow_html=True)

    if cls["overridden"]:
        st.markdown(
            f"<div class='lfi-alert'><b>Override applied · negative equity.</b> The PD alone gives class "
            f"{cls['model']} (dashed on the scale). Equity is {fmt_eur(fin['equity'][-1])} in {years[-1]}, so the "
            f"company is assigned to class {cls['final']}, the highest-risk class.</div>",
            unsafe_allow_html=True
        )
    if LFI_CLASSES_PROVISIONAL:
        st.caption("Class scale: provisional, pending the official class boundaries.")

    st.divider()

    # ----- INDICATOR RESULTS (stessa riga del template: badge | indicatore | trend a 3 anni) -----
    st.markdown(section_header("Assessment", "Indicator Results"), unsafe_allow_html=True)

    for key in DISPLAY_INDICATORS:
        meta, ind = INDICATORS[key], case["indicators"][key]
        c = indicator_class(ind["sub_pct"])
        colA, colB, colC = st.columns([1, 3, 2.5])

        with colA:
            st.markdown(class_badge(c), unsafe_allow_html=True)

        with colB:
            st.markdown(
                f'<div class="aida-ind-fam">Indicator</div>'
                f'<div class="aida-ind-name">{meta["label"]}</div>'
                f'<div class="aida-formula">{meta["formula"]}</div>'
                f'<div class="aida-ind-value">Indicator value &nbsp; <b>{fmt_value(ind["value"], meta["fmt"])}</b></div> '
                f'<div class="aida-ind-value">Segment median &nbsp; <b>{fmt_value(ind["cluster_median"], meta["fmt"])}</b>'
                f'</div>'
                f'<div class="aida-ind-desc">'
                f'{subindex_description(ind["sub_pd"], ind["sub_pd_cluster_mean"], meta["reading"])}</div>',
                unsafe_allow_html=True
            )
            st.markdown(class_scale(c), unsafe_allow_html=True)

        with colC:
            series_key, series_label, series_fmt = meta["history"]
            hist_ = case.get("indicator_history", {}).get(series_key)
            if hist_ is None:                                       # cases.json vecchio: niente grafico, nessun errore
                st.divider()
                continue
            series = hist_["values"]                                # l'indicatore stesso sui tre bilanci
            series_label = series_label or meta["label"]
            st.markdown(f"<div class='aida-spark-title'>{series_label} · 3Y trend</div>", unsafe_allow_html=True)
            ref = ind["cluster_median"]                             # mediana del segmento dell'indicatore
            st.plotly_chart(sparkline(series, years, series_fmt, reference=ref), width="stretch", key=f"spark_{key}",
                            config=PLOT_CONFIG)
            st.markdown(f"<div class='aida-spark-note'>{trend_comment(series, series_label, meta['trend_good'])}</div>",
                        unsafe_allow_html=True)

        st.divider()

    # ----- RADAR -----
    st.markdown(section_header("Risk Profile", "Risk Profile – Radar"), unsafe_allow_html=True)
    colR1, colR2 = st.columns([2.2, 3])
    with colR1:
        st.plotly_chart(class_radar(case, DARK_MODE), width="stretch", key="radar_risk_profile", config=PLOT_CONFIG)
    with colR2:
        st.markdown(indicator_summary_table(case), unsafe_allow_html=True)
        st.caption("Family sub-index = 12-month PD on that indicator alone. Risk percentile = share of the portfolio "
                   "with a lower sub-index (0 = lowest risk, 100 = highest risk); the ticks mark the class cut-offs "
                   "at 20, 50, 75 and 90.")

    st.divider()

    # ----- AI ANALYST -----
    col_logo_2, col_title_2 = st.columns([2, 4])
    with col_logo_2:
        st.image(str(APP_DIR / "aida.png"), width="stretch")

    proposal = ({"monthly_fee": customer["monthly_new"], "months": 0} if customer.get("monthly_new") else None)
    lfi_ai_component(case, cls, proposal, customer)

    st.divider()

    # ----- PDF -----
    st.markdown(section_header("Report", "Export PDF"), unsafe_allow_html=True)

    if st.button("⬇️ Download Leasys PDF"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            genera_pdf_lfi(output_path=tmp.name, logo_path=str(APP_DIR / "logo_nuovo.png"), case=case, cls=cls)
            with open(tmp.name, "rb") as f:
                st.download_button("📥 Download PDF", f.read(), file_name="Scoring_Integrato_Leasys.pdf",
                                   mime="application/pdf")
