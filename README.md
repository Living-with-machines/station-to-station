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

Table of contents
--------------------

- [Installation and setup](#installation)
- [Description of directories](#directory-structure)
- [Content overview](#content-overview)
- [Datasets and resources](#datasets-and-resources)

## Directory structure

Our code relies on the following directory structure:

```bash
station-to-station/
├── processed/
│   ├── deezymatch/
│   ├── quicks/
│   ├── resolution/
│   └── wikidata/
├── resources/
│   ├── deezymatch/
│   ├── geonames/
│   ├── geoshapefiles/
│   ├── quicks/
│   ├── wikidata/
│   ├── wikigaz/
│   └── wikipedia/
├── quicks/
├── wikidata/
├── toponym_matching/
└── toponym_resolution/
    ├── supervised_ranking/
    │   ├── feature_files/
    │   └── models/
    └── tools/
```

## Installation

* We recommend installation via Anaconda. Refer to [Anaconda website and follow the instructions](https://docs.anaconda.com/anaconda/install/).

* Create a new environment:

```bash
conda create -n py37station python=3.7
```

* Activate the environment:

```bash
conda activate py37station
```

* Clone the repository:

```bash
git clone https://github.com/Living-with-machines/station-to-station.git
```

* Install the requirements:

```bash
cd /path/to/my/station-to-station
pip install -r requirements.txt
```

* To allow the newly created `py37station` environment to show up in the notebooks, run:

```bash
python -m ipykernel install --user --name py37station --display-name "Python (py37station)"
```

## Content overview

* Resources, inputs and outputs:
    * `resources/`: folder where resources required to run the experiments are stored.
    * `processed/`: folder where processed data and resources are stored.
* Processing code:
    * `quick/`: code for parsing and processing Quick's _Chronology_.
    * `wikidata`: code for processing Wikidata, to be used in the linking experiments.
    * `toponym_matching`: code to create the DeezyMatch datasets and models.
* Linking code:
    * `toponym_resolution`: code for linking Quick's _Chronology_ to Wikidata.
    
    
To run the experiments, follow the instructions in this order:
* Resources [README](https://github.com/Living-with-machines/station-to-station/blob/master/resources/README.md).
* Processed [README](https://github.com/Living-with-machines/station-to-station/blob/master/processed/README.md).
* Quicks [README](https://github.com/Living-with-machines/station-to-station/blob/master/quicks/README.md).
* Wikidata [README](https://github.com/Living-with-machines/station-to-station/blob/master/wikidata/README.md).
* Toponym matching [README](https://github.com/Living-with-machines/station-to-station/blob/master/toponym_matching/README.md).
* Toponym resolution [README](https://github.com/Living-with-machines/station-to-station/blob/master/toponym_resolution/README.md).


## Citation

Please acknowledge our work if you use the code or derived data, by citing:

```
Kaspar Beelen, Mariona Coll Ardanuy, Jon Lawrence, Katherine McDonough, Federico Nanni, Joshua Rhodes, Giorgia Tolfo, and Daniel CS Wilson. "Station to Station: linking and enriching historical British railway data." In XXXXXX (XXXX), pp. XXX--XXX. 2021.
```

```bibtex
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

Original data from _Railway Passenger Stations in Great Britain: a Chronology_ by Michael Quick. Used with permission from The Railway and Canal Historical Society ©.

Work for this paper was produced as part of Living with Machines. This project, funded by the UK Research and Innovation (UKRI) Strategic Priority Fund, is a multidisciplinary collaboration delivered by the Arts and Humanities Research Council (AHRC), with The Alan Turing Institute, the British Library and the Universities of Cambridge, East Anglia, Exeter, and Queen Mary University of London.

## License

- The source code is licensed under MIT License.
- Copyright (c) 2020 The Alan Turing Institute, British Library Board, Queen Mary University of London, University of Exeter, University of East Anglia and University of Cambridge.
