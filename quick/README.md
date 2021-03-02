# Process Quick's railway guide

Michael Quick's _Railway Passenger Stations in Great Britain: A Chronology_ (_Quicks_ dataset for short) contains detailed information on railway stations in Great Britain, such as on opening and closing dates, companies operating at the stations, railway lines, alternate names, etc.

The pdf is available [online](https://rchs.org.uk/wp-content/uploads/2020/09/Railway-Passenger-Stations-v5.02.pdf) and a docx file is available upon request (stored [here](https://lwmincomingquicks.blob.core.windows.net/quicks/quick.docx) for internal use within LwM).

We have manually cropped section 4 out of the Word document and created a new Word document with it, making sure we keep the same format. The resulting Word document has 433 pages and is stored [here](https://lwmincomingquicks.blob.core.windows.net/quicks/quick_section4.docx), for internal LwM use. In the README and code we assume the Quick's Section 4 Word document is stored in `PlaceLinking/resources/quicks/` under the name `quick_section4.docx` (this is its location on _ToponymVM_).

Notebook `process_railway_stations.ipynb` reads the Quick's Section 4 Word document and identifies main stations, substations, and their description.

It returns a dataframe `outputs/quicks_processed.pkl` (and `outputs/quicks_processed.tsv`) with the following columns:

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

It also returns two `.txt` files with the queries prepared in the format required by DeezyMatch:
* `PlaceLinking/toponym_matching/toponyms/quicks_mainst_queries` formats the main station names as queries.
* `PlaceLinking/toponym_matching/toponyms/quicks_subst_queries` formats the substation names as queries.

Besides, the notebook uses regular expressions and other text matching functions on the Description, to extract information on disambiguators (e.g. "near London") and railway companies (e.g. "[LY]" for Lancashire and Yorkshire Railway), map location information (e.g. "{Saffron Walden - Ashdon}" or "{map 16}"), alternate names (e.g. "GRAHAMSTON" for Barrhead), cross-referenced stations (e.g. "HEREFORD" for Barrs Court Junction), and opening and closing dates. This expanded dataset is stored as `outputs/quicks_parsed.tsv` and `outputs/quicks_parsed.pkl`.

The alternate names are prepared in the format required by DeezyMatch as well, as `PlaceLinking/toponym_matching/toponyms/quicks_altnames_queries`.