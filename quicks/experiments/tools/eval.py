import pandas as pd

def get_true_and_ranking(row,approach):
    true = row["Wikidata ID"]
    ranking = [[k,v] for k, v in sorted(row[approach].items(), key=lambda item: item[1], reverse = True)]
    return true, ranking

def p1(row,approach):
    true, ranking = get_true_and_ranking(row, approach)
    if len(ranking)>0:
        first = ranking[0][0]
        if first == true:
            return 1.0
        else:
            return 0.0
    else:
        return 0.0 # note that if the correct one is not retrieved at all, we give 0

def avgP (row,approach):
    true, ranking = get_true_and_ranking(row, approach)
    for r in range(len(ranking)):
        if ranking[r][0] == true:
            return 1.0/(r+1.0) # checking at which position we find the correct one
    return 0.0 # note that if the correct one is not retrieved at all, we give 0