import numpy as np
import pandas as pd
from haversine import haversine
from ast import literal_eval
import re
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from urllib.parse import quote
import random
import pathlib
import subprocess
import itertools
from tqdm import tqdm

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

def closest_geo(gazetteer_df, c, place_cands, closest):
    closest = 100000
    st_lat = gazetteer_df.loc[c]["latitude"]
    st_lon = gazetteer_df.loc[c]["longitude"]
    for mc in place_cands:
        if gazetteer_df.loc[c]["english_label"] != gazetteer_df.loc[mc]["english_label"]:
            pl_lat = gazetteer_df.loc[mc]["latitude"]
            pl_lon = gazetteer_df.loc[mc]["longitude"]
            dcands = haversine((st_lat, st_lon), (pl_lat, pl_lon))
            if dcands < closest:
                closest = dcands
    return closest

def feature_selection(candrank, df, gazetteer_df, wikipedia_entity_overall_dict, experiment=True):

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
        
        locstext = []
        if type(row["LocsMapsDescr"]) == str:
            locstext += [row["LocsMapsDescr"][1:-1]]
        disambtext = []
        if type(row["Disambiguator"]) == str:
            disambtext += literal_eval(row["Disambiguator"])
        altnmtext = []
        if type(row["Altnames"]) == str:
            altnmtext += literal_eval(row["Altnames"])
        refstext = []
        if type(row["Referenced"]) == str:
            refstext += literal_eval(row["Referenced"])
        
        disambiguator_text = list(set([row["MainStation"]] + disambtext + locstext + altnmtext + refstext))
        disambiguator_text = [x for x in disambiguator_text if x]
        disambiguator_text = [x.title() if x.isupper() else x for x in disambiguator_text]
        disambiguator_text = ", ".join(disambiguator_text)
        disambiguator_text = re.sub(" +", " ", disambiguator_text).strip()
        disambiguator_text = "" if len(disambiguator_text) <= 5 else disambiguator_text
        
        if type(subst_cands) == float:
            subst_cands = dict()
        if type(place_cands) == float:
            place_cands = dict()
        if type(altnm_cands) == float:
            altnm_cands = dict()

        all_cands = list(set(list(subst_cands.keys()) + list(place_cands.keys()) + list(altnm_cands.keys())))
        
        for c in all_cands:
            
            exact_match = 0
            label = ""
            if experiment == True:
                label = row["Final Wikidata ID"]
            if label.startswith("Q"):
                exact_match = 1
            label = label.replace("opl:", "")
            label = label.replace("ppl:", "")
            binary_label = 0
            if c == label:
                binary_label = 1

            feature_vector = [0.0]*9

            # 1. Candidate source and selection confidence:
            if c in subst_cands:
                feature_vector[0] = round(subst_cands[c], 4)
            if c in place_cands:
                feature_vector[1] = round(place_cands[c], 4)
            if c in altnm_cands:
                feature_vector[2] = round(altnm_cands[c], 4)

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
                feature_vector[3] = round(util.pytorch_cos_sim(embeddings[0], embeddings[1]).item(), 4)

                # 3. Wikidata class
                if not (type(wikidata_data["instance_of"]) == float and np.isnan(wikidata_data["instance_of"])):
                    for inst in literal_eval(wikidata_data["instance_of"]):
                        if inst in stn_wkdt_classes:
                            feature_vector[4] = 1.0
                            continue
                if not (type(wikidata_data["instance_of"]) == float and np.isnan(wikidata_data["instance_of"])):
                    for inst in literal_eval(wikidata_data["instance_of"]):
                        if inst in ppl_wkdt_classes:
                            feature_vector[5] = 1.0
                            continue

                # 4. Substation place compatibility
                closest = 100000
                if c in subst_cands or c in altnm_cands:
                    closest = closest_geo(gazetteer_df, c, place_cands, closest)
                closest = 10.0 if closest > 10.0 else closest
                feature_vector[6] = round((10 - closest)/10, 4)

                # 4. Substation place compatibility
                closest = 100000
                if c in place_cands:
                    closest = closest_geo(gazetteer_df, c, subst_cands, closest)
                if c in place_cands:
                    closest = closest_geo(gazetteer_df, c, altnm_cands, closest)

                closest = 10.0 if closest > 10.0 else closest
                feature_vector[7] = round((10 - closest)/10, 4)
                
                if not (type(wikidata_data["wikititle"]) == float and np.isnan(wikidata_data["wikititle"])):
                    inlinks = wikipedia_entity_overall_dict.get(quote(wikidata_data["wikititle"], safe=''), 0)
                    if inlinks > max_inlinks:
                        max_inlinks = inlinks
                    feature_vector[8] = inlinks
                
            except KeyError:
                continue

            mainid_column.append(row["MainId"])
            subid_column.append(row["SubId"])
            query_column.append(row["SubStFormatted"])
            candidate_column.append(c)
            feature_columns.append(feature_vector)
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

def train_classifier(inpdf, use_cols):
    
    df = inpdf.copy()
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
    tuned_parameters = [{'kernel': ['linear'], 'C': [0.01, 0.1, 1, 10, 100, 1000]}]

    clf_gs = GridSearchCV(SVC(), tuned_parameters, scoring = 'f1_macro')
    clf_gs.fit(X_train, y_train)

    print(clf_gs.best_params_)
    
    clf = SVC(**clf_gs.best_params_,probability=True)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print("Classification report on the test split of the dev set:")
    print(classification_report(y_pred,y_test))
    print(clf.coef_)
    
    return clf
        

# ----------------------------------
# Our methods
# ----------------------------------

def our_method_simple(df, clf_stations, use_cols_stations, gazetteer_df, results_test_df):
    
    dResolved = dict()
    for subid in list(set(list(df.SubId.unique()))):
        
        predicted_final = ""
        predicted_probs = 0.0
        
        cands = df[df.SubId==subid].Candidate.values

        # Stations classifier:
        X_stations = df.loc[df.SubId==subid,use_cols_stations].values
        probs_stations = [x[1] for x in clf_stations.predict_proba(X_stations)]
        predicted_probs = max(probs_stations)
        predicted_final = cands[probs_stations.index(predicted_probs)]
        
        dResolved[subid] = predicted_final
        
    results_test_df["our_method_all"] = results_test_df['SubId'].map(dResolved)
    
    return results_test_df

def our_method_comb(df, clf_stations, use_cols_stations, clf_places, use_cols_places, gazetteer_df, threshold, results_test_df):
    
    dResolved = dict()
    for subid in list(set(list(df.SubId.unique()))):
        
        predicted_final = ""
        predicted_probs = 0.0
        
        cands = df[df.SubId==subid].Candidate.values

        # Stations classifier:
        X_stations = df.loc[df.SubId==subid,use_cols_stations].values
        probs_stations = [x[1] for x in clf_stations.predict_proba(X_stations)]
        predicted_probs = max(probs_stations)
        predicted_final = cands[probs_stations.index(predicted_probs)]
        
        # If the probability is lower than the threshold we've previously identified:
        if predicted_probs < threshold:

            # Places classifier:
            X_places = df.loc[df.SubId==subid,use_cols_places].values
            probs_places = [x[1] for x in clf_places.predict_proba(X_places)]
            predicted_probs = max(probs_places)
            predicted_final = cands[probs_places.index(predicted_probs)]
        
        dResolved[subid] = predicted_final
        
    results_test_df["our_method_comb"] = results_test_df['SubId'].map(dResolved)
    
    return results_test_df


# This one keeps the info we'll like to have when applying to the whole Quicks dataset (type of prediction and confs):
def our_method_comb_keepconf(df, clf_stations, use_cols_stations, clf_places, use_cols_places, gazetteer_df, threshold, results_test_df):
    
    dResolved = dict()
    dStationsConf = dict()
    dPlacesConf = dict()
    dTypePrediction = dict()
    dLatitude = dict()
    dLongitude = dict()
    for subid in list(set(list(df.SubId.unique()))):
        
        predicted_final_station = ""
        predicted_final_place = ""
        predicted_probs = 0.0
        
        cands = df[df.SubId==subid].Candidate.values

        # Stations classifier:
        X_stations = df.loc[df.SubId==subid,use_cols_stations].values
        probs_stations = [x[1] for x in clf_stations.predict_proba(X_stations)]
        predicted_probs_station = max(probs_stations)
        predicted_final_station = cands[probs_stations.index(predicted_probs_station)]
        
        # Places classifier:
        X_places = df.loc[df.SubId==subid,use_cols_places].values
        probs_places = [x[1] for x in clf_places.predict_proba(X_places)]
        predicted_probs_place = max(probs_places)
        predicted_final_place = cands[probs_places.index(predicted_probs_place)]
        
        dStationsConf[subid] = round(predicted_probs_station, 2)
        dPlacesConf[subid] = round(predicted_probs_place, 2)
        
        # If the probability is lower than the threshold we've previously identified:
        dResolved[subid] = predicted_final_station
        dTypePrediction[subid] = "station"
        if predicted_probs_station < threshold:
            dResolved[subid] = predicted_final_place
            dTypePrediction[subid] = "place"
            
        dLatitude[subid] = gazetteer_df.loc[dResolved[subid]]["latitude"]
        dLongitude[subid] = gazetteer_df.loc[dResolved[subid]]["longitude"]
        
    results_test_df["prediction"] = results_test_df['SubId'].map(dResolved)
    results_test_df["typePrediction"] = results_test_df['SubId'].map(dTypePrediction)
    results_test_df["station_conf"] = results_test_df['SubId'].map(dStationsConf)
    results_test_df["place_conf"] = results_test_df['SubId'].map(dPlacesConf)
    results_test_df["latitude"] = results_test_df['SubId'].map(dLatitude)
    results_test_df["longitude"] = results_test_df['SubId'].map(dLongitude)
    
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


def skyline(features_df, test_df):
    
    dResolved = dict()
    for subid in list(set(list(features_df.SubId.unique()))):
        
        predicted_final = ""

        cands = features_df[features_df.SubId==subid].Candidate.values
        predicted_final = cands[features_df[features_df.SubId==subid]["Label"].argmax()]
        
        dResolved[subid] = predicted_final
        
    test_df["skyline"] = test_df['SubId'].map(dResolved)
    
    return test_df


# ----------------------------------
# RankLib
# ----------------------------------

def convert_feature_file_format(partition,features, filter):

    if filter == "exact":
        outfile = partition+"_exact-ranklib.tsv"
    elif filter == "notexact":
        outfile = partition+"_notexact-ranklib.tsv"
    else:
        outfile = partition+"_all-ranklib.tsv"

    out_feat_folder = "supervised_ranking/feature_files/"
    out_model_folder = "supervised_ranking/models/"
    pathlib.Path(out_feat_folder).mkdir(parents=True, exist_ok=True)
    pathlib.Path(out_model_folder).mkdir(parents=True, exist_ok=True)
    out = open(out_feat_folder+ outfile,"w")
    # MainId	SubId	Query	Candidate	f_0	f_1	f_2	f_3	f_4	f_5	f_6	f_7	f_8	Label	Exact
    current_qid = 0
    current_sub_id = 0
    for _id,line in features.iterrows():
        feat_vect = []
        filter_flag = line["Exact"]
        if filter == "exact" and filter_flag!=1:
            continue
        if filter == "notexact" and filter_flag!=0:
            continue

        label = line["Label"]
        cand = line["Candidate"]
        feat_vect.append(str(label))
        sub_id = line ["SubId"]
        if sub_id != current_sub_id:
            current_sub_id = sub_id
            current_qid+=1
        feat_vect.append("qid:"+str(current_qid))
        feat_counter = 1
        for f in range(4,13):
            feat_vect.append(str(feat_counter)+":"+str(line.iloc[f]))
            feat_counter+=1
        feat_vect.append("# "+ str(cand)+ " "+ str(current_sub_id))
        out.write(" ".join(feat_vect))
        out.write("\n")
    out.close()
    return out_feat_folder+ outfile

def ranklib(dev_feat_file,test_feat_file,filter,code_folder,cross_val,test_df):

    pathlib.Path(code_folder+"station-to-station/processed/ranklib/").mkdir(parents=True, exist_ok=True)
    dev = convert_feature_file_format("dev",dev_feat_file,filter=filter)
    feature_file = code_folder+"station-to-station/resources/ranklib/features.txt"
    feature_used = open(feature_file,"r").read().replace('\n'," ")

    if cross_val == True:
        
        out =  subprocess.check_output(["java", "-jar",code_folder+"station-to-station/resources/ranklib/RankLib-2.13.jar","-train",dev,"-ranker","4","-kcv", "5", "-metric2t","P@1", "-metric2T", "P@1","-feature",feature_file])
        out = out.decode("utf-8").split("\n")[-15:]
        return out
    else:
        test = convert_feature_file_format("test",test_feat_file,filter="all")
        out = subprocess.check_output(["java", "-jar",code_folder+"station-to-station/resources/ranklib/RankLib-2.13.jar","-train",dev,"-test",test,"-ranker","4","-metric2t","P@1", "-metric2T", "P@1","-save",code_folder+"station-to-station/processed/ranklib/model.run","-feature",feature_file])
        train_performance = out.decode("utf-8").split("\n")[-6]
        test_performance = out.decode("utf-8").split("\n")[-4]
        print (train_performance,test_performance)
        subprocess.check_output(["java", "-jar",code_folder+"station-to-station/resources/ranklib/RankLib-2.13.jar","-load",code_folder+"station-to-station/processed/ranklib/model.run","-rank",test,"-indri",code_folder+"station-to-station/processed/ranklib/rank.txt","-feature",feature_file])
        
        rank = open(code_folder+"station-to-station/processed/ranklib/rank.txt","r").read().strip().split("\n")
        q_ids = set([int(x.split(" ")[3]) for x in rank])

        results = {}

        for q_id in q_ids:
            scores = [[x.split(" ")[2],float(x.split(" ")[5])] for x in rank if int(x.split(" ")[3])==q_id]
            scores.sort(key=lambda x: x[1],reverse=True)
            results[q_id] = scores[0][0]
        print ("feature used:",feature_used)

    test_df["ranklib"] = test_df['SubId'].map(results)
    
    return test_df