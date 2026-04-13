""" 
    nájsť stanice
    načítať dáta
    odfiltrovať premenné
    spraviť mesačne priemery
    pripraviť dataframe pre vykreslenie
    """
from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[2] # file, aktualny subor, abs. cesta, odva priecinky vyssie
RAW_DIR = ROOT / "data" / "raw" / "time_series" / "ghcn" # cesta k datasetu
BY_YEAR_DIR = RAW_DIR / "by_year" # ročné súbory
STATIONS_DIR = RAW_DIR / "stations" # zoznam staníc


def read_stations_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)  # dtype=str - načitanie ako text

    cols = {c.lower().strip(): c for c in df.columns} #dict male pismena

    out = pd.DataFrame({                                           #dataframe len s potrebnými stĺpcami
        "station": df[cols.get("id", df.columns[0])].astype(str),
        "name": df[cols.get("name", df.columns[-1])].astype(str),
        "state": df[cols.get("state", df.columns[-2])] if "state" in cols else ""
    })

    out["name_up"] = out["name"].str.upper()  # ak sa názov stĺpca nenájde, prida sa nazov s velkymi písmenami -> pri filtrovani
    return out


def _read_stations_txt(path: Path) -> pd.DataFrame:   #to isté, len ak sú stĺpce fixed width
    colspecs = [
        (0, 11), (12, 20), (21, 30), (31, 37),
        (38, 40), (41, 71), (72, 75), (76, 79), (80, 85)
    ]

    names = [                                                   # určenie presného poradia stĺpcov v txt
        "station", "latitude", "longitude", "elevation",
        "state", "name", "gsn", "hcncrn", "wmo"
    ]

    df = pd.read_fwf(path, colspecs=colspecs, names=names, dtype=str)  # pomenovanie stĺpcov vo fixed-width
    df["name_up"] = df["name"].str.upper() # ak sa názov stĺpca nenájde, prida sa nazov s velkymi písmenami -> pri filtrovani

    return df[["station", "name", "state", "name_up"]]


def read_stations() -> pd.DataFrame:
    csv_path = STATIONS_DIR / "ghcnd-stations.csv"    # cesta k obom formátom
    txt_path = STATIONS_DIR / "ghcnd-stations.txt"

    if txt_path.exists():                    # ak je txt verzia, tak táto
        return _read_stations_txt(txt_path)

    if csv_path.exists():                   # ak je csv verzia
        try:
            return read_stations_csv(csv_path)
        except Exception as e:
            raise ValueError(                               # ak neexistuju, = chyba
                f"Stations CSV sa nepodarilo načítať: {e}. "
                f"Odporúčané je použiť ghcnd-stations.txt."
            )

    raise FileNotFoundError(
        "Nenašiel sa ghcnd-stations.txt ani ghcnd-stations.csv v priečinku stations."
    )

def find_station_ids_by_names(names_like: list[str]) -> pd.DataFrame:   
    st = read_stations()                                   # načita tabuľku staníc
 
    mask = False                                          # # filter, čiastočná zhoda podľa názvu
    for nm in names_like:
        mask = mask | st["name_up"].str.contains(nm.upper(), na=False)

    return st[mask][["station", "name"]].drop_duplicates()      # vzhovujúce stanice bez duplicít


def _read_by_year(year: int, station_ids: list[str] | None = None) -> pd.DataFrame:
    path = BY_YEAR_DIR / f"{year}.csv.gz"                  # cesta k súboru

    if not path.exists():
        raise FileNotFoundError(f"Chýba súbor {path}")  # ak nie, = chyba

    cols = ["station", "date", "element", "value", "mflag", "qflag", "sflag", "obstime"] # pomenuje názvy stĺpcov

    chunks = []                    # po častiach, kvoli úspore pamate
    reader = pd.read_csv(
        path,
        header=None,
        names=cols,
        compression="gzip",
        usecols=[0, 1, 2, 3, 5],  # stanica, datum, element, hodnota, qflag
        chunksize=500_000,
        dtype={
            "station": "string",
            "date": "string",
            "element": "string",
            "value": "float32",
            "qflag": "string",
        },
        low_memory=True
    )

    for chunk in reader:
        chunk = chunk[chunk["qflag"].isna()] # len riadky bez quality flagu
        chunk = chunk[chunk["element"].isin(["TAVG", "TMAX", "TMIN"])] # len teplotné záznamy

        if station_ids is not None:
            chunk = chunk[chunk["station"].isin(station_ids)]  # len zadané stanice

        if not chunk.empty:
            chunks.append(chunk[["station", "date", "element", "value"]]) # neprázdne chunky sa odložia

    if not chunks:
        return pd.DataFrame(columns=["station", "date", "element", "value"]) # ak nic neostalo, vráti prázdny dataframe

    df = pd.concat(chunks, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce") # spojenie chunkov a vráti datetime

    return df # celý dataframe za celý rok


def load_noaa_monthly_tavg(years: list[int], station_name_filters: list[str] = None) -> pd.DataFrame: # vráti roky a názvy

    station_ids = None # nie je vybratá stanicea

    if station_name_filters:                                # ak sú zadané filtre, najde sa ID stanice
        st = find_station_ids_by_names(station_name_filters)

        if st.empty:          # ak nič = chyba
            raise ValueError(
                f"Nenašli sa žiadne stanice pre filtre: {station_name_filters}"
            )

        print("Použité stanice:")
        print(st)

        station_ids = st["station"].dropna().astype(str).unique().tolist()  # vyberú sa id stanice ako zoznam

    frames = [_read_by_year(y, station_ids=station_ids) for y in years]  # načítajú sa roky a odstránia prázdne dataframe
    frames = [f for f in frames if not f.empty]

    if not frames:
        raise ValueError("Po filtrovaní nezostali žiadne NOAA dáta.") # aknič = chyba

    df = pd.concat(frames, ignore_index=True)  # spojenie všetkých rokov
    df["value_c"] = df["value"] / 10.0  # teploty z desatín na celé stupne

    piv = df.pivot_table(                     # dáta prepivotuju 
        index=["station", "date"],
        columns="element",
        values="value_c"
    ).reset_index()

    if "TAVG" not in piv.columns:    # ak chýba TAVG, vypočíta sa 
        piv["TAVG"] = (piv["TMAX"] + piv["TMIN"]) / 2

    monthly = (
        piv.set_index("date")         # agregácia podľa stanice, po mesiacoch a spriemerovanie dennych teplot na mesačný priemer
        .groupby("station")["TAVG"]
        .resample("MS")
        .mean()
        .reset_index()
    )

    if piv.empty:                                              # kontrola ci je pivot prazdny
        raise ValueError("Pivot je prázdny. Skontroluj stanice alebo dostupnosť dát.")

    result = (
        monthly.groupby("date")["TAVG"]   # mesačné rady sa spriemerujú, spoločný priemer pre všetky stanice
        .mean()
        .reset_index()
        .rename(columns={"TAVG": "value"})
        .sort_values("date")
        .reset_index(drop=True)
    )

    return result    # výstup len date a value