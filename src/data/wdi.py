from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
WDI_PATH = ROOT / "data" / "raw" / "correlations" / "wdi" / "WDICSV.csv"


def load_wdi_correlations(
    years: list[int] | None = None,
    indicators: list[str] | None = None
) -> pd.DataFrame:
    """
    Načíta WDI dáta, vyberie zvolené roky a indikátory
    a vráti pivotovanú tabuľku:
        riadky = krajiny
        stĺpce = indikátory
        hodnoty = numerické hodnoty spriemerované naprieč zvolenými rokmi
    """

    if not WDI_PATH.exists():
        raise FileNotFoundError(f"Chýba súbor {WDI_PATH}. Skontrolujte umiestnenie.")

    if years is None:
        years = [2018, 2019, 2020, 2021, 2022]

    if indicators is None:
        indicators = [
            "GDP per capita (current US$)",
            "Life expectancy at birth, total (years)",
            "Urban population (% of total population)",
            "Individuals using the Internet (% of population)",
        ]

    df = pd.read_csv(WDI_PATH)

    year_cols = [str(y) for y in years if str(y) in df.columns]
    if not year_cols:
        raise ValueError("Žiadny z požadovaných rokov sa nenašiel v datasete.")

    df = df[df["Indicator Name"].isin(indicators)].copy()
    df = df[["Country Name", "Indicator Name"] + year_cols].copy()

    df = df.melt(
        id_vars=["Country Name", "Indicator Name"],
        value_vars=year_cols,
        var_name="year",
        value_name="value"
    )

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])

    df = (
        df.groupby(["Country Name", "Indicator Name"])["value"]
        .mean()
        .reset_index()
    )

    pivot = df.pivot_table(
        index="Country Name",
        columns="Indicator Name",
        values="value",
        aggfunc="mean"
    )

    pivot = pivot.dropna()
    return pivot