# Resources

Several external resources have been employed in our experiments.

This README lists the external resources that are required. Most of them are already processed and stored in our Zenodo repository **[here](Add link to Zenodo)**, but not all. Follow the instructions in this document to obtain all required external datasets and resources and store them in the right location.

Resources are divided into the following directories:
* [`deezymatch`](#deezymatch)
* [`geonames`](#geonames)
* [`geoshapefiles`](#geoshapefiles)
* [`quicks`](#quicks)
* [`wikidata`](#wikidata)
* [`wikigaz`](#wikigaz)
* [`wikipedia`](#wikipedia)

### DeezyMatch

All needed files are provided in this GitHub repository, you do not need to do anything else.

### Geonames

* Download the [GB table](http://download.geonames.org/export/dump/GB.zip), and store the unzipped file (`GB.txt`) in `station-to-station/resources/geonames/`. We have used the `2021-04-26 09:01` version in our experiments.
* Download the [alternateNameV2 table](http://download.geonames.org/export/dump/alternateNamesV2.zip), and store the unzipped files (`alternateNamesV2.txt` and `iso-languagecodes.txt`) in `station-to-station/resources/geonames/`. We have used the `2021-04-26 09:11` version in our experiments.

### Geoshapefiles

* Download the Boundary-Line™ ESRI Shapefile from https://osdatahub.os.uk/downloads/open/BoundaryLine (see [licence](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)). Unzip it and copy `bdline_essh_gb/Data/GB/european_region_region.shp` to the `geoshapefiles/` folder.

### Quicks

**[TODO] Q: Can we upload the Word document? If answer is no, link to Zenodo processed files.**

### Wikidata

* Download the already processed Wikidata gazetteers (`altname_gb_gazetteer.pkl`, `altname_gb_stations_gazetteer.pkl`, `gb_gazetteer.csv`, `gb_stations_gazetteer.csv`, `uk_approx_gazetteer.csv`) from our Zenodo repository **[TODO here](Add link to Zenodo)**, and store them in `station-to-station/processed/wikidata/`.
    > **Note:** You can replicate the steps to produce the Wikidata gazetteers by running our code [to create gazetteers from Wikidata](https://github.com/Living-with-machines/station-to-station/tree/dev/wikidata).

### Wikigaz

* Download the minimal English WikiGazetteer (`wikigaz_en_basic.pkl`) from our Zenodo repository **[TODO here](Add link to Zenodo)**, and store it in `station-to-station/processed/wikigaz/`.
    > **Note:** You can generate the complete WikiGazetteer from scratch following the instructions [here](https://github.com/Living-with-machines/lwm_GIR19_resolving_places/tree/dev/gazetteer_construction) and obtain its minimal form running the code [here](https://github.com/Living-with-machines/LwM_SIGSPATIAL2020_ToponymMatching/blob/master/processing/gazetteers/generate_wikigazetteers.ipynb).

### Wikipedia

* Download the Wikipedia inlinks table (`overall_entity_freq.pickle`) from our Zenodo repository **[TODO here](Add link to Zenodo)**, and store it in `station-to-station/processed/wikipedia/`.
    > **Note:** You can generate this table by following our code to process a Wikidata dump from scratch, extracting and structuring pages, mention/entity statistics and in- /out-link information, following the instructions [here](https://github.com/Living-with-machines/station-to-station/tree/dev/wikipediaprocessing).
