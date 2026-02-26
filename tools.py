from monday_client import fetch_deals, fetch_work_orders
from data_cleaning import clean_items
from bi_engine import pipeline_by_sector

def handle_tool_call(tool_name, args, trace_log):

    if tool_name == "get_pipeline_by_sector":

        trace_log.append("Calling Monday Deals board API...")
        raw_deals = fetch_deals()

        trace_log.append("Calling Monday Work Orders board API...")
        raw_work = fetch_work_orders()

        deals_df = clean_items(raw_deals, trace_log)
        work_df = clean_items(raw_work, trace_log)

        if deals_df is None:
            return {"error": "Failed to fetch Deals data."}

        return pipeline_by_sector(deals_df, args["sector"], trace_log)

    return {"error": "Unknown tool"}
