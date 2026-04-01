# %% objects
DESCRIZIONI = {
    "struttura": {
        1: "Struttura patrimoniale molto solida.",
        2: "Buon equilibrio patrimoniale.",
        3: "Capitalizzazione sufficiente.",
        4: "Struttura finanziaria fragile.",
        5: "Grave sottocapitalizzazione."
    },
    "liquidita": {
        1: "Elevata liquidità di breve periodo.",
        2: "Liquidità adeguata.",
        3: "Equilibrio borderline.",
        4: "Tensione di liquidità.",
        5: "Grave carenza di liquidità."
    },
    "leva": {
        1: "Indebitamento sostenibile.",
        2: "Leva sotto controllo.",
        3: "Indebitamento significativo.",
        4: "Debito elevato.",
        5: "Indebitamento critico."
    },
    "cashflow": {
        1: "Elevata capacità di generare cassa.",
        2: "Buona generazione di cassa.",
        3: "Cash flow moderato.",
        4: "Debole autofinanziamento.",
        5: "Grave inefficienza operativa."
    },
    "profitability": {
        1: "Oneri finanziari trascurabili.",
        2: "Oneri finanziari contenuti.",
        3: "Incidenza rilevante.",
        4: "Oneri elevati.",
        5: "Carico finanziario critico."
    },
    "cagr_ricavi": {
        1: "Crescita dei ricavi estremamente robusta (≥20%), indice di forte competitività, capacità di scalare e accelerazione commerciale.",
        2: "Crescita sostenuta (10–20%), superiore alla media di mercato; domanda in espansione e execution efficace.",
        3: "Crescita non negativa ma moderata (0–10%): posizionamento stabile, sviluppo organico, mantenimento delle quote.",
        4: "Contrazione lieve (−10%–0%): segnali di rallentamento; pressione competitiva o mercato meno dinamico.",
        5: "Contrazione significativa (<−10%): stagnazione o perdita di competitività; revisione del modello commerciale consigliata."
    }
}

DESCRIZIONI_eng = {
    "struttura": {
        1: "Very solid capital structure.",
        2: "Good capital balance.",
        3: "Adequate capitalization.",
        4: "Fragile financial structure.",
        5: "Severe undercapitalization."
    },
    "liquidita": {
        1: "High short-term liquidity.",
        2: "Adequate liquidity.",
        3: "Borderline equilibrium.",
        4: "Liquidity tension.",
        5: "Severe liquidity shortage."
    },
    "leva": {
        1: "Sustainable indebtedness.",
        2: "Leverage under control.",
        3: "Significant indebtedness.",
        4: "High debt level.",
        5: "Critical indebtedness."
    },
    "cashflow": {
        1: "High cash generation capacity.",
        2: "Good cash generation.",
        3: "Moderate cash flow.",
        4: "Weak self-financing capacity.",
        5: "Severe operating inefficiency."
    },
    "profitability": {
        1: "Negligible financial expenses.",
        2: "Low financial expenses.",
        3: "Significant incidence.",
        4: "High financial charges.",
        5: "Critical financial burden."
    },
    "cagr_ricavi": {
        1: "Extremely robust revenue growth (≥20%), indicating strong competitiveness, scalability, and commercial acceleration.",
        2: "Sustained growth (10–20%), above market average; expanding demand and effective execution.",
        3: "Non-negative but moderate growth (0–10%): stable positioning, organic development, and market share preservation.",
        4: "Slight contraction (−10%–0%): signs of slowdown; competitive pressure or less dynamic market.",
        5: "Significant contraction (<−10%): stagnation or loss of competitiveness; a revision of the commercial model is recommended."
    }
}

DESCRIZIONE_INTEGRATO = {
    1: "Profilo complessivo molto solido.",
    2: "Profilo solido con lievi attenzioni.",
    3: "Profilo intermedio.",
    4: "Profilo fragile.",
    5: "Profilo critico."
}

DESCRIZIONE_INTEGRATO_eng = {
    1: "Overall profile is very strong.",
    2: "Strong profile with minor concerns.",
    3: "Intermediate profile.",
    4: "Weak profile.",
    5: "Critical profile."
}

INDICATOR_META = {
    "struttura": {
        "label": "Patrimonio netto / Attivo",
        "positivo": "up",
        "commenti": {
            "up": "Il rafforzamento progressivo della capitalizzazione indica una struttura patrimoniale in miglioramento.",
            "down": "La riduzione dell’incidenza del patrimonio netto segnala un indebolimento della struttura patrimoniale.",
            "flat": "La struttura patrimoniale risulta sostanzialmente stabile nel periodo osservato."
        }
    },
    "liquidita": {
        "label": "Attivo a breve / Passivo a breve",
        "positivo": "up",
        "commenti": {
            "up": "La dinamica crescente del capitale circolante evidenzia un miglioramento della posizione di liquidità.",
            "down": "La contrazione del rapporto segnala una progressiva tensione nella gestione della liquidità.",
            "flat": "Il profilo di liquidità rimane complessivamente stabile nel triennio."
        }
    },
    "leva": {
        "label": "(Debiti totali − Liquidità) / EBITDA",
        "positivo": "down",
        "commenti": {
            "up": "L’aumento della leva finanziaria indica una minore sostenibilità del debito nel tempo.",
            "down": "La riduzione della leva finanziaria segnala un miglioramento della sostenibilità dell’indebitamento.",
            "flat": "Il livello di leva finanziaria risulta sostanzialmente invariato nel periodo analizzato."
        }
    },
    "cashflow": {
        "label": "Cash flow / Attivo",
        "positivo": "up",
        "commenti": {
            "up": "La maggiore capacità di generazione di cassa riflette un miglioramento dell’efficienza degli asset.",
            "down": "La riduzione della capacità di generare cassa evidenzia un indebolimento dell’efficienza operativa.",
            "flat": "La capacità di generazione di cassa risulta stabile nel triennio."
        }
    },
    "profitability": {
        "label": "Oneri finanziari / Ricavi",
        "positivo": "down",
        "commenti": {
            "up": "L’incremento del peso degli oneri finanziari penalizza progressivamente la redditività.",
            "down": "La riduzione dell’incidenza degli oneri finanziari migliora la sostenibilità economica.",
            "flat": "Il peso degli oneri finanziari sui ricavi risulta sostanzialmente stabile."
        }
    }
}

INDICATOR_META_eng = {
    "struttura": {
        "label": "Net Worth / Total Assets",
        "positivo": "up",
        "commenti": {
            "up": "The progressive strengthening of capitalization indicates an improving capital structure.",
            "down": "The reduction in the equity ratio signals a weakening of the capital structure.",
            "flat": "The capital structure remains substantially stable over the observed period."
        }
    },
    "liquidita": {
        "label": "Current Assets / Current Liabilities",
        "positivo": "up",
        "commenti": {
            "up": "The increasing trend in working capital indicates an improvement in the liquidity position.",
            "down": "The contraction of the ratio signals rising pressure in liquidity management.",
            "flat": "The liquidity profile remains overall stable over the three-year period."
        }
    },
    "leva": {
        "label": "(Total Debts - Liquidity) / EBITDA",
        "positivo": "down",
        "commenti": {
            "up": "The increase in financial leverage indicates lower debt sustainability over time.",
            "down": "The reduction in financial leverage signals an improvement in debt sustainability.",
            "flat": "The level of financial leverage remains substantially unchanged over the period analysed."
        }
    },
    "cashflow": {
        "label": "Cash Flow / Total Assets",
        "positivo": "up",
        "commenti": {
            "up": "The improved cash-generation ability reflects greater asset efficiency.",
            "down": "The decline in cash-generation capacity highlights a weakening of operational efficiency.",
            "flat": "Cash-generation capacity remains stable over the three-year period."
        }
    },
    "profitability": {
        "label": "Financial Payables / Revenue",
        "positivo": "down",
        "commenti": {
            "up": "The increasing weight of financial expenses progressively penalizes profitability.",
            "down": "The reduction in financial-expense incidence improves economic sustainability.",
            "flat": "The weight of financial expenses relative to revenue remains substantially stable."
        }
    }
}

radar_labels = [
    "Struttura Patrimoniale",
    "Liquidità",
    "Leva Finanziaria",
    "Flussi di Cassa",
    "Profitability"
]

radar_labels_eng = [
    "Capital Structure",
    "Current Liquidity",
    "Debt Sustainability",
    "Cash Flow",
    "Profitability"
]

colori_classi_radar = {
    1: "#2ecc71",
    2: "#a9dfbf",
    3: "#f1c40f",
    4: "#e74c3c",
    5: "#922b21"
}

INDICATOR_META = {
    "struttura": {
        "label": "Patrimonio netto / Attivo",
        "positivo": "up",
        "commenti": {
            "up": "Il rafforzamento progressivo della capitalizzazione indica una struttura patrimoniale in miglioramento.",
            "down": "La riduzione dell’incidenza del patrimonio netto segnala un indebolimento della struttura patrimoniale.",
            "flat": "La struttura patrimoniale risulta sostanzialmente stabile nel periodo osservato."
        }
    },
    "liquidita": {
        "label": "Attivo a breve / Passivo a breve",
        "positivo": "up",
        "commenti": {
            "up": "La dinamica crescente del capitale circolante evidenzia un miglioramento della posizione di liquidità.",
            "down": "La contrazione del rapporto segnala una progressiva tensione nella gestione della liquidità.",
            "flat": "Il profilo di liquidità rimane complessivamente stabile nel triennio."
        }
    },
    "leva": {
        "label": "(Debiti totali − Liquidità) / EBITDA",
        "positivo": "down",
        "commenti": {
            "up": "L’aumento della leva finanziaria indica una minore sostenibilità del debito nel tempo.",
            "down": "La riduzione della leva finanziaria segnala un miglioramento della sostenibilità dell’indebitamento.",
            "flat": "Il livello di leva finanziaria risulta sostanzialmente invariato nel periodo analizzato."
        }
    },
    "cashflow": {
        "label": "Cash flow / Attivo",
        "positivo": "up",
        "commenti": {
            "up": "La maggiore capacità di generazione di cassa riflette un miglioramento dell’efficienza degli asset.",
            "down": "La riduzione della capacità di generare cassa evidenzia un indebolimento dell’efficienza operativa.",
            "flat": "La capacità di generazione di cassa risulta stabile nel triennio."
        }
    },
    "profitability": {
        "label": "Oneri finanziari / Ricavi",
        "positivo": "down",
        "commenti": {
            "up": "L’incremento del peso degli oneri finanziari penalizza progressivamente la redditività.",
            "down": "La riduzione dell’incidenza degli oneri finanziari migliora la sostenibilità economica.",
            "flat": "Il peso degli oneri finanziari sui ricavi risulta sostanzialmente stabile."
        }
    }
}

descr_cagr = {
    "up": "Ricavi in rafforzamento: CAGR positivo e in miglioramento della trazione commerciale.",
    "down": "Ricavi in contrazione: CAGR negativo e calo della dinamica commerciale.",
    "flat": "Ricavi sostanzialmente stabili: CAGR prossimo allo zero."
}

descr_cagr_eng = {
    "up": "Revenues strengthening: positive CAGR and improving commercial traction.",
    "down": "Revenues contracting: negative CAGR and weakening commercial momentum.",
    "flat": "Revenues broadly stable: CAGR close to zero."
}

COLORI_CLASSI = {
    1: "#2ecc71",
    2: "#a9dfbf",
    3: "#f1c40f",
    4: "#e74c3c",
    5: "#922b21"
}
