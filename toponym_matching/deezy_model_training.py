from DeezyMatch import train as dm_train
from DeezyMatch import plot_log
from DeezyMatch import finetune as dm_finetune
from DeezyMatch import inference as dm_inference
from DeezyMatch import inference as dm_inference
from DeezyMatch import combine_vecs

from pathlib import Path
from shutil import copyfile

import pandas as pd
import numpy as np
import time

# --------------------------------------
# TRAIN THE BRITISH ISLES DEEZYMATCH MODEL
# --------------------------------------

# If model does not exist already, train a new model:
if not Path('../processed/deezymatch/models/wikidata_british_isles/wikidata_british_isles.model').is_file():
    # train a new model
    dm_train(input_file_path="../processed/deezymatch/input_dfm.yaml",
         dataset_path="../processed/deezymatch/datasets/british_isles_toponym_pairs.txt",
         model_name="wikidata_british_isles")
    

# --------------------------------------
# FINE-TUNE THE BRITISH ISLES DEEZYMATCH MODEL WITH THE STATIONS DATASET
# --------------------------------------

if not Path('../processed/deezymatch/models/wikidata_british_isles_stations/wikidata_british_isles_stations.model').is_file():
# fine-tune a pretrained model stored at pretrained_model_path and pretrained_vocab_path 
    dm_finetune(input_file_path="../processed/deezymatch/input_dfm.yaml", 
            dataset_path="../processed/deezymatch/datasets/british_isles_stations_toponym_pairs.txt", 
            model_name="wikidata_british_isles_stations",
            pretrained_model_path="../processed/deezymatch/models/wikidata_british_isles/wikidata_british_isles.model", 
            pretrained_vocab_path="../processed/deezymatch/models/wikidata_british_isles/wikidata_british_isles.vocab")


# --------------------------------------
# GENERATE AND COMBINE CANDIDATE VECTORS
# --------------------------------------

##### UTILS

# Formatting candidates for DeezyMatch innput:
def format_for_candranker(gazname, unique_placenames_array):
    """
    This function returns the unique alternate names in a given gazetteer
    in the format required by DeezyMatch candidate ranker."""
    Path("/".join(gazname.split("/")[:-1])).mkdir(parents=True, exist_ok=True)
    with open(gazname + ".txt", "w") as fw:
        for pl in unique_placenames_array:
            pl = pl.strip()
            if pl:
                pl = pl.replace('"', "")
                fw.write(pl.strip() + "\t0\tfalse\n")

# Generating and combining candidate vectors:
def findcandidates(candidates, dm_model, inputfile):

    # generate vectors for candidates (specified in dataset_path) 
    # using a model stored at pretrained_model_path and pretrained_vocab_path 
    if not Path("../processed/deezymatch/candidate_vectors/" + candidates + "_" + dm_model + "/embeddings/").is_dir():
        start_time = time.time()
        dm_inference(input_file_path="../processed/deezymatch/models/" + dm_model + "/input_dfm.yaml",
                     dataset_path="../processed/deezymatch/candidate_toponyms/" + candidates + ".txt", 
                     pretrained_model_path="../processed/deezymatch/models/" + dm_model + "/" + dm_model + ".model", 
                     pretrained_vocab_path="../processed/deezymatch/models/" + dm_model + "/" + dm_model + ".vocab",
                     inference_mode="vect",
                     scenario="../processed/deezymatch/candidate_vectors/" + candidates + "_" + dm_model)
        elapsed = time.time() - start_time
        print("Generate candidate vectors: %s" % elapsed)

    # combine vectors stored in the scenario in candidates/ and save them in combined/
    if not Path("../processed/deezymatch/combined/" + candidates + "_" + dm_model).is_dir():
        start_time = time.time()
        combine_vecs(rnn_passes=["fwd", "bwd"], 
                     input_scenario="../processed/deezymatch/candidate_vectors/" + candidates + "_" + dm_model, 
                     output_scenario="../processed/deezymatch/combined/" + candidates + "_" + dm_model, 
                     print_every=1000)
        elapsed = time.time() - start_time
        print("Combine candidate vectors: %s" % elapsed)

        
##### IN USE
# Generate candidate vectors for the British Isles gazetteer
wkgazetteer = pd.read_pickle("../processed/wikidata/altname_british_isles_gazetteer.pkl")
unique_placenames_array = list(set(list(np.array(wkgazetteer["altname"]))))
format_for_candranker("../processed/deezymatch/candidate_toponyms/british_isles", unique_placenames_array)

candidates = "british_isles"
dm_model = "wikidata_british_isles"
inputfile = "input_dfm"

findcandidates(candidates, dm_model, inputfile)
        
# Generate candidate vectors for the British Isles stations gazetteer
wkgazetteer = pd.read_pickle("../processed/wikidata/altname_british_isles_stations_gazetteer.pkl")
unique_placenames_array = list(set(list(np.array(wkgazetteer["altname"]))))
format_for_candranker("../processed/deezymatch/candidate_toponyms/british_isles_stations", unique_placenames_array)

candidates = "british_isles_stations"
dm_model = "wikidata_british_isles_stations"
inputfile = "input_dfm"

findcandidates(candidates, dm_model, inputfile)