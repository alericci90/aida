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
_ACTIVE_DARK = False

def inject_theme(dark: bool = False):
    """Inietta il tema. dark=False -> light (default), dark=True -> dark premium."""
    global _ACTIVE_DARK
    _ACTIVE_DARK = dark
    if dark:
        st.markdown("<style>" + _DARK_CSS + "</style>", unsafe_allow_html=True)
        return
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


# ---------------------------------------------------------------------------
# CHART PALETTE (grafici plotly coerenti tra light e dark)
# ---------------------------------------------------------------------------
CHART_LIGHT = dict(line="#0A1F44", marker="#0A1F44", grid="rgba(159,178,214,0.18)",
                   axis="rgba(159,178,214,0.35)", radar_line="#0A1F44",
                   radar_fill="rgba(10,31,68,0.10)", tick="#9aa7c0",
                   angular="#0A1F44", hover="#0A1F44")
CHART_DARK  = dict(line="#8FA8E0", marker="#E8EEFB", grid="rgba(159,178,214,0.14)",
                   axis="rgba(159,178,214,0.22)", radar_line="#9DB4E8",
                   radar_fill="rgba(110,143,214,0.16)", tick="#94A3C4",
                   angular="#E8EEFB", hover="#0F1729")

def chart_colors(dark=None):
    """Colori grafici per il tema. Se dark=None usa il tema attivo da inject_theme()."""
    if dark is None:
        dark = _ACTIVE_DARK
    return CHART_DARK if dark else CHART_LIGHT


# ---------------------------------------------------------------------------
# DARK THEME CSS (premium finance)
# ---------------------------------------------------------------------------
_DARK_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
:root{
  --bg:#070C18; --panel:#0F1729; --panel2:#131D33;
  --line:rgba(159,178,214,.12); --line2:rgba(159,178,214,.20);
  --text:#E8EEFB; --mute:#94A3C4; --dim:#6E7C9C;
  --red:#E2231A; --red-warm:#FF6A3D; --grad-red:linear-gradient(120deg,#E2231A,#FF6A3D);
  --c1:#1FBE86; --c2:#7FCB6E; --c3:#F5C24B; --c4:#FF7E3E; --c5:#E5544A;
  --glow:0 0 0 1px rgba(255,255,255,.03), 0 30px 60px -38px rgba(0,0,0,.8);
}
.stApp,[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(1100px 560px at 50% -10%, rgba(226,35,26,.10), transparent 58%),
    radial-gradient(900px 600px at 88% 8%, rgba(110,143,214,.06), transparent 60%),
    linear-gradient(180deg,#070C18 0%,#0A1020 100%) !important;
  color:var(--text);
}
html,body,[class*="css"]{ font-family:'Inter',system-ui,sans-serif; color:var(--text); }
[data-testid="stHeader"]{ background:transparent; }
.block-container{ padding-top:2.2rem; padding-bottom:4rem; max-width:1280px; }
::selection{ background:var(--red); color:#fff; }
h1,h2,h3,h4{ font-family:'Space Grotesk',sans-serif !important; color:var(--text) !important; letter-spacing:-.01em; font-weight:700 !important; }
[data-testid="stHeading"] h1,[data-testid="stHeading"] h2{ font-size:clamp(1.35rem,2.4vw,1.9rem)!important; padding-bottom:.55rem; border-bottom:1px solid var(--line2); }
.mono{ font-family:'JetBrains Mono',monospace; }
hr,[data-testid="stDivider"]{ border:none!important; height:1px!important; background:linear-gradient(90deg,transparent,var(--line2) 18%,var(--line2) 82%,transparent)!important; margin:1.6rem 0!important; }

/* radio segmented */
[data-testid="stRadio"]>label p{ font-family:'JetBrains Mono'; font-size:.7rem; letter-spacing:.16em; text-transform:uppercase; color:var(--dim); }
[data-testid="stRadio"] [role="radiogroup"]{ gap:.5rem; flex-wrap:wrap; background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:.45rem; box-shadow:var(--glow); }
[data-testid="stRadio"] [role="radiogroup"] label{ margin:0!important; padding:.55rem 1rem; border-radius:10px; font-family:'Space Grotesk'; font-weight:600; font-size:.9rem; color:var(--mute); cursor:pointer; transition:.22s; }
[data-testid="stRadio"] [role="radiogroup"] label:hover{ background:rgba(255,255,255,.04); color:var(--text); }
[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked){ background:var(--grad-red); color:#fff; box-shadow:0 14px 28px -16px rgba(226,35,26,.6); }
[data-testid="stRadio"] [role="radiogroup"] label>div:first-child{ display:none; }

/* inputs */
[data-testid="stSelectbox"] label p,[data-testid="stTextArea"] label p,[data-testid="stNumberInput"] label p,[data-testid="stFileUploader"] label p{ font-family:'JetBrains Mono'; font-size:.7rem; letter-spacing:.12em; text-transform:uppercase; color:var(--dim); }
[data-baseweb="select"]>div,[data-testid="stTextArea"] textarea,[data-testid="stNumberInput"] input{ border-radius:11px!important; border:1px solid var(--line2)!important; background:var(--panel)!important; color:var(--text)!important; font-family:'Inter'!important; }
[data-baseweb="select"] *{ color:var(--text)!important; }
[data-baseweb="select"]>div:focus-within,[data-testid="stTextArea"] textarea:focus,[data-testid="stNumberInput"] input:focus{ border-color:var(--red)!important; box-shadow:0 0 0 3px rgba(226,35,26,.18)!important; }

/* buttons */
.stButton>button,[data-testid="stFormSubmitButton"]>button,[data-testid="stDownloadButton"]>button{ font-family:'Space Grotesk'; font-weight:700; border-radius:11px; padding:.62rem 1.4rem; border:none; background:var(--grad-red); color:#fff; box-shadow:0 16px 30px -16px rgba(226,35,26,.6); transition:transform .2s,box-shadow .2s,filter .2s; }
.stButton>button:hover,[data-testid="stFormSubmitButton"]>button:hover,[data-testid="stDownloadButton"]>button:hover{ transform:translateY(-2px); filter:brightness(1.06); color:#fff; }

[data-testid="stFileUploaderDropzone"]{ background:var(--panel); border:1.5px dashed var(--line2); border-radius:14px; color:var(--mute); }
[data-testid="stForm"]{ background:var(--panel); border:1px solid var(--line); border-radius:18px; padding:1.4rem 1.5rem; box-shadow:var(--glow); }
[data-testid="stAlert"]{ border-radius:12px; border:1px solid var(--line2); background:var(--panel2); color:var(--text); }
[data-testid="stPlotlyChart"]{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:.4rem .4rem 0; box-shadow:var(--glow); }

/* custom components */
.aida-eyebrow{ font-family:'JetBrains Mono'; font-size:.7rem; letter-spacing:.3em; text-transform:uppercase; color:var(--red-warm); display:flex; align-items:center; gap:.7rem; margin-bottom:.15rem; }
.aida-eyebrow::after{ content:""; height:1px; flex:1; max-width:120px; background:currentColor; opacity:.4; }
.aida-sec-title{ font-family:'Space Grotesk'; font-weight:700; color:var(--text); font-size:clamp(1.3rem,2.4vw,1.85rem); line-height:1.05; margin:0 0 .2rem; }
.aida-kpi-grid{ display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:.8rem; margin:.4rem 0 .2rem; }
.aida-kpi{ position:relative; overflow:hidden; background:linear-gradient(180deg,var(--panel2),var(--panel)); border:1px solid var(--line); border-radius:14px; padding:1rem 1.05rem .95rem 1.2rem; box-shadow:var(--glow); transition:transform .25s,border-color .25s; }
.aida-kpi:hover{ transform:translateY(-3px); border-color:var(--line2); }
.aida-kpi .kbar{ position:absolute; left:0; top:0; width:4px; height:100%; background:var(--grad-red); box-shadow:0 0 18px rgba(226,35,26,.5); }
.aida-kpi.accent-ink .kbar{ background:linear-gradient(180deg,#6E8FD6,#3a4f86); box-shadow:0 0 18px rgba(110,143,214,.4); }
.aida-kpi .klabel{ font-family:'JetBrains Mono'; font-size:.64rem; letter-spacing:.06em; text-transform:uppercase; color:var(--mute); line-height:1.3; min-height:2.2em; }
.aida-kpi .kvalue{ font-family:'Space Grotesk'; font-weight:700; font-size:1.45rem; color:var(--text); margin-top:.35rem; line-height:1; word-break:break-word; }
.aida-kpi .ksub{ font-family:'JetBrains Mono'; font-size:.6rem; color:var(--dim); margin-top:.25rem; }
.aida-chip{ display:inline-flex; align-items:center; gap:.5rem; padding:.5rem .85rem; border-radius:11px; color:#06121f; font-family:'Space Grotesk'; font-weight:700; font-size:.82rem; box-shadow:0 0 22px -2px var(--chipglow,rgba(0,0,0,.4)); }
.aida-chip .dot{ width:8px; height:8px; border-radius:50%; background:rgba(0,0,0,.35); }
.aida-chip .cls{ font-family:'JetBrains Mono'; font-size:.62rem; letter-spacing:.12em; opacity:.7; }
.aida-formula{ font-family:'JetBrains Mono'; font-size:.85rem; color:#C7D3EA; background:rgba(255,255,255,.03); border:1px solid var(--line); border-left:3px solid var(--red); border-radius:10px; padding:.6rem .85rem; margin:.5rem 0 .6rem; line-height:1.5; }
.aida-ind-fam{ font-family:'JetBrains Mono'; font-size:.62rem; letter-spacing:.14em; text-transform:uppercase; color:var(--red-warm); margin-bottom:.35rem; }
.aida-ind-name{ font-family:'Space Grotesk'; font-weight:700; color:var(--text); font-size:1.12rem; line-height:1.1; margin-bottom:.15rem; }
.aida-ind-value{ font-family:'JetBrains Mono'; font-size:.78rem; color:var(--mute); background:rgba(255,255,255,.03); border:1px solid var(--line); border-radius:8px; padding:.18rem .5rem; display:inline-block; margin-bottom:.55rem; }
.aida-ind-value b{ color:var(--text); }
.aida-ind-desc{ font-size:.95rem; line-height:1.55; color:#B8C4DC; }
.aida-spark-title{ font-family:'JetBrains Mono'; font-size:.62rem; letter-spacing:.1em; text-transform:uppercase; color:var(--mute); font-weight:600; margin-bottom:.3rem; }
.aida-disclaimer{ background:var(--panel); border:1px solid var(--line); border-left:4px solid var(--dim); border-radius:10px; padding:.8rem 1rem; color:var(--mute); font-size:.85rem; line-height:1.5; }
.aida-disclaimer b{ color:var(--text); }
.aida-bubble{ font-size:.92rem; line-height:1.55; padding:.7rem .95rem; border-radius:12px; margin:.25rem 0; max-width:94%; }
.aida-bubble .lbl{ font-family:'JetBrains Mono'; font-size:.56rem; letter-spacing:.12em; text-transform:uppercase; display:block; margin-bottom:.3rem; }
.aida-bubble.user{ background:var(--panel2); border:1px solid var(--line); color:#D7E0F2; margin-left:auto; }
.aida-bubble.user .lbl{ color:var(--mute); }
.aida-bubble.ai{ background:var(--panel); border:1px solid var(--line); color:#C7D3EA; box-shadow:var(--glow); }
.aida-bubble.ai .lbl{ color:var(--red-warm); }
.aida-hero{ display:flex; align-items:center; justify-content:space-between; gap:1.2rem; flex-wrap:wrap; margin-bottom:.4rem; }
.aida-hero .brand{ display:flex; align-items:center; gap:.9rem; }
.aida-hero .brand .glyph{ width:42px; height:42px; border-radius:12px; background:var(--grad-red); display:grid; place-items:center; color:#fff; font-family:'Space Grotesk'; font-weight:700; font-size:1.05rem; box-shadow:0 0 26px -4px rgba(226,35,26,.6); }
.aida-hero .brand .txt .t{ font-family:'Space Grotesk'; font-weight:700; font-size:1.15rem; color:var(--text); line-height:1; }
.aida-hero .brand .txt .s{ font-family:'JetBrains Mono'; font-size:.62rem; letter-spacing:.18em; text-transform:uppercase; color:var(--mute); margin-top:.25rem; }
.aida-hero .tag{ font-family:'JetBrains Mono'; font-size:.6rem; letter-spacing:.14em; text-transform:uppercase; color:var(--red-warm); border:1px solid rgba(255,106,61,.3); background:rgba(255,106,61,.08); padding:.35rem .65rem; border-radius:8px; }
"""


# ---------------------------------------------------------------------------
# COMPONENTI LFI (aggiunti per la dashboard del Leasys Financial Index)
# ---------------------------------------------------------------------------
#  Usano le variabili del tema scuro con un ripiego per il tema chiaro.
_LFI_CSS = r"""
.lfi-badge{ display:inline-flex; align-items:center; gap:.55rem; color:#fff; padding:.7rem 1.05rem; border-radius:13px;
  font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.25rem; box-shadow:0 14px 28px -14px rgba(0,0,0,.6); }
.lfi-badge .dot{ width:9px; height:9px; border-radius:50%; background:rgba(255,255,255,.85); }
.lfi-badge .of{ font-size:.8rem; font-weight:500; opacity:.8; }
.lfi-badge .lab{ font-family:'JetBrains Mono',monospace; font-size:.62rem; letter-spacing:.12em; opacity:.9; margin-left:.25rem; }
.lfi-pd{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:3.1rem; line-height:1; color:var(--text,#0A1F44); }
.lfi-pd-label{ font-family:'JetBrains Mono',monospace; font-size:.66rem; letter-spacing:.14em; text-transform:uppercase;
  color:var(--mute,#52617e); margin-bottom:.45rem; }
.lfi-pd-band{ font-family:'JetBrains Mono',monospace; font-size:.8rem; color:var(--mute,#52617e); margin-top:.5rem; }
.lfi-note{ font-size:.9rem; line-height:1.55; color:var(--mute,#52617e); margin-top:.6rem; }
.lfi-note b{ color:var(--text,#0A1F44); }
.lfi-alert{ border:1px solid rgba(255,106,61,.35); border-left:4px solid var(--red-warm,#FF6A3D); background:rgba(255,106,61,.08);
  border-radius:10px; padding:.7rem .95rem; font-size:.88rem; line-height:1.5; color:var(--text,#0A1F44); margin-top:.8rem; }
.lfi-scale{ display:flex; gap:4px; margin-top:.3rem; }
.lfi-scale .cell{ flex:1; text-align:center; padding:.5rem 0; border-radius:8px; font-family:'JetBrains Mono',monospace;
  font-size:.78rem; color:var(--mute,#52617e); background:color-mix(in srgb,var(--cc) 16%,transparent);
  border:1px solid color-mix(in srgb,var(--cc) 30%,transparent); }
.lfi-scale .cell.on{ background:var(--cc); color:#fff; font-weight:700; border-color:var(--cc);
  box-shadow:0 0 0 2px var(--text,#0A1F44), 0 10px 22px -10px var(--cc); transform:translateY(-2px); }
.lfi-scale .cell.model{ border:2px dashed var(--cc); color:var(--text,#0A1F44); }
.lfi-scale-legend{ display:flex; justify-content:space-between; font-family:'JetBrains Mono',monospace; font-size:.58rem;
  letter-spacing:.1em; text-transform:uppercase; color:var(--dim,#7c8aa6); margin-top:.35rem; }
.lfi-drv{ display:inline-flex; flex-direction:column; gap:.2rem; border:1px solid color-mix(in srgb,var(--dc) 45%,transparent);
  border-left:4px solid var(--dc); background:color-mix(in srgb,var(--dc) 10%,transparent); border-radius:10px;
  padding:.55rem .8rem; min-width:150px; }
.lfi-drv .arrow{ color:var(--dc); font-size:.85rem; line-height:1; }
.lfi-drv .eff{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.92rem; color:var(--text,#0A1F44); }
.lfi-drv .pts{ font-family:'JetBrains Mono',monospace; font-size:.68rem; color:var(--mute,#52617e); }
.lfi-factors{ display:flex; flex-direction:column; gap:.45rem; }
.lfi-factor{ display:flex; justify-content:space-between; gap:.8rem; align-items:baseline; padding:.5rem .75rem;
  border-radius:9px; border:1px solid var(--line,rgba(159,178,214,.16)); border-left:3px solid var(--dc);
  background:var(--panel,#fff); font-size:.9rem; color:var(--text,#0A1F44); }
.lfi-factor .v{ font-family:'JetBrains Mono',monospace; font-size:.72rem; color:var(--mute,#52617e); white-space:nowrap; }
.lfi-table{ width:100%; border-collapse:collapse; font-size:.88rem; background:var(--panel,#fff);
  border:1px solid var(--line,rgba(159,178,214,.16)); border-radius:12px; overflow:hidden; }
.lfi-table th{ font-family:'JetBrains Mono',monospace; font-size:.66rem; letter-spacing:.12em; text-transform:uppercase;
  color:var(--mute,#52617e); text-align:right; padding:.6rem .9rem; border-bottom:1px solid var(--line2,rgba(159,178,214,.3)); }
.lfi-table th:first-child{ text-align:left; }
.lfi-table td{ padding:.42rem .9rem; border-bottom:1px solid var(--line,rgba(159,178,214,.16)); color:var(--text,#0A1F44); }
.lfi-table td.num{ text-align:right; font-family:'JetBrains Mono',monospace; font-size:.82rem; }
.lfi-table td.neg{ color:#E5544A; }
.lfi-table tr.grp td{ font-family:'JetBrains Mono',monospace; font-size:.62rem; letter-spacing:.14em; text-transform:uppercase;
  color:var(--red-warm,#E2231A); padding-top:.8rem; }
.lfi-table tr.sub td:first-child{ padding-left:1.8rem; color:var(--mute,#52617e); }
.lfi-pill{ display:inline-block; color:#fff; font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.74rem;
  padding:.18rem .55rem; border-radius:7px; white-space:nowrap; }
.lfi-sub{ display:flex; flex-direction:column; align-items:flex-start; gap:.3rem; margin-bottom:.6rem; }
.lfi-sub .t{ font-family:'JetBrains Mono',monospace; font-size:.58rem; letter-spacing:.12em; text-transform:uppercase;
  color:var(--mute,#52617e); }
.lfi-sub .v{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.5rem; line-height:1; color:var(--text,#0A1F44); }
.lfi-subtable td .ind{ font-family:'JetBrains Mono',monospace; font-size:.66rem; color:var(--mute,#52617e); margin-top:.15rem; }
.lfi-subtable td.bar{ width:30%; white-space:nowrap; }
.lfi-subtable td.bar .track{ display:inline-block; vertical-align:middle; width:72%; height:8px; border-radius:5px;
  background:var(--line2,rgba(159,178,214,.25)); overflow:hidden; margin-right:.5rem; }
.lfi-subtable td.bar .fill{ height:100%; border-radius:5px; }
.lfi-subtable td.bar span{ font-family:'JetBrains Mono',monospace; font-size:.74rem; color:var(--mute,#52617e); }
.lfi-pill{ display:inline-block; color:#fff; font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.78rem;
  padding:.18rem .6rem; border-radius:7px; min-width:1.6rem; text-align:center; }
.lfi-subtable td{ padding:.45rem .7rem; }
.lfi-subtable td .ind{ font-family:'JetBrains Mono',monospace; font-size:.64rem; color:var(--mute,#52617e); margin-top:.15rem; }
.lfi-subtable td.dim{ color:var(--mute,#52617e); }
.lfi-subtable td.bar{ width:30%; white-space:nowrap; }
.lfi-subtable td.bar .track{ position:relative; display:inline-block; vertical-align:middle; width:74%; height:8px;
  border-radius:5px; background:rgba(159,178,214,.22); margin-right:.5rem; }
.lfi-subtable td.bar .cut{ position:absolute; top:-3px; width:1px; height:14px; background:var(--mute,#52617e); opacity:.7; }
.lfi-subtable td.bar .mark{ position:absolute; top:-4px; width:12px; height:16px; margin-left:-6px; border-radius:4px;
  box-shadow:0 0 0 2px var(--panel,#0F1729); }
.lfi-subtable td.bar span{ font-family:'JetBrains Mono',monospace; font-size:.74rem; color:var(--mute,#52617e); }
"""


def inject_lfi_css():
    """Stili dei componenti LFI: da chiamare dopo inject_theme()."""
    st.markdown("<style>" + _LFI_CSS + "</style>", unsafe_allow_html=True)
