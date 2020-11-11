# DeezyMatch for toponym matching

Follow the installation instructions from [here](
https://github.com/Living-with-machines/LwM_SIGSPATIAL2020_ToponymMatching#installation), and activate the `py37deezy` conda environment.

## Create a toponym matching dataset

Run [create_britTM_dataset.py](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/toponym_matching/create_britTM_dataset.py):
```
python create_britTM_dataset.py
```

You will need to have downloaded the English version of WikiGazetteer from [here](https://zenodo.org/record/4034819). This readme assumes the `wikigaz_en_basic.pkl` dataframe is stored in `/resources/wikigazetteer`. 

This script is adapted from https://github.com/Living-with-machines/LwM_SIGSPATIAL2020_ToponymMatching/blob/master/processing/toponym_matching_datasets/wikigaz/generate_wikigaz_comb.py

## Train DeezyMatch models

Run [train_DMmodels.ipynb](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/toponym_matching/train_DMmodels.ipynb) to train the models.

## Find candidates with DeezyMatch

Run [candidate_selection.ipynb](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/toponym_matching/candidate_selection.ipynb) to find candidates, given a model, a set of queries and a set of candidates. In this particular example, these are the inputs:
* **Model:** `models/wikigaz_en_001`, trained in [train_DMmodels.ipynb](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/toponym_matching/train_DMmodels.ipynb).
* **Set of queries:** `gazetteers/bho_queries.txt`, obtained following [these instructions](https://github.com/Living-with-machines/PlaceLinking/tree/fuzzy_matching/bho).
* **Set of candidates:** `gazetteers/britwikidata_candidates.txt`, obtained following [these instructions](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/wikidata/README.md).