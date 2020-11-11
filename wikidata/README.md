# Extract and process Wikidata entities

## Extract relevant entities

Run [entity_extraction.py](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/wikidata/entity_extraction.py) to create a gazetteer from Wikidata. 

This script is partially based on https://akbaritabar.netlify.app/how_to_use_a_wikidata_dump.

Before running this script, download a full Wikidata dump from [here](https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2). In this script we assume the downloaded `bz2` file is stored in `/resources/wikidata/`. You will have to uncomment the `Parse all WikiData` section.

The output is in the form of `.csv` files, each containing 5,000 geographical entities extracted from Wikidata, with the following fields (a description of each can be found in the code comments):

```
'wikidata_id', 'english_label', 'instance_of', 'description_set', 'alias_dict', 'nativelabel', 'population_dict', 'area', 'hcounties', 'date_opening', 'date_closing', 'inception_date', 'dissolved_date', 'follows', 'replaces', 'adm_regions', 'countries', 'continents', 'capital_of', 'borders', 'near_water', 'latitude', 'longitude', 'wikititle', 'geonamesIDs', 'toIDs', 'vchIDs', 'vob_placeIDs', 'vob_unitIDs', 'epns', 'os_grid_ref', 'connectswith', 'street_address', 'adjacent_stations', 'ukrailcode', 'connectline'
```

This script also outputs another file: `british_isles.csv`, which is a subset of Wikidata, containing entities that are located either in the United Kingdom or Ireland.

## Processing Wikidata candidates

The [wikidata_candidate_processing.ipynb](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/wikidata/wikidata_candidate_processing.ipynb) notebook takes `british_isles.csv` as input, and produces two outputs:
* An altname-centric British Wikidata gazetteer: `../toponym_matching/gazetteers/britwikidata_gazetteer.pkl`
* The candidates (aka unique altnames) input file for candidate ranker: `../toponym_matching/gazetteers/britwikidata_candidates.txt`

## Exploratory notebooks

The other two notebooks in this folder are exploratory:
* [wd_feature_exploration.ipynb](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/wikidata/wd_feature_exploration.ipynb): Wikidata features exploration.
* [wd_instanceof_exploration.ipynb](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/wikidata/wd_instanceof_exploration.ipynb): exploration of Wikidata `instance_of` feature.