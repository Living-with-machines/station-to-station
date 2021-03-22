# Extract and process Wikidata entities

The scripts in this folder create Wikidata-derived gazetteers that are used in the experiments.

Run the following two scripts:
1. Run [entity_extraction.py](https://github.com/Living-with-machines/PlaceLinking/blob/18-refactor-wiki-pipeline/wikidata/entity_extraction.py) to extract relevant entities and create Wikidata gazetteers, see [below](https://github.com/Living-with-machines/PlaceLinking/tree/18-refactor-wiki-pipeline/wikidata#1-extract-relevant-entities) for more information.
2. Run [extend_altnames.py](https://github.com/Living-with-machines/PlaceLinking/blob/18-refactor-wiki-pipeline/wikidata/extend_altnames.py) to expand the alternate names in the gazetteers, see [below](https://github.com/Living-with-machines/PlaceLinking/tree/18-refactor-wiki-pipeline/wikidata#2-extending-altnames) for more information.

## Extracting relevant entities

Run [entity_extraction.py](https://github.com/Living-with-machines/PlaceLinking/blob/18-refactor-wiki-pipeline/wikidata/entity_extraction.py) to create gazetteers from Wikidata. 

This script consists of three parts:

#### i. Parse Wikidata for geographic entities

This first part is partially based on https://akbaritabar.netlify.app/how_to_use_a_wikidata_dump.

Before running this script, download a full Wikidata dump from [here](https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2). In this script we assume the downloaded `bz2` file is stored in `/resources/wikidata/`. You will have to uncomment the `Parse all WikiData` section (rows 370-398).

The output is in the form of `.csv` files, stored in `../resources/wikidata/extracted`, each containing 5,000 geographical entities extracted from Wikidata with the following fields (a description of each can be found in the code comments):

```
'wikidata_id', 'english_label', 'instance_of', 'description_set', 'alias_dict', 'nativelabel', 'population_dict', 'area', 'hcounties', 'date_opening', 'date_closing', 'inception_date', 'dissolved_date', 'follows', 'replaces', 'adm_regions', 'countries', 'continents', 'capital_of', 'borders', 'near_water', 'latitude', 'longitude', 'wikititle', 'geonamesIDs', 'toIDs', 'vchIDs', 'vob_placeIDs', 'vob_unitIDs', 'epns', 'os_grid_ref', 'connectswith', 'street_address', 'adjacent_stations', 'ukrailcode', 'connectline', 'connectservice', 'getty', 'heritage_designation', 'ownedby', 'postal_code', 'street_located'
```

The [feature_exploration.ipynb](https://github.com/Living-with-machines/PlaceLinking/blob/18-refactor-wiki-pipeline/wikidata/feature_exploration.ipynb) notebook allows exploring Wikidata features for different query entities.

#### ii. Create an approximate subset with entities from the British Isles

In this step, we create a subset with those entities that are part of the British Isles, to have a more manageable dataset. At this stage we favour recall. We perform this filtering in the following manner: we keep Wikidata entities for which the country field is Q145 (United Kingdom) or Q27 (Ireland) or entities that fall within a coordinate boundary box loosely corresponding to the British Isles and for which their country field is not Q142 (France) or Q31 (Belgium), as some locations from these countries unavoidably fell within the boundary box as well.

The result is stored as `../resources/wikidata/british_isles_gazetteer.csv`. See its first rows:

| id | wikidata_id | english_label            | instance_of | description_set                                   | alias_dict                                        | ... | heritage_designation | postal_code  |
|---|-------------|--------------------------|-------------|---------------------------------------------------|---------------------------------------------------|-----|----------------------|--------------|
| 0 | Q63607865   | Kilberry Head            | ['Q185113'] | {'cape in Argyll and Bute, Scotland'}             | {'en': ['Kilberry Head']}                         | ... | NaN                  | NaN          |
| 1 | Q63759247   | Sandhurst Memorial Park  | ['Q22698']  | {'memorial park in Sandhurst, Berkshire'}         | {'en': ['Sandhurst Memorial Park']}               | ... | NaN                  | NaN          |
| 2 | Q63781193   | Currie railway station   | ['Q55488']  | {'railway station in City of Edinburgh, Scotla... | {'en': ['Currie railway station']}                | ... | NaN                  | NaN          |
| 3 | Q63859929   | Stannington War Memorial | ['Q575759'] | {'war memorial in Stannington, Sheffield, Sout... | {'en': ['Stannington War Memorial']}              | ... | Q15700834            | NaN          |
| 4 | Q63860920   | 2 Darnley Road           | ['Q3947']   | {'house in Leeds'}                                | {'en-gb': ['2 Darnley Road'], 'en': ['2 Darnle... | ... | NaN                  | ['LS16 5JF'] |

#### iii. Create an approximate subset with railway station entities from the British Isles

In this step, we create a further subset of those entries in the British Isles that are either instances of station-related classes (manually identified) or their English label has the words `station`, `stop`, or `halt`, not preceded by typical non-railway station stations such as 'police', 'signal', 'power', 'lifeboat', 'pumping', or 'transmitting'.

The result is stored as `../resources/wikidata/british_isles_stations_gazetteer.csv`. See its first rows:

| id | wikidata_id | english_label                             | instance_of | description_set                                   | alias_dict                                        | ... | street_located | postal_code |
|---|-------------|-------------------------------------------|-------------|---------------------------------------------------|---------------------------------------------------|-----|----------------|-------------|
| 0 | Q63781193   | Currie railway station                    | ['Q55488']  | {'railway station in City of Edinburgh, Scotla... | {'en': ['Currie railway station']}                | ... | NaN            | NaN         |
| 1 | Q5597551    | Grassington & Threshfield railway station | ['Q55488']  | set()                                             | {'en': ['Grassington & Threshfield railway sta... | ... | NaN            | NaN         |
| 2 | Q5597568    | Grassmoor railway station                 | ['Q55488']  | set()                                             | {'en': ['Grassmoor railway station']}             | ... | NaN            | NaN         |
| 3 | Q5599719    | Great Ormesby railway station             | ['Q55488']  | set()                                             | {'en': ['Great Ormesby railway station']}         | ... | NaN            | NaN         |
| 4 | Q5601497    | Greatstone-on-Sea Halt railway station    | ['Q55488']  | set()                                             | {'en': ['Greatstone-on-Sea Halt railway statio... | ... | NaN            | NaN         |


## Expanding the altnames

Run [extend_altnames.py](https://github.com/Living-with-machines/PlaceLinking/blob/18-refactor-wiki-pipeline/wikidata/extend_altnames.py) to extend the altnames of the British Isles gazetteer and the British Isles stations gazetteer, and to create altname-centric gazetteers (i.e. not WikidataID-centric).

The altnames come from the following sources:
* Wikidata `alias_dict`, `english_label`, and `native_label` fields.
* Wikipedia (via [Wikigaz](https://github.com/Living-with-machines/lwm_GIR19_resolving_places/tree/master/gazetteer_construction)).
* Geonames alternate names.

This results in two different dataframes, one for the British Isles gazetteer (stored in `../resources/wikidata/altname_british_isles_gazetteer.pkl`) and one for the British Isles stations gazetteer (stored in `../resources/wikidata/altname_british_isles_gazetteer.pkl`).

See the first rows of the British Isles stations altnames-centric gazetteer:

|   | wkid      | altname                                   | source        | lat      | lon       |
|---|-----------|-------------------------------------------|---------------|----------|-----------|
| 0 | Q63781193 | Currie railway station                    | english_label | 55.90310 | -3.283500 |
| 1 | Q5597551  | Grassington railway station               | wikigaz       | 54.07050 | -2.009800 |
| 2 | Q5597551  | Threshfield Station                       | wikigaz       | 54.07050 | -2.009800 |
| 3 | Q5597551  | Grassington & Threshfield railway station | english_label | 54.07050 | -2.009800 |
| 4 | Q5597551  | Threshfield railway station               | wikigaz       | 54.07050 | -2.009800 |
