**TO DO:** Change link to provided resources (from onedrive to zenodo)!

# Resources

Several external resources have been employed in our experiments.

## Download resources from Zenodo

Many of the resources we use for our experiments can be downloaded from [here](https://thealanturininstitute-my.sharepoint.com/:u:/g/personal/mcollardanuy_turing_ac_uk/Ecmzmb2pwolKuFQMMbjYcWQBN3kYoXB2xRgZdRCP2ZVyEQ?e=eAadQH).

Download the compressed file `resources.zip` and unzip it, so the following directories hang directly from the main `resources/` folder:
* `deezymatch/`
* `geonames/`
* `geoshapefiles/`
* `quicks/`
* `ranklib/`
* `wikidata/`
* `wikigaz/`
* `wikipedia/`

You will realize that some of the directories will be empty. This is because we cannot share all the resources we used in our experiments. Please follow the instructions below to obtain the remaining files and store them in the right location.

## Obtain remaining resources

### Geonames

Download the [GB table](http://download.geonames.org/export/dump/GB.zip), and store the unzipped file (`GB.txt`) in the `geonames/` folder. We have used the `2021-04-26 09:01` version in our experiments.

Download the [alternateNameV2 table](http://download.geonames.org/export/dump/alternateNamesV2.zip), and store the unzipped files (`alternateNamesV2.txt` and `iso-languagecodes.txt`) in the `geonames/` folder. We have used the `2021-04-26 09:11` version in our experiments.

### Geoshapefiles

Download the Boundary-Line™ ESRI Shapefile from https://osdatahub.os.uk/downloads/open/BoundaryLine (see [licence](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)). Unzip it and copy the following files under the `geoshapefiles/` folder:
* `european_region_region.dbf`
* `european_region_region.prj`
* `european_region_region.shp`
* `european_region_region.shx`

### Ranklib

Download the Ranklib `.jar` file from the Lemur project [RankLib page](https://sourceforge.net/p/lemur/wiki/RankLib/) and store it in `ranklib/`. In our experiments, we have used version 2.13, available [here](https://sourceforge.net/projects/lemur/files/lemur/RankLib-2.13/). If this is not available anymore, we would suggest that you get the most recent binary [from here](https://sourceforge.net/projects/lemur/files/lemur/).

### Wikidata

Download a full Wikidata dump from [here](https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2) and store the `latest-all.json.bz2` file in `wikidata/`.

## Resources file structure

After following the steps above, you should have the following file structure:
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
│   │   ├── european_region_region.dbf
│   │   ├── european_region_region.prj
│   │   ├── european_region_region.shp
│   │   └── european_region_region.shx
│   ├── quicks/
│   │   ├── annotations.tsv
│   │   ├── companies.tsv
│   │   └── index2map.tsv
│   ├── ranklib/
│   │   ├── features.txt
│   │   └── RankLib-2.13.jar
│   ├── README.md
│   ├── wikidata/
│   │   └── latest-all.json.bz2
│   ├── wikigaz/
│   │   └── wikigaz_en_basic.pkl
│   └── wikipedia/
│       └── overall_entity_freq.pickle
└── ...
```

### Information about the resources we shared

#### DeezyMatch

DeezyMatch input and vocabulary files have been obtained from [its github repository](https://github.com/Living-with-machines/DeezyMatch/).

#### Quicks

We are providing the following manually derived datasets used for parsing Quick's _Chronology_:
* `annotations.tsv`: this file contains the manual annotations performed by experts in our team.
* `companies.tsv`: this file is also manually curated; it links companies (free-text strings) identified in the _Chronology_ to their Wikidata ID.
* `index2map.tsv`: this file contains the mapping between the _Chronology_ map id and the places represented in the maps (obtained from an appendix in the _Chronology_).

_Note:_ Additionally, the code in `station-to-station/quicks` assumes that `quick_section4.docx` (i.e. the relevant chapter of the original `.docx`) is also located in this folder. You will not need this to run the experiments.

#### Wikigaz

We share a minimal version of the English WikiGazetteer (`wikigaz_en_basic.pkl`), obtained from the [Zenodo repository](https://zenodo.org/record/4034819#.YL8m8TZKi-8) of the following paper (see its [Github respository](https://github.com/Living-with-machines/LwM_SIGSPATIAL2020_ToponymMatching) as well):
```
Mariona Coll Ardanuy, Kasra Hosseini, Katherine McDonough, Amrey Krause, Daniel van Strien, and Federico Nanni. "A Deep Learning Approach to Geographical Candidate Selection through Toponym Matching." arxiv:2009.08114. 2020.
```

You can generate the complete WikiGazetteer from scratch following the instructions [here](https://github.com/Living-with-machines/lwm_GIR19_resolving_places/tree/master/gazetteer_construction) and obtain the minimal version used in our experiments by running the code [here](https://github.com/Living-with-machines/LwM_SIGSPATIAL2020_ToponymMatching/blob/master/processing/gazetteers/generate_wikigazetteers.ipynb).

#### Wikipedia 

We share a pickled `Counter` object (`overall_entity_freq.pickle`) that maps Wikipedia pages to the number of inlinks (e.g. `Archway, London` has 64 inlinks and `London` has 75678 inlinks), a common measure of entity relevance.

You can generate this table by following our code to process a Wikipedia dump from scratch, extracting and structuring pages, mention/entity statistics and in- /out-link information, following the instructions [here](https://github.com/fedenanni/Reimplementing-TagMe).
