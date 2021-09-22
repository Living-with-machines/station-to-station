# Using DeezyMatch for toponym matching

### Create a toponym matching dataset

Run [deezy_dataset_creation.py] to create a toponym pairs dataset from the `station-to-station/processed/wikidata/altname_gb_gazetteer.tsv` dataframe (created from [these steps](https://github.com/Living-with-machines/station-to-station/blob/main/wikidata/README.md)), which will be used to train a DeezyMatch model. Run the script with `gb` as parameter (this parameter specifies that we're using the `gb` gazetteer to create the toponym pairs dataset):

```bash
python deezy_dataset_creation.py -g gb
```

The output of this step is `station-to-station/processed/deezymatch/datasets/gb_toponym_pairs.txt`, a toponym matching dataset which contains pairs of toponyms and whether one is a name variation of the other. See some rows:
| Toponym 1 | Toponym2 | Match |
| ---------- | ---------- | ------- |
| Hoddom Castle| Clarsach Lumanach | False|
| Hoddom Castle| Millom Castle | False |
| Hoddom Castle| Hoddom Castle | True |
| Hoddom Castle| Hoddam Castle | True |


### Train DeezyMatch models

Run `deezy_model_training.py` to train the model we will use to find and rank Wikidata candidates for each entry in Quicks. This will also create vectors for all alternate names in both the `gb` and the `gb_stations` gazetteers.

```bash
python deezy_model_training.py
```

The outputs of this step are stored under `station-to-station/processed/deezymatch/`. In particular, this step creates:
* A DeezyMatch model (`wikidata_gb`) trained on the toponym pairs that have resulted from the previous step, stored under `station-to-station/processed/deezymatch/models/wikidata_gb/`.
* The set of all possible name variations of all Wikidata candidates, stored under `station-to-station/processed/deezymatch/candidate_toponyms/`.
* The DeezyMatch vectors corresponding to the `candidate_toponyms`, stored under `station-to-station/processed/deezymatch/candidate_vectors/`.