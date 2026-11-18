# %% functions
# ============================================================================
#  AIDA · LEASYS FINANCIAL INDEX — FORMATTAZIONE, GRAFICI, PDF
# ----------------------------------------------------------------------------
#  Nessun calcolo del modello: qui si formattano numeri e si disegnano i
#  risultati letti da lfi_engine. Le funzioni fmt_* sono le stesse usate per
#  costruire il testo passato all'AI Analyst: un numero ha la stessa forma
#  nella pagina e nel prompt.
# ============================================================================
MOCKUP_BUILD = "2026-11-18.1340"          # versione del mock-up: deve coincidere con app.py

import math

import plotly.graph_objects as go

from lfi_engine import class_color, indicator_class
from objects import AREAS, BAND_LABELS, DISPLAY_INDICATORS, FINANCIAL_ITEMS, INDICATORS
from style import chart_colors

NA = "n/a"
RISK_UP, RISK_DOWN, NEUTRAL = "#E5544A", "#1FBE86", "#7c8aa6"
DRIVER_NEUTRAL = 0.02          # |driver| sotto questa soglia = effetto trascurabile


# ---------------------------------------------------------------------------
# FORMATTAZIONE (separatore migliaia = virgola, decimali = punto)
# ---------------------------------------------------------------------------
def _missing(x) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x))


def fmt_eur(x) -> str:
    """Importo in euro senza decimali: €1,234,000 / -€313,000."""
    if _missing(x):
        return NA
    return f"{'-' if x < 0 else ''}€{abs(x):,.0f}"


def fmt_pct(x, nd: int = 2, signed: bool = False) -> str:
    """Quota espressa come percentuale: 0.0149 -> 1.49%."""
    if _missing(x):
        return NA
    return f"{x * 100:{'+' if signed else ''},.{nd}f}%"


def fmt_ratio(x, nd: int = 3, signed: bool = False) -> str:
    if _missing(x):
        return NA
    return f"{x:{'+' if signed else ''},.{nd}f}"


def fmt_value(x, kind: str) -> str:
    """Valore di un indicatore secondo il suo formato (objects.INDICATORS[...]['fmt'])."""
    if kind == "eur":
        return fmt_eur(x)
    if kind == "pct":
        return fmt_pct(x, 1)
    if kind == "pct_signed":
        return fmt_pct(x, 1, signed=True)
    if kind == "ratio_signed":
        return fmt_ratio(x, 3, signed=True)
    if kind == "years":
        return NA if _missing(x) else f"{x:.1f} years"
    return fmt_ratio(x, 3)


def fmt_driver(d) -> str:
    """Driver in punti di log-odds con il moltiplicatore sugli odds: +0.61 (odds ×1.84)."""
    if _missing(d):
        return NA
    return f"{d:+.2f} (odds ×{math.exp(d):.2f})"


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fmt_customer(v, kind: str) -> str:
    """Valore di un campo cliente (objects.CUSTOMER_FIELDS): eur | int | date (AAAA-MM-GG) | text. None = '—'."""
    if v is None or v == "":
        return "—"
    if kind == "eur":
        return f"€ {v:,.0f}"
    if kind == "int":
        return f"{int(v):,}"
    if kind == "date":
        y, m, d = (int(x) for x in str(v).split("-"))
        return f"{d:02d} {MONTHS[m - 1]} {y}"
    return str(v)


def driver_effect(d) -> str:
    """Lettura qualitativa del driver rispetto alla pratica media del segmento."""
    if _missing(d) or abs(d) < DRIVER_NEUTRAL:
        return "neutral"
    return "raises risk" if d > 0 else "lowers risk"


def ordinal(n: float) -> str:
    n = int(round(n))
    suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


# ---------------------------------------------------------------------------
# HTML (solo presentazione)
# ---------------------------------------------------------------------------
def class_badge(cls: dict) -> str:
    """Badge della classe: stesso aspetto del template originale (functions.badge), con il colore della classe."""
    col, lab = cls["color"], BAND_LABELS[cls["band"]]
    return (
        f"<span style='display:inline-flex;align-items:center;gap:.5rem;"
        f"background:{col};color:#fff;padding:.5rem .85rem;border-radius:11px;"
        f"font-family:\"Space Grotesk\",sans-serif;font-weight:700;font-size:.82rem;"
        f"letter-spacing:.01em;box-shadow:0 12px 24px -14px rgba(0,0,0,.45);'>"
        f"<span style='width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,.85);'></span>"
        f"Class {cls['final']}"
        f"<span style='font-family:\"JetBrains Mono\",monospace;font-size:.6rem;"
        f"letter-spacing:.12em;opacity:.85;'>{lab}</span>"
        f"</span>"
    )


def score_trend_comment(classes) -> str:
    """Commento al trend dello score integrato (stesso testo del template)."""
    if classes[-1] < classes[0]:
        return "The overall risk profile shows a progressive improvement over the three-year period."
    if classes[-1] > classes[0]:
        return "The overall risk profile shows a deterioration over the period analysed."
    return "The overall risk profile appears broadly stable over the three-year period."


def subindex_description(sub_pd: float, reference_pd: float, reading: str) -> str:
    """Testo sotto l'indicatore: livello di rischio del sottoindice rispetto alla media del segmento + lettura."""
    r = sub_pd / reference_pd
    level = ("well below" if r < 0.5 else "below" if r < 0.85 else "in line with" if r <= 1.15
             else "above" if r <= 1.75 else "well above")
    return f"On this indicator alone, default risk is {level} the average of its segment. {reading}"


def trend_comment(values, label: str, trend_good) -> str:
    """Commento all'andamento su tre esercizi (stessa soglia del template: variazione oltre il 5 % del valore
    iniziale). trend_good = "up" / "down" se il verso e' favorevole per il modello, None se non e' univoco."""
    v0, v2 = values[0], values[-1]
    if _missing(v0) or _missing(v2):
        return f"{label}: the three-year trend is not available for all fiscal years."
    delta = v2 - v0
    if abs(delta) <= max(abs(v0) * 0.05, 1e-6):
        return f"{label} is broadly stable over the three-year period."
    state = "up" if delta > 0 else "down"
    moved = "has increased" if state == "up" else "has decreased"
    if trend_good is None:
        return f"{label} {moved} over the three-year period."
    signal = "a favourable" if state == trend_good else "an unfavourable"
    return f"{label} {moved} over the three-year period: {signal} signal on this indicator."


def class_scale(cls: dict) -> str:
    """Striscia delle classi con la classe finale evidenziata (e quella del modello, se c'e' override)."""
    n = cls["n"]
    cells = []
    for c in range(1, n + 1):
        css = "cell on" if c == cls["final"] else ("cell model" if c == cls["model"] else "cell")
        cells.append(f"<div class='{css}' style='--cc:{class_color(c, n)};'>{c}</div>")
    return (
        "<div class='lfi-scale'>" + "".join(cells) + "</div>"
        "<div class='lfi-scale-legend'><span>lowest risk</span><span>highest risk</span></div>"
    )


def indicator_summary_table(case: dict) -> str:
    """Tabella sintetica accanto al radar: per indicatore il sottoindice di famiglia, la media del segmento, il
    percentile di rischio nel portafoglio (con i tagli delle classi) e la classe 1-5. Dal piu' al meno rischioso."""
    cuts = "".join(f"<span class='cut' style='left:{p}%;'></span>" for p in (20, 50, 75, 90))
    rows = []
    for k in sorted(DISPLAY_INDICATORS, key=lambda k: -case["indicators"][k]["sub_pct"]):
        m, ind = INDICATORS[k], case["indicators"][k]
        c = indicator_class(ind["sub_pct"])
        pct = ind["sub_pct"]
        rows.append(
            f"<tr><td>{m['label']}<div class='ind'>{m['family_label']} · value {fmt_value(ind['value'], m['fmt'])}"
            f"</div></td>"
            f"<td class='num'>{fmt_pct(ind['sub_pd'])}</td><td class='num dim'>{fmt_pct(ind['sub_pd_cluster_mean'])}</td>"
            f"<td class='bar'><div class='track'>{cuts}<div class='mark' style='left:{pct:.0f}%;"
            f"background:{c['color']};'></div></div><span>{pct:.0f}</span></td>"
            f"<td class='num'><span class='lfi-pill' style='background:{c['color']};'>{c['final']}</span></td></tr>")
    return ("<table class='lfi-table lfi-subtable'><thead><tr><th>Indicator · family</th><th>Sub-index PD</th>"
            "<th>Segment avg</th><th>Risk percentile</th><th>Class</th></tr></thead><tbody>" + "".join(rows)
            + "</tbody></table>")


def financial_table(case: dict) -> str:
    """Tabella HTML delle voci di bilancio sui tre esercizi (euro)."""
    years, fin = case["years"], case["financials_eur"]
    head = "".join(f"<th>{y}</th>" for y in years)
    rows = []
    for group, items in FINANCIAL_ITEMS:
        rows.append(f"<tr class='grp'><td colspan='{len(years) + 1}'>{group}</td></tr>")
        for key, label in items:
            sub = " class='sub'" if label.startswith("  ") else ""
            cells = "".join(
                f"<td class='num{' neg' if (not _missing(v) and v < 0) else ''}'>{fmt_eur(v)}</td>" for v in fin[key])
            rows.append(f"<tr{sub}><td>{label.strip()}</td>{cells}</tr>")
    return (f"<table class='lfi-table'><thead><tr><th>EUR</th>{head}</tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>")


# ---------------------------------------------------------------------------
# GRAFICI
# ---------------------------------------------------------------------------
def _base_layout(cc: dict, height: int) -> dict:
    return dict(
        height=height, margin=dict(l=30, r=12, t=12, b=26),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color=cc["tick"]),
        hoverlabel=dict(bgcolor=cc["line"], font=dict(color=cc["hover"], family="JetBrains Mono")),
    )


def sparkline(values, years, kind: str = "ratio", reference=None, reference_label: str = "Segment median",
              y_range=None):
    """Andamento su tre esercizi. kind = formato dei valori ("ratio" | "pct" | "eur" | "class").
    reference = valore del segmento di riferimento, disegnato come linea tratteggiata; y_range = [min, max]."""
    cc = chart_colors()
    tickformat = {"pct": ".1%", "eur": ",.0f", "class": "d"}.get(kind, ".3f")
    hover = {"pct": "%{y:.1%}", "eur": "€%{y:,.0f}", "class": "Class %{y}"}.get(kind, "%{y:.3f}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=values, mode="lines+markers", connectgaps=False,
        line=dict(color=cc["line"], width=2.5, shape="spline", smoothing=0.6),
        marker=dict(size=8, color=cc["marker"], line=dict(color=cc["hover"], width=2)),
        hovertemplate="Year %{x}<br>" + hover + "<extra></extra>"
    ))
    layout = _base_layout(cc, 200)
    layout.update(
        xaxis=dict(title="", tickmode="array", tickvals=years, tickfont=dict(size=10, color=cc["tick"]),
                   showgrid=False, showline=True, linewidth=1, linecolor=cc["axis"], zeroline=False),
        yaxis=dict(title="", tickformat=tickformat, tickfont=dict(size=10, color=cc["tick"]), showgrid=True,
                   gridcolor=cc["grid"], showline=False, zeroline=False),
    )
    if y_range is not None:
        layout["yaxis"].update(range=y_range, dtick=1)
    elif reference is not None and not _missing(reference):
        # la scala comprende sempre la linea del segmento, anche quando e' fuori dall'intervallo dei valori
        pts = [v for v in values if not _missing(v)] + [reference]
        lo, hi = min(pts), max(pts)
        pad = (hi - lo) * 0.15 if hi > lo else max(abs(hi) * 0.1, 1e-3)
        layout["yaxis"].update(range=[lo - pad, hi + pad])
    fig.update_layout(**layout)
    if reference is not None and not _missing(reference):
        fig.add_hline(y=reference, line=dict(color=cc["tick"], width=1.2, dash="dash"),
                      annotation_text=reference_label, annotation_position="top left",
                      annotation_font=dict(size=9, color=cc["tick"]))
    return fig


def class_radar(case: dict, dark: bool = True):
    """Radar del profilo di rischio (stesso grafico del template): classe 1-5 di ogni indicatore."""
    cc = chart_colors()
    classes = [indicator_class(case["indicators"][k]["sub_pct"]) for k in DISPLAY_INDICATORS]
    n = classes[0]["n"]
    closed = lambda x: x + [x[0]]
    short = {"liquidita_su_attivo": "Cash buffer", "quick_ratio_aumento_estremo": "Quick ratio<br>jump",
             "tfr_su_attivo": "TFR /<br>assets", "asset_turnover": "Asset<br>turnover",
             "d_asset_turnover_2y": "Asset turnover<br>change 2Y", "vol_ricavi_3y": "Revenue<br>volatility",
             "imposte_su_utile_ante": "Tax<br>rate", "clca": "Short-term<br>debt", "cagr_attivo_1y": "Asset<br>growth",
             "d_ebitda_su_attivo_2y": "EBITDA/assets<br>change 2Y"}          # etichette brevi: il radar sta in mezza pagina
    labels = closed([short.get(k, INDICATORS[k]["label"]) for k in DISPLAY_INDICATORS])
    values = closed([c["final"] for c in classes])
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values, theta=labels, fill="toself", fillcolor=cc["radar_fill"],
                                  line=dict(color=cc["radar_line"], width=2.5), name="Risk Profile", showlegend=False))
    fig.add_trace(go.Scatterpolar(r=values, theta=labels, mode="markers", showlegend=False,
                                  marker=dict(size=14, color=closed([c["color"] for c in classes]),
                                              line=dict(color=cc["hover"] if dark else "white", width=2))))
    fig.update_layout(
        font=dict(family="Inter, system-ui, sans-serif", color=cc["tick"]),
        polar=dict(bgcolor="rgba(255,255,255,0)",
                   radialaxis=dict(visible=True, range=[1, n], tickvals=list(range(1, n + 1)),
                                   tickfont=dict(size=11, color=cc["tick"]), gridcolor=cc["grid"], linecolor=cc["grid"]),
                   angularaxis=dict(tickfont=dict(size=11, color=cc["angular"]), gridcolor=cc["grid"],
                                    linecolor=cc["grid"])),
        showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=560,
        margin=dict(t=60, b=60, l=95, r=95))
    return fig


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------
def genera_pdf_lfi(output_path: str, logo_path: str, case: dict, cls: dict) -> None:
    """Report PDF del caso: risultato LFI, aree, indicatori, bilancio."""
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Image as RLImage, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    blu = HexColor("#00467a")
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Titolo", fontName="Helvetica-Bold", fontSize=18, textColor=blu, spaceAfter=14))
    styles.add(ParagraphStyle(name="Sezione", fontName="Helvetica-Bold", fontSize=12, textColor=blu,
                              spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle(name="Testo", fontSize=10, leading=13, spaceAfter=6))

    def _table(data, widths, header=True):
        t = Table(data, colWidths=widths)
        style = [("GRID", (0, 0), (-1, -1), 0.4, blu), ("FONT", (0, 0), (-1, -1), "Helvetica"),
                 ("FONTSIZE", (0, 0), (-1, -1), 8.5), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]
        if header:
            style += [("BACKGROUND", (0, 0), (-1, 0), HexColor("#eaf1f8")), ("FONT", (0, 0), (-1, 0), "Helvetica-Bold")]
        t.setStyle(TableStyle(style))
        return t

    lfi = case["lfi"]
    story = [RLImage(logo_path, width=6 * cm, height=3 * cm), Spacer(1, 14),
             Paragraph("Leasys Financial Index", styles["Titolo"]),
             Paragraph(f"<b>{case['case_id']}</b> · {case['sector']} · {case['size_class']} · latest statement "
                       f"{case['years'][-1]} · scored {case['scoring_month']}", styles["Testo"]),
             Paragraph("LFI result", styles["Sezione"])]
    res = [["Risk class", f"{cls['final']} of {cls['n']} ({BAND_LABELS[cls['band']]})"],
           ["Probability of default (12 months)", fmt_pct(lfi["pd"])],
           ["90% credible band", f"{fmt_pct(lfi['pd_low'])} – {fmt_pct(lfi['pd_high'])}"],
           ["Segment average PD", fmt_pct(lfi["cluster_pd_mean"])]]
    if cls["overridden"]:
        res.append(["Override", f"Negative equity: class {cls['model']} from the PD moved to class {cls['final']}"])
    story.append(_table(res, [7 * cm, 9 * cm], header=False))

    story.append(Paragraph("Indicator results", styles["Sezione"]))
    rows = [["Family", "Indicator", "Value", "Sub-index PD", "Segment avg", "Class"]]
    for k in DISPLAY_INDICATORS:
        meta, ind = INDICATORS[k], case["indicators"][k]
        rows.append([meta["family_label"], meta["label"], fmt_value(ind["value"], meta["fmt"]),
                     fmt_pct(ind["sub_pd"]), fmt_pct(ind["sub_pd_cluster_mean"]), str(indicator_class(ind["sub_pct"])["final"])])
    story.append(_table(rows, [3.4 * cm, 5 * cm, 2.3 * cm, 2.2 * cm, 1.3 * cm, 1.8 * cm]))

    story.append(Paragraph("Financial statements (EUR)", styles["Sezione"]))
    rows = [[""] + [str(y) for y in case["years"]]]
    for _, items in FINANCIAL_ITEMS:
        for key, label in items:
            rows.append([label.strip()] + [fmt_eur(v) for v in case["financials_eur"][key]])
    story.append(_table(rows, [7 * cm, 3 * cm, 3 * cm, 3 * cm]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("The LFI is a statistical estimate based on financial statements and company age only. "
                           "It does not replace the analyst's judgement nor constitute a formal credit decision.",
                           styles["Testo"]))
    doc.build(story)
