from pathlib import Path
import pandas as pd
from tools import selection_methods

import time
import numpy as np
from pathlib import Path
from collections import OrderedDict
from tools import eval_methods, selection_methods, resolution_methods
from tqdm.auto import tqdm
from dateutil import parser
import pickle
import re
tqdm.pandas()

setting = "allquicks" # dev or test
num_candidates = 1

# Load Wikipedia inlinks:
with open("../resources/wikipedia/overall_entity_freq.pickle", 'rb') as fp:
    wikipedia_entity_overall_dict = pickle.load(fp)
    
# DeezyMatch parameters:
dm_model = "wikidata_gb"
inputfile = "input_dfm"
candrank_metric = "faiss" # 'faiss', 'cosine', 'conf'
candrank_thr = 3

# The following is a default value. The threshold if we use one of the other
# two metrics should not be higher than 1.
if candrank_metric in ['cosine', 'conf']:
    candrank_thr = 1

    
# -------------------------------
# Candidate selection:
# Run candidate selection on all Quicks
# -------------------------------

if not Path("../processed/resolution/candranking_" + setting + ".pkl").is_file():

    df = pd.read_pickle("../resources/quicks/quicks_parsed.pkl")
    alts_df = pd.read_csv("../resources/quicks/quicks_altname_" + setting + ".tsv", sep="\t")
    wkdt_df_places = pd.read_csv("../processed/wikidata/altname_gb_gazetteer.tsv", sep="\t")
    wkdt_df_stations = pd.read_csv("../processed/wikidata/altname_gb_stations_gazetteer.tsv", sep="\t")
    
    # ---------------
    # DeezyMatch
    candidates = "gb_stations"
    queries = "quicks_stations"
    query_column = "SubStFormatted"
    ranked_candidates = selection_methods.find_deezymatch_candidates(wkdt_df_stations, df, query_column, dm_model, inputfile, candidates, queries, candrank_metric, candrank_thr, num_candidates)
    df = pd.merge(left=df, right=ranked_candidates, how="left", left_on=query_column, right_on="query")
    df = df.rename(columns={"wkcands":"cr_deezy_match_stations"})
    df = df.drop(columns = ["query"])
    print("Deezy match done!")

    candidates = "gb"
    queries = "quicks_places"
    query_column = "MainStation"
    ranked_candidates = selection_methods.find_deezymatch_candidates(wkdt_df_places, df, query_column, dm_model, inputfile, candidates, queries, candrank_metric, candrank_thr, num_candidates)
    df = pd.merge(left=df, right=ranked_candidates, how="left", left_on=query_column, right_on="query")
    df = df.rename(columns={"wkcands":"cr_deezy_match_places"})
    df = df.drop(columns = ["query"])
    print("Deezy match done!")

    candidates = "gb_stations"
    queries = "quicks_altns"
    query_column = "Altname"
    ranked_candidates = selection_methods.find_deezymatch_candidates(wkdt_df_stations, alts_df, query_column, dm_model, inputfile, candidates, queries, candrank_metric, candrank_thr, num_candidates)
    alts_df = pd.merge(left=alts_df, right=ranked_candidates, how="left", left_on=query_column, right_on="query")
    alts_df = alts_df.rename(columns={"wkcands":"cr_deezy_match_alts"})
    alts_df = alts_df.drop(columns = ["query"])
    print("Deezy match done!")

    # Add altnames to dataframe:
    # Add deezymatch altnames to dataframe:
    dAlts = dict()
    altn_candidates = []
    for i, row in alts_df.iterrows():
        if row["SubId"] in dAlts:
            dAlts[row["SubId"]].update(row["cr_deezy_match_alts"])
        else:
            dAlts[row["SubId"]] = row["cr_deezy_match_alts"]
    for i, row in df.iterrows():
        if row["SubId"] in dAlts:
            altn_candidates.append(dict(OrderedDict(dAlts[row["SubId"]])))
        else:
            altn_candidates.append(dict())
    df["cr_deezy_match_alts"] = altn_candidates

    # ---------------
    # Store candidate selection
    df.to_pickle("../processed/resolution/candranking_" + setting + ".pkl")
    
gazetteer_df = pd.read_csv("../processed/wikidata/gb_gazetteer.csv", header=0, index_col=0, low_memory=False)
    
# -------------------------------
# Feature selection:
# Extract features for all Quicks
# -------------------------------

setting = "allquicks"
candrank = "deezy_match"
features_file = "../processed/resolution/features_" + setting + "_" + candrank + ".tsv"
if not Path(features_file).is_file():
    df = pd.read_pickle("../processed/resolution/candranking_" + setting + ".pkl")
    exp_df = resolution_methods.feature_selection(candrank, df, gazetteer_df, wikipedia_entity_overall_dict, False)
    exp_df.drop_duplicates(subset=['SubId','Candidate'], inplace=True)
    exp_df.to_csv(features_file, sep="\t")
print(candrank + " " + setting + " done!")

features_all = pd.read_csv("../processed/resolution/features_allquicks_" + candrank + ".tsv",sep='\t', index_col=0)

# -------------------------------
# Place linking:
# Our method comb: Combine stations and places classifiers
# -------------------------------

use_cols_all = ["f_0", "f_1", "f_2", "f_3", "f_4", "f_5", "f_6", "f_7", "f_8"] 

features_dev_df = pd.read_csv("../processed/resolution/features_deezy_match_dev1.tsv",sep='\t', index_col=0)

# Train railway stations classifier (exact setting):
dev_df = features_dev_df # development set feature vectors
df_exact = dev_df[dev_df["Exact"] == 1]
use_cols_stations = use_cols_all
# Train the classifier:
clf_stations = resolution_methods.train_classifier(df_exact, use_cols_all)

# Train places classifier (not exact setting):
dev_df = features_dev_df # development set feature vectors
df_inexact = dev_df[dev_df["Exact"] == 0]
use_cols_places = use_cols_all
# Train the classifier:
clf_places = resolution_methods.train_classifier(df_inexact, use_cols_all)

# Find optimal threshold for stations/places:
optimal_threshold = 0.0
keep_acc = 0.0
for th in np.arange(0, 1, 0.05):
    th = round(th, 2)
    results_dev_df = pd.read_csv("../resources/quicks/quicks_dev.tsv", sep="\t")
    results_dev_df = resolution_methods.our_method_comb(features_dev_df, clf_stations, use_cols_stations, clf_places, use_cols_places, gazetteer_df, th, results_dev_df)
    acc = eval_methods.topres_exactmetrics(results_dev_df, "our_method_comb", False)
    if acc >= keep_acc:
        optimal_threshold = th
        keep_acc = acc

print(optimal_threshold, keep_acc)

features_test_df = pd.read_csv("../processed/resolution/features_allquicks_deezy_match.tsv",sep='\t', index_col=0)
results_test_df = pd.read_pickle("../resources/quicks/quicks_parsed.pkl")

# Apply our classification methods:
results_test_df = resolution_methods.our_method_comb_keepconf(features_test_df, clf_stations, use_cols_stations, clf_places, use_cols_places, gazetteer_df, optimal_threshold, results_test_df)

results_test_df.to_csv("../processed/resolution/resolved_deezy_match_allquicks_nv1.tsv", sep="\t", index=False)

# -------------------------------
# Filter out ghost entries and cross-references
# -------------------------------

df = pd.read_csv("../processed/resolution/resolved_deezy_match_allquicks_nv1.tsv", sep="\t")

re_altname = r"(\b[A-Z]+(?:[A-Z \&\'\-(St|at|on|upon)])*[A-Z])+\b"
re_referenced = r"\b(?:[Ss]ee|[Ss]ee under)\b " + re_altname

# ---------------------------------------------
# Function to filter out entries that are cross-references:
def is_ref(desc):
    if desc:
        if re.match(r".*\b(?<!\()(?:[Ss]ee|[Ss]ee under)\b " + re_altname, desc[:25]) and len(desc) < 100:
            return False
    return True
    
# ---------------------------------------------
# Add column to dataframe that allows filtering out cross_ref entries:
df["cross_ref"] = True
df.loc[df.apply(lambda x: is_ref(x["Description"]), axis=1), "cross_ref"] = False

# ---------------------------------------------
# Add column to dataframe that allows filtering out ghost place entries:
main_ids = list(df.MainId.unique())

df["ghost_entry"] = False
for m_id in main_ids:
    tdf = df[df["MainId"] == m_id]
    m_subid = df[df["MainId"] == m_id].iloc[0].SubId
    if tdf.shape[0] > 1:
        if tdf.iloc[0].MainStation == tdf.iloc[0].SubStation:
            s_ids = list(tdf.SubId.unique())
            for s_id in s_ids:
                
                # Transfer ghost entry knowledge to its stations:
                    
                # Ghost FirstOpening value is given to station FirstOpening if empty:
                if not type(df[df["SubId"] == s_id].iloc[0].FirstOpening) == str:
                    df.loc[df.SubId == s_id, 'FirstOpening'] = tdf.iloc[0].FirstOpening
                    df.loc[df.SubId == m_subid, 'ghost_entry'] = True
                    
                # Ghost LastClosing value is given to station LastClosing if empty:
                if not type(df[df["SubId"] == s_id].iloc[0].LastClosing) == str:
                    df.loc[df.SubId == s_id, 'LastClosing'] = tdf.iloc[0].LastClosing
                    df.loc[df.SubId == m_subid, 'ghost_entry'] = True
                    
                # If ghost FirstCompanyWkdt is not empty and station FirstCompanyWkdt is empty,
                # then station FirstCompanyWkdt gets the value from ghost FirstCompanyWkdt.
                # If ghost FirstCompanyWkdt is not empty and station FirstCompanyWkdt is also
                # not empty, then AltCompaniesWkdt gets the value from ghost FirstCompanyWkdt.
                if type(tdf.iloc[0].FirstCompanyWkdt) == str:
                    if not type(df[df["SubId"] == s_id].iloc[0].FirstCompanyWkdt) == str:
                        df.loc[df.SubId == s_id, 'FirstCompanyWkdt'] = tdf.iloc[0].FirstCompanyWkdt
                        df.loc[df.SubId == m_subid, 'ghost_entry'] = True
                    else:
                        df.loc[df.SubId == m_subid, 'ghost_entry'] = False

# Replace empty values by "unknown":
df["LastClosing"].fillna("unknown", inplace=True)
df["FirstOpening"].fillna("unknown", inplace=True)
df["selected_entity"].fillna("unknown", inplace=True)
df["selected_entity_label"].fillna("unknown", inplace=True)
df["selected_entity_type"].fillna("unknown", inplace=True)
df["selected_entity_latitude"].fillna("unknown", inplace=True)
df["selected_entity_longitude"].fillna("unknown", inplace=True)
df["predicted_station"].fillna("unknown", inplace=True)
df["conf_station"].fillna(0.0, inplace=True)
df["predicted_place"].fillna("unknown", inplace=True)
df["conf_place"].fillna(0.0, inplace=True)

# -------------------------------
# Normalize opening and closing dates
# -------------------------------

def normalize_dates(i):
    # Catch errors
    i = i.replace("Sep tember", "September")
    i = i.replace("Oct ober", "October")
    i = i.replace("Dec ember", "December")
    i = i.replace("Apr il", "April")
    i = i.replace("29 February 1937", "28 February 1937") # Error in original dataset!
    if i == "still open":
        return "still open"
    elif not i == "unknown":
        d = parser.parse(i)
        return d.strftime("%Y-%m-%d")
    return "unknown"

df["FirstOpening"] = df['FirstOpening'].apply(lambda x: normalize_dates(x))
df["LastClosing"] = df['LastClosing'].apply(lambda x: normalize_dates(x))

# Store resolved dataset:
df = df.drop(["Description", "Disambiguator", "Companies", "LocsMaps", "LocsMapsDescr"], axis=1)
df = df.rename({"MainId":"PlaceId", "SubId":"StationId", "MainStation":"Place", "SubStFormatted":"Station", "SubStation":"AbbrStation", "FirstCompanyWkdt":"Company", "AltCompaniesWkdt":"AltCompanies", "FirstOpening":"Opening", "LastClosing":"Closing"}, axis=1)
df.to_csv("../processed/resolution/StopsGB.tsv", sep="\t", index=False)