# Process Quick's railway guide

Michael Quick's _Railway Passenger Stations in Great Britain: A Chronology_ (_Quicks_ dataset for short) contains detailed information on railway stations in Great Britain, such as on opening and closing dates, companies operating at the stations, railway lines, alternate names, etc.

The pdf is available [online](https://rchs.org.uk/wp-content/uploads/2020/09/Railway-Passenger-Stations-v5.02.pdf) and a docx file is available upon request.

We have manually cropped section 4 out of the Word document and created a new Word document with it, making sure we keep the same format. The resulting Word document has 433 pages and is stored in `station-to-station/resources/quicks/` under the name `quick_section4.docx`.

The python notebook `process_railway_stations.ipynb` reads the Quick's Section 4 Word document and identifies main stations, substations, and their description.

It returns a dataframe `../processed/quicks/quicks_processed.pkl` with the following columns:

|   | MainId | MainStation          | SubId | SubStation           | Description                                       | SubStFormatted         |
|---|--------|----------------------|-------|----------------------|---------------------------------------------------|------------------------|
| 0 | 1      | ABBEY                | 1     | A TOWN               | [NB] op 3 September 1856** as A; TOWN added 18... | ABBEY TOWN             |
| 1 | 1      | ABBEY                | 2     | A JUNCTION           | [Cal] op 31 August 1870 (co ½ T 26 September)...  | ABBEY JUNCTION         |
| 2 | 1      | ABBEY                | 3     | A JUNCTION           | [NB] op 8 August 1870 (D&C 14) ; clo 1 Septem...  | ABBEY JUNCTION         |
| 3 | 2      | ABBEY & WEST DEREHAM | 4     | ABBEY & WEST DEREHAM | [GE] op 1 August 1882 (Thetford & Watton Times... | ABBEY AND WEST DEREHAM |
| 4 | 3      | ABBEY FOREGATE       | 5     | ABBEY FOREGATE       | – see SHREWSBURY.                                 | ABBEY FOREGATE         |

Column description:
* **MainId:** Main station ID
* **MainStation:** Name of main station
* **SubId:** Substation ID
* **SubStation:** Name of the substation as appears in Quick's (often abbreviated, e.g. "A TOWN" for "ABBEY TOWN")
* **Description:** Text that accompanies a station or substation
* **SubStFormatted:** String-formatted name of the substation.

Besides, the notebook uses regular expressions on the Description to extract information on disambiguators (e.g. "near London") and railway companies (e.g. "[LY]" for `Lancashire and Yorkshire Railway`), map location information (e.g. "{Saffron Walden - Ashdon}" or "{map 16}"), alternate names (e.g. "GRAHAMSTON" for Barrhead), cross-referenced stations (e.g. "HEREFORD" for Barrs Court Junction), and opening and closing dates. This expanded dataset is stored as `../processed/quicks/quicks_parsed.pkl`.

Finally, we create `dev` and `test` dataframes from manually annotated entries (i.e. Quicks entries manually annotated to Wikidata IDs). The resulting dataframes are stored as `../processed/quicks/quicks_dev.pkl` and `../processed/quicks/quicks_test.pkl`.
