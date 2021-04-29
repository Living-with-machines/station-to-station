# Resources

This file lists the external data required to run the experiments. They are divided into the following directories:
* `deezymatch`
* `geonames`
* [`geoshapefiles`](#geoshapefiles)
* `quicks`
* [`wikidata`](#wikidata)

[TODO] Add instructions on how to obtain the required resources.

### Wikidata

* Download a full [Wikidata dump](https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2) and store the downloaded `bz2` file in `station-to-station/resources/wikidata/`. We have used the `21-Apr-2021 23:42` version in our experiments.

### Geonames

* Download the [GB table](http://download.geonames.org/export/dump/GB.zip), and store the unzipped file (`GB.txt`) in `station-to-station/resources/geonames/`. We have used the `2021-04-26 09:01` version in our experiments.
* Download the [alternateNameV2 table](http://download.geonames.org/export/dump/alternateNamesV2.zip), and store the unzipped files (`alternateNamesV2.txt` and `iso-languagecodes.txt`) in `station-to-station/resources/geonames/`. We have used the `2021-04-26 09:11` version in our experiments.

### Geoshapefiles

* Download the Boundary-Line™ ESRI Shapefile from https://osdatahub.os.uk/downloads/open/BoundaryLine (see [licence](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)). Unzip it and copy `bdline_essh_gb/Data/GB/european_region_region.shp` to the `geoshapefiles/` folder.