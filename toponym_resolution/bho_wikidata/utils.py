import random
import functools
from IPython.display import display, clear_output
from ipywidgets import Button, Dropdown, HTML, HBox, IntSlider, FloatSlider, Textarea, Output
from datetime import datetime
import json
import pickle
import collections
import urllib.parse
from pathlib import Path
import ast


# ----------------------------------------------------------------
# Function that commbines two dictionaries and
# keeps the smallest value in case of overlapping
# keys:
def combine_dicts(func, *dicts):
    default = collections.defaultdict(set)
    for d in dicts:
        for k, v in d.items():
            default[k].add(v)
    return {k: func(v) for k, v in default.items()}


# ----------------------------------------------------------------
# Function that finds the Wikidata IDs of DeezyMatch's returned matches.
# * Input:
#     * row: a ranker_results df row (fields: id, query, pred_score,
#            faiss_distance, cosine_sim, ...)
#     * gazetteer: gazetteer where candidates have been obtained from
#                  (fields: wkid, altname, source, lat, lon)
#     * ranking: candidate ranking metric (must be one column of the
#                'row' argument.)
# * Output: a dictionary with DeezyMatch candidates aligned with their
#           Wikidata IDs, per row.
def match_cands_wikidata(row,gazetteer,ranking):
    wikidata_cands = {}
    cands = row[ranking]
    for cand,score in cands.items():
        wikidataIds = gazetteer[gazetteer["altname"] == cand]["wkid"]
        for _id in wikidataIds:
            if _id not in wikidata_cands:
                wikidata_cands[_id] = score
    return wikidata_cands


# ----------------------------------------------------------------
# Function that selects interesting entries to annotate.
def select_entries_to_annotate(bho_dataset, bho_cands, almost_exact_threshold, likely_match_threshold, unlikely_match_threshold):
    description = []
    wikidata_candidates = []
    for i, row in bho_dataset.iterrows():
        if row["redirected"] == False: # Redirected entries are disregarded
            toponyms = ast.literal_eval(row["toponyms"])
            wikidata_cands = dict()
            for t in toponyms:
                temp_wikidata_cands = bho_cands[bho_cands["query"] == t.strip()]["wikidata_cands"]
                if not temp_wikidata_cands.empty:
                    temp_wikidata_cands = temp_wikidata_cands.item()
                    wikidata_cands = combine_dicts(min, wikidata_cands, temp_wikidata_cands)
            wikidata_cands = dict(sorted(wikidata_cands.items(), key=lambda item: item[1]))
            cand_keys = list(wikidata_cands.keys())

            # Categorize the row according to candidates string similarity:
            if len(wikidata_cands) >= 1:
                # Case 1: multiple almost exact matches
                if wikidata_cands[cand_keys[0]] < almost_exact_threshold and wikidata_cands[cand_keys[1]] < almost_exact_threshold:
                    description.append("multiple_exact")
                    wikidata_candidates.append(wikidata_cands)
                # Case 2: one almost exact match, other competitive potential matches
                elif wikidata_cands[cand_keys[0]] < almost_exact_threshold and wikidata_cands[cand_keys[1]] < likely_match_threshold:
                    description.append("unique_exact_with_competition")
                    wikidata_candidates.append(wikidata_cands)
                # Case 3: one almost exact match, other matches non competitive
                elif wikidata_cands[cand_keys[0]] < almost_exact_threshold and wikidata_cands[cand_keys[1]] > likely_match_threshold:
                    description.append("unique_exact_no_competition")
                    wikidata_candidates.append(wikidata_cands)
                # Case 4: no almost-exact matches, but likely potential matches
                elif wikidata_cands[cand_keys[0]] < likely_match_threshold:
                    description.append("no_exact_potential_match")
                    wikidata_candidates.append(wikidata_cands)
                # Case 5: no almost-exact matches, only less likely potential matches
                elif wikidata_cands[cand_keys[0]] > likely_match_threshold and wikidata_cands[cand_keys[0]] <= unlikely_match_threshold:
                    description.append("potential_no_match")
                    wikidata_candidates.append(wikidata_cands)
                # Case 6: only unlikely potential matches
                elif wikidata_cands[cand_keys[0]] > unlikely_match_threshold:
                    description.append("unlikely_match")
                    wikidata_candidates.append(wikidata_cands)
            # Case 7: no candidates
            else:
                description.append("no_candidates")
                wikidata_candidates.append({})
        else:
            description.append("redirection")
            wikidata_candidates.append({})
    
    return description, wikidata_candidates


# ----------------------------------------------------------------
# Function that maps a Wikidata ID to its corresponding Wikipedia page.
# * Input: wikidata2wikipedia mapper (from: https://pypi.org/project/wikimapper/) and a Wikidata ID.
#          This step assumes Wikipedia contents processed into json files.
# * Output: The 2nd-6th lines of the main section of the corresponding Wikipedia page content, and
#           the title of the corresponding Wikipedia page
def map_wikidata2wikidump(wikidataId, mapper, path):
    wikititles = mapper.id_to_titles(wikidataId)
    wikititles = [urllib.parse.quote(title.replace("_"," ")) for title in wikititles]
    wikidata_text = ""
    keep_title = ""
    for title in wikititles:
        if Path(path + title+".json").is_file():
            wikidump = path + title+".json"
            with open(wikidump) as f:
                data = json.load(f)
                tmp_wkdt_text = " ".join(data["Main"]["content"][1:5])
                if len(tmp_wkdt_text) > len(wikidata_text):
                    wikidata_text = tmp_wkdt_text
                    keep_title = title
    if wikidata_text == "":
        wikidata_text = "[No Wikipedia page]"
    return wikidata_text, keep_title


# ----------------------------------------------------------------
# Function that creates the items to annotate in the right format:
def create_annotation_items(sampled_df, wikidata_gazetteer, mapper, path):  

    # Fetch interesting fields to help annotators disambiguate:
    # Prepare the data and fields to annotate:
    resolutions = []
    for i, row in sampled_df.iterrows():
        bho_id = row["bho_id"]
        bho_title = row["title"]
        bho_content = ast.literal_eval(row["content"].strip())
        bho_country = row["country"]
        bho_xmlfile = row["xmlfile"]
        bho_wkcandidates = dict()
        wkcds = row["wikidata_cands"]

        if wkcds:
            min_value = min(wkcds.values())
            best_wikidata_matches = [key for key, value in wkcds.items() if value == min_value]
            for wkcd in best_wikidata_matches:
                wkdf = wikidata_gazetteer[wikidata_gazetteer["wikidata_id"] == wkcd]
                wkcd_hc = []
                wikidata_text = ""
                wikidata_title = ""
                if not wkdf.empty:
                    # Get location's historical counties:
                    hcounties = ast.literal_eval(wkdf.iloc[0]["hcounties"])
                    for hc in hcounties:
                        hcountydf = wikidata_gazetteer[wikidata_gazetteer["wikidata_id"] == hc]
                        if not hcountydf.empty:
                            wkcd_hc.append(hcountydf.iloc[0]["english_label"])
                    # Wikidata candidate disambiguators:
                    wikidata_text, wikidata_title = map_wikidata2wikidump(wkcd, mapper, path)
                    wkcand_disambiguators = (wkdf.iloc[0]["english_label"], wkdf.iloc[0]["description_set"], wikidata_text, wikidata_title, wkcd_hc)
                    bho_wkcandidates[wkdf.iloc[0]["wikidata_id"]] = wkcand_disambiguators
                
        resolutions.append([bho_id, bho_title, bho_content, bho_wkcandidates, bho_country, bho_xmlfile])
        
    # This converts the BHO data to annotate (and the corresponding Wikidata
    # candidates) into a dictionary, where the value is empty (it will be
    # eventually filled with the annotation):
    resolution_strings = dict()
    for r in resolutions:
        longstring = "=========================\nBHO ENTRY"
        longstring += " [ID "
        longstring += str(r[0])
        longstring += "]: " + r[1] + " [[[" + r[4].strip() + ": " + r[5].strip() + "]]]" + "\n"
        longstring += "=========================\n"
        longstring += r[2][0].strip()
        longstring += "\n"
        longstring += "\n"
        longstring += "=========================\n"
        longstring += "WIKIDATA CANDIDATES\n"
        longstring += "========================="
        if r[3]:
            for cd in r[3]:
                if type(r[3][cd][0]) == str:
                    longstring += "\n-------------------------\n"
                    longstring += "* " + cd + " (" + r[3][cd][0] + ")"
                    longstring += "\n-------------------------\n"
                    if r[3][cd][4]:
                        longstring += "[Historical county] " + ", ".join(r[3][cd][4]) + "\n"
                    description = ""
                    if r[3][cd][2] != "[No Wikipedia page]":
                        description = r[3][cd][2].strip()
                    else:
                        description = r[3][cd][1].strip()
                    longstring += "[Description] " + description + "\n"
                    longstring += "[Wikidata link] https://www.wikidata.org/wiki/" + cd + "\n"
                    if r[3][cd][3]:
                        longstring += "[Wikipedia link] https://en.wikipedia.org/wiki/" + r[3][cd][3] + "\n"

        longstring += "=========================\n"
        resolution_strings[longstring] = ""
    
    annotations_folder = "../../annotations/bho_to_wikidata/"
    Path(annotations_folder).mkdir(parents=True, exist_ok=True)
    with open(annotations_folder + "samples_to_annotate.json", 'w') as json_file:
        json.dump(resolution_strings, json_file)
    
    
    