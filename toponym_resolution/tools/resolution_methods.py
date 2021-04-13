import numpy as np
import pandas as pd
from haversine import haversine
from ast import literal_eval
import re
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import LinearSVC, SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, f1_score
from urllib.parse import quote
import random

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
# Feature selection
# ----------------------------------

def feature_selection(candrank, df, gazetteer_df, wikipedia_entity_overall_dict):
    
    bbox_gb = [-7.84,49.11,1.97,61.2]

    mainid_column = []
    subid_column = []
    query_column = []
    candidate_column = []
    feature_columns = []
    goldstandard_column = []
    exact_match_column = []
    
    max_inlinks = 0
        
    for i, row in df.iterrows():
        
        subst_cands = row["cr_" + candrank + "_stations"]
        place_cands = row["cr_" + candrank + "_places"]
        altnm_cands = row["cr_" + candrank + "_alts"]
        
        disambiguator_text = row["MainStation"] + ", ".join(row["Disambiguator"]) + " " + row["LocsMapsDescr"][1:-1] + ", ".join(row["Altnames"]) + ", ".join(row["Referenced"])
        disambiguator_text = re.sub(" +", " ", disambiguator_text).strip()
        disambiguator_text = disambiguator_text.title()
        disambiguator_text = "" if len(disambiguator_text) <= 5 else disambiguator_text

        all_cands = list(set(list(subst_cands.keys()) + list(place_cands.keys()) + list(altnm_cands.keys())))
        for c in all_cands:
            
            exact_match = 0
            label = row["Final Wikidata ID"]
            if label.startswith("Q"):
                exact_match = 1
            label = label.replace("opl:", "")
            label = label.replace("ppl:", "")
            binary_label = 0
            if c == label:
                binary_label = 1

            local_compatibility = [0]*9

            # 1. Candidate source and selection confidence:
            if c in subst_cands:
                local_compatibility[0] = round((5 - subst_cands[c])/5, 2)
            if c in place_cands:
                local_compatibility[1] = round((5 - place_cands[c])/5, 2)
            if c in altnm_cands:
                local_compatibility[2] = round((5 - altnm_cands[c])/5, 2)

            # 2. Text compatibility between Quicks and Wikidata entry:
            try:
                wikidata_data = gazetteer_df.loc[c]
                wikidata_text = ""
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
                    if st_lat > bbox_gb[1] and st_lat < bbox_gb[3] and st_lon > bbox_gb[0] and st_lon < bbox_gb[2]:
                        for mc in place_cands:
                            if place_cands[mc] < 1.0: # High DeezyMatch confidence
                                pl_lat = gazetteer_df.loc[mc]["latitude"]
                                pl_lon = gazetteer_df.loc[mc]["longitude"]
                                dcands = haversine((st_lat, st_lon), (pl_lat, pl_lon))
                                if dcands < closest:
                                    closest = dcands
                closest = 10.0 if closest > 10.0 else closest
                local_compatibility[6] = round((10 - closest)/10, 2)

                # 4. Substation place compatibility
                closest = 100000
                if c in place_cands:
                    st_lat = gazetteer_df.loc[c]["latitude"]
                    st_lon = gazetteer_df.loc[c]["longitude"]
                    if st_lat > bbox_gb[1] and st_lat < bbox_gb[3] and st_lon > bbox_gb[0] and st_lon < bbox_gb[2]:
                        for mc in subst_cands:
                            if subst_cands[mc] < 1.0: # High DeezyMatch confidence
                                pl_lat = gazetteer_df.loc[mc]["latitude"]
                                pl_lon = gazetteer_df.loc[mc]["longitude"]
                                dcands = haversine((st_lat, st_lon), (pl_lat, pl_lon))
                                if dcands < closest:
                                    closest = dcands
                    for mc in altnm_cands:
                        if altnm_cands[mc] < 1.0:
                            pl_lat = gazetteer_df.loc[mc]["latitude"]
                            pl_lon = gazetteer_df.loc[mc]["longitude"]
                            dcands = haversine((st_lat, st_lon), (pl_lat, pl_lon))
                            if dcands < closest:
                                closest = dcands

                closest = 10.0 if closest > 10.0 else closest
                local_compatibility[7] = round((10 - closest)/10, 2)
                
                if not (type(wikidata_data["wikititle"]) == float and np.isnan(wikidata_data["wikititle"])):
                    inlinks = wikipedia_entity_overall_dict.get(quote(wikidata_data["wikititle"], safe=''), 0)
                    if inlinks > max_inlinks:
                        max_inlinks = inlinks
                    local_compatibility[8] = inlinks
                
            except KeyError:
                continue

            mainid_column.append(row["MainId"])
            subid_column.append(row["SubId"])
            query_column.append(row["SubStFormatted"])
            candidate_column.append(c)
            feature_columns.append(local_compatibility)
            goldstandard_column.append(binary_label)
            exact_match_column.append(exact_match)

    # Normalize wikipedia inlinks column:
    for ifc in range(len(feature_columns)):
        feature_columns[ifc][8] = round((feature_columns[ifc][8]/max_inlinks), 6)
    
    exp_df = pd.DataFrame()
    exp_df["MainId"] = mainid_column
    exp_df["SubId"] = subid_column
    exp_df["Query"] = query_column
    exp_df["Candidate"] = candidate_column
    features_df = pd.DataFrame(feature_columns, columns = ["f_" + str(i) for i in range(0, len(feature_columns[0]))])
    exp_df = pd.concat([exp_df, features_df], axis=1).reindex(exp_df.index)
    exp_df["Label"] = goldstandard_column
    exp_df["Exact"] = exact_match_column
    return exp_df


# ----------------------------------
# Classification
# ----------------------------------

def train_classifier(df, use_cols, run):
    df.drop_duplicates(subset=['Query','Candidate'], inplace=True)
    
    # Split dev set into train and test:
    queries = list(df.Query.unique()) 
    random.Random(42).shuffle(queries)
    test_cutoff = int(len(queries)*.5)
    train_q, test_q = queries[test_cutoff:],queries[:test_cutoff]
    print("Queries in train and test:", len(train_q),len(test_q))
    
    train = df[df.Query.isin(train_q)]
    test = df[df.Query.isin(test_q)]
    X_train = train[use_cols].values
    y_train = train.Label.values
    X_test = test[use_cols].values
    y_test = test.Label.values
    print("Instances in train and test:", len(y_train),len(y_test))
    
    # Find optimal parameters:
    tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4], 'C': [0.01, 0.1, 1, 10, 100, 1000]},
                    {'kernel': ['linear'], 'C': [0.01, 0.1, 1, 10, 100, 1000]}]

    clf_gs = GridSearchCV(SVC(), tuned_parameters, scoring = 'f1_macro')
    clf_gs.fit(X_train, y_train)

    print(clf_gs.best_params_)
    
    clf = SVC(**clf_gs.best_params_,probability=True)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    print("Classification report on dev test set:")
    print(classification_report(y_pred,y_test))
    
    # Train classifier with all data using the best parameters:
    if run == "test":
        X_all = df[use_cols].values
        y_all = df.Label.values
        clf = SVC(**clf_gs.best_params_)
        clf.fit(X_all,y_all)
    
    return clf


def find_thresholds(df, clf_stations, use_cols_stations, gazetteer_df, minthr, maxthr, stepthr, mindist):
    for th in np.arange(minthr, maxthr, stepthr):
        tp = 0
        fn = 0
        fp = 0

        for subid in list(set(list(df.SubId.unique()))):

            query = df[df["SubId"] == subid].iloc[0].Query
            cands = df[df.SubId==subid].Candidate.values
            gs_labels = list(df[(df.SubId==subid) & (df.Label==1)].Candidate.values)
            y = df[df.SubId==subid].Label.values

            # Stations classifier:
            X_stations = df.loc[df.SubId==subid,use_cols_stations].values
            probs_stations = [round(x[1], 4) for x in clf_stations.predict_proba(X_stations)]
            predicted_station_prob = max(probs_stations)
            predicted_station = cands[probs_stations.index(predicted_station_prob)]
            predicted_station_coords = gazetteer_df.loc[predicted_station][["latitude", "longitude"]].to_list()

            gs_coords = []
            if gs_labels:
                gs_label = gs_labels[0]
                gs_coords = gazetteer_df.loc[gs_label][["latitude", "longitude"]].to_list()

                if haversine(gs_coords, predicted_station_coords) <= mindist and th > predicted_station_prob:
                    tp += 1
                elif haversine(gs_coords, predicted_station_coords) <= mindist  and th <= predicted_station_prob:
                    fn += 1
                elif haversine(gs_coords, predicted_station_coords) > mindist  and th > predicted_station_prob:
                    fp += 1

        fscore = 0.0
        if tp > 0:
            precision = tp/(tp+fn)
            recall = tp/(tp+fp)
            fscore = (2 * precision * recall) / (precision + recall)
            
        print("Stations threshold:", round(th, 2), round(fscore, 4))
        

# ----------------------------------
# Our methods
# ----------------------------------

def our_method(df, clf_stations, use_cols_stations, clf_places, use_cols_places, gazetteer_df, threshold, results_test_df):
    
    dResolved = dict()
    for subid in list(set(list(df.SubId.unique()))):
        
        predicted_final = ""
        predicted_probs = 0.0
        
        cands = df[df.SubId==subid].Candidate.values

        # Stations classifier:
        X_stations = df.loc[df.SubId==subid,use_cols_stations].values
        probs_stations = [round(x[1], 4) for x in clf_stations.predict_proba(X_stations)]
        predicted_station_prob = max(probs_stations)
        predicted_station = cands[probs_stations.index(predicted_station_prob)]

        # Places classifier:
        X_places = df.loc[df.SubId==subid,use_cols_places].values
        probs_places = [round(x[1], 4) for x in clf_places.predict_proba(X_places)]
        predicted_place_prob = max(probs_places)
        predicted_place = cands[probs_places.index(predicted_place_prob)]
            
        predicted_final = predicted_place
        predicted_probs = predicted_place_prob
        if predicted_station_prob > threshold:
            predicted_final = predicted_station
            predicted_probs = predicted_station_prob
        
        dResolved[subid] = predicted_final
        
    results_test_df["our_method"] = results_test_df['SubId'].map(dResolved)
    
    return results_test_df


# ----------------------------------
# Baselines
# ----------------------------------

def candrank_most_confident(features_df, test_df):    
    
    dResolved = dict()
    for subid in list(set(list(features_df.SubId.unique()))):
        
        predicted_final = ""
        predicted_probs = 0.0

        cands = features_df[features_df.SubId==subid].Candidate.values
        
        predicted_station = cands[features_df[features_df.SubId==subid]['f_0'].argmax()]
        predicted_place = cands[features_df[features_df.SubId==subid]['f_1'].argmax()]
        
        dResolved[subid] = predicted_place
        if predicted_station:
            dResolved[subid] = predicted_station
        
    test_df["candrank_most_confident"] = test_df['SubId'].map(dResolved)
    
    return test_df


def wikipedia_most_relevant(features_df, test_df):
    
    dResolved = dict()
    for subid in list(set(list(features_df.SubId.unique()))):
        
        predicted_final = ""
        predicted_probs = 0.0

        cands = features_df[features_df.SubId==subid].Candidate.values
        
        predicted = cands[features_df[features_df.SubId==subid]['f_8'].argmax()]
        
        dResolved[subid] = predicted
        
    test_df["wikipedia_most_relevant"] = test_df['SubId'].map(dResolved)
    
    return test_df


def semantically_most_similar(features_df, test_df):
    
    dResolved = dict()
    for subid in list(set(list(features_df.SubId.unique()))):
        
        predicted_final = ""
        predicted_probs = 0.0

        cands = features_df[features_df.SubId==subid].Candidate.values
        
        predicted = cands[features_df[features_df.SubId==subid]['f_3'].argmax()]
        
        dResolved[subid] = predicted
        
    test_df["semantically_most_similar"] = test_df['SubId'].map(dResolved)
    
    return test_df