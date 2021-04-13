import pandas as pd
from haversine import haversine
from sklearn.metrics import hamming_loss
from sklearn.metrics import jaccard_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import zero_one_loss

# ----------------------------------
# CANDIDATE SELECTION
# ----------------------------------

def get_true_and_ranking(row,approach, relv_cols, reverse):
    
    # Combine candidates from different columns:
    dCandidates = dict()
    for rc in relv_cols:
        for cand in row[rc]:
            if not cand in dCandidates:
                dCandidates[cand] = row[rc][cand]
            else:
                dCandidates[cand] = row[rc][cand]
    
    # Return true and sorted ranked candidates
    # Watch out! The reverse parameter changes depending on the candidate ranking metric:
    true = row["Final Wikidata ID"]
    true = true.replace("ppl:", "")
    true = true.replace("opl:", "")
    ranking = [[k,v] for k, v in sorted(dCandidates.items(), key=lambda item: item[1], reverse = reverse)]
    return true, ranking

def isRetrieved(row, approach, relv_cols, ncands, reverse):
    true, ranking = get_true_and_ranking(row, approach, relv_cols, reverse)
    ranking = ranking[:ncands]
    retrieved = [x[0] for x in ranking]
    if true in retrieved:
        return 1.0
    else:
        return 0.0

def p1(row,approach, relv_cols, reverse):
    true, ranking = get_true_and_ranking(row, approach, relv_cols, reverse)
    if len(ranking)>0:
        first = ranking[0][0]
        if first == true:
            return 1.0
        else:
            return 0.0
    else:
        return 0.0 # note that if the correct one is not retrieved at all, we give 0

def pAt(row, approach, relv_cols, ncands, reverse):
    true, ranking = get_true_and_ranking(row, approach, relv_cols, reverse)
    if len(ranking)>0:
        ranking = ranking[:ncands]
        for pred in ranking:
            if pred[0] == true:
                return 1.0
    
    return 0.0 # note that if the correct one is not retrieved at all, we give 0

def avgP (row, approach, relv_cols, ncands, reverse):
    true, ranking = get_true_and_ranking(row, approach, relv_cols, reverse)
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
    true = df["Final Wikidata ID"].to_list()
    true = [t.replace("opl:", "").replace("ppl:", "") for t in true]
    prediction = df[approach].to_list()
    print("Hamming Loss:", hamming_loss(true, prediction))
    print("Accuracy Score:", accuracy_score(true, prediction))
    print("Jaccard Score:", jaccard_score(true, prediction, average="macro"))

def distance_in_km(gazdf, gs, pred):
    gs = gs.replace("opl:", "").replace("ppl:", "")
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
    df["km_dist"] = df.apply(lambda row: distance_in_km(gazdf,row["Final Wikidata ID"],row[approach]), axis=1)
    print("Accuracy at 1:", accuracy_at_km(df["km_dist"], 1))
    print("Accuracy at 5:", accuracy_at_km(df["km_dist"], 5))
    print("Accuracy at 10:", accuracy_at_km(df["km_dist"], 10))
    