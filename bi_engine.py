import pandas as pd

SECTOR_COL = "text_mm0y8szr"
VALUE_COL = "numeric_mm0ynd8h"
STATUS_COL = "color_mm0ywp8m"

def pipeline_by_sector(deals_df, sector, trace_log):

    deals_df[SECTOR_COL] = deals_df[SECTOR_COL].fillna("").str.lower().str.strip()
    deals_df[STATUS_COL] = deals_df[STATUS_COL].fillna("").str.lower().str.strip()

    filtered = deals_df[
        deals_df[SECTOR_COL] == sector.lower().strip()
    ]

    if filtered.empty:
        return {"message": f"No deals found for sector {sector}."}

    # Only open pipeline
    open_deals = filtered[
        filtered[STATUS_COL] != "closed"
    ]

    open_deals = open_deals.copy()
    
    open_deals[VALUE_COL] = (
        open_deals[VALUE_COL]
        .replace(r"[^\d.]", "", regex=True)
        .replace("", 0)
        .astype(float)
    )

    total_value = round(float(open_deals[VALUE_COL].sum()), 2)

    trace_log.append(f"Filtered {len(open_deals)} open deals for sector {sector}.")
    trace_log.append(f"Pipeline value computed: {total_value}")

    return {
        "final_answer": f"The {sector} sector currently has {len(open_deals)} open deals with a total pipeline value of ₹{total_value:,.2f}."
    }

def filter_by_quarter(df, date_col, quarter_string):
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    current_year = pd.Timestamp.now().year
    
    if quarter_string.lower() == "this quarter":
        current_q = pd.Timestamp.now().quarter
        return df[
            (df[date_col].dt.year == current_year) &
            (df[date_col].dt.quarter == current_q)
        ]
    
    return df
