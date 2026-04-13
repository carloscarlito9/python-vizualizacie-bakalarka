from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely import wkt

ROOT = Path(__file__).resolve().parents[2]
GEO_RAW = ROOT / "data" / "raw" / "geo" / "slovakia"


def load_geometry(file_name: str, layer: str | None = None) -> gpd.GeoDataFrame:
    path = GEO_RAW / file_name
    if not path.exists():
        raise FileNotFoundError(f"Súbor {file_name} nebol nájdený v {GEO_RAW}")

    suffix = path.suffix.lower()

    if suffix == ".gpkg":
        if layer is not None:
            return gpd.read_file(path, layer=layer)
        return gpd.read_file(path)

    if suffix == ".shp":
        return gpd.read_file(path)

    if suffix in [".json", ".geojson"]:
        return gpd.read_file(path)

    if suffix == ".csv":
        df = pd.read_csv(path)

        if "geometry" in df.columns:
            df["geometry"] = df["geometry"].apply(wkt.loads)
            return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

        if "geometry_wkt" in df.columns:
            df["geometry"] = df["geometry_wkt"].apply(wkt.loads)
            return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

        if {"lat", "lon"}.issubset(df.columns):
            return gpd.GeoDataFrame(
                df,
                geometry=gpd.points_from_xy(df["lon"], df["lat"]),
                crs="EPSG:4326"
            )

        raise ValueError("CSV nemá geometry / geometry_wkt / lat-lon")

    raise ValueError("Nepodporovaný formát")


def process_choropleth_data(
    districts_file: str,
    pois_file: str,
    districts_layer: str = "okres_2",
    district_code_col: str = "LAU1_CODE",
    district_name_col: str = "NM3",
    join_predicate: str = "within",
) -> gpd.GeoDataFrame:

    districts = load_geometry(districts_file, layer=districts_layer)
    pois = load_geometry(pois_file)

    if districts.crs is None or pois.crs is None:
        raise ValueError("CRS chyba")

    districts = districts.to_crs("EPSG:4326")
    pois = pois.to_crs("EPSG:4326")

    joined = gpd.sjoin(
        pois,
        districts[[district_code_col, district_name_col, "geometry"]],
        how="left",
        predicate=join_predicate
    )

    counts = (
        joined.groupby(district_code_col)
        .size()
        .rename("poi_count")
        .reset_index()
    )

    districts = districts.merge(counts, on=district_code_col, how="left")
    districts["poi_count"] = districts["poi_count"].fillna(0).astype(int)

    districts["indicator"] = districts["poi_count"]
    districts["indicator_label"] = "Počet POI"
    districts["label"] = districts[district_name_col].astype(str)

    keep_cols = [
        district_code_col,
        district_name_col,
        "poi_count",
        "indicator",
        "indicator_label",
        "label",
        "geometry"
    ]

    return districts[keep_cols].copy()

    

