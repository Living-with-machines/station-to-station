# Extract and process Wikidata entities

The scripts in this folder create Wikidata-derived gazetteers that are used in the experiments.

## 1. Extract relevant entities

Run [entity_extraction.py](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/wikidata/entity_extraction.py) to create gazetteers from Wikidata. 

This script consists of three parts:

#### i. Parse Wikidata for geographic entities

This first part is partially based on https://akbaritabar.netlify.app/how_to_use_a_wikidata_dump.

Before running this script, download a full Wikidata dump from [here](https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2). In this script we assume the downloaded `bz2` file is stored in `/resources/wikidata/`. You will have to uncomment the `Parse all WikiData` section (rows 370-398).

The output is in the form of `.csv` files, stored in `../resources/wikidata/extracted`, each containing 5,000 geographical entities extracted from Wikidata with the following fields (a description of each can be found in the code comments):

```
'wikidata_id', 'english_label', 'instance_of', 'description_set', 'alias_dict', 'nativelabel', 'population_dict', 'area', 'hcounties', 'date_opening', 'date_closing', 'inception_date', 'dissolved_date', 'follows', 'replaces', 'adm_regions', 'countries', 'continents', 'capital_of', 'borders', 'near_water', 'latitude', 'longitude', 'wikititle', 'geonamesIDs', 'toIDs', 'vchIDs', 'vob_placeIDs', 'vob_unitIDs', 'epns', 'os_grid_ref', 'connectswith', 'street_address', 'adjacent_stations', 'ukrailcode', 'connectline', 'connectservice', 'getty', 'heritage_designation', 'ownedby', 'postal_code', and 'street_located'
```

#### ii. Create an approximate subset with entities from the British Isles

In this step, we create a subset with those entities that are part of the British Isles, to have a more manageable dataset. At this stage we favour recall. We perform this filtering in the following manner: we keep Wikidata entities for which the country field is Q145 (United Kingdom) or Q27 (Ireland) or entities that fall within a coordinate boundary box loosely corresponding to the British Isles and for which their country field is not Q142 (France) or Q31 (Belgium), as some locations from these countries unavoidably fell within the boundary box as well.

The result is stored as `../resources/wikidata/british_isles_gazetteer.csv`. 

See the first rows of the .csv:

| id | wikidata_id | english_label            | instance_of | description_set                                   | alias_dict                                        | ... | heritage_designation | postal_code  |
|---|-------------|--------------------------|-------------|---------------------------------------------------|---------------------------------------------------|-----|----------------------|--------------|
| 0 | Q63607865   | Kilberry Head            | ['Q185113'] | {'cape in Argyll and Bute, Scotland'}             | {'en': ['Kilberry Head']}                         | ... | NaN                  | NaN          |
| 1 | Q63759247   | Sandhurst Memorial Park  | ['Q22698']  | {'memorial park in Sandhurst, Berkshire'}         | {'en': ['Sandhurst Memorial Park']}               | ... | NaN                  | NaN          |
| 2 | Q63781193   | Currie railway station   | ['Q55488']  | {'railway station in City of Edinburgh, Scotla... | {'en': ['Currie railway station']}                | ... | NaN                  | NaN          |
| 3 | Q63859929   | Stannington War Memorial | ['Q575759'] | {'war memorial in Stannington, Sheffield, Sout... | {'en': ['Stannington War Memorial']}              | ... | Q15700834            | NaN          |
| 4 | Q63860920   | 2 Darnley Road           | ['Q3947']   | {'house in Leeds'}                                | {'en-gb': ['2 Darnley Road'], 'en': ['2 Darnle... | ... | NaN                  | ['LS16 5JF'] |

#### iii. Create an approximate subset with railway station entities from the British Isles

In this step, we create a further subset of those entries in the British Isles that are either instances of station-related classes (manually identified) or their English label has the words `station`, `stop`, or `halt`, not preceded by typical non-railway station stations such as 'police', 'signal', 'power', 'lifeboat', 'pumping', or 'transmitting'.

The result is stored as `../resources/wikidata/british_isles_stations_gazetteer.csv`.

See the first rows of the .csv:

| x | wikidata_id | english_label                             | instance_of | description_set                                   | alias_dict                                        | ... | street_located | postal_code |
|---|-------------|-------------------------------------------|-------------|---------------------------------------------------|---------------------------------------------------|-----|----------------|-------------|
| 0 | Q63781193   | Currie railway station                    | ['Q55488']  | {'railway station in City of Edinburgh, Scotla... | {'en': ['Currie railway station']}                | ... | NaN            | NaN         |
| 1 | Q5597551    | Grassington & Threshfield railway station | ['Q55488']  | set()                                             | {'en': ['Grassington & Threshfield railway sta... | ... | NaN            | NaN         |
| 2 | Q5597568    | Grassmoor railway station                 | ['Q55488']  | set()                                             | {'en': ['Grassmoor railway station']}             | ... | NaN            | NaN         |
| 3 | Q5599719    | Great Ormesby railway station             | ['Q55488']  | set()                                             | {'en': ['Great Ormesby railway station']}         | ... | NaN            | NaN         |
| 4 | Q5601497    | Greatstone-on-Sea Halt railway station    | ['Q55488']  | set()                                             | {'en': ['Greatstone-on-Sea Halt railway statio... | ... | NaN            | NaN         |


## Processing Wikidata candidates

The [wikidata_candidate_processing.ipynb](https://github.com/Living-with-machines/PlaceLinking/blob/fuzzy_matching/wikidata/wikidata_candidate_processing.ipynb) notebook takes `british_isles.csv` as input, and produces two outputs:
* An altname-centric British Wikidata gazetteer: `../toponym_matching/gazetteers/britwikidata_gazetteer.pkl`
* The corresponding candidates (aka unique altnames) input file for candidate ranker: `../toponym_matching/gazetteers/britwikidata_candidates.txt`

The notebook also produces the following two outputs:
* An altname-centric British Wikidata gazetteer with only railway stations: `../toponym_matching/gazetteers/stnwikidata_gazetteer.pkl`
* The corresponding candidates (aka unique altnames) input file for candidate ranker: `../toponym_matching/gazetteers/stnwikidata_candidates.txt`