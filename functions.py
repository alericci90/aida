# %% functions
import os
import plotly.graph_objects as go
import tempfile

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from io import BytesIO

from objects import INDICATOR_META, INDICATOR_META_eng


def commento_trend(valori):
    v0, v1, v2 = valori  # anno_bil-2, anno_bil-1, anno_bil

    delta_tot = v2 - v0
    soglia = abs(v0) * 0.05  # 5% per considerare variazione significativa

    if delta_tot > soglia:
        return "L’indicatore evidenzia un miglioramento progressivo nel triennio."
    elif delta_tot < -soglia:
        return "L’indicatore mostra un progressivo deterioramento nel triennio."
    else:
        return "L’indicatore risulta sostanzialmente stabile nel periodo analizzato."


def genera_pdf_leasys(
        output_path,
        logo_path,
        dati_bilancio,
        classi,
        descrizioni,
        score_int,
        descrizione_int,
        indicatori_calcolati=None,
        grafici=None
):
    # --- import locali per evitare side effects ---


    blu = HexColor("#00467a")

    # -----------------------------------------------------------
    # DOCUMENTO PDF
    # -----------------------------------------------------------
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()
    # Evita doppie definizioni se la funzione viene richiamata più volte
    if "Titolo" not in styles:
        styles.add(ParagraphStyle(
            name="Titolo",
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=blu,
            spaceAfter=20
        ))
    if "Testo" not in styles:
        styles.add(ParagraphStyle(
            name="Testo",
            fontSize=11,
            spaceAfter=8
        ))

    story = []

    # -----------------------------------------------------------
    # LOGO
    # -----------------------------------------------------------
    story.append(RLImage(logo_path, width=6 * cm, height=3 * cm))
    story.append(Spacer(1, 20))

    # -----------------------------------------------------------
    # TITOLO PRINCIPALE
    # -----------------------------------------------------------
    story.append(Paragraph("Financial Index Dashboard", styles["Titolo"]))

    # -----------------------------------------------------------
    # DATI DI BILANCIO (valori iniziali)
    # -----------------------------------------------------------
    story.append(Paragraph("<b>Indicatori di bilancio</b>", styles["Testo"]))

    tab_bilancio = [[k, f"€ {v:,.0f}"] for k, v in dati_bilancio.items()]
    table = Table(tab_bilancio, colWidths=[8 * cm, 6 * cm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, blu),
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#eaf1f8")),
        ("FONT", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10)
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    # -----------------------------------------------------------
    # INDICATORI CALCOLATI (ind1..ind5 + CAGR)
    # -----------------------------------------------------------
    if indicatori_calcolati:
        story.append(Paragraph("<b>Indicatori calcolati</b>", styles["Testo"]))
        tab_calc = [[k, f"{v:.4f}" if v is not None else ""] for k, v in indicatori_calcolati.items()]
        table2 = Table(tab_calc, colWidths=[8 * cm, 6 * cm])
        table2.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, blu),
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#eaf1f8")),
            ("FONT", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10)
        ]))
        story.append(table2)
        story.append(Spacer(1, 20))

    # -----------------------------------------------------------
    # RISULTATI PER INDICATORE (testo + classe)
    # -----------------------------------------------------------
    story.append(Paragraph("<b>Risultati per indicatore</b>", styles["Testo"]))
    for nome, valore, classe, key, _ in classi:
        story.append(Paragraph(
            f"<b>{nome}</b> – Classe {classe}<br/>{descrizioni[key][classe]}",
            styles["Testo"]
        ))
    story.append(Spacer(1, 20))

    # -----------------------------------------------------------
    # SCORE INTEGRATO
    # -----------------------------------------------------------
    story.append(Paragraph(
        f"<b>Score integrato:</b> Classe {score_int}<br/>{descrizione_int}",
        styles["Testo"]
    ))
    story.append(Spacer(1, 20))

    # -----------------------------------------------------------
    # UTILS: inserimento immagine con ridimensionamento anti-LayoutError
    # -----------------------------------------------------------
    def _append_image(flowables, img_obj, max_width=14*cm, max_height=18*cm, title=None):
        """
        img_obj: può essere un RLImage già creato, oppure un path/BytesIO per costruirlo.
        """
        if not isinstance(img_obj, RLImage):
            img = RLImage(img_obj)
        else:
            img = img_obj

        # scaling proporzionale
        ratio_w = max_width / img.imageWidth
        ratio_h = max_height / img.imageHeight
        ratio = min(ratio_w, ratio_h, 1.0)  # non ingrandire

        img.drawWidth = img.imageWidth * ratio
        img.drawHeight = img.imageHeight * ratio

        if title:
            flowables.append(Paragraph(f"<b>{title}</b>", styles["Testo"]))
        flowables.append(img)
        flowables.append(Spacer(1, 15))

    # -----------------------------------------------------------
    # GRAFICI (SPARKLINE + RADAR) — in-memory preferito, fallback su temp
    # -----------------------------------------------------------
    tmp_files_for_cleanup = []

    if grafici:
        story.append(Paragraph("<b>Grafici</b>", styles["Titolo"]))

        # Import lazy per evitare overhead se non servono
        # Plotly figure -> bytes (PNG)
        def _fig_to_png_bytes(fig):
            # Preferisci to_image (in-memory) se disponibile
            try:
                # plotly >= 4.9, richiede kaleido installato
                png_bytes = fig.to_image(format="png", scale=2)
                return png_bytes
            except Exception:
                return None

        for nome, fig in grafici.items():
            png_bytes = _fig_to_png_bytes(fig)
            if png_bytes:
                bio = BytesIO(png_bytes)
                _append_image(story, bio, title=nome)
            else:
                # Fallback: scrivi su file temporaneo e NON cancellare finché il doc non è costruito
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                tmp.close()  # chiudi handle per evitare lock su Windows
                try:
                    # usa write_image (kaleido) — se non disponibile, solleva eccezione
                    fig.write_image(tmp.name, scale=2)
                    tmp_files_for_cleanup.append(tmp.name)
                    _append_image(story, tmp.name, title=nome)
                except Exception:
                    # Se anche questo fallisce, salta il grafico
                    try:
                        os.unlink(tmp.name)
                    except Exception:
                        pass
                    story.append(Paragraph(f"<i>Impossibile renderizzare il grafico: {nome}</i>", styles["Testo"]))
                    story.append(Spacer(1, 10))

    # -----------------------------------------------------------
    # BUILD PDF (e cleanup eventuali file temporanei DOPO il build)
    # -----------------------------------------------------------
    try:
        doc.build(story)
    finally:
        # Su Windows il lock si libera solo dopo il build; ora possiamo pulire
        for p in tmp_files_for_cleanup:
            try:
                os.unlink(p)
            except Exception:
                # Se non riuscisse, evitiamo di rompere il flusso
                pass


def sparkline(values, anno_bil, score_intg=False):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[anno_bil - 2, anno_bil - 1, anno_bil],
        y=values,
        mode="lines+markers",
        line=dict(color="#00467a", width=2),
        marker=dict(size=6),
        hovertemplate="Anno %{x}<br>Valore %{y:.4f}<extra></extra>"
    ))

    # layout comune
    base_layout = dict(
        height=220,          # più basso = più rettangolare
        width=700,           # aggiunto: lo rende più largo
        margin=dict(l=30, r=10, t=10, b=25),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="Anno",
            tickmode="array",
            tickvals=[anno_bil - 2, anno_bil - 1, anno_bil],
            tickfont=dict(size=9),
            showline=True,
            linewidth=1,
            linecolor="#00467a"
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=9),
            showline=True,
            linewidth=1,
            linecolor="#00467a"
        )
    )

    # caso specifico per score_intg
    if score_intg:
        base_layout["yaxis"]["range"] = [1, 5]

    fig.update_layout(**base_layout)
    return fig


def classe_struttura(x):
    if x >= 0.40:
        return 1
    elif x >= 0.30:
        return 2
    elif x >= 0.20:
        return 3
    elif x >= 0.10:
        return 4
    else:
        return 5


def classe_liquidita(x):
    if x >= 1.8:
        return 1
    elif x >= 1.3:
        return 2
    elif x >= 1.0:
        return 3
    elif x >= 0.7:
        return 4
    else:
        return 5


def classe_leva(x):
    if x <= 1.5:
        return 1
    elif x <= 3.0:
        return 2
    elif x <= 5.0:
        return 3
    elif x <= 7.0:
        return 4
    else:
        return 5


def classe_cashflow(x):
    if x >= 0.10:
        return 1
    elif x >= 0.06:
        return 2
    elif x >= 0.03:
        return 3
    elif x >= 0.00:
        return 4
    else:
        return 5


def classe_profit(x):
    if x <= 0.01:
        return 1
    elif x <= 0.03:
        return 2
    elif x <= 0.06:
        return 3
    elif x <= 0.10:
        return 4
    else:
        return 5


def classe_cagr(x):
    if x >= 0.20:
        return 1
    elif x >= 0.10:
        return 2
    elif x >= 0:
        return 3
    elif x >= -0.1:
        return 4
    else:
        return 5


def badge(c):
    colori = {1: "#2ecc71", 2: "#a9dfbf", 3: "#f1c40f", 4: "#e74c3c", 5: "#922b21"}
    return f"<span style='background:{colori[c]};color:white;padding:8px 16px;border-radius:12px;font-weight:700;'>Classe {c}</span>"


def commento_trend_intelligente(valori, key):
    v0, v1, v2 = valori
    delta = v2 - v0
    soglia = max(abs(v0) * 0.05, 1e-6)

    if abs(delta) <= soglia:
        stato = "flat"
    else:
        stato = "up" if delta > 0 else "down"

    meta = INDICATOR_META[key]

    return meta["commenti"][stato]


def commento_trend_intelligente_eng(valori, key):
    v0, v1, v2 = valori
    delta = v2 - v0
    soglia = max(abs(v0) * 0.05, 1e-6)

    if abs(delta) <= soglia:
        stato = "flat"
    else:
        stato = "up" if delta > 0 else "down"

    meta = INDICATOR_META_eng[key]

    return meta["commenti"][stato]


def commento_score_integrato(storico):
    if storico[2] < storico[0]:
        return "Il profilo di rischio complessivo evidenzia un miglioramento progressivo nel triennio."
    elif storico[2] > storico[0]:
        return "Il profilo di rischio complessivo mostra un deterioramento nel periodo analizzato."
    else:
        return "Il profilo di rischio complessivo risulta sostanzialmente stabile nel triennio."


def commento_score_integrato_eng(storico):
    if storico[2] < storico[0]:
        return "The overall risk profile shows a progressive improvement over the three-year period."
    elif storico[2] > storico[0]:
        return "The overall risk profile shows a deterioration over the period analysed."
    else:
        return "The overall risk profile appears broadly stable over the three-year period."


def commento_cagr_ricavi(valori, descr_cagr):
    v0, v1, v2 = valori
    delta = v2 - v0
    soglia = max(abs(v0) * 0.05, 1e-6)
    if abs(delta) <= soglia:
        stato = "flat"
    else:
        stato = "up" if delta > 0 else "down"
    meta = descr_cagr[stato]
    return meta


def commento_cagr_ricavi_eng(valori, descr_cagr_eng):
    v0, v1, v2 = valori
    delta = v2 - v0
    soglia = max(abs(v0) * 0.05, 1e-6)
    if abs(delta) <= soglia:
        stato = "flat"
    else:
        stato = "up" if delta > 0 else "down"
    meta = descr_cagr_eng[stato]
    return meta
