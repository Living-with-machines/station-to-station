# DeezyMatch for toponym matching

Follow the installation instructions from [here](
https://github.com/Living-with-machines/LwM_SIGSPATIAL2020_ToponymMatching#installation), and activate the `py37deezy` conda environment.

**Note:** The code in this folder depends on having processed Wikidata. Make sure you have followed [these steps](https://github.com/Living-with-machines/PlaceLinking/blob/dev/wikidata/README.md) before attempting to run the following scripts.

## Create a toponym matching dataset

Run [deezy_dataset_creation.py] to create the toponym pairs dataset, which will be the training data to train a DeezyMatch model. This will need the gazetteer to be specified. Run the script both with `british_isles` and `british_isles_stations`:
```
python deezy_dataset_creation.py -g british_isles
```

## Train DeezyMatch models

Run [deezy_model_training.ipynb](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/toponym_matching/train_DMmodels.ipynb) to train and fine-tune the models.

## Find candidates with DeezyMatch: Quicks to Wikidata

Run [`candidate_selection_quicks_wikidata.py`](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/toponym_matching/candidate_selection_quicks_wikidata.py) to find the best ranking of candidates, given a model, a set of queries and a set of candidates.

This script runs four different DeezyMatch scenarios, query/candidate rankings are stored in `toponym_matching/ranker_results/`:
    * Quick's main entries as queries; Wikidata British railway station gazetteer entries as candidates.
    * Quick's sub entries as queries; Wikidata British railway station gazetteer entries as candidates.
    * Quick's alternate names as queries; Wikidata British railway station gazetteer entries as candidates.
    * Quick's main entries as queries; Wikidata British full gazetteer entries as candidates.

Note that this will require that you have already trained a DeezyMatch model, e.g. `models/wikigaz_en_001`, `models/wikigaz_en_002`, or `models/wikigaz_en_003`, trained in [train_DMmodels.ipynb](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/toponym_matching/train_DMmodels.ipynb).