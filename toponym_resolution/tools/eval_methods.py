import pandas as pd
from haversine import haversine
from sklearn.metrics import hamming_loss
from sklearn.metrics import jaccard_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import zero_one_loss

# ----------------------------------
# CANDIDATE SELECTION
# ----------------------------------

def get_true_and_ranking(row,approach, reverse):
    true = row["Final Wikidata ID"]
    ranking = [[k,v] for k, v in sorted(row[approach].items(), key=lambda item: item[1], reverse = reverse)]
    return true, ranking

def p1(row,approach, reverse):
    true, ranking = get_true_and_ranking(row, approach, reverse)
    if len(ranking)>0:
        first = ranking[0][0]
        if first == true:
            return 1.0
        else:
            return 0.0
    else:
        return 0.0 # note that if the correct one is not retrieved at all, we give 0

def pAt(row,approach, ncands, reverse):
    true, ranking = get_true_and_ranking(row, approach, reverse)
    if len(ranking)>0:
        ranking = ranking[:ncands]
        for pred in ranking:
            if pred[0] == true:
                return 1.0
    
    return 0.0 # note that if the correct one is not retrieved at all, we give 0

def avgP (row,approach, ncands, reverse):
    true, ranking = get_true_and_ranking(row, approach, reverse)
    if len(ranking)>0:
        ranking = ranking[:ncands]
    for r in range(len(ranking)):
        if ranking[r][0] == true:
            return 1.0/(r+1.0) # checking at which position we find the correct one
    return 0.0 # note that if the correct one is not retrieved at all, we give 0


# ----------------------------------
# TOPONYM RESOLUTION
# ----------------------------------

def topres_exactmetrics(df, approach):
    df["Final Wikidata ID"] = df["Final Wikidata ID"].str.replace("opl:.*", "", regex=True)
    df["Final Wikidata ID"] = df["Final Wikidata ID"].str.replace("ppl:.*", "", regex=True)
    true = df["Final Wikidata ID"].to_list()
    prediction = df[approach].to_list()
    print("Hamming Loss:", hamming_loss(true, prediction))
    print("Accuracy Score:", accuracy_score(true, prediction))
    print("Jaccard Score:", jaccard_score(true, prediction, average="macro"))

def distance_in_km(gazdf, gs, pred):
    gs_coords = None
    if gs in gazdf.index:
        gs_coords = tuple(gazdf.loc[gs][["latitude", "longitude"]].to_list())
    pred_coords = None
    if pred in gazdf.index:
        pred_coords = tuple(gazdf.loc[pred][["latitude", "longitude"]].to_list())
    if not gs_coords and not pred_coords: # If both gold standard and prediction are None, distance is 0:
        return 0.0
    if not gs_coords or not pred_coords: # If only one is None, return a large number:
        return 10000
    return round(haversine(gs_coords, pred_coords), 2)

def accuracy_at_km(km_dist, min_km):
    km_dist = km_dist.to_list()
    dist_list = [1 if dist <= min_km else 0 for dist in km_dist]
    return dist_list.count(1) / len(dist_list)

def topres_distancemetrics(gazdf, df, approach):
    tmp_df = df.copy()
    tmp_df["Final Wikidata ID"] = tmp_df["Final Wikidata ID"].str.replace("opl:.*", "", regex=True)
    tmp_df["Final Wikidata ID"] = tmp_df["Final Wikidata ID"].str.replace("ppl:.*", "", regex=True)
    tmp_df["km_dist"] = tmp_df.apply(lambda row: distance_in_km(gazdf,row["Final Wikidata ID"],row[approach]), axis=1)
    print("Accuracy at 1:", accuracy_at_km(tmp_df["km_dist"], 1))
    print("Accuracy at 5:", accuracy_at_km(tmp_df["km_dist"], 5))
    print("Accuracy at 10:", accuracy_at_km(tmp_df["km_dist"], 10))
    