# Linking Quicks to Wikidata

The code in this folder contains the experiments to link entries in Quicks to entries in Wikidata.

Run the code in the following order:

1. `candidate_selection.py`: This script finds Wikidata candidates for the entries in Quicks. You can run different experiments, which you can specify in lines 86-100 of the code.  The output of this step is a set of dataframes stored as `.pkl` files in `../processed/resolution/`. Each file (`candranking_xxx_mattch_xxxx.pkl`) contains Wikidata candidates (and confidence score based on string similarity) for each Quicks entry, based in the experiment settings (i.e. type of candidate ranking approach and number of variations accepted).

To run this script:
```bash
python candidate_selection.py
```

2. `toponym_resolution.py`: This script takes as input the output of the previous one (i.e. the dataframes with Wikidata candidates for each Quicks entry), and tries to find the best possible matching, based on the features of both the Quicks entry and the Wikidata entry under comparison. The output of this step is:
    * A set of feature dataframes stored as `.tsv` files: there is one file `features_xxx_match_xxxx.tsv` per experiment, which stores for a given setting and for each Quicks-Wikidata candidate pair, compatibility features such as string similarity, Wikidata entry relevance, etc.
    * A set of resolution dataframes stored as `.pkl` files: there is one file `resolved_xxx_match_xxxx.pkl` per experiment, which stores for each Quicks entry the preferred resolved Wikidata ID for each one of the differernt resolution methods.

To run this script:
```bash
python toponym_resolution.py
```

3. `evaluation.ipynb`: This notebook uses the outputs of the previous two scripts to evaluate the quality of the candidate ranking methods and toponym resolution methods. It returns the evaluation tables that we provide in our paper.