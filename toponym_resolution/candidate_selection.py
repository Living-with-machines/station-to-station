import time
import numpy as np
import pandas as pd
from pathlib import Path
from collections import OrderedDict
from tools import eval_methods, selection_methods
from tqdm.auto import tqdm
tqdm.pandas()


# Options (looped over at the end of the script):
devtest_settings = ["dev", "test"]
cr_approaches = ["deezy_match", "partial_match", "perfect_match"]
ncand_options = [1, 3, 5]


# ----------------------------------------
# Function that finds candidates for each scenario:
def perform_candrank(setting, approach, num_candidates):
    
    if not Path("../processed/resolution/candranking_" + approach + "_" + setting + str(num_candidates) + ".pkl").is_file():

        df = pd.read_pickle("../processed/quicks/quicks_" + setting + ".pkl")
        alts_df = pd.read_pickle("../processed/quicks/quicks_altname_" + setting + ".pkl")
        wkdt_df_places = pd.read_pickle("../processed/wikidata/altname_gb_gazetteer.pkl")
        wkdt_df_stations = pd.read_pickle("../processed/wikidata/altname_gb_stations_gazetteer.pkl")

        # ---------------
        # Skyline
        df["skyline"] = df.apply(lambda row: selection_methods.skyline_match(row["Final Wikidata ID"], wkdt_df_places), axis=1)
        print("Skyline done!")

        if approach == "perfect_match":
            # ---------------
            # Perfect Match
            df["cr_perfect_match_stations"] = df.apply(lambda row: selection_methods.perfect_match(row["SubStFormatted"], wkdt_df_stations), axis=1)
            df["cr_perfect_match_places"] = df.apply(lambda row: selection_methods.perfect_match(row["MainStation"], wkdt_df_places), axis=1)
            alts_df["cr_perfect_match_alts"] = alts_df.apply(lambda row: selection_methods.perfect_match(row["Altname"], wkdt_df_stations), axis=1)
            print("Perfect match done!") 

        if approach == "partial_match":
            # ---------------
            # Partial Match
            df["cr_partial_match_stations"] = df.apply(lambda row: selection_methods.partial_match(row["SubStFormatted"], wkdt_df_stations, num_candidates), axis=1)
            df["cr_partial_match_places"] = df.apply(lambda row: selection_methods.partial_match(row["MainStation"], wkdt_df_places, num_candidates), axis=1)
            alts_df["cr_partial_match_alts"] = alts_df.apply(lambda row: selection_methods.partial_match(row["Altname"], wkdt_df_stations, num_candidates), axis=1)
            print("Partial match done!")

        if approach == "deezy_match":
            # ---------------
            # DeezyMatch
            candidates = "gb_stations"
            dm_model = "wikidata_gb"
            inputfile = "input_dfm"
            queries = "quicks_stations"
            candrank_metric = "faiss" # 'faiss', 'cosine', 'conf'
            candrank_thr = 3
            quicks_query_column = "SubStFormatted"
            df["cr_deezy_match_stations"] = selection_methods.find_deezymatch_candidates(wkdt_df_stations, df, quicks_query_column, dm_model, inputfile, candidates, queries, candrank_metric, candrank_thr, num_candidates)

            candidates = "gb"
            dm_model = "wikidata_gb"
            inputfile = "input_dfm"
            queries = "quicks_places"
            candrank_metric = "faiss" # 'faiss', 'cosine', 'conf'
            candrank_thr = 3
            quicks_query_column = "MainStation"
            df["cr_deezy_match_places"] = selection_methods.find_deezymatch_candidates(wkdt_df_places, df, quicks_query_column, dm_model, inputfile, candidates, queries, candrank_metric, candrank_thr, num_candidates)

            candidates = "gb_stations"
            dm_model = "wikidata_gb"
            inputfile = "input_dfm"
            queries = "quicks_altns"
            candrank_metric = "faiss" # 'faiss', 'cosine', 'conf'
            candrank_thr = 3
            quicks_query_column = "Altname"
            alts_df["cr_deezy_match_alts"] = selection_methods.find_deezymatch_candidates(wkdt_df_stations, alts_df, quicks_query_column, dm_model, inputfile, candidates, queries, candrank_metric, candrank_thr, num_candidates)
            print("Deezy match done!")

        # Add altnames to dataframe:
        # Add deezymatch altnames to dataframe:
        dAlts = dict()
        altn_candidates = []
        for i, row in alts_df.iterrows():
            if row["SubId"] in dAlts:
                dAlts[row["SubId"]].update(row["cr_" + approach + "_alts"])
            else:
                dAlts[row["SubId"]] = row["cr_" + approach + "_alts"]
        for i, row in df.iterrows():
            if row["SubId"] in dAlts:
                altn_candidates.append(dict(OrderedDict(dAlts[row["SubId"]])))
            else:
                altn_candidates.append(dict())
        df["cr_" + approach + "_alts"] = altn_candidates

        # ---------------
        # Store candidate selection
        Path("../processed/resolution/").mkdir(parents=True, exist_ok=True)
        df.to_pickle("../processed/resolution/candranking_" + approach + "_" + setting + str(num_candidates) + ".pkl")

        
# -----------------------------------
# Run the different candrank experiments
for setting in devtest_settings:
    for approach in cr_approaches:
        for num_candidates in ncand_options:
            perform_candrank(setting, approach, num_candidates)