import argparse
import datetime
import pandas as pd
from pathlib import Path
import multiprocessing as mp
from geopy.distance import great_circle
from Levenshtein import distance as levDist
import random
import tqdm

"""
This script creates positive and negative matching pairs of toponyms given a gazetteer of alternate names. The code is based on https://github.com/Living-with-machines/LwM_SIGSPATIAL2020_ToponymMatching/blob/master/processing/toponym_matching_datasets/wikigaz/generate_wikigaz_comb.py
"""

def get_placename_and_unique_alt_names(place_dict):
    """given a place we retrieve altnames and location (we don't use location for the moment)"""
    
    placename = place_dict['placename']
    unique_alt_names = list(place_dict['altnames'])
    placeloc = (place_dict["lat"], place_dict["lon"])
    
    return placename, unique_alt_names, placeloc

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
        
def get_ngrams(placename, maxngrams,minngrams):
    
    ngrams = []
    for nlen in range(maxngrams,minngrams,-1):
        for ii in range(len(placename)-nlen+1):
            ngrams.append(placename[ii:(ii+nlen)])
    return ngrams


def get_final_wrong_cands_challenging(cand_ngrams,unique_alt_names,placename,placeloc,n_neg_cand_to_generate,place_id,wiki_ids,altnames):

    selected_wrong_cands = set()
    
    """
    for each ngram, we send a query to the DB
    at the moment i'm parallelizing at the placename step, but this could be also parallelized
    so searching different ngrams at the same time
    """
    # We take all altnames that:
    # * contain the a candidate ngram
    # * are not possible positive altnames of the toponym
    # * are not exact matches of the toponym
    # * their length difference with respect to the toponym is less than 5 characters
    for cand_ngram in cand_ngrams:
        collected_wrong_cands = {x for x in altnames.keys() if cand_ngram in x if place_id not in altnames[x] and x!= placename and x not in unique_alt_names and (abs(len(x) - len(placename)) <= 5)}
        for k in collected_wrong_cands:
            if k not in selected_wrong_cands:
                selected_wrong_cands.add(k)
    
    # we filter out alternate names that can correspond to locations within 50 km from
    # the main location
    mindistance = kilometre_distance
    filtered_by_distance = set()
    for x in selected_wrong_cands:
        within_distance = False
        for alt in altnames[x]:
            lat_alt = float(wiki_ids[alt]["lat"])
            lon_alt = float(wiki_ids[alt]["lon"])
            lat_main = float(wiki_ids[place_id]["lat"])
            lon_main = float(wiki_ids[place_id]["lon"])
            if great_circle((lat_alt, lon_alt), (lat_main,lon_main)).km < mindistance:
                within_distance = True
                break
        if within_distance == False:
            filtered_by_distance.add(x)
                
    selected_wrong_cands = filtered_by_distance
        
    if len(selected_wrong_cands)<1:
        return None
    
    # we rank them using LevDist so that we have on top the most similar wrong ones 
    rank_wrong_cands = [[placename,x,levDist(x,placename)] for x in selected_wrong_cands]
    
    # we sort them, from more similar to less (unlike in the trivial setting)
    rank_wrong_cands.sort(key=lambda x: x[2])
    
    # and we keep only the top n, depending on the number of positive candidates
    final_wrong_cands = rank_wrong_cands[:n_neg_cand_to_generate]
    
    return final_wrong_cands

def get_final_wrong_cands_trivial(unique_alt_names,placename,placeloc,n_neg_cand_to_generate,place_id,wiki_ids,altnames):

    selected_wrong_cands = set()
    
    # We take 50 random altnames that:
    # * are not possible positive altnames of the toponym
    # * are not exact matches of the toponym
    # * their length difference with respect to the toponym is less than 5 characters
    collected_wrong_cands = {x for x in random.sample(altnames.keys(), 50)}
    for k in collected_wrong_cands:
        if place_id not in altnames[k] and k != placename and k not in unique_alt_names and (abs(len(k) - len(placename)) <= 5):
            if k not in selected_wrong_cands:
                selected_wrong_cands.add(k)
        
    if len(selected_wrong_cands)<1:
        return None
    
    # we rank them using LevDist so that we have on top the most similar wrong ones 
    rank_wrong_cands = [[placename,x,levDist(x,placename)] for x in selected_wrong_cands]
    
    # we sort them, from more dissimilar to less (unlike in the challenging setting):
    rank_wrong_cands.sort(key=lambda x: x[2], reverse=True)
    
    # and we keep only the top n, depending on the number of positive candidates
    final_wrong_cands = rank_wrong_cands[:n_neg_cand_to_generate]
    
    return final_wrong_cands

def normalized_lev(s1, s2):
    return 1 - int(levDist(s1, s2)) / float(max(1, len(s1), len(s2)))

def generate_cands(place_id):
    
    place_dict = wiki_ids[place_id]

    placename, unique_alt_names, placeloc = \
            get_placename_and_unique_alt_names(place_dict)

    challenging_alt_names = [u for u in unique_alt_names if u != placename]
    challenging_alt_names = [u for u in challenging_alt_names if normalized_lev(u, placename) > 0.5]
    challenging_alt_names = list(set(challenging_alt_names))

    final_cands_chall = []
    final_cands_trivial = []
    final_cands = []

    """
    ### CHALLENGING PAIRS:
    """
    if len(challenging_alt_names)>0:
        
        # the number of neg candidates depend on the number of positive candidates
        n_neg_cand_to_generate = len(challenging_alt_names)
        
        """
        this has a huge impact on performance. it's the number of ngrams we will retrieve
        at the moment n is equal to length of the placename -1 to -3
        for Barcelona: ['Barcelon', 'arcelona', 'Barcelo', 'arcelon', 'rcelona']
        other cutoffs will give better results, but the number of queries will explode
        like this, with -3 and -5: ['Barcel','arcelo','rcelon','celona','Barce','arcel','rcelo','celon','elona']
        --- Update (4 Sep 2020)
        Using:         
        maxcutoff = len(placename)-1
        mincutoff = len(placename)-3
        
        will result in more challenging/interesting examples. (current setting) 
        
        The downside is that the number of found pairs will be 
        less than more generous cutoffs, e.g.:
        
        maxcutoff = len(placename)-1
        mincutoff = 1
        Take the example:
        s1 = "London" 
        cand_ngrams = get_ngrams(s1,len(s1)-1,1); print(cand_ngrams)
        OUTPUT:
        ['Londo', 'ondon', 'Lond', 'ondo', 'ndon', 'Lon', 'ond', 'ndo', 'don', 'Lo', 'on', 'nd', 'do', 'on']
        whereas:
        cand_ngrams = get_ngrams(s1,len(s1)-1,len(s1)-3); print(cand_ngrams) 
        OUTPUT:
        ['Londo', 'ondon', 'Lond', 'ondo', 'ndon']
        There are different ways to deal with these cases, e.g.:
        * We could pass the whole cand_ngrams and have a break in get_final_wrong_cands_challenging, i.e.
        stop searching for pairs when a specific number of candidates is reached
        * Pass cand_ngrams = cand_ngrams[:N] 
        """
        
        maxcutoff = len(placename)-1
        mincutoff = len(placename)-5

        cand_ngrams = get_ngrams(placename,maxcutoff,mincutoff)
        
        # now, having a set of ngams, we try to retrieve negative candidates
        # so candidates that are similar based on ngrams overlap, like Marcelona for Barcelona
        final_cands_chall = get_final_wrong_cands_challenging(cand_ngrams,challenging_alt_names,placename,placeloc,n_neg_cand_to_generate,place_id,wiki_ids,altnames)

        if final_cands_chall != None:
            # we keep only placename and wrongcand and add the label False
            final_cands_chall = [x[:2]+["False"] for x in final_cands_chall]
                
            # we double check and in case the number of neg is less than the pos
            # we take only a random selection of the positive
            
            n_final_wrong = len(final_cands_chall)

            random.shuffle(challenging_alt_names)
            
            # we add the positive as well with the label
            for i in range(n_final_wrong):
                alt_name_cand = [placename,challenging_alt_names[i],"True"]
                final_cands_chall.append(alt_name_cand)

        """
        ### TRIVIAL PAIRS:
        # * indented twice: if there are challenging pairs, we also get trivial pairs.
        # * indented once: for each toponym, get trivial pairs.
        """

        trivial_alt_names = [u for u in unique_alt_names if u.lower() == placename.lower()]

        # Randomly with probabily 1/20 we add a lower-cased toponym or upper-cased toponym as alternate name:
        random_add = random.choice(range(0,20))
        if random_add == 2:
            trivial_alt_names.append(placename.lower())
        if random_add == 3:
            trivial_alt_names.append(placename.upper())

        # the number of neg candidates depend on the number of positive candidates
        n_neg_cand_to_generate = len(trivial_alt_names)

        # we try to retrieve negative trivial pairs for as many positive pairs
        final_cands_trivial = get_final_wrong_cands_trivial(trivial_alt_names,placename,placeloc,n_neg_cand_to_generate,place_id,wiki_ids,altnames)

        if final_cands_trivial != None:
            # we keep only placename and wrongcand and add the label False
            final_cands_trivial = [x[:2]+["False"] for x in final_cands_trivial]

            # we double check and in case the number of neg is less than the pos
            # we take only a random selection of the positive

            n_final_wrong = len(final_cands_trivial)

            random.shuffle(trivial_alt_names)

            # we add the positive as well with the label
            for i in range(n_final_wrong):
                alt_name_cand = [placename,trivial_alt_names[i],"True"]
                final_cands_trivial.append(alt_name_cand)
    
    # We join trivial and challenging pairs   
    if final_cands_trivial:
        final_cands += final_cands_trivial

    if final_cands_chall:
        final_cands += final_cands_chall
    
    if final_cands:
        return final_cands

    else:
        return None


def main(kilometre_distance, N, titles_per_chunk, out_file):
                
    p = mp.Pool(processes = N)
    start = datetime.datetime.now()
    
    # i have divided the list of wiki titles in small chunks 
    # so i can process a few at a times and identify how long it will take
    for split in tqdm.tqdm(wiki_titles_splits):
        
        # we assign them to different processes
        res = p.map(generate_cands, split)
        
        # we exclude the Nones
        res = [x for x in res if x!= None]
        res = [y for x in res for y in x if len(y)>1]
        
        #write out the results
        for el in res:
            out_file.write('\t'.join(el)+"\n")
            
def process_args(number_cpus, input_gazetteer):
    gazdf = pd.read_pickle(input_gazetteer)
    gazdf = gazdf[gazdf['altname'].str.len() < 50]
    
    wiki_ids = {row["wkid"]:{"placename":row["altname"], "altnames":set(),"lat":"","lon":""} for i, row in gazdf.iterrows()}
    altnames = {row["altname"]:set() for i, row in gazdf.iterrows()}
    
    for i,row in gazdf.iterrows():
        if len(wiki_ids[row["wkid"]]["altnames"])==0:
            wiki_ids[row["wkid"]]["lat"] = row["lat"]
            wiki_ids[row["wkid"]]["lon"] = row["lon"]

        if row["altname"] not in wiki_ids[row["wkid"]]["altnames"]:
            wiki_ids[row["wkid"]]["altnames"].add(row["altname"])

        if row["wkid"] not in altnames[row["altname"]]:
            altnames[row["altname"]].add(row["wkid"])

    wiki_titles = [x for x in wiki_ids.keys()]

    random.shuffle(wiki_titles)
    
    # we organize it in chunks, each chink has titles_per_chunk titles
    wiki_titles_splits = list(chunks(wiki_titles, titles_per_chunk))

    if number_cpus < 0:
        # how many cpu to be used
        N = mp.cpu_count()
    else:
        N = int(number_cpus)
    
    return N, wiki_titles, wiki_titles_splits, wiki_ids, altnames

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gazetteer",
                    help="Gazetter from which to create the toponym matching dataset. Options:\n*british_isles\n*british_isles_stations", required=True)
    parser.add_argument("-n", "--number_cpus", default=-1, 
                    help="Number of CPUs to be used for processing. Default: -1 (use all)")
    parser.add_argument("-tc", "--titles_per_chunk", default=5000, 
                    help="Number of titles per chunk")
    parser.add_argument("-km", "--kilometre_distance", default=50, 
                    help="Minimum distance of negative toponym pair")
    args = parser.parse_args()

    # Parameters you can tune tune:
    kilometre_distance = int(args.kilometre_distance)
    number_cpus = int(args.number_cpus) # Use all
    titles_per_chunk = int(args.titles_per_chunk)
    
    gazetteer = args.gazetteer # gb or gb_stations
    
    input_gazetteer = "../processed/wikidata/altname_" + gazetteer + "_gazetteer.pkl"
    output_dataset = "../processed/deezymatch/datasets/" + gazetteer + "_toponym_pairs.txt"
    Path("../processed/deezymatch/datasets/").mkdir(parents=True, exist_ok=True)
    
    output_file = open(output_dataset, "w")
    N, wiki_titles, wiki_titles_splits, wiki_ids, altnames = process_args(number_cpus, input_gazetteer)
    main(kilometre_distance, N, titles_per_chunk, output_file)
    output_file.close()