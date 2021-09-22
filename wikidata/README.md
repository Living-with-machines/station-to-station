# Extract and process Wikidata entities

The scripts in this folder create the Wikidata-derived gazetteers that are used to link Quick's _Chronology_ to Wikidata.

### Table of contents

- [Summary of steps](#summary-of-steps)
- [Description of steps](#description-of-steps)
  - [Section 1: Extracting relevant entities](#section-1-extracting-relevant-entities)
  - [Section 2: Create gazetteers](#section-2-create-gazetteers)
  - [Section 3: Expanding the altnames](#section-3-expanding-the-altnames)

### Summary of steps

Run the code in the following order (from the `wikidata/` directory):

1. Extract all location entries from a Wikidata dump (uncomment the `Parse all WikiData` section, i.e. rows 372-400. Warning: this step takes about 2 full days). See [here](#section-1-extracting-relevant-entities) for more information:

```bash
python entity_extraction.py
```

2. Create the Wikidata gazetteers. See [here](#section-2-create-gazetteers) for more information:

```bash
python create_gazetteers.py
```

3. Expand the alternate names. See [here](#section-3-expanding-the-altnames) for more information:

```bash
python extend_altnames.py
```

:warning: Make sure you have obtained the relevant resources described in the [resources readme](https://github.com/Living-with-machines/station-to-station/blob/main/resources.md).


### Description of steps

The following sections provide further information on each of the steps.


#### Section 1: Extracting relevant entities

Script `entity_extraction.py` extracts locations from Wikidata (and their relevant properties).

This script is partially based on https://akbaritabar.netlify.app/how_to_use_a_wikidata_dump.

This script assumes that you have already downloaded a full Wikidata dump from [here](https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2) (as described in the [resources readme](https://github.com/Living-with-machines/station-to-station/blob/main/resources.md#wikidata)). We assume the downloaded `bz2` file is stored under `station-to-station/resources/wikidata/`.

Before running the script, you will have to uncomment the `Parse all WikiData` section (rows 372-400). Beware that this step will take about 2 full days.

The output is in the form of `.csv` files that will be created under `../resources/wikidata/extracted/`, each containing 5,000 rows corresponding to geographical entities extracted from Wikidata with the following fields (corresponding to wikidata properties, e.g. `P7959` for [historical county](https://www.wikidata.org/wiki/Property:P7959); a description of each can be found as comments in the [code](https://github.com/Living-with-machines/station-to-station/blob/main/wikidata/entity_extraction.py#L37-L335), ):

```
'wikidata_id', 'english_label', 'instance_of', 'description_set', 'alias_dict', 'nativelabel', 'population_dict', 'area', 'hcounties', 'date_opening', 'date_closing', 'inception_date', 'dissolved_date', 'follows', 'replaces', 'adm_regions', 'countries', 'continents', 'capital_of', 'borders', 'near_water', 'latitude', 'longitude', 'wikititle', 'geonamesIDs', 'toIDs', 'vchIDs', 'vob_placeIDs', 'vob_unitIDs', 'epns', 'os_grid_ref', 'connectswith', 'street_address', 'adjacent_stations', 'ukrailcode', 'connectline', 'connectservice', 'getty', 'heritage_designation', 'ownedby', 'postal_code', 'street_located'
```

The `feature_exploration.ipynb` notebook will allow you to explore Wikidata entries and their features for specific Wikidata records. It is not part of the pipeline.


#### Section 2: Create gazetteers

Run `create_gazetteers.py` to create different Wikidata gazetteers.

This will create three different gazetteers:
* Approximate UK gazetteer (point i)
* GB gazetteer (point ii)
* GB stations gazetteer (point iii)

The following subsections describe how they are created.

##### i. Create an approximate subset with entities in the UK

In this step, we create an approximate subset of those entities that are in the UK today, to have a more manageable dataset. At this stage we favour recall (we want to make sure all relevant entities are there, at the expense of precision; we will favour precision at a late point). We perform this filtering in the following manner: we keep Wikidata entities whose coordinates fall within a very-approximated coordinate boundary box enclosing the UK.

The result is stored as `../processed/wikidata/uk_approx_gazetteer.csv`.

##### ii. Create a the GB subset

This step creates a strict GB gazetteer using a GB shapefile (the [resources readme](https://github.com/Living-with-machines/station-to-station/blob/main/resources.md#geoshapefiles) describes how to obtain it), by filtering out all locations that are not contained within the polygons described in the shapefile.

The result is stored as `../processed/wikidata/gb_gazetteer.csv`.

##### iii. Create an approximate subset with GB station entities

In this step, we create a further subset of those entries in the UK that are either instances of station-related classes (manually specified, see the full list [here](https://github.com/Living-with-machines/station-to-station/blob/main/wikidata/create_gazetteers.py#L118-L122)) or their English label has the words `station`, `stop`, or `halt`, not preceded by typical non-railway station stations such as 'police', 'signal', 'power', 'lifeboat', 'pumping', or 'transmitting'.

The result is stored as `../processed/wikidata/gb_stations_gazetteer.csv`.


#### Section 3: Expanding the altnames

Run `extend_altnames.py` to extend the altnames of the GB gazetteer and the GB stations gazetteer, and to create altname-centric gazetteers (i.e. instead of WikidataID-centric).

The altnames come from the following sources:
* Wikidata `alias_dict`, `english_label`, and `native_label` fields.
* Geonames alternate names.
* WikiGazetteer alternate names.

This process results in two different dataframes:
* `../processed/wikidata/altname_gb_gazetteer.tsv` is the expanded altname-centric version of `gb_gazetteer`,
* `../processed/wikidata/altname_gb_stations_gazetteer.tsv` is the altname-centric version of `gb_stations_gazetteer`.

See some rows of the GB stations altnames-centric gazetteer:

|    | wkid      | altname                                   | source         | lat       | lon       |
|----|-----------|-------------------------------------------|----------------|-----------|-----------|
| 29 | Q23070582 | Conway Marsh railway station              | english_label  | 53.286861 | -3.85256  |
| 30 | Q23070582 | Conway Morfa railway station              | wikigaz        | 53.286861 | -3.85256  |
| 31 | Q2178092  | Deganwy Railway Station                   | geonames       | 53.295000 | -3.83300  |
| 32 | Q2178092  | Deganwy station                           | wikigaz        | 53.295000 | -3.83300  |