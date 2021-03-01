from DeezyMatch import inference as dm_inference
from DeezyMatch import combine_vecs
from DeezyMatch import candidate_ranker

from pathlib import Path
import pandas as pd
import time

def findcandidates(candidates, queries, dm_model, inputfile, candrank_metric, candrank_thr, num_candidates, overwrite=False):
    
    # --------------------------------------
    # GENERATE AND COMBINE CANDIDATE VECTORS
    
    # generate vectors for candidates (specified in dataset_path) 
    # using a model stored at pretrained_model_path and pretrained_vocab_path 
    if not Path("./candidates/" + candidates + "_" + dm_model + "/embeddings/").is_dir() or overwrite == True:
        start_time = time.time()
        dm_inference(input_file_path="./models/" + dm_model + "/" + inputfile + ".yaml",
                     dataset_path="./gazetteers/" + candidates + ".txt", 
                     pretrained_model_path="./models/" + dm_model + "/" + dm_model + ".model", 
                     pretrained_vocab_path="./models/" + dm_model + "/" + dm_model + ".vocab",
                     inference_mode="vect",
                     scenario="candidates/" + candidates + "_" + dm_model)
        elapsed = time.time() - start_time
        print("Generate candidate vectors: %s" % elapsed)

    # combine vectors stored in the scenario in candidates/ and save them in combined/
    if not Path("./combined/" + candidates + "_" + dm_model).is_dir() or overwrite == True:
        start_time = time.time()
        combine_vecs(rnn_passes=["fwd", "bwd"], 
                     input_scenario="candidates/" + candidates + "_" + dm_model, 
                     output_scenario="combined/" + candidates + "_" + dm_model, 
                     print_every=1000)
        elapsed = time.time() - start_time
        print("Combine candidate vectors: %s" % elapsed)
    
    # --------------------------------------
    # GENERATE AND COMBINE QUERY VECTORS
    
    # generate vectors for queries (specified in dataset_path) 
    # using a model stored at pretrained_model_path and pretrained_vocab_path 
    if not Path("./queries/" + queries + "_" + dm_model + "/embeddings/").is_dir() or overwrite == True:
        start_time = time.time()
        dm_inference(input_file_path="./models/" + dm_model + "/" + inputfile + ".yaml",
                     dataset_path="./toponyms/" + queries + ".txt", 
                     pretrained_model_path="./models/" + dm_model + "/" + dm_model + ".model", 
                     pretrained_vocab_path="./models/" + dm_model + "/" + dm_model + ".vocab",
                     inference_mode="vect",
                     scenario="queries/" + queries + "_" + dm_model)
        elapsed = time.time() - start_time
        print("Generate candidate vectors: %s" % elapsed)

    # combine vectors stored in the scenario in queries/ and save them in combined/
    if not Path("./combined/" + queries + "_" + dm_model).is_dir() or overwrite == True:
        start_time = time.time()
        combine_vecs(rnn_passes=["fwd", "bwd"], 
                     input_scenario="queries/" + queries + "_" + dm_model, 
                     output_scenario="combined/" + queries + "_" + dm_model, 
                     print_every=1000)
        elapsed = time.time() - start_time
        print("Combine candidate vectors: %s" % elapsed)
        
    # Select candidates based on L2-norm distance (aka faiss distance):
    # find candidates from candidate_scenario 
    # for queries specified in query_scenario
    if not Path("ranker_results/" + queries + "_" + candidates + "_" + dm_model + "_" + candrank_metric + ".pkl").is_file() or overwrite == True:
        start_time = time.time()
        candidates_pd = \
            candidate_ranker(query_scenario="./combined/" + queries + "_" + dm_model,
                             candidate_scenario="./combined/" + candidates + "_" + dm_model, 
                             ranking_metric=candrank_metric, 
                             selection_threshold=candrank_thr, 
                             num_candidates=num_candidates, 
                             search_size=num_candidates, 
                             output_path="ranker_results/" + queries + "_" + candidates + "_" + dm_model + "_" + candrank_metric + str(num_candidates), 
                             pretrained_model_path="./models/" + dm_model + "/" + dm_model + ".model", 
                             pretrained_vocab_path="./models/" + dm_model + "/" + dm_model + ".vocab")
        elapsed = time.time() - start_time
        print("Rank candidates: %s" % elapsed)

# -------------------------------------------------
# Setting:
candidates = "stnwikidata_candidates"
queries = "quicks_mainst_queries"
dm_model = "wikigaz_en_003"
inputfile = "input_dfm_003"
candrank_metric = "faiss" # 'faiss', 'cosine', 'conf'
candrank_thr = 50
num_candidates = 10
overwrite = True

findcandidates(candidates, queries, dm_model, inputfile, candrank_metric, candrank_thr, num_candidates, overwrite)

print("Done")

# -------------------------------------------------
# Setting:
candidates = "stnwikidata_candidates"
queries = "quicks_subst_queries"
dm_model = "wikigaz_en_003"
inputfile = "input_dfm_003"
candrank_metric = "faiss" # 'faiss', 'cosine', 'conf'
candrank_thr = 50
num_candidates = 10
overwrite = True

findcandidates(candidates, queries, dm_model, inputfile, candrank_metric, candrank_thr, num_candidates, overwrite)

print("Done")

# -------------------------------------------------
# Setting:
candidates = "stnwikidata_candidates"
queries = "quicks_altnames_queries"
dm_model = "wikigaz_en_003"
inputfile = "input_dfm_003"
candrank_metric = "faiss" # 'faiss', 'cosine', 'conf'
candrank_thr = 50
num_candidates = 10
overwrite = True

findcandidates(candidates, queries, dm_model, inputfile, candrank_metric, candrank_thr, num_candidates, overwrite)

print("Done")

# -------------------------------------------------
# Setting:
candidates = "britwikidata_candidates"
queries = "quicks_mainst_queries"
dm_model = "wikigaz_en_003"
inputfile = "input_dfm_003"
candrank_metric = "faiss" # 'faiss', 'cosine', 'conf'
candrank_thr = 50
num_candidates = 10
overwrite = True

findcandidates(candidates, queries, dm_model, inputfile, candrank_metric, candrank_thr, num_candidates, overwrite)

print("Done")