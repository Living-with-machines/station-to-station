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

## Find candidates with DeezyMatch

Run [candidate_selection.ipynb](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/toponym_matching/candidate_selection.ipynb) to find candidates, given a model, a set of queries and a set of candidates. In this particular example, these are the inputs:
* **Model:** `models/wikigaz_en_001`, trained in [train_DMmodels.ipynb](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/toponym_matching/train_DMmodels.ipynb).
* **Set of queries:** `gazetteers/bho_queries.txt`, obtained following [these instructions](https://github.com/Living-with-machines/PlaceLinking/tree/fuzzy_matching/bho).
* **Set of candidates:** `gazetteers/britwikidata_candidates.txt`, obtained following [these instructions](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/wikidata/README.md).