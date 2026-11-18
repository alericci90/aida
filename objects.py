# %% objects
# ============================================================================
#  AIDA · LEASYS FINANCIAL INDEX — METADATI DEL MODELLO (nessuna logica)
# ----------------------------------------------------------------------------
#  Unica fonte per: scala delle classi, aree, indicatori del nucleo, scheda del
#  modello. La dashboard (app.py) e il prompt dell'AI Analyst
#  (funzione_ai_azure_eng.py) leggono da qui: cambiando una definizione in
#  questo file cambiano insieme la pagina e cio' che viene detto all'LLM.
# ============================================================================

# ---------------------------------------------------------------------------
# SCALA DELLE CLASSI DI RISCHIO
# ---------------------------------------------------------------------------
# Tagli ufficiali forniti dall'utente il 18/11/2026: 5 soglie sulla PD calibrata (pd_cal) -> 6 classi.
# Ogni valore e' l'estremo superiore della classe (PD < soglia); l'ultima classe non ha tetto.
# Il numero di classi e' len(LFI_CLASS_CUTS) + 1: cambiando la lista tutto il resto si adegua.
LFI_CLASS_CUTS = [0.006187781657340546, 0.015126294306543511, 0.03135440708411206, 0.051596325904445246,
                  0.08868207243027773]
LFI_CLASSES_PROVISIONAL = False     # True mostra in pagina l'avviso "scala provvisoria"

# Override: patrimonio netto negativo -> classe peggiore, qualunque sia la PD.
OVERRIDE_NEGATIVE_EQUITY = True

# Colori di riferimento (il colore di ogni classe e' interpolato su questa scala) ed etichette di fascia.
BAND_COLORS = {1: "#16976A", 2: "#67B35A", 3: "#E9B820", 4: "#EE6B2C", 5: "#9E1B14"}     # classe 3 = giallo
# Colori delle 6 classi dell'LFI (1 verde -> 3 giallo -> 6 rosso scuro)
LFI_CLASS_COLORS = {1: "#16976A", 2: "#67B35A", 3: "#E9B820", 4: "#EE8A2C", 5: "#E0532A", 6: "#9E1B14"}

# Classi degli INDICATORI (5 classi, 1 = lowest risk): percentile di rischio del sottoindice di famiglia nel
# portafoglio. Classe 1 [0, 20), 2 [20, 50), 3 [50, 75), 4 [75, 90), 5 [90, 100].
IND_CLASS_CUTS_PCT = [20, 50, 75, 90]
BAND_LABELS = {1: "EXCELLENT", 2: "GOOD", 3: "ADEQUATE", 4: "WEAK", 5: "CRITICAL"}
BAND_DESCRIPTIONS = {
    1: "Default risk well below the portfolio average.",
    2: "Default risk below the portfolio average.",
    3: "Default risk in line with the portfolio average.",
    4: "Default risk above the portfolio average.",
    5: "Default risk well above the portfolio average.",
}

# ---------------------------------------------------------------------------
# SEGMENTI (cluster del modello)
# ---------------------------------------------------------------------------
CLUSTER_LABELS = {
    "industria_lower": "Agriculture, Industry & Manufacturing · revenue below EUR 5M",
    "industria_higher": "Agriculture, Industry & Manufacturing · revenue above EUR 5M",
    "costruzioni": "Construction & Real Estate",
    "commercio_lower": "Trade, Tourism & Consumer Services · revenue below EUR 5M",
    "commercio_higher": "Trade, Tourism & Consumer Services · revenue above EUR 5M",
    "finance": "ICT, Finance, Insurance & Professional Services",
    "socioculturali": "Social, Cultural & Recreational Services",
    "rac": "Rental & Transport",
}

# ---------------------------------------------------------------------------
# AREE (sottoscore del nucleo): ordine di presentazione
# ---------------------------------------------------------------------------
AREAS = {
    "liquidity": "Liquidity",
    "anagrafica": "Company age",
    "structure": "Workforce structure",
    "efficiency": "Efficiency",
    "dynamics": "Revenue stability",
    "earnings_quality": "Earnings quality",
    "leverage": "Short-term leverage",
    "growth": "Asset growth",
    "profitability": "Profitability trend",
}

# ---------------------------------------------------------------------------
# GLI 11 INDICATORI DEL NUCLEO (Run O solocore)
# ---------------------------------------------------------------------------
# trend_good: verso favorevole della serie a 3 esercizi mostrata nel grafico ("up" / "down"), None se il verso
#             non e' univoco per il modello (il commento al trend descrive solo l'andamento)
# family    : famiglia del modello (una per indicatore: e' la chiave del sottoindice di famiglia)
# direction : "risk" = valori alti aumentano il rischio; "protective" = lo riducono
#             (verso con cui l'indicatore entra nel modello; "from data" dove non era imposto)
# fmt       : come si mostra il valore -> "ratio" | "pct" | "pct_signed" | "ratio_signed" | "years"
# history   : (serie a 3 esercizi da mostrare nel grafico, etichetta, formato) oppure None
#             la serie e' una chiave di case["ratio_history"] o di case["financials_eur"]
INDICATORS = {
    "liquidita_su_attivo": dict(
        trend_good='up', family="liquidity", family_label="Liquidity",
        label="Cash buffer", area="liquidity", direction="protective", fmt="pct",
        formula="Liquidity / Total assets",
        reading="Share of assets held in cash and liquid financial assets: the buffer available to meet payments.",
        history=("liquidita_su_attivo", "Liquidity / Total assets", "pct")),
    "quick_ratio_aumento_estremo": dict(
        trend_good=None, family="dyn_liquidity", family_label="Liquidity dynamics",
        label="Sharp rise in quick ratio", area="liquidity", direction="risk", fmt="ratio",
        formula="max(Quick ratio(t) − Quick ratio(t−1), 0)  ·  Quick ratio = (Current assets − Inventories) / Current liabilities",
        reading="Size of the one-year jump in the quick ratio (0 if it fell). In the portfolio the one-year change in "
                "the quick ratio has a U-shaped relation with default: an abrupt jump goes with higher risk, like an "
                "abrupt fall.",
        history=("quick_ratio", "Quick ratio", "ratio")),
    "eta_azienda": dict(
        trend_good=None, family="anagrafica", family_label="Company age",
        label="Company age", area="anagrafica", direction="protective", fmt="years",
        formula="Years since the start of activity, at the application date",
        reading="In the portfolio, younger companies default more often.",
        history=None),
    "tfr_su_attivo": dict(
        trend_good='up', family="structure", family_label="Structure",
        label="Severance provision on assets", area="structure", direction="protective (from data)", fmt="pct",
        formula="Employee severance provision (TFR) / Total assets",
        reading="A proxy of a stable, structured workforce: companies with a sizeable provision built up over the "
                "years default less often.",
        history=("tfr_su_attivo", "TFR / Total assets", "pct")),
    "asset_turnover": dict(
        trend_good='up', family="efficiency", family_label="Efficiency",
        label="Asset turnover", area="efficiency", direction="protective", fmt="ratio",
        formula="Revenue / Total assets",
        reading="Revenue generated per euro of assets.",
        history=("asset_turnover", "Revenue / Total assets", "ratio")),
    "d_asset_turnover_2y": dict(
        trend_good='up', family="dyn_efficiency", family_label="Efficiency dynamics",
        label="Asset turnover change (2Y)", area="efficiency", direction="protective", fmt="ratio_signed",
        formula="Asset turnover(t) − Asset turnover(t−2)",
        reading="Whether assets are producing more or less revenue than two years earlier.",
        history=("asset_turnover", "Revenue / Total assets", "ratio")),
    "vol_ricavi_3y": dict(
        trend_good=None, family="dynamics", family_label="Revenue dynamics",
        label="Revenue volatility (3Y)", area="dynamics", direction="risk", fmt="ratio",
        formula="Standard deviation / |mean| of revenue over the last three fiscal years",
        reading="How unstable revenue has been, in either direction: strong swings go with higher risk.",
        history=("revenue", "Revenue", "eur")),
    "imposte_su_utile_ante": dict(
        trend_good='up', family="earnings_quality", family_label="Earnings quality",
        label="Effective tax rate", area="earnings_quality", direction="protective (from data)", fmt="pct",
        formula="Taxes / Pre-tax result  (only if the pre-tax result is positive; capped at 150%)",
        reading="In the portfolio a higher effective tax rate goes with lower risk. Not available when the "
                "pre-tax result is zero or negative: in that case the model uses the risk level observed for "
                "companies without a positive pre-tax result.",
        history=("imposte_su_utile_ante", "Taxes / Pre-tax result", "pct")),
    "clca": dict(
        trend_good='down', family="leverage", family_label="Leverage",
        label="Short-term debt on assets", area="leverage", direction="risk", fmt="pct",
        formula="Debts due within 12 months / Total assets",
        reading="Weight of the debts to be repaid within the year on total assets.",
        history=("clca", "Short-term debts / Total assets", "pct")),
    "cagr_attivo_1y": dict(
        trend_good=None, family="dyn_growth", family_label="Growth dynamics",
        label="Asset growth (1Y)", area="growth", direction="risk (from data)", fmt="pct_signed",
        formula="Total assets(t) / Total assets(t−1) − 1",
        reading="Very fast balance-sheet growth in one year goes with higher risk (expansion ahead of the company's "
                "financial capacity).",
        history=("total_assets", "Total assets", "eur")),
    "d_ebitda_su_attivo_2y": dict(
        trend_good='up', family="dyn_profitability", family_label="Profitability dynamics",
        label="EBITDA on assets change (2Y)", area="profitability", direction="protective", fmt="ratio_signed",
        formula="EBITDA / Total assets(t) − EBITDA / Total assets(t−2)  ·  EBITDA = gross operating margin + other income/charges",
        reading="Whether gross operating profitability has improved or worsened over two years.",
        history=("ebitda_su_attivo", "EBITDA / Total assets", "pct")),
}

# ---------------------------------------------------------------------------
# VOCI DI BILANCIO MOSTRATE (chiave in case["financials_eur"] -> etichetta)
# ---------------------------------------------------------------------------
FINANCIAL_ITEMS = [
    ("Income statement", [
        ("revenue", "Revenue"), ("ebitda", "EBITDA"), ("ebit", "EBIT"),
        ("financial_expenses", "Financial expenses"), ("pre_tax_result", "Pre-tax result"),
        ("taxes", "Taxes"), ("net_income", "Net income"), ("cash_flow", "Cash flow")]),
    ("Assets", [
        ("total_assets", "Total assets"), ("current_assets", "Current assets"),
        ("inventories", "Inventories"), ("liquidity", "Liquidity")]),
    ("Equity and liabilities", [
        ("equity", "Equity"), ("severance_provision", "Severance provision (TFR)"),
        ("long_term_debt", "Debts due beyond 12 months"), ("bank_debt_long", "  of which bank debt (beyond 12 months)"),
        ("short_term_debt", "Debts due within 12 months"), ("bank_debt_short", "  of which bank debt (within 12 months)"),
        ("current_liabilities", "Current liabilities")]),
]

# ---------------------------------------------------------------------------
# SCHEDA DEL MODELLO (numeri dal log del Run O solocore, 16/11/2026)
# ---------------------------------------------------------------------------
MODEL_INFO = {
    "name": "Leasys Financial Index (LFI)",
    "version": "Run O · fixed core",
    "target": "Default on Leasys within 12 months of the application (more than 90 days past due)",
    "sample": "57,014 applications from 39,719 companies, April 2022 – October 2025",
    "structure": "Logistic model on 11 indicators shared by all companies; level and slope specific to each of the "
                 "8 sector / size segments",
    "calibration": "Hierarchical Bayesian calibration on observed 12-month defaults, with a 90% credible band",
    "gini_test": "53.31%",          # Gini test osservate, media sui 12 fold
    "gini_test_activated": "53.78%",
    "gini_train": "55.68%",
    "validation": "3 × 4-fold cross-validation by company",
}

# ---------------------------------------------------------------------------
# INDICATORI MOSTRATI IN "INDICATOR RESULTS" E NEL RADAR
# ---------------------------------------------------------------------------
# L'eta' dell'azienda non e' un indicatore di bilancio: resta nel modello e nello SHAP, non in queste sezioni.
DISPLAY_INDICATORS = [k for k in INDICATORS if k != "eta_azienda"]

# Voci dell'ultimo bilancio mostrate nelle card "Financial Statement Indicators" (chiave -> etichetta)
FINANCIAL_CARDS = [
    ("equity", "Net Worth"), ("total_assets", "Total Assets"), ("current_assets", "Current Assets"),
    ("inventories", "Inventories"), ("liquidity", "Liquidity"), ("current_liabilities", "Current Liabilities"),
    ("short_term_debt", "Debts Due Within 12 Months"), ("severance_provision", "Severance Provision (TFR)"),
    ("revenue", "Revenues"), ("ebitda", "EBITDA"), ("pre_tax_result", "Pre-tax Result"), ("taxes", "Taxes"),
]

# Card "Customer Data": tre gruppi, in quest'ordine. (gruppo, chiave nel file payline/<case_id>.json, etichetta, formato)
# formato: eur | int | date | text. Nel mock-up i valori sono simulati da tools/build_cases.py.
CUSTOMER_FIELDS = [
    ("Company details", "name", "Company name", "text"),
    ("Company details", "tax_code", "Tax code", "text"),
    ("Company details", "id_bp", "Business partner ID (id_bp)", "text"),
    ("Relationship with Leasys", "customer_since", "Customer since", "date"),
    ("Relationship with Leasys", "plafond_status", "Credit line (plafond) status", "text"),
    ("Relationship with Leasys", "plafond_expiry", "Last plafond expiry", "date"),
    ("Relationship with Leasys", "outstanding", "Outstanding", "eur"),
    ("Relationship with Leasys", "plafond_granted", "Last plafond granted", "eur"),
    ("Relationship with Leasys", "plafond_under_review", "Plafond under review", "eur"),
    ("Relationship with Leasys", "past_due_band", "Past-due band", "text"),
    ("Relationship with Leasys", "past_due_fees", "Past-due rental fees", "eur"),
    ("Relationship with Leasys", "past_due_extra_fees", "Past-due extra fees", "eur"),
    ("Relationship with Leasys", "tax_loss", "Written-off amount (tax loss)", "eur"),
    ("Relationship with Leasys", "security_deposit", "Security deposit held by Leasys", "eur"),
    ("Relationship with Leasys", "previous_rejections", "Previous rejections", "text"),
    ("Relationship with Leasys", "guarantees", "Sureties and guarantors on previous applications", "text"),
    ("Relationship with Leasys", "repayment_plans", "Repayment plans", "text"),
    ("Leasys fleet", "active_contracts", "Active contracts (vehicles in fleet)", "int"),
    ("Leasys fleet", "pipeline_vehicles", "Pipeline: vehicles approved, not yet delivered", "int"),
    ("Leasys fleet", "monthly_commitment", "Monthly commitment: current + new request", "text"),
    ("Leasys fleet", "claims", "Previous claims or total losses", "text"),
    ("Leasys fleet", "services", "Vehicles with fire & theft / road tax or other services", "text"),
    ("Leasys fleet", "buyback", "Vehicles with Stellantis buy-back", "text"),
]
