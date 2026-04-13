from pyrosm import OSM, get_data
from pathlib import Path
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[2]
PBF_PATH = ROOT / "data" / "raw" / "geo" / "slovakia" / "slovakia-260323.osm.pbf"
OUTPUT_PATH = ROOT / "data" / "raw" / "geo" / "slovakia" / "pois.geojson"

def extract_pois_from_pbf(filter_tags=None):
    """
    Načíta PBF súbor a vyexportuje vybrané POI do GeoJSON.
    Predvolene exportuje nemocnice, školy a bankomaty.
    """
    if not PBF_PATH.exists():
        raise FileNotFoundError(f"Súbor {PBF_PATH} nebol nájdený. Uistite sa, že ste stiahli slovakia-latest.osm.pbf z Geofabrik.")

    # Inicializácia OSM parsera
    osm = OSM(str(PBF_PATH))

    # Definícia filtrov (kľúč 'amenity' v OSM obsahuje väčšinu POI)
    if filter_tags is None:
        custom_filter = {"amenity": ["hospital", "school", "atm", "pharmacy", "bank"]}
    else:
        custom_filter = filter_tags

    # Extrakcia POI (vráti GeoDataFrame)
    print(f"Extrahuje sa dáta z {PBF_PATH.name}... (môže to trvať niekoľko minút)")
    pois = osm.get_pois(custom_filter=custom_filter)

    if pois is None or pois.empty:
        print("Neboli nájdené žiadne POI pre zadaný filter.")
        return

    # Uloženie do GeoJSON (formát, ktorý používa váš geo.py loader)
    pois.to_file(OUTPUT_PATH, driver='GeoJSON')
    print(f"Export dokončený: {OUTPUT_PATH}")

if __name__ == "__main__":
    extract_pois_from_pbf()