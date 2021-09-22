# Using DeezyMatch for toponym matching

### Create a toponym matching dataset

Run [deezy_dataset_creation.py] to create a toponym pairs dataset from the `station-to-station/processed/wikidata/altname_gb_gazetteer.tsv` dataframe (created from [these steps](https://github.com/Living-with-machines/station-to-station/blob/main/wikidata/README.md)), which will be used to train a DeezyMatch model. Run the script with `gb` as parameter (this parameter specifies that we're using the `gb` gazetteer to create the toponym pairs dataset):

```bash
python deezy_dataset_creation.py -g gb
```

### Train DeezyMatch models

Run `deezy_model_training.py` to train the model we will use to find and rank Wikidata candidates for each entry in Quicks. This will also create vectors for all alternate names in both the `gb` and the `gb_stations` gazetteers.

```bash
python deezy_model_training.py
```
