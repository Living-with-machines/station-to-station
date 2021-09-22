# Process _Railway Passenger Stations in Great Britain: a Chronology_

The code in this folder parses and processes Michael Quick's book _Railway Passenger Stations in Great Britain: a Chronology_ into structured datasets to be used in the experiments.

:warning: To run this code, you will need:
* A copy of the `.docx` version of the _Chronology_.
* The resources described [here](https://github.com/Living-with-machines/station-to-station/blob/main/resources.md).

The output files from this step (needed for running the experiments) are provided in `station-to-station/resources/quicks/`.


## Description of the dataset and derived data

Michael Quick's _Railway Passenger Stations in Great Britain: A Chronology_ (Quick's _Chronology_ for short) contains detailed information on railway stations in Great Britain, such as on opening and closing dates, companies operating at the stations, railway lines, alternate names, etc.

The pdf is available [online](https://rchs.org.uk/wp-content/uploads/2020/09/Railway-Passenger-Stations-v5.02.pdf) and a docx file is available upon request to The Railway and Canal Historical Society.

We have manually cropped section 4 out of the Word document and created a new Word document with it, making sure we keep the same format. The resulting Word document has 433 pages and is stored in `station-to-station/resources/quicks/` under the name `quick_section4.docx`.

The python script `process_railway_stations.py` reads the Quick's Section 4 Word document and identifies main stations, substations, and their description.

It returns a dataframe `station-to-station/resources/quicks/quicks_processed.pkl` with the following columns:

| MainId | SubId | MainStation | SubStation | SubStFormatted                              | Description                                       |                                                   |                            |
|--------|-------|------------------------|---------------------------------------------|---------------------------------------------------|---------------------------------------------------|----------------------------|
| 1      | 1     | ABBEY                  | A TOWN                                      | ABBEY TOWN                                        | [NB] op 3 September 1856** as A; TOWN added 18... |                            |
| 1      | 2     | ABBEY                  | A JUNCTION                                  | ABBEY JUNCTION                                    | [Cal] op 31 August 1870                           | (co ½ T 26 September)...   |
| 1      | 3     | ABBEY                  | A JUNCTION                                  | ABBEY JUNCTION                                    | [NB] op 8 August 1870                             | (D&C 14) ; clo 1 Septem... |
| 2      | 4     | ABBEY & WEST DEREHAM   | ABBEY & WEST DEREHAM ABBEY AND WEST DEREHAM | [GE] op 1 August 1882 (Thetford & Watton Times... |                                                   |                            |
| 3      | 5     | ABBEY FOREGATE         | ABBEY FOREGATE                              | ABBEY FOREGATE                                    | – see SHREWSBURY.                                 |                            |

Column description:
* **MainId:** Internal autoincrement ID of the place where the station is located.
* **SubId:** Internal autoincrement ID of the station.
* **MainStation:** Name of the place where the station is located.
* **SubStation:** Name of the station as appears in the _Chronology_, i.e. abbreviated (e.g. 'A TOWN' for 'ABBEY TOWN').
* **SubStFormatted:** Automatically expanded name of the station (e.g. 'ABBEY TOWN' for 'A TOWN').
* **Description:** Text that describes a station.

The notebook then uses regular expressions on the `Description` to extract information on disambiguators (e.g. "near London") and railway companies (e.g. "[LY]" for `Lancashire and Yorkshire Railway`), map location information (e.g. "{Saffron Walden - Ashdon}" or "{map 16}"), alternate names (e.g. "GRAHAMSTON" for Barrhead), cross-referenced stations (e.g. "HEREFORD" for Barrs Court Junction), and opening and closing dates. This expanded dataset is stored as `station-to-station/resources/quicks/quicks_parsed.pkl`.

Finally, we create `dev` and `test` dataframes from manually annotated entries (i.e. Quicks entries manually annotated to Wikidata IDs). The resulting dataframes are stored as:
* `station-to-station/resources/quicks/quicks_dev.tsv`
* `station-to-station/resources/quicks/quicks_test.tsv`.

Additionally, we also extract all alternate names for the parsed files:
* `quicks_altname_allquicks.tsv`
* `quicks_altname_dev.tsv`
* `quicks_altname_test.tsv`
