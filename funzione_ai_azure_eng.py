# %% funzione_ai.py
import hashlib
import json
import streamlit as st

from new_azure_llm import call_azure_llm


def bilancio_ai_component_eng(anno_bil, bilancio_data: dict):
    """
    Componente Streamlit riutilizzabile per:
    - analisi di solvibilità
    - Q&A con memoria (follow-up)
    - vincolo dominio economico-finanziario
    - visualizzazione storica coerente (analisi iniziale + Q/A)

    Input:
        bilancio_data (dict): dati di bilancio con temporalità esplicita (t, t-1, t-2)
    """

    # =====================================================
    # PROMPT DI SISTEMA (FISSO, NASCOSTO)
    # =====================================================
    SYSTEM_PROMPT = f"""
    You are a cautious and professional financial analyst.
    Mandatory rules:
    - Use ONLY the financial statements and indicators provided.
    - The data are time‑stamped:
        - t   = latest available financial statement
        - t‑1 = previous year
        - t‑2 = two years before
        - where t = {anno_bil}
    - Evaluate both absolute levels and time dynamics.
    - Provide qualitative, concise, and non‑definitive assessments. Do not introduce external information or assumptions not supported by the data.
    - If a request is not related to economic, financial, or accounting topics, politely refuse and explain the limitation.
    - Style: financial report. Maximum 7 sentences per response.
    - MANDATORY numerical formatting:
        - decimal separator: dot (.)
        - thousands separator: comma (,)
        - EVERY number mentioned in the text must be manually rewritten in this format.
        - EVERY financial‑statement item (not indicators) must have no decimals and must be expressed in Euro €.
    - MANDATORY answer in English.
    """.strip()

    # =====================================================
    # FILTRO DOMINIO (SOFT GUARDRAIL)
    # =====================================================
    FORBIDDEN_KEYWORDS = [
        "recipe", "cooking", "holidays", "travel", "music", "movie", "TV series", "sports", "training", "medicine",
        "politics", "history", "art", "literature", "philosophy", "technology", "programming", "coding", "gaming",
        "animals", "nature", "astronomy", "space", "fashion", "beauty", "lifestyle", "entertainment", "relationships",
        "psychology", "self-help", "motivation", "education", "school", "university", "career"
    ]

    # =====================================================
    # UTILITY: FORMATTAZIONE NUMERICA (US-style: 1,234.56)
    # =====================================================
    def format_number_us(x, decimals=None):
        if x is None:
            return None
        try:
            if isinstance(x, bool):
                return x
            if isinstance(x, int):
                return f"{x:,}"
            if isinstance(x, float):
                d = 2 if decimals is None else int(decimals)
                return format(x, f",.{d}f")
            return x
        except Exception:
            return x


    def deep_format_numbers(obj, default_decimals=2):
        if isinstance(obj, dict):
            return {k: deep_format_numbers(v, default_decimals) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [deep_format_numbers(v, default_decimals) for v in obj]
        elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
            return format_number_us(obj, default_decimals)
        else:
            return obj


    def is_financial_query(text: str) -> bool:
        text = (text or "").lower()
        return not any(k in text for k in FORBIDDEN_KEYWORDS)


    def compute_bilancio_fingerprint(bilancio_data: dict) -> str:
        """
        Crea un fingerprint stabile del bilancio per capire se è cambiato.
        """
        serialized = json.dumps(bilancio_data, sort_keys=True)
        return hashlib.md5(serialized.encode("utf-8")).hexdigest()


    # =====================================================
    # INIZIALIZZAZIONE STATO
    # =====================================================
    current_fp = compute_bilancio_fingerprint(bilancio_data)

    if "bilancio_fingerprint" not in st.session_state:
        st.session_state.bilancio_fingerprint = current_fp

    elif st.session_state.bilancio_fingerprint != current_fp:
        # 🔥 NUOVO BILANCIO → RESET COMPLETO AI
        st.session_state.bilancio_fingerprint = current_fp

        st.session_state.bilancio_analysis_done = False
        st.session_state.bilancio_initial_analysis = None
        st.session_state.history = []
        st.session_state.indicators_str = None

        # opzionale: pulisce eventuali input pendenti
        if "bilancio_user_question" in st.session_state:
            st.session_state.bilancio_user_question = ""

    if "bilancio_analysis_done" not in st.session_state:
        st.session_state.bilancio_analysis_done = False

    # Analisi iniziale (stringa) da rendere sempre
    if "bilancio_initial_analysis" not in st.session_state:
        st.session_state.bilancio_initial_analysis = None

    # Storico Q/A: lista di dict {"question": str, "answer": str}
    if "history" not in st.session_state:
        st.session_state.history = []

    # Stringa indicatori, per costruire il contesto testuale nei follow-up
    if "indicators_str" not in st.session_state:
        st.session_state.indicators_str = None

    # (Opzionale) limite turni per contenere la lunghezza del prompt
    MAX_TURNS = 12

    # =====================================================
    # UTILITY: FORMATTAZIONE INDICATORI
    # =====================================================
    def build_indicators_str(bil_data: dict) -> str:
        """
        Ritorna una stringa leggibile degli indicatori (se presenti) o,
        in mancanza, un riassunto JSON dei dati rilevanti.
        """
        try:
            if isinstance(bil_data, dict) and "indicatori" in bil_data:
                formatted = deep_format_numbers(bil_data["indicatori"])
            else:
                formatted = deep_format_numbers(bil_data)
            return json.dumps(formatted, indent=2, ensure_ascii=False)
        except Exception:
            return str(bil_data)


    # =====================================================
    # OPZIONI: RESET CONVERSAZIONE
    # =====================================================
    # with st.expander("⚙️ Opzioni"):
    #     if st.button("🔄 Reset conversazione"):
    #         st.session_state.bilancio_analysis_done = False
    #         st.session_state.bilancio_initial_analysis = None
    #         st.session_state.history = []
    #         st.session_state.indicators_str = None
    #         # Pulisce eventuale input dell'utente
    #         if "bilancio_user_question" in st.session_state:
    #             st.session_state.bilancio_user_question = ""
    #         st.experimental_rerun()

    # =====================================================
    # ANALISI INIZIALE (eseguita una sola volta)
    # =====================================================
    if not st.session_state.bilancio_analysis_done:
        with st.form("ai_start_form"):
            start_analysis = st.form_submit_button("🧠 Start AI Analysis")
            
        if start_analysis:
            with st.spinner("Financial‑statement analysis in progress...")

                # Preparazione payload e indicatori per i follow-up
                payload_dict = deep_format_numbers(bilancio_data)
                payload = json.dumps(payload_dict, indent=2, ensure_ascii=False)

                st.session_state.indicators_str = build_indicators_str(bilancio_data)

                initial_prompt = f"""
                Based on the following financial‑statement data and indicators,
                provide a qualitative and prudent assessment of the company’s solvency.
                The data include:
                financial‑statement items over three fiscal years
                derived financial indicators, with formulas:
                indicator 1 = equity / total assets
                indicator 2 = current assets / current liabilities
                indicator 3 = (total debt − liquidity) / EBITDA
                indicator 4 = cash flow / total assets
                indicator 5 = financial expenses / revenue
                Do not use the term "indicator" or any abbreviation such as "ind".
                explicit time labels (t, t‑1, t‑2), where t = {anno_bil}. Do not use the term "t".
                MANDATORY answer in English.
                Data:
                {payload}
                """.strip()

                # Chiamata LLM: prompt iniziale come unico messaggio utente
                analysis = call_azure_llm(
                    system_prompt=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": initial_prompt}]
                )

                # Salvo analisi iniziale e stato
                st.session_state.bilancio_initial_analysis = analysis
                st.session_state.bilancio_analysis_done = True

    # =====================================================
    # SEZIONE ANALISI INIZIALE (sempre visibile se esiste)
    # =====================================================
    if st.session_state.bilancio_analysis_done:
        st.markdown("### 🧠 Initial credit analysis")
        if st.session_state.bilancio_initial_analysis:
            st.write(st.session_state.bilancio_initial_analysis)
        else:
            st.info("The initial analysis is not available.")

    # =====================================================
    # DISCLAIMER
    # =====================================================
    st.markdown(
        """
        <div style="background-color:#f8f9fa; padding:12px; border-left:4px solid #6c757d;">
            <strong>Disclaimer</strong><br>
            The assessments generated by the AI analyst are based exclusively on the data provided and may contain inaccuracies.
            The analyses do not replace human professional judgment nor constitute any form of formal credit assessment.
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # FOLLOW-UP CON MEMORIA (CHAT STYLE)
    # =====================================================
    if st.session_state.bilancio_analysis_done:

        st.markdown("---")
        st.subheader("💬 Chat with the AI Analyst")

        # 1️⃣ MOSTRA SEMPRE LO STORICO (PRIMA DEL FORM)
        if st.session_state.history:
            for turn in st.session_state.history:
                st.markdown("**👤 Operator:**")
                st.markdown(turn["question"])
                st.markdown("**🤖 AI Analyst:**")
                st.markdown(turn["answer"])
                st.markdown("---")

        # 2️⃣ FORM SOLO PER LA NUOVA DOMANDA
        with st.form(key="bilancio_followup_form"):

            user_question = st.text_area(
                "New question",
                placeholder="E.g. Does the current level of financial leverage allow the company to absorb new car‑leasing debt without excessively deteriorating its risk profile?"
            )

            submitted = st.form_submit_button("💬 Invia")

        # 3️⃣ GESTIONE SUBMIT
        if submitted:

            q = (user_question or "").strip()
            if not q:
                st.warning("Insert a question before sending.")
                return

            if not is_financial_query(q):
                st.warning("⚠️ I can answer only economic or financial‑statement–related questions.")
                return

            indicators_block = st.session_state.indicators_str
            analysis_block = st.session_state.bilancio_initial_analysis

            conversation = f"""
    Indicators:
    {indicators_block}

    Initial analysis:
    {analysis_block}
    """

            for turn in st.session_state.history[-MAX_TURNS:]:
                conversation += f"\nUser: {turn['question']}"
                conversation += f"\nAnalyst: {turn['answer']}"

            conversation += f"\nUtente: {q}\nAnalista:"

            with st.spinner("Processing response..."):
                answer = call_azure_llm(
                    system_prompt=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": conversation}]
                )

            st.session_state.history.append({
                "question": q,
                "answer": answer
            })

            # forza refresh visivo mantenendo lo stato
            st.rerun()
