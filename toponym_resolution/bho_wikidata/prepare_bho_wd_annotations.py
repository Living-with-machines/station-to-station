import utils
import pandas as pd
import collections
import ast
from wikimapper import WikiMapper
from pathlib import Path
import urllib.parse
import json
import html
from tqdm.auto import tqdm
tqdm.pandas()

candidates = "britwikidata_candidates"
min_wkdtgazetteer = "britwikidata_gazetteer"
max_wkdtgazetteer = "british_isles"
queries = "bho_queries"
dm_model = "wikigaz_en_002"
candrank_metric = "faiss" # 'faiss', 'cosine', 'conf'
mapper = WikiMapper("/resources/wikidata2wikipedia/index_enwiki-20190420.db") # WikiMapper object (see https://pypi.org/project/wikimapper/)
wikipedia_path = "/resources/wikipedia/extractedResources/Aspects/"

# Load candidate ranking results:
bho_cands = pd.read_pickle("../../toponym_matching/ranker_results/" + queries + "_" + candidates + "_" + dm_model + "_" + candrank_metric + ".pkl")

# Load minimal wikidata gazetteer (fields: wkid, altname, source, lat, lon) from which candidates were created:
wikidatagaz_df = pd.read_pickle("../../toponym_matching/gazetteers/" + min_wkdtgazetteer + ".pkl")

# Load maximal wikidata gazetteer (fields: wikidata_id, english_label, instance_of, description_set...):
wikidata_gazetteer = pd.read_csv("../../wikidata/" + max_wkdtgazetteer + ".csv", index_col=0, low_memory=False)

# Load csv-structured BHO dataset:
bho_dataset = pd.read_csv("../../bho/bho.csv", index_col="id", low_memory=False)

wkdataIDs_file = queries + "_" + candidates + "_" + dm_model + "_" + candrank_metric + "_wikidataIDs.pkl"
if not Path(queries + "_" + candidates + "_" + dm_model + "_" + candrank_metric + "_wikidataIDs.pkl").is_file():
    # Add column to candidate ranking results with Wikidata IDs corresponding to matches
    bho_cands['wikidata_cands'] = bho_cands.progress_apply(lambda row : utils.match_cands_wikidata(row,wikidatagaz_df,"faiss_distance"), axis=1) 
    bho_cands.to_pickle(wkdataIDs_file)
else:
    bho_cands = pd.read_pickle(wkdataIDs_file)

# Find interesting entries to annotate, according to the following thresholds:
"""
In order to get interesting samples to annotate, categorize each BHO entry according to its returned
wikidata candidates:
* multiple_exact: more than one almost-exact candidates on wikidata
* unique_exact_with_competition: one almost-exact candidate, second most similar is also a likely match
* unique_exact_no_competition: one almost-exact candidate, second most similar is a less likely match
* no_exact_potential_match: no almost-exact candidate, but most similar candidate is likely
* potential_no_match: no almost-exact candidate, and most similar candidate is less likely
* unlikely_match: no almost-exact candidate, and most similar candidate is an unlikely

Almost-exact, likely, less likely, and unlikely scenarios are defined via similarity thresholds.
"""
almost_exact_threshold = 0.5 # Max similarity threshold for almost-exact match
likely_match_threshold = 5 # Max similarity threshold for likely match
unlikely_match_threshold = 10 # Min similarity threshold for unlikely match

description, wikidata_candidates = utils.select_entries_to_annotate(bho_dataset, bho_cands, almost_exact_threshold, likely_match_threshold, unlikely_match_threshold)

bho_dataset["linking_scenario"] = description
bho_dataset["wikidata_cands"] = wikidata_candidates
bho_dataset["bho_id"] = bho_dataset.index

# Print full dataset statistics:
print(bho_dataset.linking_scenario.value_counts())

# Remove entries that are redirections:
bho_dataset = bho_dataset[bho_dataset["linking_scenario"] != "redirection"]

# Select number of samples per category to annotate:
sample_counts = {
    'multiple_exact': 50,
    'unique_exact_no_competition': 50,
    'unique_exact_with_competition': 50,
    'no_exact_potential_match': 100,
    'potential_no_match': 100,
    'unlikely_match': 100,
    'no_candidates': bho_dataset[bho_dataset["linking_scenario"] == "no_candidates"].shape[0] # Take all instances
}

# Subsample per category according to numbers in the sample_counts dictionary:
sampled_df = pd.DataFrame()
for k in sample_counts:
    temp_df = bho_dataset[bho_dataset["linking_scenario"] == k].sample(sample_counts[k], random_state=42).reset_index(drop=True)
    sampled_df = pd.concat([sampled_df, temp_df], ignore_index=True)
    
# Remove duplicate rows:
sampled_df = sampled_df.drop_duplicates(subset=["title", "toponyms", "contextwords"])

# Print sampled dataset statistics:
print(sampled_df.linking_scenario.value_counts())

# Shuffle dataframe:
sampled_df = sampled_df.sample(frac=1, random_state=42).reset_index(drop=True)

# Fetch wikipedia description and wikidata infos of the instances to annotate and format results:
utils.create_annotation_items(sampled_df, wikidata_gazetteer, mapper, wikipedia_path)
