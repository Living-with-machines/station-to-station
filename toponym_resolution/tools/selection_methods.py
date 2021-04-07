import pandas as pd
import numpy as np
from pathlib import Path
from DeezyMatch import inference as dm_inference
from DeezyMatch import combine_vecs
from DeezyMatch import candidate_ranker
import time

# --------------------------------------
# Perfect match
# --------------------------------------

def perfect_match(name,wikidata_df):
    res = wikidata_df[["wkid"]]
    res["method"] = wikidata_df.apply(lambda row: check_if_identical(name,row), axis=1)
    res = res.dropna().set_index('wkid').to_dict()["method"]
    return res 


def check_if_identical(name,row):
    if name.lower() == row["altname"].lower():
        return 1.0

# --------------------------------------
# Skyline
# --------------------------------------

def skyline(gs_wkid,wikidata_df):
    res = dict()
    if gs_wkid.startswith("Q"):
        res[gs_wkid] = 1.0
    else:
        res["NotExists"] = 0.0
    return res


# --------------------------------------
# Partial overlap match
# --------------------------------------

def partial_match(name,wikidata_df):
    res = wikidata_df[["wkid"]]
    res["method"] = wikidata_df.apply(lambda row: check_if_contained(name,row), axis=1)
    res = res.dropna().set_index('wkid').to_dict()["method"]
    return res 

def check_if_contained(name,row):
    if name.lower() in row["altname"].lower():
        return len(name)/len(row["altname"])

    
# --------------------------------------
# Deezy match
# --------------------------------------

# Returning wikidata IDs for retrieved toponyms:
def match_cands_wikidata_stn(row,gazetteer,ranking):
    wikidata_cands = {}
    cands = [(k, row[ranking][k]) for k in row[ranking]]
    
    # Find wikidata IDs:
    for cand,score in cands:
        wikidataIds = gazetteer[gazetteer["altname"].str.lower() == cand.lower()]["wkid"]
        for _id in wikidataIds:
            if _id not in wikidata_cands:
                wikidata_cands[_id] = score
                
    return wikidata_cands

# Formatting candidates for DeezyMatch innput:
def format_for_candranker(gazname, unique_placenames_array):
    """
    This function returns the unique alternate names in a given gazetteer
    in the format required by DeezyMatch candidate ranker."""
    Path(gazname).mkdir(parents=True, exist_ok=True)
    with open(gazname + ".txt", "w") as fw:
        for pl in unique_placenames_array:
            pl = pl.strip()
            if pl:
                pl = pl.replace('"', "")
                fw.write(pl.strip() + "\t0\tfalse\n")

def find_deezymatch_candidates(gazetteer, quicks_df, quicks_query_column, dm_model, inputfile, candidates, queries, candrank_metric, candrank_thr, num_candidates):
    # Generate candidate vectors for the British Isles gazetteer
    unique_placenames_array = list(set(list(np.array(quicks_df[quicks_query_column]))))
    format_for_candranker("../processed/deezymatch/query_toponyms/" + queries, unique_placenames_array)
    
    # generate vectors for queries (specified in dataset_path) 
    # using a model stored at pretrained_model_path and pretrained_vocab_path 
    start_time = time.time()
    dm_inference(input_file_path="../processed/deezymatch/models/" + dm_model + "/" + inputfile + ".yaml",
                 dataset_path="../processed/deezymatch/query_toponyms/" + queries + ".txt", 
                 pretrained_model_path="../processed/deezymatch/models/" + dm_model + "/" + dm_model + ".model", 
                 pretrained_vocab_path="../processed/deezymatch/models/" + dm_model + "/" + dm_model + ".vocab",
                 inference_mode="vect",
                 scenario="../processed/deezymatch/query_vectors/" + queries + "_" + dm_model)
    elapsed = time.time() - start_time
    print("Generate query vectors: %s" % elapsed)

    # combine vectors stored in the scenario in queries/ and save them in combined/
    start_time = time.time()
    combine_vecs(rnn_passes=["fwd", "bwd"], 
                 input_scenario="../processed/deezymatch/query_vectors/" + queries + "_" + dm_model, 
                 output_scenario="../processed/deezymatch/combined/" + queries + "_" + dm_model, 
                 print_every=1000)
    elapsed = time.time() - start_time
    print("Combine query vectors: %s" % elapsed)
        
    # Select candidates based on L2-norm distance (aka faiss distance):
    # find candidates from candidate_scenario 
    # for queries specified in query_scenario
    start_time = time.time()
    candidates_pd = \
        candidate_ranker(query_scenario="../processed/deezymatch/combined/" + queries + "_" + dm_model,
                         candidate_scenario="../processed/deezymatch/combined/" + candidates + "_" + dm_model, 
                         ranking_metric=candrank_metric, 
                         selection_threshold=candrank_thr, 
                         num_candidates=num_candidates, 
                         search_size=num_candidates, 
                         output_path="../processed/deezymatch/ranker_results/" + queries + "_" + candidates + "_" + dm_model + "_" + candrank_metric + str(num_candidates), 
                         pretrained_model_path="../processed/deezymatch/models/" + dm_model + "/" + dm_model + ".model", 
                         pretrained_vocab_path="../processed/deezymatch/models/" + dm_model + "/" + dm_model + ".vocab")
    elapsed = time.time() - start_time
    print("Rank candidates: %s" % elapsed)
    
    ranked_candidates = pd.read_pickle("../processed/deezymatch/ranker_results/" + queries + "_" + candidates + "_" + dm_model + "_" + candrank_metric + str(num_candidates) + ".pkl")
    ranked_candidates["wkcands"] = ranked_candidates.progress_apply(lambda row : match_cands_wikidata_stn(row,gazetteer,"faiss_distance"), axis=1)
    return pd.merge(left=quicks_df, right=ranked_candidates, how='left', left_on=quicks_query_column, right_on='query')[["wkcands"]]