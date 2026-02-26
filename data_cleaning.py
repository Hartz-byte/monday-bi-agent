import pandas as pd

def clean_items(raw_json, trace_log):
    if "errors" in raw_json:
        trace_log.append(f"Monday API Error: {raw_json['errors']}")
        return None

    boards = raw_json.get("data", {}).get("boards", [])
    if not boards:
        trace_log.append("No boards returned.")
        return None

    all_cleaned = []

    for board in boards:

        trace_log.append(f"\n===== BOARD: {board.get('name', 'Unknown')} =====")

        columns_meta = board.get("columns", [])
        trace_log.append("COLUMN METADATA")

        for col in columns_meta:
            trace_log.append(
                f"Column Title: {col['title']} | "
                f"Column ID: {col['id']} | "
                f"Column Type: {col['type']}"
            )

        items = board.get("items_page", {}).get("items", [])

        if not items:
            trace_log.append("No items found in this board.")
            continue

        cleaned = []

        for item in items:
            record = {"name": item["name"]}

            for col in item["column_values"]:
                record[col["id"]] = col["text"]

            cleaned.append(record)

        df_board = pd.DataFrame(cleaned)

        trace_log.append("----- DATAFRAME DTYPES -----")
        trace_log.append(str(df_board.dtypes))

        if not df_board.empty:
            trace_log.append("----- SAMPLE ROW -----")
            trace_log.append(str(df_board.iloc[0].to_dict()))

        df_board["board_name"] = board.get("name")
        all_cleaned.append(df_board)

    if not all_cleaned:
        return None, {}

    final_df = pd.concat(all_cleaned, ignore_index=True)
    
    col_metadata = boards[0].get("columns", []) if boards else []
    
    return final_df, col_metadata
