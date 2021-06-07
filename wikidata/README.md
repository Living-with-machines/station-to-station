# Extract and process Wikidata entities

The scripts in this folder create the Wikidata-derived gazetteers that are used to link the Chronology to Wikidata.

### Table of contents

- [Entity extraction](#section-1-extracting-relevant-entities)
- [Create gazetteers](#section-2-create-gazetteers)
- [Extend altnames](#section-3-expanding-the-altnames)

### Section 1: Extracting relevant entities

Run `entity_extraction.py` to extract locations from Wikidata and relevant properties. 

This script is partially based on https://akbaritabar.netlify.app/how_to_use_a_wikidata_dump.

Before running this script, download a full Wikidata dump from [here](https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2). In this script we assume the downloaded `bz2` file is stored in `../resources/wikidata/`. You will have to uncomment the `Parse all WikiData` section (rows 372-400).

The output is in the form of `.csv` files, stored in `../resources/wikidata/extracted`, each containing 5,000 geographical entities extracted from Wikidata with the following fields (a description of each can be found in the code comments):

```
'wikidata_id', 'english_label', 'instance_of', 'description_set', 'alias_dict', 'nativelabel', 'population_dict', 'area', 'hcounties', 'date_opening', 'date_closing', 'inception_date', 'dissolved_date', 'follows', 'replaces', 'adm_regions', 'countries', 'continents', 'capital_of', 'borders', 'near_water', 'latitude', 'longitude', 'wikititle', 'geonamesIDs', 'toIDs', 'vchIDs', 'vob_placeIDs', 'vob_unitIDs', 'epns', 'os_grid_ref', 'connectswith', 'street_address', 'adjacent_stations', 'ukrailcode', 'connectline', 'connectservice', 'getty', 'heritage_designation', 'ownedby', 'postal_code', 'street_located'
```

The `feature_exploration.ipynb` notebook allows exploring Wikidata features for different query entities. It is not part of the pipeline.

### Section 2: Create gazetteers

Run `create_gazetteers.py` to create three different Wikidata gazetteers:
* Approximate UK gazetteer (point i)
* GB gazetteer (point ii)
* GB stations gazetteer (point iii)

The following subsections describe how they are created.

#### i. Create an approximate subset with entities in the UK

In this step, we create an approximate subset with those entities that are in the UK today, to have a more manageable dataset. At this stage we favour recall (we want to make sure we have all relevant entities, we will favour precision at a late point). We perform this filtering in the following manner: we keep Wikidata entities whose coordinates fall within a very-approximated coordinate boundary box enclosing the UK.

The result is stored as `../processed/wikidata/uk_approx_gazetteer.csv`. See some rows:

| id | wikidata_id | english_label            | instance_of | description_set                                   | alias_dict                                        | ... | heritage_designation | postal_code  |
|---|-------------|--------------------------|-------------|---------------------------------------------------|---------------------------------------------------|-----|----------------------|--------------|
| 0 | Q63607865   | Kilberry Head            | ['Q185113'] | {'cape in Argyll and Bute, Scotland'}             | {'en': ['Kilberry Head']}                         | ... | NaN                  | NaN          |
| 1 | Q63759247   | Sandhurst Memorial Park  | ['Q22698']  | {'memorial park in Sandhurst, Berkshire'}         | {'en': ['Sandhurst Memorial Park']}               | ... | NaN                  | NaN          |
| 2 | Q63781193   | Currie railway station   | ['Q55488']  | {'railway station in City of Edinburgh, Scotla... | {'en': ['Currie railway station']}                | ... | NaN                  | NaN          |
| 3 | Q63859929   | Stannington War Memorial | ['Q575759'] | {'war memorial in Stannington, Sheffield, Sout... | {'en': ['Stannington War Memorial']}              | ... | Q15700834            | NaN          |
| 4 | Q63860920   | 2 Darnley Road           | ['Q3947']   | {'house in Leeds'}                                | {'en-gb': ['2 Darnley Road'], 'en': ['2 Darnle... | ... | NaN                  | ['LS16 5JF'] |

#### ii. Create a the GB subset

This step creates a strict GB gazetteer using a GB shapefile: Boundary-Line™ ESRI Shapefile from https://osdatahub.os.uk/downloads/open/BoundaryLine (licence: http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) (we assume it is stored in `../resources/geoshapefiles/`), by filtering out all locations that are not contained within the polygons described in the shapefile.

The result is stored as `../processed/wikidata/gb_gazetteer.csv`.

#### iii. Create an approximate subset with GB station entities

In this step, we create a further subset of those entries in the UK that are either instances of station-related classes (manually identified) or their English label has the words `station`, `stop`, or `halt`, not preceded by typical non-railway station stations such as 'police', 'signal', 'power', 'lifeboat', 'pumping', or 'transmitting'.

The result is stored as `../processed/wikidata/gb_stations_gazetteer.csv`. See some sample rows:

| id | wikidata_id | english_label                             | instance_of | description_set                                   | alias_dict                                        | ... | street_located | postal_code |
|---|-------------|-------------------------------------------|-------------|---------------------------------------------------|---------------------------------------------------|-----|----------------|-------------|
| 0 | Q63781193   | Currie railway station                    | ['Q55488']  | {'railway station in City of Edinburgh, Scotla... | {'en': ['Currie railway station']}                | ... | NaN            | NaN         |
| 1 | Q5597551    | Grassington & Threshfield railway station | ['Q55488']  | set()                                             | {'en': ['Grassington & Threshfield railway sta... | ... | NaN            | NaN         |
| 2 | Q5597568    | Grassmoor railway station                 | ['Q55488']  | set()                                             | {'en': ['Grassmoor railway station']}             | ... | NaN            | NaN         |
| 3 | Q5599719    | Great Ormesby railway station             | ['Q55488']  | set()                                             | {'en': ['Great Ormesby railway station']}         | ... | NaN            | NaN         |
| 4 | Q5601497    | Greatstone-on-Sea Halt railway station    | ['Q55488']  | set()                                             | {'en': ['Greatstone-on-Sea Halt railway statio... | ... | NaN            | NaN         |


### Section 3: Expanding the altnames

Run `extend_altnames.py` to extend the altnames of the GB gazetteer and the GB stations gazetteer, and to create altname-centric gazetteers (i.e. instead of WikidataID-centric).

The altnames come from the following sources:
* Wikidata `alias_dict`, `english_label`, and `native_label` fields.
* Geonames alternate names.

This results in two different dataframes, one for the GB gazetteer (stored in `../processed/wikidata/altname_gb_gazetteer.pkl`) and one for the GB stations gazetteer (stored in `../processed/wikidata/altname_gb_stations_gazetteer.pkl`).

See some rows of the GB stations altnames-centric gazetteer:

|    | wkid      | altname                                   | source         | lat       | lon       |
|----|-----------|-------------------------------------------|----------------|-----------|-----------|
| 40 | Q2031838  | Wainfleet railway station                 | english_label  | 53.105000 | 0.235000  |
| 41 | Q7796688  | Thorpe Culvert Railway Station            | geonames       | 53.123031 | 0.199369  |
| 42 | Q7796688  | Thorpe Culvert railway station            | english_label  | 53.123031 | 0.199369  |
| 43 | Q7616289  | Stickney railway station                  | english_label  | 53.098800 | 0.004540  |
| 44 | Q4723950  | Sutterton                                 | wikidata_alias | 52.890700 | -0.083389 |