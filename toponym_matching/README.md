# Using DeezyMatch for toponym matching

Follow the installation instructions from [here](**Instructions**), and activate the `py37deezy` conda environment.

**Note:** The code in this folder depends on having processed Wikidata. Make sure you have followed [these steps](https://github.com/Living-with-machines/PlaceLinking/blob/dev/wikidata/README.md) before trying to run the following scripts.

### Create a toponym matching dataset

Run [deezy_dataset_creation.py] to create the toponym pairs dataset, which will be the training data to train a DeezyMatch model. You will need to specify the gazetteer you want to create the dataset from. Run the script both with `gb` and `gb_stations`:
```
python deezy_dataset_creation.py -g gb
```
and:
```
python deezy_dataset_creation.py -g gb_stations
```

### Train DeezyMatch models

Run [deezy_model_training.py](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/toponym_matching/train_DMmodels.ipynb) to train the model we will use to find and rank Wikidata candidates for each entry in Quicks. This will also create vectors for all alternate names in both the `gb` and the `gb_stations` gazetteers.