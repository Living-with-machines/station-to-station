# Linking BHO to Wikidata

This section covers the folder `PlaceLinking/toponym_resolution/bho_wikidata/`.

The `prepare_bho_wd_annotations.py` script combines data previously processed elsewhere in this repository. Follow the documentation in the following folders, in this order:
* `wikidata/` to create a gazetteer from Wikidata entries that are locations, and the following files needed as input:
    * `PlaceLinking/wikidata/british_isles.csv`: A subset of the Wikidata gazetteer, containing entities that are located either in the United Kingdom or Ireland.
    * `PlaceLinking/wikidata/britwikidata_gazetteer.pkl`: An altname-centric British Wikidata gazetteer. (now located in `PlaceLinking/toponym_matching/gazetteers/`, @mcollardanuy to change location of file and paths accordingly)
    * `PlaceLinking/toponym_matching/gazetteers/britwikidata_candidates.txt`: The candidates (aka unique altnames) input file formatted for DeezyMatch candidate ranker.
* `wikipedia/` to create the content one .json file for each Wikipedia entry, where the filename is the Wikipedia title plus the `.json` extension, with path `/resources/wikipedia/extractedResources/Aspects/` (@fedenanni to add and edit this).
* `bho/` to process and structure the BHO topographical dictionaries dataset, and create the following files needed as input:
    * `PlaceLinking/toponym_matching/toponyms/bho_queries.txt`: The queries (aka toponyms in the BHO dataset) input file formatted for DeezyMatch candidate ranker.
    * `PlaceLinking/bho/bho.csv`: The BHO dataset, with one row per entry and the following columns: id, title, toponyms, contextwords, redirected, content, country, xmlfile, report_title.
* `toponym_matching` to train a DeezyMatch model (stored in `PlaceLinking/toponym_matching/models/`) and apply it to find Wikidata candidates for BHO toponyms, therefore creating a dataframe with Wikidata candidates ranked for each BHO toponyms, stored in `PlaceLinking/toponym_matching/ranker_results/`.

**To do**

- [ ] @fedenanni to edit and document code to create one file-per-wikipedia-entry resource.
- [ ] @mcollardanuy to add somewhere documentation on WikiMapper and building an index.
- [ ] @mcollardanuy to channge location of wikidata gazetteers.
- [ ] @mcollardanuy to document `prepare_bho_wd_annotations.py` well.