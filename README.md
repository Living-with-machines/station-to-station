<div align="center">
    <h1>Station to Station:<br>
        Linking and enriching historical British railway data</h1>
 
<p align="center">
    <a href="https://github.com/Living-with-machines/station-to-station/blob/master/LICENSE">
        <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg">
    </a>
    <br/>
</p>
</div>

This repository provides underlying code and materials for the paper `Station to Station: Linking and enriching historical British railway data`.

## Table of contents

This is the main directory for Place Linking experiments, which contains:
* `resources/`: folder where required data and resources are stored.
* `processed/`: folder where processed data and resources are stored.
* `quick/`: parsing and processing of Quick's _Chronology_.
* `wikidata`: processing of Wikidata, to be used in linking experiments.
* `wikipediaprocessing`: processing of Wikipedia, to be used in linking experiments.
* `toponym_matching`: scripts to create the DeezyMatch datasets and models.
* `toponym_resolution`: where toponym resolution happens.

## Installation

## Directory structure

**[TO DO: Update]**

To reproduce this experiment:

1. Process the Quicks dataset ([readme](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/quick/README.md) and [notebook](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/quick/process_railway_stations.ipynb)). This step will output:
    * `quick/outputs/quicks_processed.pkl` and `quick/outputs/quicks_processed.tsv`: structured Quick's dataset.
    * `quick/outputs/quicks_parsed.pkl` and `quick/outputs/quicks_parsed.tsv`: structured Quick's dataset with regex-parsed descriptions.
    * `toponym_matching/toponyms/quicks_mainst_queries.txt`: Quick's main entries formatted as queries for DeezyMatch.
    * `toponym_matching/toponyms/quicks_subst_queries.txt`: Quick's sub entries formatted as queries for DeezyMatch.
    * `toponym_matching/toponyms/quicks_altnames_queries.txt`: Quick's altnames formatted as queries for DeezyMatch.
    
2. Process Wikidata ([readme](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/wikidata/README.md), [script](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/wikidata/entity_extraction.py), and [notebook](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/wikidata/wikidata_candidate_processing.ipynb)). This step will output:
    * `wikidata/british_isles.csv`: a subset of Wikidata, containing entities that are located either in the United Kingdom or Ireland.
    * An altname-centric British Wikidata gazetteer: `toponym_matching/gazetteers/britwikidata_gazetteer.pkl`
    * An altname-centric British Wikidata gazetteer with only railway stations: `toponym_matching/gazetteers/stnwikidata_gazetteer.pkl`
    * And the corresponding candidates (aka unique altnames) input file for DeezyMatch's candidate ranker: `toponym_matching/gazetteers/britwikidata_candidates.txt` and `toponym_matching/gazetteers/stnwikidata_candidates.txt`.
    
3. Run DeezyMatch to obtain candidates for queries ([readme](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/toponym_matching/README.md) and [script](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/toponym_matching/candidate_selection_quicks_wikidata.py)). This step runs four different DeezyMatch scenarios, query/candidate rankings are stored in `toponym_matching/ranker_results/`:
    * Quick's main entries as queries; Wikidata British railway station gazetteer entries as candidates.
    * Quick's sub entries as queries; Wikidata British railway station gazetteer entries as candidates.
    * Quick's alternate names as queries; Wikidata British railway station gazetteer entries as candidates.
    * Quick's main entries as queries; Wikidata British full gazetteer entries as candidates.
    
4. Find Wikidata candidates for Quick's queries ([notebook](https://github.com/Living-with-machines/PlaceLinking/blob/quicks_wiki_alignment/toponym_resolution/quicks_wikidata/quicks_to_wikidata_candrank.ipynb)). This notebook returns a dataframe with the structured Quick's dataset with the best Wikidata candidates for each entry.

## Datasets and resources

All produced datasets and resources (including the DeezyMatch models) can be found in Zenodo [here](**TODO add link**).

## Evaluation results

## Citation

Please acknowledge our work if you use the code or derived data in your work, by citing:

```
Kaspar Beelen, Mariona Coll Ardanuy, Jon Lawrence, Katherine McDonough, Federico Nanni, Joshua Rhodes, Giorgia Tolfo, and Daniel CS Wilson. "Station to Station: linking and enriching historical British railway data." In XXXXXX (XXXX), pp. XXX--XXX. 2021.
```

```
@inproceedings{lwm-station-to-station-2021,
    title = "Station to Station: linking and enriching historical British railway data",
    author = "Beelen, Kaspar and
      Coll Ardanuy, Mariona and
      Lawrence, Jon and
      McDonough, Katherine and
      Nanni, Federico and
      Rhodes, Joshua and
      Tolfo, Giorgia and
      Wilson, Daniel CS",
    booktitle = "XXXXXXXXXXX",
    year = "2021",
    address = "XXXXXXX",
    publisher = "XXXXXXX",
    url = "XXXXXXX",
    pages = "XXX--XXX",
}
```

#### Author contributions
In the paper, authors are listed in alphabetical order. The following are sorted by amount of contribution and, if equal, alphabetically:
* **Conceptualization:** KM, JL, DW
* **Methodology:** MCA, FN, KB
* **Implementation:** MCA, FN, KB, GT
* **Reprodducibility:** FN, MCA
* **Historical Analysis:** KB, KM, JL, JR, DW
* **Data Acquisition and Curation:** MCA, GT, FN, DW
* **Annotation:** JL KM
* **Project Management:** MCA
* **Writing and Editing:** all authors
 
## Acknowledgements

We thank Ted Cheers and the Railway and Canal Historical Society for sharing the OOXML-formatted _Railway Passenger Stations in Great Britain: a Chronology_ byMichael Quick. Work for this paper was produced as part of Living with Machines. This project, funded by the UK Research and Innovation (UKRI) Strategic Priority Fund, is a multidisciplinary collaboration delivered by the Arts and Humanities Research Council (AHRC), with The Alan Turing Institute, the British Library and the Universities of Cambridge, East Anglia, Exeter, and Queen Mary University of London.

## License

- The source code is licensed under MIT License.
- Copyright (c) 2020 The Alan Turing Institute, British Library Board, Queen Mary University of London, University of Exeter, University of East Anglia and University of Cambridge.
