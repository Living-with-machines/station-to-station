# Process Quick's railway guide

This dataset is a chronology of railway stations in Great Britain containing information on opening and closing dates, companies operating at the stations, railway lines, alternate names, station types, etc.

The pdf is available [online](https://rchs.org.uk/wp-content/uploads/2020/09/Railway-Passenger-Stations-v5.02.pdf) and a docx file is available upon request (stored [here](https://lwmincomingquicks.blob.core.windows.net/quicks/quick.docx) for internal use within LwM).

We have manually cropped section 4 out of the Word document and created a new Word document with it, making sure we keep the same format. The resulting Word document has 433 pages and is stored [here](https://lwmincomingquicks.blob.core.windows.net/quicks/quick_section4.docx), for internal LwM use.

In the README and code we assume the Quick's Section 4 Word document is stored in `PlaceLinking/resources/quicks/` under the name `quick_section4.docx`.

Notebook `process_railway_stations.ipynb` reads the Quick's Section 4 Word document and identifies main stations, substations, and their description.

It returns a dataframe with the following columns:

|   | MainId | MainStation          | SubId | SubStation           | Description                                       | SubStFormatted         |
|---|--------|----------------------|-------|----------------------|---------------------------------------------------|------------------------|
| 0 | 1      | ABBEY                | 1     | A TOWN               | [NB] op 3 September 1856** as A; TOWN added 18... | ABBEY TOWN             |
| 1 | 1      | ABBEY                | 2     | A JUNCTION           | [Cal] op 31 August 1870 (co ½ T 26 September)...  | ABBEY JUNCTION         |
| 2 | 1      | ABBEY                | 3     | A JUNCTION           | [NB] op 8 August 1870 (D&C 14) ; clo 1 Septem...  | ABBEY JUNCTION         |
| 3 | 2      | ABBEY & WEST DEREHAM | 0     | ABBEY & WEST DEREHAM | [GE] op 1 August 1882 (Thetford & Watton Times... | ABBEY AND WEST DEREHAM |
| 4 | 3      | ABBEY FOREGATE       | 0     | ABBEY FOREGATE       | – see SHREWSBURY.                                 | ABBEY FOREGATE         |

Column description:
* **MainId:** Main station ID (autoincremental)
* **MainStation:** Name of main station
* **SubId:** Substation ID (complements MainID)
* **SubStation:** Name of the substation as appears in Quick's (often abbreviated, e.g. "A TOWN" for "ABBEY TOWN")
* **Description:** Text that accompanies a station or substation
* **SubStFormatted:** String-formatted name of the substation.

It also returns two `.txt` files with the queries prepared in the format required by DeezyMatch:
* `PlaceLinking/toponym_matching/toponyms/quicks_mainst_queries` formats the main station names as queries.
* `PlaceLinking/toponym_matching/toponyms/quicks_subst_queries` formats the substation names as queries.
