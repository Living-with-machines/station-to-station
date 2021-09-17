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

def skyline_match(gs_wkid,wikidata_df_ids):
    res = dict()
    if gs_wkid in wikidata_df_ids:
        res[gs_wkid] = 1.0
    else:
        res["NotExists"] = 0.0
    return res


# --------------------------------------
# Partial overlap match
# --------------------------------------

def partial_match(name,wikidata_df,num_candidates):
    res = wikidata_df[["wkid"]]
    res["method"] = wikidata_df.apply(lambda row: check_if_contained(name,row), axis=1)
    res = res.dropna()
    top_scores = sorted(list(set(list(res["method"].unique()))), reverse=True)[:num_candidates]
    res = res[res["method"].isin(top_scores)]
    res = res.set_index('wkid').to_dict()["method"]
    return res 

def check_if_contained(name,row):
    if name.lower() in row["altname"].lower():
        return len(name)/len(row["altname"])

    
# --------------------------------------
# Deezy match
# --------------------------------------

# Normalize ranking scores:
def normalize_ranking(score, measure, thr):
    normalized_score = score
    if measure == "faiss_distance" or measure == "cosine_dist" or measure == "1-pred_score":
        normalized_score = (thr - score) / thr
    return normalized_score

# Returning wikidata IDs for retrieved toponyms:
def match_cands_wikidata_stn(row,gazetteer,ranking,candrank_thr):
    wikidata_cands = {}
    
    cands = [(k, normalize_ranking(row[ranking][k], ranking, candrank_thr)) for k in row[ranking]]
    
    # Find wikidata IDs:
    for cand,score in cands:
        wikidataIds = gazetteer[gazetteer["altname"].str.lower() == cand.lower()]["wkid"]
        for _id in wikidataIds:
            if _id not in wikidata_cands:
                wikidata_cands[_id] = score
                
    return wikidata_cands

# Formatting altname candidates for DeezyMatch input:
def format_for_candranker(gazname, df, query_column):
    """
    This function returns the unique alternate names in a given gazetteer
    in the format required by DeezyMatch candidate ranker."""
    if query_column == "Altname":
        df = df.drop_duplicates(subset=["Altname"])
        with open(gazname + ".txt", "w") as fw:
            for i, row in df.iterrows():
                fw.write(row["Altname"] + "\t0\tfalse\n")
    if query_column == "MainStation":
        df = df.drop_duplicates(subset=["MainStation"])
        with open(gazname + ".txt", "w") as fw:
            for i, row in df.iterrows():
                fw.write(row["MainStation"] + "\t0\tfalse\n")
    if query_column == "SubStFormatted":
        df = df.drop_duplicates(subset=["SubStFormatted"])
        with open(gazname + ".txt", "w") as fw:
            for i, row in df.iterrows():
                fw.write(row["SubStFormatted"] + "\t0\tfalse\n")


def find_deezymatch_candidates(gazetteer, quicks_df, query_column, dm_model, inputfile, candidates, queries, candrank_metric, candrank_thr, num_candidates):
    Path("../processed/deezymatch/query_toponyms/").mkdir(parents=True, exist_ok=True)
    # Generate candidate vectors for the British Isles gazetteer
    format_for_candranker("../processed/deezymatch/query_toponyms/" + queries + "_" + query_column, quicks_df, query_column)
    
    # generate vectors for queries (specified in dataset_path) 
    # using a model stored at pretrained_model_path and pretrained_vocab_path 
    start_time = time.time()
    dm_inference(input_file_path="../processed/deezymatch/models/" + dm_model + "/" + inputfile + ".yaml",
                 dataset_path="../processed/deezymatch/query_toponyms/" + queries + "_" + query_column + ".txt", 
                 pretrained_model_path="../processed/deezymatch/models/" + dm_model + "/" + dm_model + ".model", 
                 pretrained_vocab_path="../processed/deezymatch/models/" + dm_model + "/" + dm_model + ".vocab",
                 inference_mode="vect",
                 scenario="../processed/deezymatch/query_vectors/" + queries + "_" + query_column + "_" + dm_model)
    elapsed = time.time() - start_time
    print("Generate query vectors: %s" % elapsed)

    # combine vectors stored in the scenario in queries/ and save them in combined/
    start_time = time.time()
    combine_vecs(rnn_passes=["fwd", "bwd"], 
                 input_scenario="../processed/deezymatch/query_vectors/" + queries + "_" + query_column + "_" + dm_model, 
                 output_scenario="../processed/deezymatch/combined/" + queries + "_" + query_column + "_" + dm_model, 
                 print_every=1000)
    elapsed = time.time() - start_time
    print("Combine query vectors: %s" % elapsed)
        
    # Select candidates based on L2-norm distance (aka faiss distance):
    # find candidates from candidate_scenario 
    # for queries specified in query_scenario
    start_time = time.time()
    candidates_pd = \
        candidate_ranker(query_scenario="../processed/deezymatch/combined/" + queries + "_" + query_column + "_" + dm_model,
                         candidate_scenario="../processed/deezymatch/combined/" + candidates + "_" + dm_model, 
                         ranking_metric=candrank_metric, 
                         selection_threshold=candrank_thr, 
                         num_candidates=num_candidates, 
                         search_size=num_candidates, 
                         output_path="../processed/deezymatch/ranker_results/" + queries + "_" + query_column + "_" + candidates + "_" + dm_model + "_" + candrank_metric + str(num_candidates), 
                         pretrained_model_path="../processed/deezymatch/models/" + dm_model + "/" + dm_model + ".model", 
                         pretrained_vocab_path="../processed/deezymatch/models/" + dm_model + "/" + dm_model + ".vocab")
    elapsed = time.time() - start_time
    print("Rank candidates: %s" % elapsed)
    
    ranked_candidates = pd.read_pickle("../processed/deezymatch/ranker_results/" + queries + "_" + query_column + "_" + candidates + "_" + dm_model + "_" + candrank_metric + str(num_candidates) + ".pkl")
    ranked_candidates["wkcands"] = ranked_candidates.progress_apply(lambda row : match_cands_wikidata_stn(row,gazetteer,"faiss_distance",candrank_thr), axis=1)
    
    drop_columns = ['pred_score', '1-pred_score', 'faiss_distance', 'cosine_dist', 'candidate_original_ids', 'query_original_id', 'num_all_searches']
    ranked_candidates = ranked_candidates.drop(columns=[col for col in ranked_candidates if col in drop_columns])
    
    return ranked_candidates