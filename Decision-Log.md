# Decision Log: Monday.com BI Agent
**Author:** Harsh Gupta

## 1. Project Objective
To develop an AI agent capable of answering complex business intelligence queries using live data from Monday.com Deals and Work Orders boards. The system prioritizes deterministic accuracy and transparency over generative "best guesses".

## 2. Core System Architecture
The system utilizes a hybrid LLM + Deterministic Engine approach to eliminate hallucinations:
*   **LLM Role:** Strictly limited to interpreting user intent, extracting sectors, and identifying time filters.
*   **BI Engine:** All numerical calculations are performed via Python logic (Pandas) to ensure traceability.
*   **Live Integration:** Employs real-time GraphQL API calls for every query—no caching—to guarantee data freshness.
*   **Modular Layers:** Separated into API (retrieval), Cleaning (normalization), Tool Handler (orchestration), and Streamlit UI (presentation).

## 3. Engineering for Data Resilience
To handle "messy" real-world data (missing values, inconsistent currency symbols, and null sectors), the following strategies were implemented:
*   **Normalization:** Regex-based numeric cleaning and `pd.to_numeric` with error coercion.
*   **Safe Fallbacks:** Case normalization and defensive `fillna()` logic for empty dates or null values.
*   **Quality Commentary:** Every response includes a "Data Quality" section to alert the user of missing or unreliable data points.

## 4. Business Logic & Filtering
*   **Active Pipeline Definition:** Excludes "Lost," "Completed," or "On Hold" stages to provide executives with actionable health metrics rather than historical outcomes.
*   **Time-Aware Analysis:** Supports quarter-based filtering (e.g., "Q2 2025") applied to the "Tentative Close Date" before computation.
*   **Cross-Board Intelligence:** Aggregates open deals and pipeline value (Deals board) with billed vs. outstanding receivables (Work Orders board) into a single summary.

## 5. Transparency & UX
*   **Conversational Continuity:** Maintains sector context for follow-up queries and requests clarification if parameters are missing.
*   **Traceability:** The UI displays live API fetch confirmations, column mapping, and applied filters so users can see exactly how an answer was derived.

## 6. Technical Tradeoffs
*   **Latency:** Live API calls introduce slight delays compared to cached data but ensure 100% accuracy.
*   **Scope:** Prioritized deterministic correctness and cross-board intelligence over historical trend visualizations.
