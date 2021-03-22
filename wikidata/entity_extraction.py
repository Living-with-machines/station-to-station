import bz2
import json
import glob
import pandas as pd
import pydash
import ast
from tqdm import tqdm
import pathlib
import re
from pathlib import Path

# Disable chained assignments
pd.options.mode.chained_assignment = None

languages = ['en', 'cy', 'sco', 'gd', 'ga', 'kw']


# ==========================================
# Process bz2 wikidata dump
# ==========================================
def wikidata(filename):
    with bz2.open(filename, mode='rt') as f:
        f.read(2) # skip first two bytes: "{\n"
        for line in f:
            try:
                yield json.loads(line.rstrip(',\n'))
            except json.decoder.JSONDecodeError:
                continue
                

# ==========================================
# Parse wikidata entry
# ==========================================
def parse_record(record):
    # Wikidata ID:
    wikidata_id = record['id']

    # ==========================================
    # Place description and definition
    # ==========================================

    # Main label:
    english_label = pydash.get(record, 'labels.en.value')

    # Location is instance of
    instance_of_dict = pydash.get(record, 'claims.P31')
    instance_of = None
    if instance_of_dict:
        instance_of = [pydash.get(r, 'mainsnak.datavalue.value.id') for r in instance_of_dict]

    # Descriptions in English:
    description_set = set()
    descriptions = pydash.get(record, 'descriptions')
    for x in descriptions:
        if x == 'en' or x.startswith('en-'):
            description_set.add(pydash.get(descriptions[x], 'value'))

    # Aliases and labels:
    aliases = pydash.get(record, 'aliases')
    labels = pydash.get(record, 'labels')
    alias_dict = dict()
    for x in aliases:
        if x in languages or x.startswith('en-'):
            for y in aliases[x]:
                if "value" in y:
                    if not y["value"].isupper() and not y["value"].islower() and any(x.isalpha() for x in y["value"]):
                        if x in alias_dict:
                            if not y["value"] in alias_dict[x]:
                                alias_dict[x].append(y["value"])
                        else:
                            alias_dict[x] = [y["value"]]
    for x in labels:
        if x in languages or x.startswith('en-'):
            if "value" in labels[x]:
                if not labels[x]["value"].isupper() and not labels[x]["value"].islower() and any(z.isalpha() for z in labels[x]["value"]):
                    if x in alias_dict:
                        if not labels[x]["value"] in alias_dict[x]:
                            alias_dict[x].append(labels[x]["value"])
                    else:
                        alias_dict[x] = [labels[x]["value"]]

    # Native label
    nativelabel_dict = pydash.get(record, 'claims.P1705')
    nativelabel = None
    if nativelabel_dict:
        nativelabel = [pydash.get(c, 'mainsnak.datavalue.value.text') for c in nativelabel_dict]

    # ==========================================
    # Geographic and demographic information
    # ==========================================

    # Population at: dictionary of year-population pairs
    population_dump = pydash.get(record, 'claims.P1082')
    population_dict = dict()
    if population_dump:
        for ppl in population_dump:
            pop_amount = pydash.get(ppl, 'mainsnak.datavalue.value.amount')
            pop_time = pydash.get(ppl, 'qualifiers.P585[0].datavalue.value.time')
            pop_time = "UNKNOWN" if not pop_time else pop_time
            population_dict[pop_time] = pop_amount

    # Area of location
    dict_area_units = {'Q712226' : 'square kilometre',
               'Q2737347': 'square millimetre',
               'Q2489298': 'square centimetre',
               'Q35852': 'hectare',
               'Q185078': 'are',
               'Q25343': 'square metre'}

    area_loc = pydash.get(record, 'claims.P2046[0].mainsnak.datavalue.value')
    area = None
    if area_loc:
        try:
            if area_loc.get("unit"):
                area = (area_loc.get("amount"), dict_area_units.get(area_loc.get("unit").split("/")[-1]))
        except:
            area = None

    # ==========================================
    # Historical information
    # ==========================================

    # Historical counties
    hcounties_dict = pydash.get(record, 'claims.P7959')
    hcounties = []
    if hcounties_dict:
        hcounties = [pydash.get(hc, 'mainsnak.datavalue.value.id') for hc in hcounties_dict]

    # Date of official opening (e.g. https://www.wikidata.org/wiki/Q2011)
    date_opening = pydash.get(record, 'claims.P1619[0].mainsnak.datavalue.value.time')

    # Date of official closing
    date_closing = pydash.get(record, 'claims.P3999[0].mainsnak.datavalue.value.time')

    # Inception: date or point in time when the subject came into existence as defined
    inception_date = pydash.get(record, 'claims.P571[0].mainsnak.datavalue.value.time')

    # Dissolved, abolished or demolished: point in time at which the subject ceased to exist
    dissolved_date = pydash.get(record, 'claims.P576[0].mainsnak.datavalue.value.time')

    # Follows...: immediately prior item in a series of which the subject is a part: e.g. Vanuatu follows New Hebrides
    follows_dict = pydash.get(record, 'claims.P155')
    follows = []
    if follows_dict:
        for f in follows_dict:
            follows.append(pydash.get(f, 'mainsnak.datavalue.value.id'))

    # Replaces...: item replaced: e.g. New Hebrides is replaced by 
    replaces_dict = pydash.get(record, 'claims.P1365')
    replaces = []
    if replaces_dict:
        for r in replaces_dict:
            replaces.append(pydash.get(r, 'mainsnak.datavalue.value.id'))

    # Heritage designation
    heritage_designation = pydash.get(record, 'claims.P1435[0].mainsnak.datavalue.value.id')

    # ==========================================
    # Neighbouring or part-of locations
    # ==========================================

    # Located in adminitrative territorial entities (Wikidata ID)
    adm_regions_dict = pydash.get(record, 'claims.P131')
    adm_regions = dict()
    if adm_regions_dict:
        for r in adm_regions_dict:
            regname = pydash.get(r, 'mainsnak.datavalue.value.id')
            if regname:
                entity_start_time = pydash.get(r, 'qualifiers.P580[0].datavalue.value.time')
                entity_end_time = pydash.get(r, 'qualifiers.P582[0].datavalue.value.time')
                adm_regions[regname] = (entity_start_time, entity_end_time)

    # Country: sovereign state of this item
    country_dict = pydash.get(record, 'claims.P17')
    countries = dict()
    if country_dict:
        for r in country_dict:
            countryname = pydash.get(r, 'mainsnak.datavalue.value.id')
            if countryname:
                entity_start_time = pydash.get(r, 'qualifiers.P580[0].datavalue.value.time')
                entity_end_time = pydash.get(r, 'qualifiers.P582[0].datavalue.value.time')
                countries[countryname] = (entity_start_time, entity_end_time)

    # Continents (Wikidata ID)
    continent_dict = pydash.get(record, 'claims.P30')
    continents = None
    if continent_dict:
        continents = [pydash.get(r, 'mainsnak.datavalue.value.id') for r in continent_dict]

    # Location is capital of
    capital_of_dict = pydash.get(record, 'claims.P1376')
    capital_of = None
    if capital_of_dict:
        capital_of = [pydash.get(r, 'mainsnak.datavalue.value.id') for r in capital_of_dict]

    # Shares border with:
    shares_border_dict = pydash.get(record, 'claims.P47')
    borders = []
    if shares_border_dict:
        borders = [pydash.get(t, 'mainsnak.datavalue.value.id') for t in shares_border_dict]

    # Nearby waterbodies (Wikidata ID)
    near_water_dict = pydash.get(record, 'claims.P206')
    near_water = None
    if near_water_dict:
        near_water = [pydash.get(r, 'mainsnak.datavalue.value.id') for r in near_water_dict]

    # Nearby waterbodies (Wikidata ID)
    part_of_dict = pydash.get(record, 'claims.P361')
    part_of = None
    if part_of_dict:
        part_of = [pydash.get(r, 'mainsnak.datavalue.value.id') for r in part_of_dict] 
    

    # ==========================================
    # Coordinates
    # ==========================================

    # Latitude and longitude:
    latitude = pydash.get(record, 'claims.P625[0].mainsnak.datavalue.value.latitude')
    longitude = pydash.get(record, 'claims.P625[0].mainsnak.datavalue.value.longitude')
    if latitude and longitude:
        latitude = round(latitude, 6)
        longitude = round(longitude, 6)

    # ==========================================
    # External data resources IDs
    # ==========================================

    # English Wikipedia title:
    wikititle = pydash.get(record, 'sitelinks.enwiki.title')

    # Geonames ID
    geonamesID_dict = pydash.get(record, 'claims.P1566')
    geonamesIDs = None
    if geonamesID_dict:
        geonamesIDs = [pydash.get(gn, 'mainsnak.datavalue.value') for gn in geonamesID_dict]

    # TOID: TOpographic IDentifier assigned by the Ordnance Survey to identify a feature in Great Britain
    toID_dict = pydash.get(record, 'claims.P3120')
    toIDs = None
    if toID_dict:
        toIDs = [pydash.get(t, 'mainsnak.datavalue.value') for t in toID_dict]

    # British History Online VCH ID: identifier of a place, in the British History Online digitisation of the Victoria County History
    vchID_dict = pydash.get(record, 'claims.P3628')
    vchIDs = None
    if vchID_dict:
        vchIDs = [pydash.get(t, 'mainsnak.datavalue.value') for t in vchID_dict]

    # Vision of Britain place ID: identifier of a place
    vob_placeID_dict = pydash.get(record, 'claims.P3616')
    vob_placeIDs = None
    if vob_placeID_dict:
        vob_placeIDs = [pydash.get(vobid, 'mainsnak.datavalue.value') for vobid in vob_placeID_dict]

    # Vision of Britain unit ID: identifier of an administrative unit
    vob_unitID_dict = pydash.get(record, 'claims.P3615')
    vob_unitIDs = None
    if vob_unitID_dict:
        vob_unitIDs = dict()
        for vobid in vob_unitID_dict:
            unit_id = pydash.get(vobid, 'mainsnak.datavalue.value')
            parish_name = pydash.get(vobid, 'qualifiers.P1810[0].datavalue.value')
            vob_unitIDs[unit_id] = parish_name

    # Identifier for a place in the Historical Gazetteer of England's Place Names website
    epns_dict = pydash.get(record, 'claims.P3627')
    epns = None
    if epns_dict:
        epns = [pydash.get(p, 'mainsnak.datavalue.value') for p in epns_dict]

    # Identifier in the Getty Thesaurus of Geographic Names
    getty_dict = pydash.get(record, 'claims.P1667')
    getty = None
    if getty_dict:
        getty = [pydash.get(p, 'mainsnak.datavalue.value') for p in getty_dict]

    # OS grid reference (Wikidata ID)
    os_grid_ref = pydash.get(record, 'claims.P613[0].mainsnak.datavalue.value')

    # ==========================================
    # Street-related properties
    # ==========================================

    # Street connects with
    connectswith_dict = pydash.get(record, 'claims.P2789')
    connectswith = None
    if connectswith_dict:
        connectswith = [pydash.get(c, 'mainsnak.datavalue.value.id') for c in connectswith_dict]

    # Street address
    street_address = pydash.get(record, 'claims.P6375[0].mainsnak.datavalue.value.text')

    # Located on street
    street_located = pydash.get(record, 'claims.P669[0].mainsnak.datavalue.value.id')

    # Postal code
    postal_code_dict = pydash.get(record, 'claims.P281')
    postal_code = None
    if postal_code_dict:
        postal_code = [pydash.get(c, 'mainsnak.datavalue.value') for c in postal_code_dict]

    # ==========================================
    # Rail-related properties
    # ==========================================

    # Adjacent stations
    adjacent_stations = None
    adj_st_dump = pydash.get(record, 'claims.P197')
    if adj_st_dump:
        adjacent_stations = [pydash.get(adj_st, 'mainsnak.datavalue.value.id') for adj_st in adj_st_dump]

    # UK railway station code
    ukrailcode_dict = pydash.get(record, 'claims.P4755')
    ukrailcode = None
    if ukrailcode_dict:
        ukrailcode = [pydash.get(ukrid, 'mainsnak.datavalue.value') for ukrid in ukrailcode_dict]

    # Connecting lines
    connectline_dict = pydash.get(record, 'claims.P81')
    connectline = None
    if connectline_dict:
        connectline = [pydash.get(conline, 'mainsnak.datavalue.value.id') for conline in connectline_dict]

    # Owned by
    ownedby_dict = pydash.get(record, 'claims.P127')
    ownedby = None
    if ownedby_dict:
        ownedby = [pydash.get(conline, 'mainsnak.datavalue.value.id') for conline in ownedby_dict]

    # Connecting service
    connectservice_dict = pydash.get(record, 'claims.P1192')
    connectservice = None
    if connectservice_dict:
        connectservice = [pydash.get(conline, 'mainsnak.datavalue.value.id') for conline in connectservice_dict]

    # ==========================================
    # Store records in a dictionary
    # ==========================================
    df_record = {'wikidata_id': wikidata_id, 'english_label': english_label,
                 'instance_of': instance_of, 'description_set': description_set,
                 'alias_dict': alias_dict, 'nativelabel': nativelabel,
                 'population_dict': population_dict, 'area': area,
                 'hcounties': hcounties, 'date_opening': date_opening,
                 'date_closing': date_closing, 'inception_date': inception_date,
                 'dissolved_date': dissolved_date, 'follows': follows,
                 'replaces': replaces, 'adm_regions': adm_regions,
                 'countries': countries, 'continents': continents,
                 'capital_of': capital_of, 'borders': borders, 'near_water': near_water,
                 'latitude': latitude, 'longitude': longitude, 'wikititle': wikititle,
                 'geonamesIDs': geonamesIDs, 'toIDs': toIDs, 'vchIDs': vchIDs,
                 'vob_placeIDs': vob_placeIDs, 'vob_unitIDs': vob_unitIDs,
                 'epns': epns, 'os_grid_ref': os_grid_ref, 'connectswith': connectswith,
                 'street_address': street_address, 'adjacent_stations': adjacent_stations,
                 'ukrailcode': ukrailcode, 'connectline': connectline,
                 'heritage_designation': heritage_designation, 'getty': getty,
                 'street_located': street_located, 'postal_code': postal_code,
                 'ownedby': ownedby, 'connectservice': connectservice
                }
    return df_record


# ==========================================
# Parse all WikiData
# ==========================================

### Uncomment the following to run this script (WARNING: This will take days to run, 40 hours on a machine with 64GiB of RAM):

# path = r"../resources/wikidata/extracted/"
# pathlib.Path(path).mkdir(parents=True, exist_ok=True)

# df_record_all = pd.DataFrame(columns=['wikidata_id', 'english_label', 'instance_of', 'description_set', 'alias_dict', 'nativelabel', 'population_dict', 'area', 'hcounties', 'date_opening', 'date_closing', 'inception_date', 'dissolved_date', 'follows', 'replaces', 'adm_regions', 'countries', 'continents', 'capital_of', 'borders', 'near_water', 'latitude', 'longitude', 'wikititle', 'geonamesIDs', 'toIDs', 'vchIDs', 'vob_placeIDs', 'vob_unitIDs', 'epns', 'os_grid_ref', 'connectswith', 'street_address', 'adjacent_stations', 'ukrailcode', 'connectline', 'heritage_designation', 'getty', 'street_located', 'postal_code', 'ownedby', 'connectservice'])

# header=True
# i = 0
# for record in tqdm(wikidata('/resources/wikidata/latest-all.json.bz2')):
    
#     # Only extract items with geographical coordinates (P625)
#     if pydash.has(record, 'claims.P625'):
        
#         # ==========================================
#         # Store records in a csv
#         # ==========================================
#         df_record = parse_record(record)
#         df_record_all = df_record_all.append(df_record, ignore_index=True)
#         i += 1
#         if (i % 5000 == 0):
#             pd.DataFrame.to_csv(df_record_all, path_or_buf=path + '/till_'+record['id']+'_item.csv')
#             print('i = '+str(i)+' item '+record['id']+'  Done!')
#             print('CSV exported')
#             df_record_all = pd.DataFrame(columns=['wikidata_id', 'english_label', 'instance_of', 'description_set', 'alias_dict', 'nativelabel', 'population_dict', 'area', 'hcounties', 'date_opening', 'date_closing', 'inception_date', 'dissolved_date', 'follows', 'replaces', 'adm_regions', 'countries', 'continents', 'capital_of', 'borders', 'near_water', 'latitude', 'longitude', 'wikititle', 'geonamesIDs', 'toIDs', 'vchIDs', 'vob_placeIDs', 'vob_unitIDs', 'epns', 'os_grid_ref', 'connectswith', 'street_address', 'adjacent_stations', 'ukrailcode', 'connectline'])
#         else:
#             continue
            
# pd.DataFrame.to_csv(df_record_all, path_or_buf=path + 'final_csv_till_'+record['id']+'_item.csv')
# print('i = '+str(i)+' item '+record['id']+'  Done!')
# print('All items finished, final CSV exported!')


# ====================================================
# Create an approximate subset with entities from the British Isles
# ====================================================

print("\nCreating the British Isles gazetteer.")

if not Path("../resources/wikidata/british_isles_gazetteer.csv").exists():
    path = r"../resources/wikidata/extracted/"
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    all_files = glob.glob(path + "/*.csv")

    li = []
    for filename in all_files:
        df_temp = pd.read_csv(filename, index_col=None, header=0)
        li.append(df_temp)

    df = pd.concat(li, axis=0, ignore_index=True)
    df = df.drop(columns=['Unnamed: 0'])

    def filter_britisles(lat, lon, countries):
        bbox = (-11.31,48.78,2.41,61.28)
        countries = ast.literal_eval(countries)
        for c in countries:
            if c == "Q145" or c == "Q27": # United Kingdom and Ireland
                return True
            if c == "Q142" or c == "Q31": # France and Belgium
                return False
        if float(lat) >= bbox[1] and float(lat) <= bbox[3] and float(lon) >= bbox[0] and float(lon) <= bbox[2]:
            return True
        else:
            return False

    mask = df.apply(lambda x: filter_britisles(x['latitude'], x['longitude'], x['countries']), axis=1)
    britdf = df[mask]
    britdf['latitude'] = britdf['latitude'].astype(float)
    britdf['longitude'] = britdf['longitude'].astype(float)
    britdf = britdf[britdf['latitude'].notna()]
    britdf = britdf[britdf['longitude'].notna()]
    britdf.to_csv("../resources/wikidata/british_isles_gazetteer.csv", index=False)


# ====================================================
# Create an approximate subset with railway station entities from the British Isles
# ====================================================

print("Done.\n\nCreating the British Isles stations gazetteer.")

britdf = pd.read_csv("../resources/wikidata/british_isles_gazetteer.csv", header=0, index_col=None, low_memory=False)

# From: https://docs.google.com/spreadsheets/d/1sREU_TKBU0HXoSSm7nyOw-4kId_bfu6OTEXxtdZeLl0/edit#gid=0
stn_wkdt_classes = ["Q55488", "Q4663385", "Q55491", "Q18516630", "Q1335652", "Q28109487",
                    "Q55678", "Q1567913", "Q39917125", "Q11424045", "Q14562709", "Q27020748",
                    "Q22808403", "Q85641138", "Q928830", "Q1339195", "Q27030992", "Q55485",
                    "Q17158079", "Q55493", "Q325358", "Q168565", "Q18543139", "Q11606300",
                    "Q2175765", "Q2298537", "Q19563580"]

# Most railway stations end with "railway station" in Wikidata.
re_station = r"(.*)\b(([Hh]alt)|([Ss]top)|([Ss]tation))((\, .*)|( \(.*))?$"

# Most common non-railway stations in Wikidata:
re_nostation = r".*\b(([Pp]olice [Ss]tation)|([Rr]elay [Ss]tation)|([Ff]ire [Ss]tation)|([Gg]enerating [Ss]tation)|([Ss]ignal [Ss]tation)|([Pp]ower [Ss]tation)|([Ll]ifeboat [Ss]tation)|([Pp]umping [Ss]tation)|([Tt]ransmitting [Ss]tation)|([Bb]us [Ss]tation)|([Cc]oach [Ss]tation)|([Ff]ishing [Ss]tation)).*$"

stationgaz = pd.DataFrame(columns=['wikidata_id', 'english_label', 'instance_of', 'description_set', 'alias_dict', 'nativelabel', 'population_dict', 'area', 'hcounties', 'date_opening', 'date_closing', 'inception_date', 'dissolved_date', 'follows', 'replaces', 'adm_regions', 'countries', 'continents', 'capital_of', 'borders', 'near_water', 'latitude', 'longitude', 'wikititle', 'geonamesIDs', 'toIDs', 'vchIDs', 'vob_placeIDs', 'vob_unitIDs', 'epns', 'os_grid_ref', 'connectswith', 'street_address', 'adjacent_stations', 'ukrailcode', 'connectline', 'heritage_designation', 'getty', 'street_located', 'postal_code', 'ownedby', 'connectservice'])

for i, row in tqdm(britdf.iterrows()):
    if type(row["instance_of"]) == str and type(row["english_label"]) == str:
        wkdtcl = ast.literal_eval(row["instance_of"])
        if any(x in wkdtcl for x in stn_wkdt_classes) or (re.match(re_station, row["english_label"]) and not re.match(re_nostation, row["english_label"])):
            stationgaz = stationgaz.append(row, ignore_index=True)

stationgaz.to_csv("../resources/wikidata/british_isles_stations_gazetteer.csv", index=False)