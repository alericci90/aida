# %% style.py
# ============================================================================
#  AIDA · LEASYS FINANCIAL INDEX — THEME LAYER (UI ONLY)
# ----------------------------------------------------------------------------
#  Questo modulo NON contiene logica applicativa, callback, calcoli o pipeline
#  dati. Espone solo:
#    - inject_theme()        -> inietta font + CSS globale (financial-grade)
#    - section_header(...)    -> intestazione di sezione coerente (eyebrow+titolo)
#    - kpi_card(...)          -> card KPI uniforme (label/valore/sottotitolo)
#    - rating_class(...)      -> mappa classe 1..5 -> token estetico (colore/label)
#  Tutti gli helper restituiscono stringhe HTML da passare a st.markdown.
# ============================================================================

import streamlit as st

# ---------------------------------------------------------------------------
# PALETTE (ripresa dal benchmark HTML "CCO_Call_-_Aida_v4")
# ---------------------------------------------------------------------------
INK        = "#0A1F44"   # navy brand (titoli su chiaro)
ABYSS      = "#050B1C"   # sfondo profondo
NAVY       = "#0A1734"   # pannello scuro
PANEL      = "#0B1430"   # superficie dashboard
RED        = "#E2231A"   # rosso Leasys
RED_WARM   = "#FF6A3D"   # accento caldo (gradiente AIDA)
PAPER      = "#EEF2FB"   # superficie chiara
MIST       = "#9FB2D6"   # testo attenuato su scuro
LINE       = "rgba(159,178,214,.16)"

# Scala di rating (classe 1 = migliore -> classe 5 = peggiore)
CLASS_COLORS = {
    1: "#16976A",  # excellent
    2: "#67B35A",  # good
    3: "#F3B13C",  # adequate
    4: "#EE6B2C",  # weak
    5: "#9E1B14",  # critical
}
CLASS_LABELS = {
    1: "EXCELLENT",
    2: "GOOD",
    3: "ADEQUATE",
    4: "WEAK",
    5: "CRITICAL",
}


def rating_class(c):
    """Ritorna (colore, label) per la classe c (1..5). Pura presentazione."""
    c = int(c)
    return CLASS_COLORS.get(c, "#7c8aa6"), CLASS_LABELS.get(c, "—")


# ---------------------------------------------------------------------------
# CSS GLOBALE
# ---------------------------------------------------------------------------
def inject_theme():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root{
  --ink:#0A1F44; --abyss:#050B1C; --navy:#0A1734; --panel:#0B1430;
  --red:#E2231A; --red-warm:#FF6A3D; --paper:#EEF2FB; --mist:#9FB2D6;
  --line:rgba(159,178,214,.16);
  --grad-red:linear-gradient(120deg,#E2231A 0%,#FF6A3D 100%);
  --shadow-soft:0 18px 42px -30px rgba(10,31,68,.55);
  --shadow-card:0 26px 60px -38px rgba(10,31,68,.45);
  --c1:#16976A; --c2:#67B35A; --c3:#F3B13C; --c4:#EE6B2C; --c5:#9E1B14;
}

/* ---------- BASE / SFONDO APP ---------- */
.stApp,[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(1200px 620px at 50% -8%, rgba(226,35,26,.06), transparent 60%),
    linear-gradient(180deg,#F6F8FE 0%,#EEF2FB 100%);
  color:var(--ink);
}
html, body, [class*="css"]{ font-family:'Inter',system-ui,sans-serif; color:var(--ink); }

[data-testid="stHeader"]{ background:transparent; }
.block-container{ padding-top:2.2rem; padding-bottom:4rem; max-width:1280px; }

::selection{ background:var(--red); color:#fff; }

/* ---------- TIPOGRAFIA / HEADINGS ---------- */
h1,h2,h3,h4{
  font-family:'Space Grotesk',sans-serif !important;
  color:var(--ink) !important; letter-spacing:-.01em; font-weight:700 !important;
}
[data-testid="stHeading"] h1,
[data-testid="stHeading"] h2{
  font-size:clamp(1.35rem,2.4vw,1.9rem) !important;
  padding-bottom:.55rem; margin-top:.4rem;
  border-bottom:1px solid #dde4f2;
}
.mono{ font-family:'JetBrains Mono',monospace; }

/* ---------- DIVIDER ---------- */
hr,[data-testid="stDivider"]{
  border:none !important; height:1px !important;
  background:linear-gradient(90deg,transparent,#cfd9ee 18%,#cfd9ee 82%,transparent) !important;
  margin:1.6rem 0 !important;
}

/* ---------- RADIO (segmented control) ---------- */
[data-testid="stRadio"] > label p{
  font-family:'JetBrains Mono'; font-size:.7rem; letter-spacing:.16em;
  text-transform:uppercase; color:#7c8aa6;
}
[data-testid="stRadio"] [role="radiogroup"]{
  gap:.5rem; flex-wrap:wrap;
  background:#fff; border:1px solid #dde4f2; border-radius:14px;
  padding:.45rem; box-shadow:var(--shadow-soft);
}
[data-testid="stRadio"] [role="radiogroup"] label{
  margin:0 !important; padding:.55rem 1rem; border-radius:10px;
  font-family:'Space Grotesk'; font-weight:600; font-size:.9rem;
  color:#48597a; cursor:pointer; transition:.22s;
}
[data-testid="stRadio"] [role="radiogroup"] label:hover{ background:#f1f4fb; }
[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked){
  background:var(--ink); color:#fff;
  box-shadow:0 14px 28px -16px rgba(10,31,68,.6);
}
[data-testid="stRadio"] [role="radiogroup"] label > div:first-child{ display:none; }

/* ---------- SELECTBOX / INPUT / TEXTAREA ---------- */
[data-testid="stSelectbox"] label p,
[data-testid="stTextArea"] label p,
[data-testid="stNumberInput"] label p,
[data-testid="stFileUploader"] label p{
  font-family:'JetBrains Mono'; font-size:.7rem; letter-spacing:.12em;
  text-transform:uppercase; color:#7c8aa6;
}
[data-baseweb="select"] > div,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input{
  border-radius:11px !important; border:1px solid #dde4f2 !important;
  background:#fff !important; font-family:'Inter' !important;
}
[data-baseweb="select"] > div:focus-within,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stNumberInput"] input:focus{
  border-color:var(--red) !important;
  box-shadow:0 0 0 3px rgba(226,35,26,.12) !important;
}

/* ---------- BUTTONS ---------- */
.stButton > button,
[data-testid="stFormSubmitButton"] > button,
[data-testid="stDownloadButton"] > button{
  font-family:'Space Grotesk'; font-weight:700; letter-spacing:.01em;
  border-radius:11px; padding:.62rem 1.4rem; border:none;
  background:var(--grad-red); color:#fff;
  box-shadow:0 16px 30px -16px rgba(226,35,26,.55);
  transition:transform .2s, box-shadow .2s, filter .2s;
}
.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover,
[data-testid="stDownloadButton"] > button:hover{
  transform:translateY(-2px); filter:brightness(1.04);
  box-shadow:0 22px 40px -18px rgba(226,35,26,.6); color:#fff;
}
.stButton > button:active{ transform:translateY(0); }

/* ---------- FILE UPLOADER ---------- */
[data-testid="stFileUploaderDropzone"]{
  background:#fff; border:1.5px dashed #c6d2ea; border-radius:14px;
}

/* ---------- FORM CONTAINER ---------- */
[data-testid="stForm"]{
  background:#fff; border:1px solid #dde4f2; border-radius:18px;
  padding:1.4rem 1.5rem; box-shadow:var(--shadow-card);
}

/* ---------- ALERTS ---------- */
[data-testid="stAlert"]{ border-radius:12px; border:1px solid #dde4f2; }

/* ---------- PLOTLY CARD WRAPPER ---------- */
[data-testid="stPlotlyChart"]{
  background:#fff; border:1px solid #dde4f2; border-radius:14px;
  padding:.4rem .4rem 0; box-shadow:var(--shadow-soft);
}

/* ====================================================================== */
/*  COMPONENTI CUSTOM AIDA                                                  */
/* ====================================================================== */

/* Eyebrow + titolo di sezione */
.aida-eyebrow{
  font-family:'JetBrains Mono'; font-size:.7rem; letter-spacing:.3em;
  text-transform:uppercase; color:var(--red);
  display:flex; align-items:center; gap:.7rem; margin-bottom:.15rem;
}
.aida-eyebrow::after{ content:""; height:1px; flex:1; max-width:120px;
  background:currentColor; opacity:.4; }
.aida-sec-title{
  font-family:'Space Grotesk'; font-weight:700; color:var(--ink);
  font-size:clamp(1.3rem,2.4vw,1.85rem); line-height:1.05; margin:0 0 .2rem;
}

/* Grid KPI */
.aida-kpi-grid{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
  gap:.8rem; margin:.4rem 0 .2rem;
}
.aida-kpi{
  position:relative; overflow:hidden;
  background:#fff; border:1px solid #dde4f2; border-radius:14px;
  padding:1rem 1.05rem .95rem 1.2rem; box-shadow:var(--shadow-soft);
  transition:transform .25s, border-color .25s, box-shadow .25s;
}
.aida-kpi:hover{ transform:translateY(-3px); border-color:#c6d2ea;
  box-shadow:0 22px 46px -28px rgba(10,31,68,.5); }
.aida-kpi .kbar{ position:absolute; left:0; top:0; width:4px; height:100%;
  background:var(--grad-red); }
.aida-kpi.accent-ink .kbar{ background:linear-gradient(180deg,#0A1F44,#16306e); }
.aida-kpi .klabel{
  font-family:'JetBrains Mono'; font-size:.64rem; letter-spacing:.06em;
  text-transform:uppercase; color:#7c8aa6; line-height:1.3; min-height:2.2em;
}
.aida-kpi .kvalue{
  font-family:'Space Grotesk'; font-weight:700; font-size:1.45rem;
  color:var(--ink); margin-top:.35rem; line-height:1; word-break:break-word;
}
.aida-kpi .ksub{
  font-family:'JetBrains Mono'; font-size:.6rem; letter-spacing:.04em;
  color:#9aa7c0; margin-top:.25rem;
}

/* Rating chip (badge classi) */
.aida-chip{
  display:inline-flex; align-items:center; gap:.5rem;
  padding:.5rem .85rem; border-radius:11px; color:#fff;
  font-family:'Space Grotesk'; font-weight:700; font-size:.82rem;
  letter-spacing:.02em; box-shadow:0 12px 24px -14px rgba(0,0,0,.45);
}
.aida-chip .dot{ width:8px; height:8px; border-radius:50%;
  background:rgba(255,255,255,.85); }
.aida-chip .cls{ font-family:'JetBrains Mono'; font-size:.62rem;
  letter-spacing:.12em; opacity:.85; }

/* Formula box */
.aida-formula{
  font-family:'JetBrains Mono'; font-size:.85rem; color:var(--ink);
  background:#F3F6FD; border:1px solid #E2E8F4; border-left:3px solid var(--red);
  border-radius:10px; padding:.6rem .85rem; margin:.5rem 0 .6rem; line-height:1.5;
}

/* Blocco descrizione indicatore */
.aida-ind-name{
  font-family:'Space Grotesk'; font-weight:700; color:var(--ink);
  font-size:1.12rem; line-height:1.1; margin-bottom:.15rem;
}
.aida-ind-fam{
  font-family:'JetBrains Mono'; font-size:.62rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--red); margin-bottom:.35rem;
}
.aida-ind-value{
  font-family:'JetBrains Mono'; font-size:.78rem; color:#48597a;
  background:#fff; border:1px solid #e2e8f4; border-radius:8px;
  padding:.18rem .5rem; display:inline-block; margin-bottom:.55rem;
}
.aida-ind-value b{ color:var(--ink); }
.aida-ind-desc{ font-size:.95rem; line-height:1.55; color:#3a4860; }

/* Mini-titolo sopra sparkline */
.aida-spark-title{
  font-family:'JetBrains Mono'; font-size:.62rem; letter-spacing:.1em;
  text-transform:uppercase; color:#7c8aa6; font-weight:600; margin-bottom:.3rem;
}
.aida-spark-note{ font-size:.85rem; color:#52617e; line-height:1.45;
  margin-top:.35rem; }

/* Disclaimer */
.aida-disclaimer{
  background:#F6F8FE; border:1px solid #dde4f2; border-left:4px solid #9aa7c0;
  border-radius:10px; padding:.8rem 1rem; color:#52617e; font-size:.85rem;
  line-height:1.5;
}
.aida-disclaimer b{ color:var(--ink); }

/* Chat bubbles */
.aida-bubble{ font-size:.92rem; line-height:1.55; padding:.7rem .95rem;
  border-radius:12px; margin:.25rem 0; max-width:94%; }
.aida-bubble .lbl{ font-family:'JetBrains Mono'; font-size:.56rem;
  letter-spacing:.12em; text-transform:uppercase; display:block; margin-bottom:.3rem; }
.aida-bubble.user{ background:#EEF2FB; border:1px solid #dde4f2; color:#26334d;
  margin-left:auto; border-bottom-right-radius:3px; }
.aida-bubble.user .lbl{ color:#7c8aa6; }
.aida-bubble.ai{ background:#fff; border:1px solid #dde4f2; color:#3a4860;
  border-bottom-left-radius:3px; box-shadow:var(--shadow-soft); }
.aida-bubble.ai .lbl{ color:var(--red); }

/* Hero / brand header */
.aida-hero{
  display:flex; align-items:center; justify-content:space-between;
  gap:1.2rem; flex-wrap:wrap; margin-bottom:.4rem;
}
.aida-hero .brand{ display:flex; align-items:center; gap:.9rem; }
.aida-hero .brand .glyph{
  width:42px; height:42px; border-radius:12px; background:var(--grad-red);
  display:grid; place-items:center; color:#fff; font-family:'Space Grotesk';
  font-weight:700; font-size:1.05rem; box-shadow:0 14px 28px -12px rgba(226,35,26,.55);
}
.aida-hero .brand .txt .t{ font-family:'Space Grotesk'; font-weight:700;
  font-size:1.15rem; color:var(--ink); line-height:1; }
.aida-hero .brand .txt .s{ font-family:'JetBrains Mono'; font-size:.62rem;
  letter-spacing:.18em; text-transform:uppercase; color:#7c8aa6; margin-top:.25rem; }
.aida-hero .tag{ font-family:'JetBrains Mono'; font-size:.6rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--red); border:1px solid rgba(226,35,26,.3);
  background:rgba(226,35,26,.06); padding:.35rem .65rem; border-radius:8px; }
</style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# HELPER DI RENDERING (solo HTML, nessuna logica)
# ---------------------------------------------------------------------------
def section_header(eyebrow: str, title: str):
    return (
        f'<div class="aida-eyebrow">{eyebrow}</div>'
        f'<div class="aida-sec-title">{title}</div>'
    )


def kpi_card(label: str, value: str, sub: str = "", accent_ink: bool = False):
    cls = "aida-kpi accent-ink" if accent_ink else "aida-kpi"
    sub_html = f'<div class="ksub">{sub}</div>' if sub else ""
    return (
        f'<div class="{cls}"><span class="kbar"></span>'
        f'<div class="klabel">{label}</div>'
        f'<div class="kvalue">{value}</div>{sub_html}</div>'
    )
