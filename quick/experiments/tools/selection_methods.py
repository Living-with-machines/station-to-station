import pandas as pd

def perfect_match(name,wikidata_df):
    res = wikidata_df[["wkid"]]
    res["method"] = wikidata_df.apply(lambda row: check_if_identical(name,row), axis=1)
    res = res.dropna().set_index('wkid').to_dict()["method"]
    return res 


def check_if_identical(name,row):
    if name.lower() == row["altname"].lower():
        return 1.0


def partial_match(name,wikidata_df):
    res = wikidata_df[["wkid"]]
    res["method"] = wikidata_df.apply(lambda row: check_if_contained(name,row), axis=1)
    res = res.dropna().set_index('wkid').to_dict()["method"]
    return res 

def check_if_contained(name,row):
    if name.lower() in row["altname"].lower():
        return len(name)/len(row["altname"])

