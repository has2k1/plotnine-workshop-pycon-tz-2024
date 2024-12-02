import pickle
import hashlib
from pathlib import Path
from geopandas import GeoDataFrame

__all__ = [
    "country",
    "zones",
    "regions",
    "districts",
    "lakes",
    "rivers",
]

CACHE_DIR = Path('cache/')

rename_lookup = {
    "ADM0_EN" : "country",
    "ADM1_EN" : "region",
    "ADM2_EN" : "district",
    "ADM3_EN" : "yard",
}

def clean_columns(df: GeoDataFrame):
    wanted = list(rename_lookup) + ["geometry"]
    drop = df.columns.difference(wanted)
    return df.drop(columns=drop).rename(columns=rename_lookup)


def load_file(filepath: Path):
    # load from cached file and/or
    # create one after loading
    checksum = hashlib.md5(filepath.read_bytes()).hexdigest()
    cache_filename = CACHE_DIR / f"{checksum}.pkl"
    CACHE_DIR.mkdir(exist_ok=True)
    try:
        df = pickle.load(cache_filename.open("rb"))
    except OSError:
        print(filepath)
        df = GeoDataFrame.from_file(filepath)
        pickle.dump(df, cache_filename.open("wb"))

    return df


def osm_subset(data, level):
    return (
        data.loc[data["osm_admin_level"] == str(level)]
        .drop(columns=["admin_level", "osm_admin_level", "name_en", "hasc"])
        .reset_index(drop=True)
    )

data = load_file(Path("data/maps/kontur_boundaries_TZ_20230628.gpkg"))

country = clean_columns(load_file(
    Path("./data/maps/admin-boundaries/tza_admbnda_adm0_20181019.zip")
))
# country = osm_subset(data, 2)
zones = osm_subset(data, 3)
regions = osm_subset(data, 4)
districts = osm_subset(data, 5)

all_lakes = load_file(Path("data/maps/water/tanzania-lakes.geojson"))
lakes = (
    all_lakes.loc[all_lakes["HYC_DESCRI"] == "Perennial/Permanent"]
    [["geometry"]]
)

all_rivers = load_file(Path("data/maps/water/tanzania-rivers.geojson"))
rivers = (
    all_rivers.loc[all_rivers["HYC_DESCRI"] == "Perennial/Permanent"]
    [["geometry"]]
)

