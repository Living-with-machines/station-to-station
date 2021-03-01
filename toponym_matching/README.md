# DeezyMatch for toponym matching

Follow the installation instructions from [here](
https://github.com/Living-with-machines/LwM_SIGSPATIAL2020_ToponymMatching#installation), and activate the `py37deezy` conda environment.

## Create a toponym matching dataset

Run [prepare_britwikigaz.ipynb] to create an altname-focused version of the British Isles English Wikigazetteer.

Run [create_britTM_dataset.py](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/toponym_matching/create_britTM_dataset.py) to create the toponym pairs dataset, which will be the training data to train a DeezyMatch model.:
```
python create_britTM_dataset.py
```

This script is adapted from https://github.com/Living-with-machines/LwM_SIGSPATIAL2020_ToponymMatching/blob/master/processing/toponym_matching_datasets/wikigaz/generate_wikigaz_comb.py

## Train DeezyMatch models

Run [train_DMmodels.ipynb](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/toponym_matching/train_DMmodels.ipynb) to train the models.

## Find candidates with DeezyMatch: Quicks to Wikidata

Run [`candidate_selection_quicks_wikidata.py`](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/toponym_matching/candidate_selection_quicks_wikidata.py) to find the best ranking of candidates, given a model, a set of queries and a set of candidates.

This script runs four different DeezyMatch scenarios, query/candidate rankings are stored in `toponym_matching/ranker_results/`:
    * Quick's main entries as queries; Wikidata British railway station gazetteer entries as candidates.
    * Quick's sub entries as queries; Wikidata British railway station gazetteer entries as candidates.
    * Quick's alternate names as queries; Wikidata British railway station gazetteer entries as candidates.
    * Quick's main entries as queries; Wikidata British full gazetteer entries as candidates.

Note that this will require that you have already trained a DeezyMatch model, e.g. `models/wikigaz_en_001`, `models/wikigaz_en_002`, or `models/wikigaz_en_003`, trained in [train_DMmodels.ipynb](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/toponym_matching/train_DMmodels.ipynb).