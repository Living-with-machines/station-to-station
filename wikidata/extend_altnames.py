import pandas as pd
import glob

from collections import Counter
from  itertools import chain
import pydash
import ast
import re
from pathlib import Path
from wikimapper import WikiMapper
import wget

import numpy as np

from tqdm.notebook import trange, tqdm

### --------------------------------------------
### Load British Isles gazetteer
### --------------------------------------------

# The british_isles_gazetteer.csv file is an output from entity_extraction.py, which is stored in ../resources/wikidata/.
print("Loading the British Isles gazetteer.")
britdf = pd.read_csv("../resources/wikidata/british_isles_gazetteer.csv", header=0, index_col=None, low_memory=False)


### --------------------------------------------
### Load British Isles stations gazetteer
### --------------------------------------------

# The british_isles_gazetteer.csv file is an output from entity_extraction.py, which is stored in ../resources/wikidata/.
print("\nLoading the British Isles stations gazetteer.")
stationdf = pd.read_csv("../resources/wikidata/british_isles_stations_gazetteer.csv", header=0, index_col=None, low_memory=False)


### --------------------------------------------
### Process English WikiGazetteer altnames
### --------------------------------------------

# The English WikiGazetteer can be downloaded from https://zenodo.org/record/4034819/: download the .zip. The only file we will need is 'wikigaz_en_basic.pkl', which should be stored in ../resources/wikigaz/.
print("\nCreating the English WikiGazetteer altnames dataframe.")

if not Path("../resources/wikigaz/wikigaz_altnames.pkl").exists():
    wikigaz_path = "/resources/wikigazetteer/wikigaz_en_basic.pkl"
    wikigaz_en = pd.read_pickle(wikigaz_path)

    # Filter entries if in British Isles boundary box and altname source is either wikimain or wikiredirect.
    bbox = (-11.31,48.78,2.41,61.28)
    wikigaz_en = wikigaz_en[(wikigaz_en["lat"] >= bbox[1]) & (wikigaz_en["lat"] <= bbox[3]) & (wikigaz_en["lon"] >= bbox[0]) & (wikigaz_en["lon"] <= bbox[2])]
    wikigaz_en = wikigaz_en[wikigaz_en["source"].isin(["wikimain", "wikiredirect"])]

    wikigaz_altnames = wikigaz_en[["pid", "altname"]]
    wikigaz_altnames = wikigaz_altnames.drop_duplicates(subset=["pid", "altname"], ignore_index = True)
    wikigaz_altnames.to_pickle("../resources/wikigaz/wikigaz_altnames.pkl")
    
wikigaz_altnames = pd.read_pickle("../resources/wikigaz/wikigaz_altnames.pkl")
        
    
### --------------------------------------------
### Process geonames altnames
### --------------------------------------------

# We need to download the following files from geonames:
# * http://download.geonames.org/export/dump/IE.zip
# * http://download.geonames.org/export/dump/GB.zip
# * http://download.geonames.org/export/dump/alternateNamesV2.zip
#
# Unzip the files, and make sure the following files should be stored in ../resources/geonames/:
# * alternateNamesV2.txt
# * GB.txt
# * IE.txt

print("\nProcessing geonames altnames.")

if not Path("../resources/geonames/geonames_altnames.pkl").exists():
    geoaltnames = pd.read_csv("../resources/geonames/alternateNamesV2.txt", sep="\t", names=["alternateNameId", "geonameid", "isolanguage", "alternateName", "isPreferredName", "isShortName", "isColloquial", "isHistoric", "from", "to"], index_col=None, low_memory=False)

    # Filter out alternate names that are actually pseudocodes:
    gn_pseudocodes = ["post", "link", "iata", "icao",
                      "faac", "tcid", "unlc", "abbr",
                      "wkdt", "phon", "piny", "fr_1793"] # Geonames pseucodes from here: https://www.geonames.org/manual.html

    geoaltnames = geoaltnames[~geoaltnames["isolanguage"].isin(gn_pseudocodes)]

    # Filter by languages native to the British Isles or with strong influence in toponymy:
    # gd: Scottish Gaelic
    # kw: Cornish
    # sco: Scots
    # cy: Welsh
    # ga: Irish
    # en: English
    # gv: Manx
    # br: Breton
    # fr: French
    # la: Latin
    gn_toplanguages = ["gd", "kw", "sco", "cy", "ga", "en", "gv", "br", "fr", "la"]
    geoaltnames = geoaltnames[(geoaltnames["isolanguage"].isin(gn_toplanguages)) | (geoaltnames["isolanguage"].isnull())]

    geoaltnames = geoaltnames.drop(columns=["alternateNameId", "isolanguage", "isPreferredName", "isShortName", "isColloquial", "isHistoric", "from", "to"])

    # Keep asciiname and alternateName from the GB database:
    gb_geonames = pd.read_csv("../resources/geonames/GB.txt", sep="\t", names=["geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude", "fclass", "fcode", "ccode", "cc2", "admin1", "admin2", "admin3", "admin4", "population", "elevation", "dem", "timezone", "moddate"], index_col=None, low_memory=False)
    gb_geonames = gb_geonames.drop(columns=["alternatenames", "latitude", "longitude", "fclass", "fcode", "ccode", "cc2", "admin1", "admin2", "admin3", "admin4", "population", "elevation", "dem", "timezone", "moddate"])
    gb_altnames = list(set(gb_geonames.groupby(['geonameid', 'name']).groups))
    gb_altnames.extend(list(set(gb_geonames.groupby(['geonameid', 'asciiname']).groups)))
    gb_altnames = list(set(gb_altnames))
    gb_geonames = pd.DataFrame(gb_altnames, columns = ["geonameid", "alternateName"])

    # Keep asciiname and alternateName from the IE database:
    ie_geonames = pd.read_csv("../resources/geonames/IE.txt", sep="\t", names=["geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude", "fclass", "fcode", "ccode", "cc2", "admin1", "admin2", "admin3", "admin4", "population", "elevation", "dem", "timezone", "moddate"], index_col=None, low_memory=False)
    ie_geonames = ie_geonames.drop(columns=["alternatenames", "latitude", "longitude", "fclass", "fcode", "ccode", "cc2", "admin1", "admin2", "admin3", "admin4", "population", "elevation", "dem", "timezone", "moddate"])
    ie_altnames = list(set(ie_geonames.groupby(['geonameid', 'name']).groups))
    ie_altnames.extend(list(set(ie_geonames.groupby(['geonameid', 'asciiname']).groups)))
    ie_altnames = list(set(ie_altnames))
    ie_geonames = pd.DataFrame(ie_altnames, columns = ["geonameid", "alternateName"])

    # Concatenate all altname dataframes and filter relevant rows:
    geonames_altnames = pd.concat([geoaltnames, gb_geonames, ie_geonames], ignore_index=True)
    geonames_altnames = geonames_altnames.drop_duplicates(ignore_index=True)

    # Filter out alternate names if they are not in Latin alphabet:
    def latin_alphabet(toponym):
        latin_range = re.compile(u'[\u0040-\u007F\u0080-\u00FF\u0100-\u017F\u0180-\u024F]', flags=re.UNICODE)
        if re.search(latin_range, toponym):
            return True
        else:
            return False

    geonames_altnames = geonames_altnames[geonames_altnames.apply(lambda x: latin_alphabet(x["alternateName"]), axis=1)]
    
    # For speed in later stage, keep only rows that have a corresponding Wikidata entry
    def parse_geonames(geoIDs):
        geonamesIDs = []
        if type(geoIDs) == str:
            geonamesIDs = ast.literal_eval(geoIDs)
            geonamesIDs = [int(gn) for gn in geonamesIDs if type(gn) == str]
        return geonamesIDs

    brit_geonameIDs = []
    for i, row in britdf.iterrows():
        tmp_gnalt = parse_geonames(row["geonamesIDs"])
        if tmp_gnalt:
            brit_geonameIDs.extend(tmp_gnalt)

    geonames_altnames = geonames_altnames[geonames_altnames["geonameid"].isin(brit_geonameIDs)]

    # Convert geonames ids to strings:
    geonames_altnames.geonameid = geonames_altnames.geonameid.astype(str)
    geonames_altnames.to_pickle("../resources/geonames/geonames_altnames.pkl")

geonames_altnames = pd.read_pickle("../resources/geonames/geonames_altnames.pkl")


### --------------------------------------------
### Create an altnames-centric gazetteer of the British Isles
### --------------------------------------------

print("\nCreating an altnames-centric gazetteer of the British Isles.")

if not Path("../resources/wikidata/altname_british_isles_gazetteer.pkl").exists():
    def obtain_altnames(elabel, aliases, nativelabel, wikipedia_title, geonamesIDs, wikigaz_altnames, geoaltnames):

        altnames = dict()
        if type(geonamesIDs) == str:
            geonamesIDs = ast.literal_eval(geonamesIDs)
            geon_altnames = set(geonames_altnames[geonames_altnames["geonameid"].isin(geonamesIDs)].alternateName.unique())
            for ga in geon_altnames:
                altnames[ga] = "geonames"

        if type(wikipedia_title) == str:
            wikipedia_title = wikipedia_title.replace(" ", "_")
            wgaz_altnames = set(wikigaz_altnames[wikigaz_altnames["pid"] == wikipedia_title].altname.unique())
            for wa in wgaz_altnames:
                altnames[wa] = "wikigaz"

        re_appo = r"(.+)(:?\(.+\)|(\,.+))$"
        if type(nativelabel) == str:
            nlabel = ast.literal_eval(nativelabel)
            for nl in nlabel:
                altnames[nl] = "native_label"

        if type(aliases) == str:
            aliases = ast.literal_eval(aliases)
            for language in aliases:
                for a in aliases[language]:
                    if re.match(re_appo, a):
                        a = re.match(re_appo, a).group(1).strip()
                        a = re.sub(",$", "", a)
                    altnames[a] = "wikidata_alias"

        if type(elabel) == str:
            if re.match(re_appo, elabel):
                elabel = re.match(re_appo, elabel).group(1).strip()
                elabel = re.sub(",$", "", elabel)
            altnames[elabel] = "english_label"

        return altnames

    # Apply to British Isles gazetteer dataframe:
    wkid = []
    altname = []
    source = []
    lat = []
    lon = []
    dAltnames = dict()

    for i, row in britdf.iterrows():
        dAltnames = obtain_altnames(row["english_label"], row["alias_dict"], row["nativelabel"], row["wikititle"], row["geonamesIDs"], wikigaz_altnames, geonames_altnames)
        for a in dAltnames:
            wkid.append(row["wikidata_id"])
            altname.append(a)
            source.append(dAltnames[a])
            lat.append(row["latitude"])
            lon.append(row["longitude"])

    wkdtgazetteer = pd.DataFrame()
    wkdtgazetteer["wkid"] = wkid
    wkdtgazetteer["altname"] = altname
    wkdtgazetteer["source"] = source
    wkdtgazetteer["lat"] = lat
    wkdtgazetteer["lon"] = lon

    wkdtgazetteer = wkdtgazetteer.drop_duplicates(subset = ['wkid', 'altname'])
    wkdtgazetteer = wkdtgazetteer[wkdtgazetteer['altname'].notna()]
    wkdtgazetteer.to_pickle("../resources/wikidata/altname_british_isles_gazetteer.pkl")
    
wkdtgazetteer = pd.read_pickle("../resources/wikidata/altname_british_isles_gazetteer.pkl")


### --------------------------------------------
### Create an altnames-centric gazetteer of the British Isles stations
### --------------------------------------------

print("\nCreating an altnames-centric gazetteer of the British Isles stations.")

wkdtgazetteer = pd.read_pickle("../resources/wikidata/altname_british_isles_gazetteer.pkl")
wkdtgazetteer_stn = wkdtgazetteer[wkdtgazetteer["wkid"].isin(stationdf["wikidata_id"])]
wkdtgazetteer_stn.to_pickle("../resources/wikidata/altname_british_isles_stations_gazetteer.pkl")

# Most railway stations end with "station" or "railway station", but Quick's guide
# takes it for granted that they are railway stations, so it just has "Currie" for "Currie
# railway station". Therefore, we add new alternate names without rail keywords.
re_station = r"(.*?)\b(:?([Rr]ailw[ae]y)|([Rr]ail)|([Uu]nderground)|([Tt]hameslink)|([Oo]verground)|([Tt]ube)|([Ss]ubway)|([Tt]rain)|([Mm]etrolink)|([Mm]etro)|([Tt]ram)|([Hh]alt)|([Hh]alt [Rr]ailw[ae]y))? ?(:?([Hh]alt)|([Ss]top)|([Ss]tation)|([Dd][Aa][Rr][Tt]))((\, .*)|( \(.*))?$"
re_nostation = r".*\b(([Pp]olice [Ss]tation)|([Rr]elay [Ss]tation)|([Ff]ire [Ss]tation)|([Gg]enerating [Ss]tation)|([Ss]ignal [Ss]tation)|([Pp]ower [Ss]tation)|([Ll]ifeboat [Ss]tation)|([Pp]umping [Ss]tation)|([Tt]ransmitting [Ss]tation)|([Bb]us [Ss]tation)|([Ff]ishing [Ss]tation)).*$"

penultimate_tokens = []
antepenultimate_tokens = []
for i, row in wkdtgazetteer_stn.iterrows():
    
    if row["source"] in ["english_label", "wikidata_alias", "native_label"] and re.match(re_station, row["altname"]) and not re.match(re_nostation, row["altname"]):
        newaltname = re.sub(re_station, r"\1", row["altname"])
#         print(row["altname"], "\t:::\t", newaltname)
        if newaltname:
            wkdtgazetteer_stn = wkdtgazetteer_stn.append(pd.Series([row["wkid"], newaltname, "processed", row["lat"], row["lon"]], index=wkdtgazetteer_stn.columns), ignore_index=True)

wkdtgazetteer_stn = wkdtgazetteer_stn.drop_duplicates(subset = ['wkid', 'altname'])
wkdtgazetteer_stn = wkdtgazetteer_stn[wkdtgazetteer_stn['altname'].notna()]
print(wkdtgazetteer_stn)

print("\nDone!")