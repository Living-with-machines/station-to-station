import pandas as pd

def partial_match(name,wikidata_df):
    res = wikidata_df[["wkid"]]
    res["method"] = wikidata_df.apply(lambda row: check_if_contained(name,row), axis=1)
    res = res.dropna().set_index('wkid').to_dict()["method"]
    return res 

def check_if_contained(name,row):
    if name in row["altname"].lower():
        return len(name)/len(row["altname"])

