# Resources

Several external resources have been employed in our experiments.

## Table of contents

- [Resources](#resources)
  - [Table of contents](#table-of-contents)
  - [Obtaining the Resources](#obtaining-the-resources)
  - [Resources file structure](#resources-file-structure)
  - [Additional information on shared resources](#additional-information-on-shared-resources)
    - [DeezyMatch](#deezymatch)
    - [Quicks](#quicks)
    - [Wikigaz](#wikigaz)
    - [Wikipedia inlinks](#wikipedia-inlinks)


## Obtaining the Resources

Several external resources have been employed in our experiments.

This can all be automatically downloaded using the [get_resources.ipynb](get_resources.ipynb) notebook. Manual instructions for obtaining the resources are included in the notebook too.


## Resources file structure

After following the steps in the `get_resources.ipynb`, you should have the following file structure:
```
station-to-station/
├── ...
├── resources/
│   ├── deezymatch/
│   │   ├── characters_v001.vocab
│   │   └── input_dfm.yaml
│   ├── geonames/
│   │   ├── alternateNamesV2.txt
│   │   ├── GB.txt
│   │   └── iso-languagecodes.txt
│   ├── geoshapefiles/
│   │   ├── country_region.dbf
│   │   ├── country_region.prj
│   │   ├── country_region.shp
│   │   └── country_region.shx
│   ├── quicks/
│   │   ├── annotations.tsv
│   │   ├── companies.tsv
│   │   ├── index2map.tsv
│   │   ├── quicks_altname_dev.tsv
│   │   ├── quicks_altname_test.tsv
│   │   ├── quicks_dev.tsv
│   │   └── quicks_test.tsv
│   ├── ranklib/
│   │   ├── features.txt
│   │   └── RankLib-2.13.jar
│   ├── wikidata/
│   │   └── latest-all.json.bz2
│   ├── wikigaz/
│   │   └── wikigaz_en_basic.pkl
│   └── wikipedia/
│       └── overall_entity_freq.pickle
└── ...
```

## Additional information on shared resources

In this section, we provide additional information on the resources that we share via Zenodo.

### DeezyMatch

The DeezyMatch input file and vocabulary file have been adapted from the original files (which can be found in the [DeezyMatch github repository](https://github.com/Living-with-machines/DeezyMatch/)).

### Quicks

We are providing the following datasets used for the experiments on parsing the _Chronology_ and linking it to Wikidata:
* `annotations.tsv`: this file contains the manual annotations performed by experts in our team.
* `companies.tsv`: this file is also manually curated; it links companies (free-text strings) identified in the _Chronology_ to their Wikidata ID.
* `index2map.tsv`: this file contains the mapping between the _Chronology_ map id and the places represented in the maps (manually obtained from an appendix in the _Chronology_).
* `quicks_dev.tsv`: the development set, consisting of 217 entries from the _Chronology_ that have been parsed and manually annotated with the corresponding Wikidata entry ID (obtained from running the [code to parse the _Chronology_ document](https://github.com/Living-with-machines/station-to-station/tree/main/quicks)).
* `quicks_test.tsv`: the test set, consisting of 219 entries from the _Chronology_ that have been parsed and manually annotated with the corresponding Wikidata entry ID (obtained from running the [code to parse the _Chronology_ document](https://github.com/Living-with-machines/station-to-station/tree/main/quicks)).
* `quicks_altname_dev.tsv`: Additional alternate names found in the _Chronology_ for the entries in `quicks_dev.tsv` (obtained from running the [code to parse the _Chronology_ document](https://github.com/Living-with-machines/station-to-station/tree/main/quicks)).
* `quicks_altname_test.tsv`: Additional alternate names found in the _Chronology_ for the entries in `quicks_test.tsv` (obtained from running the [code to parse the _Chronology_ document](https://github.com/Living-with-machines/station-to-station/tree/main/quicks)).

### Wikigaz

We share a minimal version of the English WikiGazetteer (`wikigaz_en_basic.pkl`). You can generate the complete WikiGazetteer from scratch following the instructions [here](https://github.com/Living-with-machines/lwm_GIR19_resolving_places/tree/master/gazetteer_construction) and obtain the minimal version used in our experiments by running the code [here](https://github.com/Living-with-machines/LwM_SIGSPATIAL2020_ToponymMatching/blob/master/processing/gazetteers/generate_wikigazetteers.ipynb).

### Wikipedia inlinks

We share a pickled `Counter` object (`overall_entity_freq.pickle`) that maps Wikipedia pages to the number of inlinks (e.g. `Archway, London` has 64 inlinks and `London` has 75678 inlinks), a common measure of entity relevance.

You can generate this table by following our code to process a Wikipedia dump from scratch, extracting and structuring pages, mention/entity statistics and in- /out-link information, following the instructions [here](https://github.com/fedenanni/Reimplementing-TagMe).
