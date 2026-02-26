from monday_client import fetch_deals, fetch_work_orders
from data_cleaning import clean_items
from bi_engine import run_business_summary

def resolve_column_map(deals_meta, work_meta):
    """
    Dynamically maps internal logic names to Monday.com Column IDs based on titles.
    """
    mapping = {}
    
    # Deals Board Map
    for col in deals_meta:
        title = col["title"].lower()
        if "sector/service" in title or (title == "sector" and col["type"] == "text"): 
            mapping["sector"] = col["id"]
        if "deal value" in title: 
            mapping["value"] = col["id"]
        if "deal status" in title: 
            mapping["status"] = col["id"]
        if "closure probability" in title:
            mapping["probability"] = col["id"]
        if "deal stage" in title:
            mapping["stage"] = col["id"]
        if "tentative close date" in title:
            mapping["tentative_close"] = col["id"]
        if "close date" in title:
            mapping["close"] = col["id"]

    # Work Order Board Map
    for col in work_meta:
        title = col["title"].lower()
        # Be very specific to avoid status columns
        if "billed value" in title and "rupees" in title and "incl" in title: 
            mapping["billed"] = col["id"]
        if "collected amount" in title and "rupees" in title: 
            mapping["collected"] = col["id"]
        if "amount receivable" in title: 
            mapping["receivable"] = col["id"]
        # Sector in Work Orders is often a status/color column
        if title == "sector" and col["type"] == "status":
            mapping["wo_sector"] = col["id"]
        
    return mapping

def handle_tool_call(tool_name, args, trace_log):

    if tool_name == "run_bi_query":

        trace_log.append("Fetching data from Monday.com...")
        raw_deals = fetch_deals()
        raw_work = fetch_work_orders()

        deals_df, deals_meta = clean_items(raw_deals, trace_log)
        work_df, work_meta = clean_items(raw_work, trace_log)

        if deals_df is None or work_df is None:
            return {"final_answer": "Failed to fetch necessary data from Monday.com boards."}

        # Dynamic Column Resolution
        column_map = resolve_column_map(deals_meta, work_meta)
        trace_log.append(f"Resolved Column Mapping: {column_map}")

        sector = args.get("sector")
        time_period = args.get("time_period")

        if not sector:
            return {"final_answer": "Please specify a sector to analyze."}

        return run_business_summary(
            deals_df,
            work_df,
            column_map,
            sector,
            trace_log,
            time_period=time_period
        )

    return {"final_answer": "Unknown tool call."}
