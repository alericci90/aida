# %% lfi_engine
# ============================================================================
#  AIDA · LEASYS FINANCIAL INDEX — ACCESSO AI RISULTATI DEL MODELLO
# ----------------------------------------------------------------------------
#  MOCK-UP: i risultati non sono calcolati qui. Sono letti da
#  repository_lfi/cases.json, estratto dal df_out del Run O solocore con
#  tools/build_cases.py (10 pratiche reali, senza dati identificativi).
#  Quando ci sara' il motore di produzione basta che load_cases() / get_case()
#  restituiscano lo stesso dizionario: app.py e l'AI Analyst non cambiano.
#
#  Struttura di un caso (vedi tools/build_cases.py):
#    case_id, note, scoring_month, sector, ateco_2dgt, size_class, cluster,
#    customer_type, years [t-2, t-1, t],
#    financials_eur {voce: [t-2, t-1, t]}            importi in euro
#    ratio_history  {indice: [t-2, t-1, t]}
#    lfi {pd, pd_low, pd_high, pd_model, xb, xb_cluster_mean, cluster_pd_mean,
#         model_decile, pd_pct_portfolio, pd_pct_cluster, n_missing_core,
#         negative_equity}
#    indicators {nome: {value, driver, portfolio_pct, portfolio_median,
#                       cluster_median, area, family, sub_pd, sub_pct}}
#  sub_pd = sottoindice di famiglia: PD che l'azienda avrebbe guardando SOLO
#  quella famiglia (sottoscore del nucleo ricalibrato con una logit univariata
#  sul default osservato: colonne subscore_fam_<famiglia>_pd del df_out);
#  sub_pct = percentile di rischio del sottoindice nel portafoglio (quota con sottoindice strettamente piu' basso):
#            da qui la classe 1-5 dell'indicatore (indicator_class).
#    areas {area: {driver, risk_pct}}
#    name (simulato), lfi_history {years, pd [t-2, t-1, t], source, negative_equity}
#  SIMULATI (non sono nel df_out): nome e dati cliente (payline/<case_id>.json). La PD
#  dell'LFI sui bilanci precedenti (lfi_history) e' REALE dove la stessa azienda ha una
#  pratica su quel bilancio (source = "model"), simulata altrimenti ("simulated").
#  cluster_pct / cluster_median / sub_pd_cluster_mean = confronto con il segmento.
#  driver = scostamento dello score (log-odds) dalla pratica media dello stesso
#  segmento: la somma dei driver degli 11 indicatori e' xb - xb_cluster_mean.
# ============================================================================
import json
from bisect import bisect_right
from math import ceil
from pathlib import Path

from objects import BAND_COLORS, IND_CLASS_CUTS_PCT, LFI_CLASS_COLORS, LFI_CLASS_CUTS, OVERRIDE_NEGATIVE_EQUITY

REPO = Path(__file__).resolve().parent / "repository_lfi"


def load_cases() -> dict:
    """Tutti i casi del repository, per case_id (ordine del file)."""
    with open(REPO / "cases.json", "r", encoding="utf-8") as f:
        return {c["case_id"]: c for c in json.load(f)}


def load_portfolio() -> dict:
    """Statistiche del portafoglio di stima (numero pratiche, PD media per segmento)."""
    with open(REPO / "portfolio.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_customer(case_id: str) -> dict:
    """Dati cliente (anagrafica, outstanding, scaduto) da payline/<case_id>.json, nello stesso formato del
    template originale. Nel mock-up i file sono simulati da tools/build_cases.py; se il file non c'e': {}."""
    path = REPO.parent / "payline" / f"{case_id}.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        j = json.load(f)
    out, sc = j.get("Outstanding", {}), j.get("Scaduto", {})
    return {
        "Name": j.get("Name"), "TaxCode": j.get("TaxCode"), "Active Contracts": j.get("Active Contracts"),
        "Overall Outstanding": out.get("Overall Oustanding"), "Rental & RMKT Total": out.get("Rental and Remarketing Total"),
        "Rental": out.get("Rental"), "Remarketing": out.get("Remarketing"),
        "Retail & Leasing Total": out.get("Retail and Leasing Total"), "Retail": out.get("Retail"),
        "Leasing": out.get("Leasing"), "Overall Past-due": sc.get("Overall Past-due"),
        "Rental fees Past-due": sc.get("Rental fees Past-due"),
        "Rental extra-fees Past-due": sc.get("Rental extra-fees Past-due"),
    }


def case_label(case: dict) -> str:
    """Etichetta del caso nel menu: non contiene ne' la PD ne' la classe."""
    return f"{case.get('name', case['case_id'])}  ·  {case['sector']}"


def lfi_class(pd_value: float, negative_equity: bool) -> dict:
    """Classe di rischio dalla PD calibrata, con l'override del patrimonio netto negativo.
    model = classe assegnata dalla PD; final = classe mostrata; band = fascia 1-5 per colore ed etichetta."""
    n = len(LFI_CLASS_CUTS) + 1
    model = bisect_right(LFI_CLASS_CUTS, pd_value) + 1
    final = n if (OVERRIDE_NEGATIVE_EQUITY and negative_equity) else model
    return dict(final=final, model=model, n=n, overridden=final != model, band=class_band(final, n),
                color=class_color(final, n))


def indicator_class(sub_pct: float) -> dict:
    """Classe di un indicatore (1-5) dal percentile di rischio del suo sottoindice di famiglia nel portafoglio:
    1 [0, 20), 2 [20, 50), 3 [50, 75), 4 [75, 90), 5 [90, 100] (objects.IND_CLASS_CUTS_PCT)."""
    n = len(IND_CLASS_CUTS_PCT) + 1
    c = bisect_right(IND_CLASS_CUTS_PCT, sub_pct) + 1
    return dict(final=c, model=c, n=n, overridden=False, band=class_band(c, n), color=class_color(c, n))


def class_band(c: int, n: int) -> int:
    """Fascia 1-5 della classe c su n classi (solo per l'etichetta del badge). Con 6 classi: 1 EXCELLENT, 2 GOOD,
    3 ADEQUATE (la classe che contiene il default medio di portafoglio), 4 WEAK, 5 e 6 CRITICAL."""
    return max(1, min(5, ceil(c * 5 / n)))


def class_color(c: int, n: int) -> str:
    """Colore della classe c su n classi: 5 classi -> BAND_COLORS, 6 -> LFI_CLASS_COLORS (classe 3 gialla in
    entrambe), altrimenti interpolato sui 5 colori di riferimento."""
    if n == len(BAND_COLORS):
        return BAND_COLORS[c]
    if n == len(LFI_CLASS_COLORS):
        return LFI_CLASS_COLORS[c]
    t = 2.0 if n == 1 else (c - 1) * 4 / (n - 1)
    lo = min(int(t), 3)
    f = t - lo
    a, b = (BAND_COLORS[lo + 1].lstrip("#"), BAND_COLORS[lo + 2].lstrip("#"))
    rgb = [round(int(a[i:i + 2], 16) * (1 - f) + int(b[i:i + 2], 16) * f) for i in (0, 2, 4)]
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def statement_age_months(case: dict) -> int:
    """Mesi tra la chiusura dell'ultimo bilancio (31/12 dell'esercizio) e il mese di scoring."""
    y, m = (int(v) for v in case["scoring_month"].split("-"))
    return (y - case["years"][-1]) * 12 + m - 12
