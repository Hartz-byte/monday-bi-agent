import pandas as pd
import re
from datetime import datetime

def apply_quarter_filter(df, date_col, time_period, trace_log):
    if not time_period or date_col not in df.columns:
        return df

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    now = datetime.now()
    current_year = now.year
    current_quarter = (now.month - 1) // 3 + 1

    trace_log.append(f"Applying time filter: {time_period}")

    # THIS QUARTER
    if time_period.lower() == "this quarter":
        filtered = df[
            (df[date_col].dt.year == current_year) &
            (df[date_col].dt.quarter == current_quarter)
        ]
        return filtered

    # LAST QUARTER
    if time_period.lower() == "last quarter":
        last_quarter = current_quarter - 1 or 4
        year = current_year if current_quarter != 1 else current_year - 1

        filtered = df[
            (df[date_col].dt.year == year) &
            (df[date_col].dt.quarter == last_quarter)
        ]
        return filtered

    # QX YYYY
    match = re.match(r"q([1-4])\s*(\d{4})", time_period.lower())
    if match:
        q = int(match.group(1))
        y = int(match.group(2))

        filtered = df[
            (df[date_col].dt.year == y) &
            (df[date_col].dt.quarter == q)
        ]
        return filtered

    # If unknown format → no filtering
    return df

def run_business_summary(deals_df, work_df, column_map, sector, trace_log, time_period=None):
    """
    Computes a deep BI summary including Deals pipeline, Probability, Stages, and Work Order financials.
    """
    # Resolve Column Names
    sector_col = column_map.get("sector", "text_mm0y8szr")
    value_col = column_map.get("value", "numeric_mm0ynd8h")
    status_col = column_map.get("status", "color_mm0ywp8m")
    prob_col = column_map.get("probability", "color_mm0y5jzt")
    stage_col = column_map.get("stage", "color_mm0y2pa6")
    
    billed_col = column_map.get("billed", "numeric_mm0ynwch")
    collected_col = column_map.get("collected", "numeric_mm0yk2h9")
    receivable_col = column_map.get("receivable", "numeric_mm0y8t8m")
    wo_sector_col = column_map.get("wo_sector", "color_mm0y9q4z")

    # Deals Filtering & Data Quality
    deals_df[sector_col] = deals_df[sector_col].fillna("").str.lower().str.strip()
    deals_df[status_col] = deals_df[status_col].fillna("").str.lower().str.strip()
    
    # Filter to sector FIRST
    filtered_deals = deals_df[deals_df[sector_col] == sector.lower().strip()].copy()
    
    # Determine which date column to use
    date_col = None
    if "tentative close date" in str(column_map).lower():
        date_col = column_map.get("tentative_close")
    elif "close date" in str(column_map).lower():
        date_col = column_map.get("close")

    # Fallback manually
    if not date_col:
        date_col = "date_mm0yfzt5"

    filtered_deals = apply_quarter_filter(
        filtered_deals,
        date_col,
        time_period,
        trace_log
    )

    if filtered_deals.empty:
        return {"final_answer": f"No active deals found for the '{sector}' sector."}

    # Count missing/empty values in filtered set BEFORE conversion
    raw_values = filtered_deals[value_col].astype(str).str.strip()
    missing_count = ((raw_values == "") | (raw_values == "nan") | (raw_values == "None")).sum()

    # Define terminal / non-pipeline stage keywords
    terminal_stage_keywords = [
        "lost",
        "completed",
        "not relevant",
        "on hold"
    ]

    # Filter active pipeline deals
    open_deals = filtered_deals[
        (filtered_deals[status_col] != "closed")
    ].copy()

    # Exclude terminal stages from pipeline
    if stage_col in open_deals.columns:
        open_deals[stage_col] = open_deals[stage_col].fillna("").str.lower()

        open_deals = open_deals[
            ~open_deals[stage_col].apply(
                lambda x: any(keyword in x for keyword in terminal_stage_keywords)
            )
        ]

        trace_log.append(
            f"Excluded terminal stages from pipeline analysis: {terminal_stage_keywords}"
        )
    
    high_prob_count = 0
    if prob_col in open_deals.columns:
        high_prob_count = len(open_deals[open_deals[prob_col].str.lower().str.contains("high", na=False)])
    
    prob_pct = round((high_prob_count / len(open_deals)) * 100, 1) if not open_deals.empty else 0
    
    stage_dist = "N/A"
    if stage_col in open_deals.columns:
        counts = open_deals[stage_col].value_counts()
        stage_dist = ", ".join([f"{stage}: {count}" for stage, count in counts.items()])

    # Clean Value Column for calculations
    open_deals[value_col] = (
        open_deals[value_col]
        .replace(r"[^\d.]", "", regex=True)
        .replace("", "0")
        .fillna("0")
        .astype(float)
    )

    total_pipeline = round(float(open_deals[value_col].sum()), 2)
    avg_size = round(total_pipeline / len(open_deals), 2) if not open_deals.empty else 0

    # Work Orders Financials (Filtered by Sector)
    if wo_sector_col in work_df.columns:
        work_df[wo_sector_col] = work_df[wo_sector_col].fillna("").str.lower().str.strip()
        work_filtered = work_df[work_df[wo_sector_col] == sector.lower().strip()].copy()
    elif sector_col in work_df.columns:
        work_df[sector_col] = work_df[sector_col].fillna("").str.lower().str.strip()
        work_filtered = work_df[work_df[sector_col] == sector.lower().strip()].copy()
    else:
        work_filtered = work_df.copy()

    for col in [billed_col, collected_col, receivable_col]:
        if col in work_filtered.columns:
            work_filtered[col] = pd.to_numeric(work_filtered[col].astype(str).replace(r"[^\d.]", "", regex=True), errors='coerce').fillna(0)
        else:
            work_filtered[col] = 0

    total_billed = work_filtered[billed_col].sum()
    total_collected = work_filtered[collected_col].sum()
    receivable = work_filtered[receivable_col].sum()

    # Construct Executive Summary
    period_label = f" ({time_period.upper()})" if time_period else ""
    summary = (
        f"### 📊 Executive Summary: {sector.upper()} SECTOR{period_label}\n\n"
        f"**Pipeline Insights:**\n"
        f"- **Total Open Deals:** {len(open_deals)}\n"
        f"- **Total Pipeline Value:** ₹{total_pipeline:,.2f}\n"
        f"- **Average Deal Size:** ₹{avg_size:,.2f}\n"
        f"- **High Probability Deals:** {prob_pct}% ({high_prob_count} deals)\n"
        f"- **Stage Distribution:** {stage_dist}\n\n"
        f"**Financial Health (Work Orders):**\n"
        f"- **Total Billed Value:** ₹{total_billed:,.2f}\n"
        f"- **Total Collected:** ₹{total_collected:,.2f}\n"
        f"- **Outstanding Receivable:** ₹{receivable:,.2f}\n\n"
        f"**⚠️ Data Quality Commentary:**\n"
        f"- Identified **{missing_count}** deals in the {sector} sector with missing/unspecified value information in the raw data."
    )

    return {"final_answer": summary}
