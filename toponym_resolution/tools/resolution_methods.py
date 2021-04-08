import numpy as np
import pandas as pd
from haversine import haversine
from ast import literal_eval
import re

from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('paraphrase-distilroberta-base-v1')

# From: https://docs.google.com/spreadsheets/d/1sREU_TKBU0HXoSSm7nyOw-4kId_bfu6OTEXxtdZeLl0/edit#gid=0
stn_wkdt_classes = ["Q55488", "Q4663385", "Q55491", "Q18516630", "Q1335652", "Q28109487",
                    "Q55678", "Q1567913", "Q39917125", "Q11424045", "Q14562709", "Q27020748",
                    "Q22808403", "Q85641138", "Q928830", "Q1339195", "Q27030992", "Q55485",
                    "Q17158079", "Q55493", "Q325358", "Q168565", "Q18543139", "Q11606300",
                    "Q2175765", "Q2298537", "Q19563580"]

ppl_wkdt_classes = ["Q532", "Q1115575", "Q486972", "Q5084", "Q3957", "Q5124673", "Q3910694", "Q515", "Q18511725", "Q1549591", "Q1357964", "Q1968403", "Q902814"]



# ----------------------------------
# Baselines
# ----------------------------------
def first_match(candidates):
    candidates = sorted(candidates, key=candidates.get)
    first_candidate = ""
    if candidates:
        first_candidate = candidates[0]
    return first_candidate


# ----------------------------------
# Methods
# ----------------------------------

def feature_based(df, gazetteer_df):

    query_column = []
    candidate_column = []
    feature_columns = []
    goldstandard_column = []
    for i, row in df.iterrows():
        
        subst_cands = row["cr_deezy_match"]
        place_cands = row["cr_deezy_match_places"]
        altnm_cands = row["cr_deezy_match_alts"]

        all_cands = list(set(list(subst_cands.keys()) + list(place_cands.keys()) + list(altnm_cands.keys())))
        for c in all_cands:

            binary_label = 0
            label = row["Final Wikidata ID"]
            label = label.replace("opl:", "")
            label = label.replace("ppl:", "")
            if c == label:
                binary_label = 1

            local_compatibility = [0]*7

            # 1. Candidate source and selection confidence:
            if c in subst_cands:
                local_compatibility[0] = round((5 - subst_cands[c])/5, 2)
            if c in place_cands:
                local_compatibility[1] = round((5 - place_cands[c])/5, 2)
            if c in altnm_cands:
                local_compatibility[2] = round((5 - altnm_cands[c])/5, 2)

            # 2. Text compatibility between Quicks and Wikidata entry:
            disambiguator_text = row["MainStation"] + ", ".join(row["Disambiguator"]) + " " + row["LocsMapsDescr"][1:-1] + ", ".join(row["Altnames"]) + ", ".join(row["Referenced"])
            disambiguator_text = re.sub(" +", " ", disambiguator_text).strip()
            disambiguator_text = disambiguator_text.title()
            disambiguator_text = "" if len(disambiguator_text) <= 5 else disambiguator_text
            wikidata_data = gazetteer_df.loc[c]
            wikidata_text = ""
            if not (type(wikidata_data["english_label"]) == float and np.isnan(wikidata_data["english_label"])):
                wikidata_text += wikidata_data["english_label"]
            if wikidata_data["description_set"] != "set()":
                wikidata_text += ", " + ", ".join(literal_eval(wikidata_data["description_set"]))
            for hc in literal_eval(wikidata_data["hcounties"]):
                wikidata_text += ", " + gazetteer_df.loc[hc]["english_label"]
            for ar in literal_eval(wikidata_data["adm_regions"]):
                if ar in gazetteer_df.index:
                    wikidata_text += ", " + gazetteer_df.loc[ar]["english_label"]
            embeddings = model.encode([disambiguator_text, wikidata_text])
            local_compatibility[3] = round(util.pytorch_cos_sim(embeddings[0], embeddings[1]).item(), 2)

            # 3. Wikidata class
            if not (type(wikidata_data["instance_of"]) == float and np.isnan(wikidata_data["instance_of"])):
                for inst in literal_eval(wikidata_data["instance_of"]):
                    if inst in stn_wkdt_classes:
                        local_compatibility[4] = 1
                        continue
            if not (type(wikidata_data["instance_of"]) == float and np.isnan(wikidata_data["instance_of"])):
                for inst in literal_eval(wikidata_data["instance_of"]):
                    if inst in ppl_wkdt_classes:
                        local_compatibility[5] = 1
                        continue

            # 4. Substation place compatibility
            closest = 100000
            if c in subst_cands or c in altnm_cands:
                st_lat = gazetteer_df.loc[c]["latitude"]
                st_lon = gazetteer_df.loc[c]["longitude"]
                for mc in place_cands:
                    pl_lat = gazetteer_df.loc[mc]["latitude"]
                    pl_lon = gazetteer_df.loc[mc]["longitude"]
                    dcands = haversine((st_lat, st_lon), (pl_lat, pl_lon))
                    if dcands < closest:
                        closest = dcands
            elif c in place_cands:
                st_lat = gazetteer_df.loc[c]["latitude"]
                st_lon = gazetteer_df.loc[c]["longitude"]
                for mc in list(subst_cands.keys()) + list(altnm_cands.keys()):
                    pl_lat = gazetteer_df.loc[mc]["latitude"]
                    pl_lon = gazetteer_df.loc[mc]["longitude"]
                    dcands = haversine((st_lat, st_lon), (pl_lat, pl_lon))
                    if dcands < closest:
                        closest = dcands
            closest = 10.0 if closest > 10.0 else closest
            local_compatibility[6] = round((100 - closest)/100, 2)

            query_column.append(row["SubStFormatted"])
            candidate_column.append(c)
            feature_columns.append(local_compatibility)
            goldstandard_column.append(binary_label)

    exp_df = pd.DataFrame()
    exp_df["Query"] = query_column
    exp_df["Candidate"] = candidate_column
    features_df = pd.DataFrame(feature_columns, columns = ["f_" + str(i) for i in range(0, len(feature_columns[0]))])
    exp_df = pd.concat([exp_df, features_df], axis=1).reindex(exp_df.index)
    exp_df["Label"] = goldstandard_column
    return exp_df