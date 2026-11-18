"""Estrae i casi d'esempio per il mock-up AIDA dal df_out del Run O solocore.
Uso: python build_cases.py <df_out.parquet> <cartella_output>
Nessun dato identificativo viene esportato (ne' codice fiscale, ne' id proposta)."""
import json, sys
from bisect import bisect_right
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from objects import LFI_CLASS_CUTS          # scala ufficiale delle classi (stessa della dashboard)

SRC, OUT = sys.argv[1], sys.argv[2]
CORE = ["quick_ratio_aumento_estremo_lastbil", "eta_azienda", "asset_turnover_lastbil", "tfr_su_attivo_lastbil",
        "liquidita_su_attivo_lastbil", "imposte_su_utile_ante_lastbil", "d_asset_turnover_2y_lastbil",
        "vol_ricavi_3y_lastbil", "clca_lastbil", "cagr_attivo_1y_lastbil", "d_ebitda_su_attivo_2y_lastbil"]
AREA = {"quick_ratio_aumento_estremo_lastbil": "liquidity", "liquidita_su_attivo_lastbil": "liquidity",
        "eta_azienda": "anagrafica", "asset_turnover_lastbil": "efficiency", "d_asset_turnover_2y_lastbil": "efficiency",
        "tfr_su_attivo_lastbil": "structure", "imposte_su_utile_ante_lastbil": "earnings_quality",
        "vol_ricavi_3y_lastbil": "dynamics", "clca_lastbil": "leverage", "cagr_attivo_1y_lastbil": "growth",
        "d_ebitda_su_attivo_2y_lastbil": "profitability"}
ITEMS = {  # chiave -> voce Cerved (migliaia di euro nel df)
    "revenue": "01.01.01 Ricavi Netti", "mol": "01.04.01 Margine Operativo Lordo",
    "saldo_diversi": "01.05.02 Saldo Ricavi/Oneri Diversi",
    "ebit": "01.06.01 Utile Corrente Ante Gestione Finanziaria", "financial_expenses": "01.07.02 Oneri Finanziari",
    "pre_tax_result": "01.09.01 Risultato Rettificato Ante Imposte", "taxes": "01.09.02 Imposte",
    "net_income": "01.11.01 Utile (Perdita) dell'Esercizio", "cash_flow": "01.12.01 Cash Flow",
    "inventories": "02.02.01 Rimanenze", "liquidity": "02.02.07 Liquidità",
    "current_assets": "02.02.08 Totale Attivo a Breve Termine", "total_assets": "02.03.01 Attivo",
    "equity": "03.01.05 Patrimonio Netto", "severance_provision": "03.02.02 Fondo Trattamento Fine Rapporto Oltre Esercizi Successivi",
    "long_term_debt": "03.02.03 Debiti Consolidati", "bank_debt_long": "03.02.04 Debiti Consolidati: di cui Verso Banche",
    "short_term_debt": "03.03.01 Debiti Entro Esercizio Successivo",
    "bank_debt_short": "03.03.02 Debiti Entro Esercizio Successivo: di cui Verso Banche",
    "current_liabilities": "03.03.05 Totale Passivo a Breve Termine"}
FAMILY = {"quick_ratio_aumento_estremo_lastbil": "dyn_liquidity", "liquidita_su_attivo_lastbil": "liquidity",
          "eta_azienda": "anagrafica", "asset_turnover_lastbil": "efficiency",
          "d_asset_turnover_2y_lastbil": "dyn_efficiency", "tfr_su_attivo_lastbil": "structure",
          "imposte_su_utile_ante_lastbil": "earnings_quality", "vol_ricavi_3y_lastbil": "dynamics",
          "clca_lastbil": "leverage", "cagr_attivo_1y_lastbil": "dyn_growth",
          "d_ebitda_su_attivo_2y_lastbil": "dyn_profitability"}       # una famiglia per indicatore del nucleo
RATIO_HIST = ["asset_turnover", "liquidita_su_attivo", "tfr_su_attivo", "clca", "imposte_su_utile_ante", "quick_ratio",
              "ebitda_su_attivo", "equity_ratio"]
LAGS = ["lastbil-2", "lastbil-1", "lastbil"]
meta = ["fiscalCodeOrPIva", "nuovo_sent_at_annomese", "atecoCerved_2dgt", "cl_atecoCerved_2dgt", "cl_dime", "cluster", "Tipo_Cliente",
        "xb", "pd_hat", "pd_cal", "pd_cal_q_lo", "pd_cal_q_hi", "classe_rischio_oss", "gamma_core",
        "intercetta_cluster", "logit_core", "n_mancanti_core", "annobil_lastbil", "annobil_lastbil-1",
        "annobil_lastbil-2", "calib_pd_cal_tutte", "cluster_n"]
cols = (meta + CORE + [f"contrib_core_{c}" for c in CORE] + [f"enc_core_{c}" for c in CORE]
        + [f"{v}_{l}" for v in ITEMS.values() for l in LAGS] + [f"{r}_{l}" for r in RATIO_HIST for l in LAGS]
        + [f"subcore_area_{a}_pct" for a in sorted(set(AREA.values()))]
        + [f"subscore_fam_{f}_pd" for f in FAMILY.values()] + ["oss_12m", "def_tot"])
df = pd.read_parquet(SRC, columns=list(dict.fromkeys(cols)))

# driver = scostamento dello score (log-odds, scala xb) dalla pratica media del cluster, per indicatore
g = df["gamma_core"]
for c in CORE:
    v = df[f"contrib_core_{c}"]
    df[f"drv_{c}"] = g * (v - v.groupby(df["cluster"]).transform("mean"))
df["xb_cluster_mean"] = df.groupby("cluster")["xb"].transform("mean")
assert np.allclose(df[[f"drv_{c}" for c in CORE]].sum(axis=1), df["xb"] - df["xb_cluster_mean"], atol=1e-8)
df["pd_pct_portfolio"] = df["pd_cal"].rank(pct=True) * 100
df["pd_pct_cluster"] = df.groupby("cluster")["pd_cal"].rank(pct=True) * 100
for c in CORE:      # posizione del valore grezzo nel portafoglio
    df[f"rawpct_{c}"] = df[c].rank(pct=True) * 100
for fam in FAMILY.values():      # sottoindice di famiglia: PD del sottoscore (logit univariata sulle osservate, Cella F)
    # percentile di rischio = quota del portafoglio con sottoindice STRETTAMENTE piu' basso (0-100). Pratiche con lo
    # stesso sottoindice (stesso tratto piatto dell'encoding isotonico: per il modello hanno lo stesso rischio) hanno
    # lo stesso percentile, quindi la stessa classe.
    s_ = df[f"subscore_fam_{fam}_pd"].round(9)
    df[f"subpct_{fam}"] = (s_.rank(method="min") - 1) / len(s_) * 100
for c in CORE:      # posizione del valore grezzo dentro il segmento (cluster)
    df[f"cluspct_{c}"] = df.groupby("cluster")[c].rank(pct=True) * 100
sub_clus_mean = df.groupby("cluster")[[f"subscore_fam_{f}_pd" for f in FAMILY.values()]].mean()
port_med = df[CORE].median()
clus_med = df.groupby("cluster")[CORE].median()

rev = [f"{ITEMS['revenue']}_{l}" for l in LAGS]
base = ((df["annobil_lastbil"] >= 2023) & (df["annobil_lastbil"] - df["annobil_lastbil-1"] == 1)
        & (df["annobil_lastbil-1"] - df["annobil_lastbil-2"] == 1) & (df[rev] > 0).all(axis=1)
        & df[[f"{ITEMS[k]}_lastbil" for k in ITEMS]].notna().all(axis=1))
pn_neg = df[f"{ITEMS['equity']}_lastbil"] < 0
complete = df["n_mancanti_core"] == 0
tax_missing = df["imposte_su_utile_ante_lastbil"].isna() & (df["n_mancanti_core"] == 1)
df["classe_lfi"] = df["pd_cal"].map(lambda p: bisect_right(LFI_CLASS_CUTS, p) + 1)   # classe dalla PD, senza override
PLAN = [  # (cluster, classe LFI dalla PD, filtro extra, nota): le 6 classi sono tutte rappresentate
    ("industria_higher", 1, complete & ~pn_neg, ""), ("finance", 1, complete & ~pn_neg, ""),
    ("commercio_higher", 2, complete & ~pn_neg, ""), ("industria_lower", 2, complete & pn_neg, "negative_equity"),
    ("costruzioni", 3, complete & ~pn_neg, ""), ("socioculturali", 3, complete & ~pn_neg, ""),
    ("commercio_lower", 4, complete & ~pn_neg, ""), ("commercio_lower", 5, tax_missing & ~pn_neg, "missing_tax_rate"),
    ("rac", 5, complete & ~pn_neg, ""), ("costruzioni", 6, complete & ~pn_neg, "")]
# STORICO REALE DELL'LFI. Nel campione molte aziende hanno pratiche su bilanci di anni diversi: la PD calibrata del
# modello sui bilanci precedenti e' quella delle loro pratiche precedenti (stesso codice fiscale, ultimo bilancio =
# quell'anno; se piu' pratiche sullo stesso bilancio, la piu' recente). Si simula solo l'anno che manca.
H = (df.sort_values("nuovo_sent_at_annomese").groupby(["fiscalCodeOrPIva", "annobil_lastbil"])
     .agg(pd_cal=("pd_cal", "last"), pn=(f"{ITEMS['equity']}_lastbil", "last"), **{c: (c, "last") for c in CORE}))
H_PD, H_PN = H["pd_cal"].to_dict(), H["pn"].to_dict()
H_IND = {c: H[c].to_dict() for c in CORE}
IQR = (df[CORE].quantile(0.75) - df[CORE].quantile(0.25)).to_dict()
LEVEL_LAGS = ["liquidita_su_attivo_lastbil", "tfr_su_attivo_lastbil", "asset_turnover_lastbil",
              "imposte_su_utile_ante_lastbil", "clca_lastbil"]          # indici di livello: t-1 e t-2 sono nel parquet


def indicator_history(r, case_rng) -> dict:
    """Ogni indicatore del nucleo (tranne l'eta') sui tre bilanci [t-2, t-1, t], con l'origine di ogni valore:
       model      = colonna del parquet (t; t-1 e t-2 per gli indici di livello)
       earlier    = pratica precedente della stessa azienda su quel bilancio (valore calcolato dal modello)
       computed   = ricalcolato dalle voci dei bilanci disponibili (quick ratio, attivo)
       simulated  = simulato: valore di t piu' un'oscillazione proporzionale alla dispersione del portafoglio"""
    cf, yrs = r["fiscalCodeOrPIva"], [int(r["annobil_lastbil-2"]), int(r["annobil_lastbil-1"])]
    qr = [r["quick_ratio_lastbil-2"], r["quick_ratio_lastbil-1"]]
    at = [r[f"{ITEMS['total_assets']}_lastbil-2"], r[f"{ITEMS['total_assets']}_lastbil-1"]]
    out = {}
    for c in CORE:
        if c == "eta_azienda":
            continue
        k = c.replace("_lastbil", "")
        vals, src = [], []
        for j, lag in enumerate(("lastbil-2", "lastbil-1")):
            v, s = None, None
            if c in LEVEL_LAGS and pd.notna(r.get(f"{k}_{lag}")):
                v, s = r[f"{k}_{lag}"], "model"
            elif (cf, yrs[j]) in H_IND[c] and pd.notna(H_IND[c][(cf, yrs[j])]):
                v, s = H_IND[c][(cf, yrs[j])], "earlier"
            elif c == "quick_ratio_aumento_estremo_lastbil" and j == 1 and pd.notna(qr[0]) and pd.notna(qr[1]):
                v, s = max(qr[1] - qr[0], 0.0), "computed"
            elif c == "cagr_attivo_1y_lastbil" and j == 1 and at[0] and at[0] > 0 and pd.notna(at[1]):
                v, s = at[1] / at[0] - 1, "computed"
            elif pd.notna(r[c]):
                v = r[c] + case_rng.normal(0, 0.35 * IQR[c])
                if c in ("quick_ratio_aumento_estremo_lastbil", "vol_ricavi_3y_lastbil"):
                    v = max(v, 0.0)
                s = "simulated"
            vals.append(f(v)); src.append(s)
        out[k] = dict(values=vals + [f(r[c])], source=src + ["model"])
    return out


def real_history(r) -> list:
    """[(pd, pn) o None] per t-2 e t-1 dalle pratiche precedenti della stessa azienda."""
    out = []
    for lag in ("annobil_lastbil-2", "annobil_lastbil-1"):
        key = (r["fiscalCodeOrPIva"], int(r[lag]))
        out.append((H_PD[key], H_PN[key]) if key in H_PD else None)
    return out


def history_classes(r) -> list:
    h = real_history(r)
    return [bisect_right(LFI_CLASS_CUTS, x[0]) + 1 if x else None for x in h] + [int(r["classe_lfi"])]


picked, n_new = [], 0
for cl, k, extra, note in PLAN:
    q = df[base & extra & (df["cluster"] == cl) & (df["classe_lfi"] == k)]
    assert len(q), (cl, k)
    if n_new >= 2 and (q["Tipo_Cliente"] == "ATTIVO").any():      # mock-up: al piu' 2 clienti nuovi (esposizione a zero)
        q = q[q["Tipo_Cliente"] == "ATTIVO"]
    target = q["pd_cal"].median()
    # priorita': 1) piu' anni di storico reale, 2) classi non tutte uguali sui tre anni, 3) PD vicina alla mediana
    hc = q.apply(history_classes, axis=1)
    rank_ = pd.DataFrame({"n_real": hc.map(lambda v: sum(x is not None for x in v[:2])),
                          "varied": hc.map(lambda v: len({x for x in v if x is not None}) > 1),
                          "dist": q["pd_cal"].sub(target).abs()}, index=q.index)
    best = rank_.sort_values(["n_real", "varied", "dist"], ascending=[False, False, True]).index[0]
    picked.append((best, note))
    n_new += int(df.loc[best, "Tipo_Cliente"] != "ATTIVO")

SECTOR = {"1": "Agriculture, Industry & Manufacturing", "2": "Construction & Real Estate",
          "3": "Trade, Tourism & Consumer Services", "4": "ICT, Finance, Insurance & Professional Services",
          "5": "Social, Cultural & Recreational Services", "6": "Rental & Transport"}
f = lambda x, nd=6: None if pd.isna(x) else round(float(x), nd)
cases = []
for n, (i, note) in enumerate(picked, 1):
    r = df.loc[i]
    years = [int(r["annobil_lastbil-2"]), int(r["annobil_lastbil-1"]), int(r["annobil_lastbil"])]
    fin = {k: [f(r[f"{v}_{l}"] * 1000, 0) for l in LAGS] for k, v in ITEMS.items()}          # euro
    fin["ebitda"] = [f((r[f"{ITEMS['mol']}_{l}"] + (0 if pd.isna(r[f"{ITEMS['saldo_diversi']}_{l}"]) else
                                                    r[f"{ITEMS['saldo_diversi']}_{l}"])) * 1000, 0) for l in LAGS]
    for k in ("mol", "saldo_diversi"):
        fin.pop(k)
    ym = str(int(r["nuovo_sent_at_annomese"]))
    cases.append(dict(
        case_id=f"LFI-{n:02d}", note=note, scoring_month=f"{ym[:4]}-{ym[4:]}",
        sector=SECTOR[str(r["cl_atecoCerved_2dgt"])[0]], ateco_2dgt=str(r["atecoCerved_2dgt"]).replace(".0", ""),
        size_class="Revenue above EUR 5M" if r["cl_dime"] == "sopra 5 mln" else "Revenue below EUR 5M",
        cluster=r["cluster"], customer_type={"NUOVO": "New customer", "ATTIVO": "Active customer",
                                            "RITORNO": "Returning customer"}[r["Tipo_Cliente"]],
        years=years, financials_eur=fin,
        ratio_history={k: [f(r[f"{k}_{l}"]) for l in LAGS] for k in RATIO_HIST},
        indicator_history=indicator_history(r, np.random.default_rng(7000 + n)),
        lfi=dict(xb=f(r["xb"]), pd_model=f(r["pd_hat"]), pd=f(r["pd_cal"]), pd_low=f(r["pd_cal_q_lo"]),
                 pd_high=f(r["pd_cal_q_hi"]), model_decile=int(r["classe_rischio_oss"]),
                 cluster_pd_mean=f(r["calib_pd_cal_tutte"]), xb_cluster_mean=f(r["xb_cluster_mean"]),
                 pd_pct_portfolio=f(r["pd_pct_portfolio"], 1), pd_pct_cluster=f(r["pd_pct_cluster"], 1),
                 n_missing_core=int(r["n_mancanti_core"]), negative_equity=bool(r[f"{ITEMS['equity']}_lastbil"] < 0)),
        indicators={c.replace("_lastbil", ""): dict(
            value=f(r[c]), driver=f(r[f"drv_{c}"]), portfolio_pct=f(r[f"rawpct_{c}"], 1),
            portfolio_median=f(port_med[c]), cluster_median=f(clus_med.loc[r["cluster"], c]),
            cluster_pct=f(r[f"cluspct_{c}"], 1),
            sub_pd_cluster_mean=f(sub_clus_mean.loc[r["cluster"], f"subscore_fam_{FAMILY[c]}_pd"]),
            area=AREA[c], family=FAMILY[c], sub_pd=f(r[f"subscore_fam_{FAMILY[c]}_pd"]),
            sub_pct=f(r[f"subpct_{FAMILY[c]}"], 1)) for c in CORE},
        areas={a: dict(driver=f(sum(r[f"drv_{c}"] for c in CORE if AREA[c] == a)),
                       risk_pct=f(r[f"subcore_area_{a}_pct"], 1)) for a in dict.fromkeys(AREA.values())}))
    c = cases[-1]
    assert abs(sum(v["driver"] for v in c["indicators"].values()) - (c["lfi"]["xb"] - c["lfi"]["xb_cluster_mean"])) < 1e-4

# ---------------------------------------------------------------------------------------------------------------
# DATI SIMULATI (mock-up): cio' che il parquet non contiene. Realistici, non reali; riproducibili (seed fisso).
#   1. anagrafica ed esposizione verso Leasys (payline/<case_id>.json, formato del template)
#   2. PD dell'LFI sui due bilanci precedenti (serve il motore di scoring: qui e' ricostruita dall'andamento di
#      liquidita', redditivita', debito a breve e patrimonio netto degli stessi bilanci)
# ---------------------------------------------------------------------------------------------------------------
NAMES = {"industria_higher": ["Officine Valdorba S.p.A."], "finance": ["Sistemi Arquenta S.r.l."],
         "commercio_higher": ["Distribuzione Montelisio S.p.A."], "industria_lower": ["Lavorazioni Ferrandia S.r.l."],
         "costruzioni": ["Edilizia Rovanto S.r.l.", "Costruzioni Pradalto S.p.A."],
         "socioculturali": ["Polisportiva Tivenna S.r.l."],
         "commercio_lower": ["Commerciale Brusata S.r.l.", "Emporio Orcellia S.r.l."],
         "rac": ["Autoservizi Castrivo S.r.l."]}
PAST_DUE_SHARE = {1: (0.0, 0.0), 2: (0.0, 0.0), 3: (0.0, 0.01), 4: (0.02, 0.05), 5: (0.06, 0.12), 6: (0.15, 0.30)}
PAST_DUE_BAND = {1: "No past due", 2: "No past due", 3: "1-30 days", 4: "1-30 days", 5: "31-60 days", 6: "61-90 days"}
Path(OUT).parent.joinpath("payline").mkdir(exist_ok=True)


def add_months(ym: str, k: int, day: int = 1) -> str:
    """'AAAA-MM' + k mesi -> 'AAAA-MM-GG'."""
    y, m = (int(x) for x in ym.split("-"))
    t_ = y * 12 + (m - 1) + k
    return f"{t_ // 12}-{t_ % 12 + 1:02d}-{day:02d}"


used = {}
for n, c in enumerate(cases, 1):
    rng = np.random.default_rng(2026 + n)
    k = used.get(c["cluster"], 0); used[c["cluster"]] = k + 1
    name = NAMES[c["cluster"]][k]
    # partita IVA e id_bp finti: codice ufficio 999 (inesistente) e prefisso SIM, non coincidono con dati veri
    tax = f"{int(rng.integers(1000000, 9999999)):07d}999{int(rng.integers(0, 10))}"
    id_bp = f"SIM{int(rng.integers(1000000, 9999999))}"
    cl = 6 if c["lfi"]["negative_equity"] else bisect_right(LFI_CLASS_CUTS, c["lfi"]["pd"]) + 1   # classe finale
    rev = c["financials_eur"]["revenue"][-1]
    sm = c["scoring_month"]
    kind = c["customer_type"]
    day = lambda: int(rng.integers(1, 28))
    age_m = int((c["indicators"]["eta_azienda"]["value"] or 30) * 12)          # mesi di attivita' dell'azienda
    back = lambda lo_, hi_: int(rng.integers(min(lo_, max(age_m - 2, 1)), max(min(hi_, age_m - 1), 2)))   # cliente da: dopo l'avvio
    # --- nuova richiesta in valutazione (ogni caso e' una pratica) ---
    n_contr = 0 if kind != "Active customer" else int(np.clip(round(rev / 450_000 * rng.uniform(0.7, 1.4)), 1, 60))
    req = int(np.clip(round((n_contr or rev / 900_000) * rng.uniform(0.15, 0.45)), 1, 25))
    fee_new = round(req * rng.uniform(520, 760), -1)
    under_review = round(req * rng.uniform(28_000, 38_000), -3)
    # --- rapporto e flotta ---
    if kind == "Active customer":
        since = add_months(sm, -back(24, 144), day())
        outstanding = round(n_contr * rng.uniform(16_000, 27_000), 0)
        granted = round(outstanding * rng.uniform(1.15, 1.6), -4)
        status = ("Active" if cl <= 4 else "Active · under monitoring" if cl == 5 else "Suspended")
        expiry = add_months(sm, int(rng.integers(2, 14)), day())
        monthly_cur = round(n_contr * rng.uniform(480, 720), -1)
        pipeline = int(rng.integers(0, max(2, round(n_contr * 0.15)) + 1)) if cl <= 4 else 0
    elif kind == "Returning customer":
        since = add_months(sm, -back(60, 140), day())
        outstanding, monthly_cur, pipeline = 0.0, 0.0, 0
        granted = round(under_review * rng.uniform(0.6, 1.2), -4)
        status = "Expired"
        expiry = add_months(sm, -int(rng.integers(14, 40)), day())
    else:                                                       # nuovo cliente
        since, expiry, status = None, None, "Not yet granted (first application)"
        outstanding, granted, monthly_cur, pipeline = 0.0, 0.0, 0.0, 0
    lo, hi = PAST_DUE_SHARE[cl]
    fees_pd = round(outstanding * rng.uniform(lo, hi), 0)
    fees_pd = fees_pd if fees_pd >= 250 else 0.0
    extra_pd = round(fees_pd * rng.uniform(0.04, 0.12), 0) if fees_pd else 0.0
    band = PAST_DUE_BAND[cl] if fees_pd else "No past due"
    tax_loss = round(rng.uniform(2_000, 15_000), -2) if (n_contr and cl == 6) else 0.0
    deposit = round(monthly_cur * rng.uniform(1, 3), -2) if (n_contr and cl >= 4) else 0.0
    rej_year = int(sm[:4]) - int(rng.integers(1, 3))
    rejections = (f"Yes · 1 application rejected ({rej_year})" if cl >= 5 or (kind != "Active customer" and cl >= 3)
                  else "No")
    guarantees = ("Personal guarantee of the managing director (application of " + str(rej_year) + ")"
                  if cl >= 4 and kind != "New customer" else "None")
    if band in ("31-60 days", "61-90 days"):
        inst = int(rng.integers(4, 10))
        repay = f"Active · {inst} monthly instalments of € {round(fees_pd / inst, -1):,.0f} remaining"
    else:
        repay = "None"
    claims_n = int(rng.poisson(n_contr * 0.12)) if n_contr else 0
    total_loss = int(claims_n >= 3 and rng.random() < 0.5)
    claims = ("None" if not claims_n else f"{claims_n} claim{'s' if claims_n > 1 else ''} in the last 24 months"
              + (f" · {total_loss} total loss" if total_loss else ""))
    ft = int(round(n_contr * rng.uniform(0.3, 0.9))) if n_contr else 0
    maint = int(round(n_contr * rng.uniform(0.2, 0.7))) if n_contr else 0
    services = ("None" if not (ft or maint) else f"{ft} with fire & theft / road tax · {maint} with maintenance & tyres")
    bb = int(round(n_contr * rng.uniform(0.1, 0.4))) if (n_contr and rng.random() < 0.6) else 0
    buyback = f"{bb} vehicle{'s' if bb > 1 else ''} (Stellantis brands)" if bb else "None"
    pay = {"_simulated": True,
           "company": {"name": name, "tax_code": tax, "id_bp": id_bp},
           "relationship": {"customer_since": since, "plafond_status": status, "plafond_expiry": expiry,
                            "outstanding": outstanding, "plafond_granted": granted,
                            "plafond_under_review": under_review, "past_due_band": band,
                            "past_due_fees": fees_pd, "past_due_extra_fees": extra_pd, "tax_loss": tax_loss,
                            "security_deposit": deposit, "previous_rejections": rejections,
                            "guarantees": guarantees, "repayment_plans": repay},
           "fleet": {"active_contracts": n_contr, "pipeline_vehicles": pipeline,
                     "monthly_commitment": (f"€ {monthly_cur:,.0f} current + € {fee_new:,.0f} new request "
                                            f"({req} vehicle{'s' if req > 1 else ''}) = € {monthly_cur + fee_new:,.0f}"),
                     "monthly_current": monthly_cur, "monthly_new": fee_new,
                     "claims": claims, "services": services, "buyback": buyback}}
    json.dump(pay, open(Path(OUT).parent / "payline" / f"{c['case_id']}.json", "w"), indent=2)
    c["name"] = name
    # PD sui bilanci precedenti: REALE (pratica precedente della stessa azienda) se c'e', altrimenti SIMULATA come
    # PD_t * exp(-delta), delta = peggioramento (+) o miglioramento (-) di liquidita', redditivita', debito a breve e
    # patrimonio netto da quell'anno
    rh, hist, src, neg = c["ratio_history"], [], [], []
    for j, real in enumerate(real_history(df.loc[picked[n - 1][0]])):
        if real is not None:
            hist.append(f(real[0])); src.append("model"); neg.append(bool(real[1] < 0))
            continue
        d = lambda key: (rh[key][2] or 0.0) - (rh[key][j] if rh[key][j] is not None else (rh[key][2] or 0.0))
        delta = float(np.clip(-3.0 * d("liquidita_su_attivo") - 2.0 * d("ebitda_su_attivo") + 1.0 * d("clca")
                              - 1.5 * d("equity_ratio"), -0.7, 0.7))
        hist.append(f(c["lfi"]["pd"] * np.exp(-delta))); src.append("simulated")
        neg.append(bool(c["financials_eur"]["equity"][j] < 0))
    c["lfi_history"] = dict(years=c["years"], pd=hist + [c["lfi"]["pd"]], source=src + ["model"],
                            negative_equity=neg + [c["lfi"]["negative_equity"]])

portfolio = dict(
    n_applications=int(len(df)), source="df_out_v1_runO_solocore.parquet",
    clusters={k: dict(n=int(v["cluster_n"]), pd_mean=f(v["calib_pd_cal_tutte"]), gamma=f(v["gamma_core"]),
                      intercept=f(v["intercetta_cluster"]))
              for k, v in df.groupby("cluster")[["cluster_n", "calib_pd_cal_tutte", "gamma_core", "intercetta_cluster"]].first().iterrows()},
    pd_mean_all=f(df["pd_cal"].mean()), pd_median_all=f(df["pd_cal"].median()),
    dr_observed=f(df.loc[df["oss_12m"] == 1, "def_tot"].mean()),      # livello medio dei sottoindici di famiglia
    subindex_range={FAMILY[c]: [f(df[f"subscore_fam_{FAMILY[c]}_pd"].min()), f(df[f"subscore_fam_{FAMILY[c]}_pd"].max())]
                    for c in CORE})
json.dump(cases, open(f"{OUT}/cases.json", "w"), indent=1)
json.dump(portfolio, open(f"{OUT}/portfolio.json", "w"), indent=1)
for c in cases:
    l = c["lfi"]
    print(c["case_id"], c["cluster"], c["years"][-1], "classe", bisect_right(LFI_CLASS_CUTS, l["pd"]) + 1, f"PD {l['pd']:.4%} [{l['pd_low']:.4%}-{l['pd_high']:.4%}] dec {l['model_decile']}",
          f"cluster {l['cluster_pd_mean']:.4%}", c["note"], f"rev {c['financials_eur']['revenue'][-1]:,.0f}")
print(json.dumps(portfolio)[:600])
