# Create a linked version of StopsGB

We assume you have followed the instructions described in the main [Readme](https://github.com/Living-with-machines/station-to-station/tree/44-improve-documentation#creating-stopsgb-from-scratch) file in order to create the StopsGB dataset from scratch. If you have, you will only need to run the following script (warning: it will take several hours):

```bash
python apply_to_all_stations.py
```

This will perform the whole linking pipeline (finding candidates with DeezyMatch, retrieving features for each candidate, and outputing the final dataset). The resulting dataset (stored as `station-to-station/processed/resolution/StopsGB.tsv`) is also available on the [British Library research repository](https://doi.org/10.23636/wvva-3d67).