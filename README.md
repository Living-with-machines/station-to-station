<div align="center">
    <h1>Station to Station</h1>
    <h2>Linking and enriching historical British railway data</h2>
</div>

This repository provides underlying code and materials for the paper `Station to Station: Linking and enriching historical British railway data`.

## Table of contents

This is the main directory for Place Linking experiments, which contains:
* `bho/`: parsing and processing of BHO Lewis' Topographical Dictionaries.
* `quick/`: parsing and processing of Quick's Railway Guide.
* `wikidata`: processing of Wikidata, to be used in linking experiments.
* `wikipediaprocessing`: processing of Wikipedia, to be used in linking experiments.
* `toponym_matching`: DeezyMatch and its inputs and ouptuts.
* `toponym_resolution`: where toponym resolution happens.

See how to reproduce a specific experiment in the subsections below.

## Quicks to Wikidata

To reproduce this experiment:

1. Process the Quicks dataset ([readme](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/quick/README.md) and [notebook](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/quick/process_railway_stations.ipynb)). This step will output:
    * `quick/outputs/quicks_processed.pkl` and `quick/outputs/quicks_processed.tsv`: structured Quick's dataset.
    * `quick/outputs/quicks_parsed.pkl` and `quick/outputs/quicks_parsed.tsv`: structured Quick's dataset with regex-parsed descriptions.
    * `toponym_matching/toponyms/quicks_mainst_queries.txt`: Quick's main entries formatted as queries for DeezyMatch.
    * `toponym_matching/toponyms/quicks_subst_queries.txt`: Quick's sub entries formatted as queries for DeezyMatch.
    * `toponym_matching/toponyms/quicks_altnames_queries.txt`: Quick's altnames formatted as queries for DeezyMatch.
    
2. Process Wikidata ([readme](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/wikidata/README.md), [script](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/wikidata/entity_extraction.py), and [notebook](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/wikidata/wikidata_candidate_processing.ipynb)). This step will output:
    * `wikidata/british_isles.csv`: a subset of Wikidata, containing entities that are located either in the United Kingdom or Ireland.
    * An altname-centric British Wikidata gazetteer: `toponym_matching/gazetteers/britwikidata_gazetteer.pkl`
    * An altname-centric British Wikidata gazetteer with only railway stations: `toponym_matching/gazetteers/stnwikidata_gazetteer.pkl`
    * And the corresponding candidates (aka unique altnames) input file for DeezyMatch's candidate ranker: `toponym_matching/gazetteers/britwikidata_candidates.txt` and `toponym_matching/gazetteers/stnwikidata_candidates.txt`.
    
3. Run DeezyMatch to obtain candidates for queries ([readme](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/toponym_matching/README.md) and [script](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/toponym_matching/candidate_selection_quicks_wikidata.py)). This step runs four different DeezyMatch scenarios, query/candidate rankings are stored in `toponym_matching/ranker_results/`:
    * Quick's main entries as queries; Wikidata British railway station gazetteer entries as candidates.
    * Quick's sub entries as queries; Wikidata British railway station gazetteer entries as candidates.
    * Quick's alternate names as queries; Wikidata British railway station gazetteer entries as candidates.
    * Quick's main entries as queries; Wikidata British full gazetteer entries as candidates.
    
4. Find Wikidata candidates for Quick's queries ([notebook](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/toponym_resolution/quicks_wikidata/quicks_to_wikidata_candrank.ipynb)). This notebook returns a dataframe with the structured Quick's dataset with the best Wikidata candidates for each entry.
