import pandas as pd
import geopandas as gpd
import shapefile
from shapely.geometry import shape, Point
import pyproj
from pathlib import Path
import ast
import re


# ====================================================
# Create an approximate subset with entities in the UK
# ====================================================

print("\nCreating the approximate UK gazetteer.")

if not Path("../processed/wikidata/uk_approx_gazetteer.csv").exists():
    path = r"../resources/wikidata/extracted/"
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    all_files = glob.glob(path + "/*.csv")

    li = []
    for filename in all_files:
        df_temp = pd.read_csv(filename, index_col=None, header=0)
        li.append(df_temp)

    df = pd.concat(li, axis=0, ignore_index=True)
    df = df.drop(columns=['Unnamed: 0'])

    def filter_uk(lat, lon, countries):
        bbox = (-9.05,48.78,2.41,61.28)
        countries = ast.literal_eval(countries)
        for c in countries:
            if c == "Q145": # United Kingdom
                return True
            if c == "Q142" or c == "Q31" or c == "Q27": # France and Belgium and Ireland
                return False
        if float(lat) >= bbox[1] and float(lat) <= bbox[3] and float(lon) >= bbox[0] and float(lon) <= bbox[2]:
            return True
        else:
            return False

    mask = df.apply(lambda x: filter_uk(x['latitude'], x['longitude'], x['countries']), axis=1)
    ukdf = df[mask]
    ukdf['latitude'] = ukdf['latitude'].astype(float)
    ukdf['longitude'] = ukdf['longitude'].astype(float)
    ukdf = ukdf[ukdf['latitude'].notna()]
    ukdf = ukdf[ukdf['longitude'].notna()]
    ukdf.to_csv("../processed/wikidata/uk_approx_gazetteer.csv", index=False)


# =======================================
# Create generic GB gazetteer
# =======================================

print("\nCreating the GB gazetteer.")

# Load the approximate UK gazetteer
gbdf = pd.read_csv("../processed/wikidata/uk_approx_gazetteer.csv", header=0, index_col=None, low_memory=False)

# Load Great Britain shapefile:
# Boundary-Line™ ESRI Shapefile from https://osdatahub.os.uk/downloads/open/BoundaryLine (licence: http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
shapefile = gpd.read_file("../resources/geoshapefiles/european_region_region.shp")

# Set coordinate system converter:
bng=pyproj.Proj('epsg:27700')
wgs84 = pyproj.Proj('epsg:4326')
transformer = pyproj.Transformer.from_crs('epsg:4326', 'epsg:27700')

# Convert coordinates from Wikidata to OSGB 1936 system (British National Grid, United Kingdom Ordnance Survey)
# Reference: http://epsg.io/27700
print("* Transforming Wikidata coordinates to OSGB 1936 system.")
gbdf["geometry"] = gbdf.apply(lambda x: Point(transformer.transform(x["latitude"], x["longitude"])), axis=1)
geodf = gpd.GeoDataFrame(gbdf).set_crs(epsg=27700)

# Inner merge if a location is contained in one of the shapefile polygons (i.e. if a
# location is in Great Britain):
print("* Filtering out loctions not in GB.")
data_merged_inner = gpd.sjoin(shapefile, geodf, how="inner", op='contains')
cols = data_merged_inner.columns.tolist()
cols = cols[16:] # Drop shapefile columns
data_merged_inner = data_merged_inner[cols]
data_merged_inner = data_merged_inner.reset_index()
data_merged_inner = data_merged_inner.drop(columns = ["index_right", "index"])

# Store GB gazetteer:
data_merged_inner.to_csv("../processed/wikidata/gb_gazetteer.csv", index=False)


# ====================================================================
# Create a subset with station entities in GB
# ====================================================================

print("\nCreating the GB stations gazetteer.")

gbdf = pd.read_csv("../processed/wikidata/gb_gazetteer.csv", header=0, index_col=None, low_memory=False)

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

for i, row in gbdf.iterrows():
    if type(row["instance_of"]) == str and type(row["english_label"]) == str:
        wkdtcl = ast.literal_eval(row["instance_of"])
        if any(x in wkdtcl for x in stn_wkdt_classes) or (re.match(re_station, row["english_label"]) and not re.match(re_nostation, row["english_label"])):
            stationgaz = stationgaz.append(row, ignore_index=True)

stationgaz.to_csv("../processed/wikidata/gb_stations_gazetteer.csv", index=False)