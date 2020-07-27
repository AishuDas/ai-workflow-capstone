import os
import pandas as pd
import json


def read_all_json_files(path, column_dict, inconsistent_col, keys):
    list_files = [pos_json for pos_json in os.listdir(path) if pos_json.endswith('.json')]
    sorted_list_files = sorted(list_files)
    master_df = pd.DataFrame(columns=keys)
    for file in sorted_list_files:
        with open(path+file, 'r') as f:
            data = json.load(f)
            invoice_df = pd.DataFrame(data)
        for i in inconsistent_col:
            if i in invoice_df.columns:
                invoice_df = invoice_df.rename(columns=column_dict)
        master_df = master_df.append(invoice_df, ignore_index=True)
    return master_df


def maintain_datatype(master_df):
    master_df = master_df.astype({ "country": str, "day": int, "month": int, "price": float, "times_viewed": int, "year": int})
    return master_df


def drop_non_numeric_invoice(master_df):
    master_df = master_df[~master_df['invoice'].str.contains("[a-zA-Z]").fillna(False)]
    return master_df
