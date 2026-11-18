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
#  dell'azienda resta nel modello e nello SHAP, non tra gli indicatori).
#  Unica sezione in piu': lo SHAP ("What drives the score"), dopo il radar.
#
#  I risultati sono letti da lfi_engine (repository_lfi/cases.json): in questo
#  mock-up non c'e' il motore di scoring, quindi "Upload Excel" e "Manual
#  Entry" restano nel menu ma non calcolano.
# ============================================================================
import tempfile
from pathlib import Path

import streamlit as st

from functions import (area_drivers_chart, class_badge, class_radar, class_scale, driver_effect, fmt_eur, fmt_pct,
                       fmt_value, genera_pdf_lfi, ordinal, score_trend_comment, sparkline, subindex_description,
                       trend_comment)
from funzione_ai_azure_eng import lfi_ai_component
from lfi_engine import (case_label, lfi_class, load_cases, load_customer, load_portfolio, statement_age_months,
                        subindex_class)
from objects import (BAND_DESCRIPTIONS, CLUSTER_LABELS, CUSTOMER_FIELDS, DISPLAY_INDICATORS, FINANCIAL_CARDS, INDICATORS,
                     LFI_CLASSES_PROVISIONAL)
from style import inject_lfi_css, inject_theme, kpi_card, section_header

# %% dashboard
APP_DIR = Path(__file__).resolve().parent     # immagini lette dalla cartella dell'app, da qualunque cartella si lanci
# CONFIG
st.set_page_config(page_title="Financial Index Dashboard", layout="wide")

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


@st.cache_data
def _cases() -> dict:
    return load_cases()


@st.cache_data
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
    customer = load_customer(case_id)

    # ----- CUSTOMER DATA (stesse card del template) -----
    st.divider()
    st.markdown(section_header("Counterparty", "Customer Data"), unsafe_allow_html=True)

    dati_cliente = {k: customer.get(k) for k in CUSTOMER_FIELDS}
    col1, col2 = st.columns(2)
    items = list(dati_cliente.items())
    for i, (nome, valore) in enumerate(items):
        col = col1 if i < len(items) / 2 else col2
        if valore is None:
            testo = "n/a"
        elif i < 3:                             # primi 3 elementi: nessun formato euro
            testo = f"{valore}"
        else:
            testo = f"€ {valore:,.0f}"
        sub = f"{case['sector']} · {case['size_class']} · {case['customer_type']}" if nome == "Name" else ""
        with col:
            st.markdown(kpi_card(nome, testo, sub=sub), unsafe_allow_html=True)

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
        st.plotly_chart(sparkline(classi_storico, years, "class", y_range=[0.7, cls["n"] + 0.3]), width="stretch",
                        key="spark_integrated_score")
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
        c = subindex_class(ind["sub_pd"])
        colA, colB, colC = st.columns([1, 3, 2.5])

        with colA:
            st.markdown(class_badge(c), unsafe_allow_html=True)

        with colB:
            segment_position = ("" if ind["value"] is None else
                                f' &nbsp;·&nbsp; {ordinal(ind["cluster_pct"])} percentile of the segment')
            st.markdown(
                f'<div class="aida-ind-fam">Indicator</div>'
                f'<div class="aida-ind-name">{meta["label"]}</div>'
                f'<div class="aida-formula">{meta["formula"]}</div>'
                f'<div class="aida-ind-value">Indicator value &nbsp; <b>{fmt_value(ind["value"], meta["fmt"])}</b></div> '
                f'<div class="aida-ind-value">Segment median &nbsp; <b>{fmt_value(ind["cluster_median"], meta["fmt"])}</b>'
                f'{segment_position}</div>'
                f'<div class="aida-ind-desc">'
                f'{subindex_description(ind["sub_pd"], ind["sub_pd_cluster_mean"], meta["reading"])}</div>',
                unsafe_allow_html=True
            )

        with colC:
            series_key, series_label, series_fmt = meta["history"]
            series = case["ratio_history"].get(series_key) or fin.get(series_key)
            st.markdown(f"<div class='aida-spark-title'>{series_label} · 3Y trend</div>", unsafe_allow_html=True)
            ref = ind["cluster_median"] if series_key == key else None      # mediana del segmento, se la serie e' l'indicatore
            st.plotly_chart(sparkline(series, years, series_fmt, reference=ref), width="stretch", key=f"spark_{key}")
            st.markdown(f"<div class='aida-spark-note'>{trend_comment(series, series_label, meta['trend_good'])}</div>",
                        unsafe_allow_html=True)

        st.divider()

    # ----- RADAR -----
    st.markdown(section_header("Risk Profile", "Risk Profile – Radar"), unsafe_allow_html=True)
    st.plotly_chart(class_radar(case, DARK_MODE), width="stretch", key="radar_risk_profile")

    st.divider()

    # ----- SHAP: contributo di ogni area allo score (qui c'e' anche l'eta' dell'azienda) -----
    st.markdown(section_header("Explanation", "What drives the score"), unsafe_allow_html=True)
    st.caption("Each bar shows how far an area moves this company's score from the average applicant of its reference "
               "segment (log-odds points). The bars add up to the distance between the company and its segment "
               "average. Company age is part of the model and appears here.")

    colL, colR = st.columns([3, 2])
    with colL:
        st.plotly_chart(area_drivers_chart(case), width="stretch", key="lfi_area_drivers")

    with colR:
        ranked = sorted(case["indicators"].items(), key=lambda t: -t[1]["driver"])
        up = [(k, v) for k, v in ranked if driver_effect(v["driver"]) == "raises risk"][:3]
        down = [(k, v) for k, v in reversed(ranked) if driver_effect(v["driver"]) == "lowers risk"][:3]

        def _factors(items, color):
            if not items:
                return "<div class='lfi-note'>None.</div>"
            return "<div class='lfi-factors'>" + "".join(
                f"<div class='lfi-factor' style='--dc:{color};'><span>{INDICATORS[k]['label']}</span>"
                f"<span class='v'>{fmt_value(v['value'], INDICATORS[k]['fmt'])} (segment "
                f"{fmt_value(v['cluster_median'], INDICATORS[k]['fmt'])}) · {v['driver']:+.2f}</span></div>"
                for k, v in items) + "</div>"

        st.markdown("<div class='aida-spark-title'>Main factors raising risk</div>" + _factors(up, "#E5544A"),
                    unsafe_allow_html=True)
        st.write("")
        st.markdown("<div class='aida-spark-title'>Main mitigating factors</div>" + _factors(down, "#1FBE86"),
                    unsafe_allow_html=True)

    st.divider()

    # ----- AI ANALYST -----
    col_logo_2, col_title_2 = st.columns([2, 4])
    with col_logo_2:
        st.image(str(APP_DIR / "aida.png"), width="stretch")

    lfi_ai_component(case, cls, None, customer)

    st.divider()

    # ----- PDF -----
    st.markdown(section_header("Report", "Export PDF"), unsafe_allow_html=True)

    if st.button("⬇️ Download Leasys PDF"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            genera_pdf_lfi(output_path=tmp.name, logo_path=str(APP_DIR / "logo_nuovo.png"), case=case, cls=cls)
            with open(tmp.name, "rb") as f:
                st.download_button("📥 Download PDF", f.read(), file_name="Scoring_Integrato_Leasys.pdf",
                                   mime="application/pdf")
