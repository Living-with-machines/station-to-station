import pandas as pd
import zipfile
import re
import collections
from lxml import etree
import pathlib
import utils
import random


docxFileName = "../resources/quicks/quick_section4.docx"
annFileName = "../resources/quicks/annotations.tsv"


### Issue a warning if either the docx Chronology or the annotations are not available:
if not pathlib.Path(docxFileName).is_file() or not pathlib.Path(annFileName).is_file():
    print("\n***WARNING:***\n\nOne of the following files does not exist:")
    print("* " + docxFileName)
    print("* " + annFileName)
    print("\nThis script will be skipped. Make sure you follow the instructions in\nhttps://github.com/Living-with-machines/station-to-station/blob/master/resources/README.md\nto make sure you have the files required to be able to run the linking experiments.")
    print()
    
### Otherwise, process and parse the docx file.
else:
    docxZip = zipfile.ZipFile(docxFileName)
    documentXML = docxZip.read('word/document.xml')
    et = etree.XML(documentXML)
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    pathlib.Path('../processed/quicks/').mkdir(parents=True, exist_ok=True)

    ### Find main stations
    mainstation = ""
    lowerstation = ""
    dText = dict()
    counter = 0
    for i, para in enumerate(et.xpath('//w:p', namespaces=ns)):
        text = para.xpath('./w:r/w:t', namespaces=ns)
        description = " ".join([t.text for t in text])
        mainstation, counter = utils.is_mainst(para, mainstation, counter, ns)
        description = description.lstrip('\x01').strip()
        if description:
            if (counter, mainstation) in dText:
                dText[(counter, mainstation)].append(description)
            else:
                description = re.sub('^(' + re.escape(mainstation) + ')', '\1', description).lstrip('\x01').strip()
                description = re.sub(r" +", " ", description).lstrip('\x01').strip()
                if description:
                    dText[(counter, mainstation)] = [description]

    ### Index main stations
    dStations = collections.OrderedDict(dText)

    indices = []
    stations = []
    descriptions = []
    for k in dStations:
        indices.append(k[0])
        stations.append(k[1])
        descriptions.append(dStations[k])

    stationdf = pd.DataFrame(columns=["Index", "Station", "Description"])
    stationdf["Index"] = indices
    stationdf["Station"] = stations
    stationdf["Description"] = descriptions
    stationdf = stationdf.set_index("Index")

    ### Detect substations
    stations = pd.DataFrame(columns=['station','type','description'])
    cols = ['MainId', 'MainStation', 'SubId', 'SubStation', 'Description']
    lst = []
    subInd = 0
    for i, row in stationdf.iterrows():
        main_station = row["Station"]
        description = row["Description"]
        dSubstations, subInd = utils.process_decription(main_station, description, subInd)
        for ss in dSubstations:
            lst.append([i, main_station, ss[0], ss[1], dSubstations[ss]])
    subsdf = pd.DataFrame(lst, columns=cols)

    ### Renaming abbreviated substations
    subsdf['SubStFormatted'] = subsdf.apply(lambda row: utils.subst_rename(row["MainStation"], row["SubStation"]), axis = 1)
    subsdf = subsdf[["MainId", "SubId", "MainStation", "SubStation", "SubStFormatted", "Description"]]
    subsdf.to_pickle('../processed/quicks/quicks_processed.pkl')

    ### Find disambiguators and companies
    parsedf = subsdf.copy()
    parsedf[['Disambiguator', 'Companies', 'FirstCompanyWkdt', 'AltCompaniesWkdt']] = parsedf.apply(lambda row: pd.Series(list(utils.detect_companies(row["Description"]))), axis = 1)

    ### Extract map information
    parsedf[['LocsMaps', 'LocsMapsDescr']] = parsedf.apply(lambda row: pd.Series(list(utils.detect_mapsInfo(row["Description"]))), axis = 1)

    ### Extact alternate and referenced railway stations
    parsedf[['Altnames', 'Referenced']] = parsedf.apply(lambda row: pd.Series(list(utils.detect_altnames(row["Description"], row["MainStation"], row["SubStFormatted"]))), axis = 1)

    ### Capture opening and closing dates
    parsedf[['FirstOpening', 'LastClosing', 'Interrupted']] = parsedf.apply(lambda row: pd.Series(list(utils.capture_dates(row["Description"]))), axis = 1)
    
    ### Drop description from dataframe before storing it
    parsedf = parsedf.drop(columns=["Description"])

    ### Store resulting dataframe
    parsedf.to_pickle('../processed/quicks/quicks_parsed.pkl')

    ### Create dev and test dataframes
    # **Note:** You will need to have the `annotations.tsv` file in `resources`.

    annotations = pd.read_csv(annFileName, sep='\t')
    annotations = annotations[annotations["Final Wikidata ID"] != "cross_reference"]
    annotations = annotations[annotations["Final Wikidata ID"] != "parsing_error"]
    annotations = annotations[annotations["Final Wikidata ID"] != "unknown"]

    annotations = annotations.sample(frac=1, random_state=42).reset_index(drop=True)

    # Split into train and test:
    queries = list(annotations.SubId.unique()) 
    random.Random(42).shuffle(queries)
    test_cutoff = int(len(queries)*.5)
    train_q, test_q = queries[test_cutoff:],queries[:test_cutoff]
    df_dev = annotations[annotations.SubId.isin(train_q)]
    df_test = annotations[annotations.SubId.isin(test_q)]

    df_test = pd.merge(df_test, parsedf, on=["MainId", "SubId", "MainStation", "SubStation", "SubStFormatted"])
    df_dev = pd.merge(df_dev, parsedf, on=["MainId", "SubId", "MainStation", "SubStation", "SubStFormatted"])

    df_dev.to_csv('../processed/quicks/quicks_dev.tsv', sep="\t", index=False)
    df_test.to_csv('../processed/quicks/quicks_test.tsv', sep="\t", index=False)

    utils.prepare_alt_queries(df_dev, "Altname", "dev")
    utils.prepare_alt_queries(df_test, "Altname", "test")
    utils.prepare_alt_queries(parsedf, "Altname", "allquicks")