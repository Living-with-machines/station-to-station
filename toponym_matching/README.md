# Using DeezyMatch for toponym matching

**Note:** The code in this folder relies on having previously processed Wikidata. Make sure you have followed [these steps](https://github.com/Living-with-machines/PlaceLinking/blob/master/wikidata/README.md) before trying to run the following scripts.

### Create a toponym matching dataset

Run [deezy_dataset_creation.py] to create the toponym pairs dataset, which will be the training data to train a DeezyMatch model. You will need to specify the gazetteer you want to create the dataset from. Run the script both with `gb` and `gb_stations`:
```bash
python deezy_dataset_creation.py -g gb
```
and:
```bash
python deezy_dataset_creation.py -g gb_stations
```

### Train DeezyMatch models

Run `deezy_model_training.py` to train the model we will use to find and rank Wikidata candidates for each entry in Quicks. This will also create vectors for all alternate names in both the `gb` and the `gb_stations` gazetteers.

```bash
python deezy_model_training.py
```
