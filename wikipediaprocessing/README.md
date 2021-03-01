The scripts here process a Wikipedia dump, extracting and structuring pages, mention/entity statistics and in- /out-link information.


### 1. Pre-process a Wikipedia Dump

First, download a Wikipedia dump from [here](https://dumps.wikimedia.org/enwiki/) (we used enwiki-20200920) and process it with the [WikiExtractor](http://medialab.di.unipi.it/wiki/Wikipedia_Extractor) with the following command:

```
python python WikiExtractor.py -l -s -o processedWiki/ [here put the path to the Wikipedia Dump .xml.bz2]
```
Note that the flag -s will keep the sections and the flag -l the links.

### Extract entity, mention and ngram frequencies + sections

Having the Wiki dump processed by the WikiExtractor in the "processedWiki/" folder, the first step is to collect a set of all entity-mentions in Wikipedia, so that you can later collect their frequency as ngrams. You can do this by using 
```
1-CollectAllMentions.py 
```
that will produce a all_mentions.pickle file. 

The second step will extract mention, ngrams and entity counts as well as mention_to_entities statistics (e.g., how many times the mention "Obama" is pointing to "Barack_Obama" and how many times to "Michele_Obama"). Statistics are still divided in the n-folders consituting the output of the WikiExtractor and will be saved in the "Store-Counts/" folder as json files. The script will also store a .json file for each entity, with all its aspects (i.e., sections, see [here](https://madoc.bib.uni-mannheim.de/49596/1/EAL.pdf) to know more about Entity-Aspect Linking). 
```
2-ExtractingFreqAndPages.py
```

The final pre-processing script will aggregate all counts in single .pickle files and save them in the "Resources/" folder. You can do this by running:
```
3-AggregateCounts.py
```
Note that after having processed each json from "Store-Counts/", the script will save an intermediate count in "extractedResources/".
