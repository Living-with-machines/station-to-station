**TO DO:** Change link to provided resources (from onedrive to zenodo)!

# Processed

This directory keeps all processed files and resources used in our experiments.

## Download files from Zenodo

Since we cannot share the original `.docx` from which we have created the processed and parsed version of Quick's _Chronology_, we instead share the structured version (and derived data) of the dataset (resulting from running the code in `station-to-station/quicks/`), that we use in our experiments. You can download the files from [here](https://thealanturininstitute-my.sharepoint.com/:u:/g/personal/mcollardanuy_turing_ac_uk/EapaANpL-XBKk9CYrXBD7_ABEPypzWAlhGMhiJyBM_p9uA?e=o1ykq9).

Please download the compressed file `processed.zip` and unzip it, so the following directories hang directly from the `processed/` folder:
* `deezymatch/`
* `quicks/`
* `ranklib/`
* `resolution/`
* `wikidata/`

Only the `quicks/` directory should contain files.

This is the file structure **before** running any experiments:
```
station-to-station/
├── ...
├── processed/
│   ├── README.md
│   ├── deezymatch/
│   ├── quicks/
│   │   ├── quicks_altname_dev.tsv
│   │   ├── quicks_altname_test.tsv
│   │   ├── quicks_dev.tsv
│   │   └── quicks_test.tsv
│   ├── ranklib/
│   ├── resolution/
│   └── wikidata/
└── ...
```

The remaining folders will be filled by running the code and experiments, as explained in [the main README](https://github.com/Living-with-machines/station-to-station/blob/master/README.md).
