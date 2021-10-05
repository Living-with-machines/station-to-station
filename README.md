<div align="center">
    <h1>Station to Station:<br>
        Linking and Enriching Historical British Railway Data</h1>
 
<p align="center">
    <a href="https://github.com/Living-with-machines/station-to-station/blob/main/LICENSE">
        <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg">
    </a>
    <br/>
</p>
</div>

This repository provides underlying code and materials for the paper _'Station to Station: Linking and Enriching Historical British Railway Data'_.

The **StopsGB** dataset is available on the British Library research repository via https://doi.org/10.23636/wvva-3d67.

Table of contents
--------------------

- [Installation and setup](#installation)
- [Directory structure](#directory-structure)
- [Content overview](#content-overview)
- [Citation](#citation)
- [Acknowledgements](#acknowledgements)
- [License](#license)


## Installation

* We recommend installation via Anaconda. Refer to [Anaconda website and follow the instructions](https://docs.anaconda.com/anaconda/install/).

* Create a new environment:

```bash
conda create -n py39station python=3.9
```

* Activate the environment:

```bash
conda activate py39station
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

* Install python-levenshtein separately with conda:

```bash
conda install -c conda-forge python-levenshtein
```

* To allow the newly created `py39station` environment to show up in the notebooks, run:

```bash
python -m ipykernel install --user --name py39station --display-name "Python (py39station)"
```

## Directory structure

Our code assumes the following directory structure:

```bash
station-to-station/
├── processed/
│   ├── deezymatch/
│   ├── quicks/
│   ├── ranklib/
│   ├── resolution/
│   └── wikidata/
├── resources/
│   ├── deezymatch/
│   ├── geonames/
│   ├── geoshapefiles/
│   ├── quicks/
│   ├── ranklib/
│   ├── wikidata/
│   ├── wikigaz/
│   └── wikipedia/
├── quicks/
├── wikidata/
├── deezymatch/
└── linking/
    └── tools/
```

## Content overview

This is a summary of the contents of each folder:

* Resources, inputs and outputs:
    * `resources/`: folder where resources required to run the experiments are stored.
    * `processed/`: folder where processed data, resources, and results are stored.
* Processing code:
    * `quick/`: code for parsing and processing Quick's _Chronology_.
    * `wikidata`: code for processing Wikidata, to be used in the linking experiments.
    * `deezymatch`: code to create the DeezyMatch datasets and models used for linking.
* Linking code:
    * `linking`: code for reproducing the experiments and for linking StopsGB to Wikidata.

### Option 1: Reproducing the experiments

To run the linking experiments, follow the instructions in this order:
1. Prepare the resources → [resources readme](https://github.com/Living-with-machines/station-to-station/blob/main/resources.md).
2. Process Wikidata → [Wikidata readme](https://github.com/Living-with-machines/station-to-station/blob/main/wikidata/README.md).
3. Create DeezyMatch datasets and models → [DeezyMatch readme](https://github.com/Living-with-machines/station-to-station/blob/main/deezymatch/README.md).
4. Reproduce the linking experiments → [Readme: reproduce linking experiments](https://github.com/Living-with-machines/station-to-station/blob/main/linking/README_reproduce_experiments.md).
    
### Option 2: Creating StopsGB from scratch

:warning: You will only be able to create StopsGB from scratch if you have a copy of the MS Word version of _Railway Passenger Stations in Great Britain: a Chronology_ by Michael Quick.

To create the full `StopsGB`, follow the instructions in this order:
1. Prepare the `resources` folder → [resources readme](https://github.com/Living-with-machines/station-to-station/blob/main/resources.md).
2. Process Wikidata → [Wikidata readme](https://github.com/Living-with-machines/station-to-station/blob/main/wikidata/README.md).
3. Create DeezyMatch datasets and models → [DeezyMatch readme](https://github.com/Living-with-machines/station-to-station/blob/main/deezymatch/README.md).
4. Process Quick's Chronology into StopsGB → [Quicks readme](https://github.com/Living-with-machines/station-to-station/blob/main/quicks/README.md).
5. Resolve and georeference StopsGB → [Readme: create StopsGB](https://github.com/Living-with-machines/station-to-station/blob/main/linking/README_create_StopsGB.md).

## Citation

Please acknowledge our work if you use the code or derived data, by citing:

```
Mariona Coll Ardanuy, Kaspar Beelen, Jon Lawrence, Katherine McDonough, Federico Nanni, Joshua Rhodes, Giorgia Tolfo, and Daniel C.S. Wilson. "Station to Station: Linking and Enriching Historical British Railway Data." In Computational Humanities Research (CHR2021). 2021.
```

```bibtex
@inproceedings{lwm-station-to-station-2021,
    title = "Station to Station: Linking and Enriching Historical British Railway Data",
    author = "Coll Ardanuy, Mariona and
      Beelen, Kaspar and
      Lawrence, Jon and
      McDonough, Katherine and
      Nanni, Federico and
      Rhodes, Joshua and
      Tolfo, Giorgia and
      Wilson, Daniel CS",
    booktitle = "Computational Humanities Research",
    year = "2021",
}
```

#### Author contributions

* _Conceptualization:_ Katherine McDonough, Jon Lawrence and Daniel C. S. Wilson.
* _Methodology:_ Mariona Coll Ardanuy, Federico Nanni and Kaspar Beelen.
* _Implementation:_ Mariona Coll Ardanuy, Federico Nanni, Kaspar Beelen and Giorgia Tolfo.
* _Reproducibility:_ Federico Nanni and Mariona Coll Ardanuy.
* _Historical Analysis:_ Kaspar Beelen, Katherine McDonough, Jon Lawrence, Joshua Rhodes and Daniel C. S. Wilson.
* _Data Acquisition and Curation:_ Daniel C. S. Wilson, Mariona Coll Ardanuy, Giorgia Tolfo and Federico Nanni.
* _Annotation:_ Jon Lawrence and Katherine McDonough.
* _Project Management:_ Mariona Coll Ardanuy.
* _Writing and Editing:_ all authors.
 
## Acknowledgements

Original data from _Railway Passenger Stations in Great Britain: a Chronology_ by Michael Quick. Used with permission from The Railway and Canal Historical Society ©.

Work for this paper was produced as part of Living with Machines. This project, funded by the UK Research and Innovation (UKRI) Strategic Priority Fund, is a multidisciplinary collaboration delivered by the Arts and Humanities Research Council (AHRC), with The Alan Turing Institute, the British Library and the Universities of Cambridge, East Anglia, Exeter, and Queen Mary University of London.

## License

The source code is licensed under MIT License.

Copyright © 2021 The Alan Turing Institute, British Library Board, Queen Mary University of London, University of Exeter, University of East Anglia and University of Cambridge.
