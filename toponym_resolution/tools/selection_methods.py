import pandas as pd
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

# def deezy_match(name, wikidata_df, dm_model, gazetteer, input_file, candidates, candrank_metric, candrank_thr, num_candidates):
#     # gazetteer: british_isles or british_isles_stations
#     res = wikidata_df[["wkid"]]
#     res["method"] = wikidata_df.apply(lambda row: check_if_deezymatch(name,row), axis=1)
#     res = res.dropna().set_index('wkid').to_dict()["method"]
#     return res

# def check_if_deezymatch(name, row, dm_model, gazetteer):
#     # Generate candidate vectors for the British Isles gazetteer
#     unique_placenames_array = list(set(list(np.array(row["altname"]))))
#     format_for_candranker("../processed/deezymatch/query_toponyms/" + gazetteer, unique_placenames_array)
    
#     # generate vectors for queries (specified in dataset_path) 
#     # using a model stored at pretrained_model_path and pretrained_vocab_path 
#     start_time = time.time()
#     dm_inference(input_file_path="./models/" + dm_model + "/" + inputfile + ".yaml",
#                  dataset_path="./toponyms/" + queries + ".txt", 
#                  pretrained_model_path="./models/" + dm_model + "/" + dm_model + ".model", 
#                  pretrained_vocab_path="./models/" + dm_model + "/" + dm_model + ".vocab",
#                  inference_mode="vect",
#                  scenario="queries/" + queries + "_" + dm_model)
#     elapsed = time.time() - start_time
#     print("Generate candidate vectors: %s" % elapsed)

#     # combine vectors stored in the scenario in queries/ and save them in combined/
#     start_time = time.time()
#     combine_vecs(rnn_passes=["fwd", "bwd"], 
#                  input_scenario="queries/" + queries + "_" + dm_model, 
#                  output_scenario="combined/" + queries + "_" + dm_model, 
#                  print_every=1000)
#     elapsed = time.time() - start_time
#     print("Combine candidate vectors: %s" % elapsed)
        
#     # Select candidates based on L2-norm distance (aka faiss distance):
#     # find candidates from candidate_scenario 
#     # for queries specified in query_scenario
#     start_time = time.time()
#     candidates_pd = \
#         candidate_ranker(query_scenario="./combined/" + queries + "_" + dm_model,
#                          candidate_scenario="./combined/" + candidates + "_" + dm_model, 
#                          ranking_metric=candrank_metric, 
#                          selection_threshold=candrank_thr, 
#                          num_candidates=num_candidates, 
#                          search_size=num_candidates, 
#                          output_path="ranker_results/" + queries + "_" + candidates + "_" + dm_model + "_" + candrank_metric + str(num_candidates), 
#                          pretrained_model_path="./models/" + dm_model + "/" + dm_model + ".model", 
#                          pretrained_vocab_path="./models/" + dm_model + "/" + dm_model + ".vocab")
#     elapsed = time.time() - start_time
#     print("Rank candidates: %s" % elapsed)