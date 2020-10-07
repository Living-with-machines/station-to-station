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