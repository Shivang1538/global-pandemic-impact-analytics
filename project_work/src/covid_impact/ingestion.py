"""Data ingestion and source normalisation."""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import requests

JHU_CONFIRMED = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
JHU_DEATHS = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
JHU_RECOVERED = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"

WORLD_BANK_INDICATORS = {
    "NY.GDP.PCAP.PP.CD": "GDP_Per_Capita_PPP",
    "SP.POP.TOTL": "Population",
    "SP.DYN.LE00.IN": "Life_Expectancy",
    "SH.XPD.CHEX.GD.ZS": "Health_Expenditure_Pct_GDP",
}


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    destination.write_bytes(response.content)


def download_jhu(output_dir: Path) -> None:
    """Download the three global JHU time-series files."""
    for name, url in {
        "confirmed_global.csv": JHU_CONFIRMED,
        "deaths_global.csv": JHU_DEATHS,
        "recovered_global.csv": JHU_RECOVERED,
    }.items():
        download_file(url, output_dir / name)


def _latest_world_bank(indicator: str, start_year: int = 2019, end_year: int = 2021) -> pd.DataFrame:
    url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&per_page=20000"
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    payload = response.json()
    rows = payload[1]
    df = pd.DataFrame(rows)
    df["date"] = pd.to_numeric(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df[df["date"].between(start_year, end_year)].dropna(subset=["value"])
    df = df.sort_values("date").drop_duplicates("country", keep="last")
    return df[["country", "value"]].rename(columns={"country": "Country", "value": WORLD_BANK_INDICATORS[indicator]})


def download_world_bank(output_path: Path) -> pd.DataFrame:
    """Fetch selected World Bank indicators and return one row per country."""
    combined = None
    for indicator in WORLD_BANK_INDICATORS:
        current = _latest_world_bank(indicator)
        combined = current if combined is None else combined.merge(current, on="Country", how="outer")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output_path, index=False)
    return combined


def load_jhu_wide(raw_dir: Path) -> pd.DataFrame:
    """Combine JHU wide files into a tidy country-date dataset."""
    frames = {}
    for metric in ["Confirmed", "Deaths", "Recovered"]:
        file = raw_dir / f"{metric.lower()}_global.csv"
        df = pd.read_csv(file)
        date_cols = df.columns[4:]
        df = df.groupby("Country/Region")[date_cols].sum().reset_index()
        df = df.rename(columns={"Country/Region": "Country"})
        frames[metric] = df

    merged = frames["Confirmed"].merge(frames["Deaths"], on="Country", suffixes=("_Confirmed", "_Deaths"))
    merged = merged.merge(frames["Recovered"], on="Country", suffixes=("", "_Recovered"))
    date_cols = [c for c in merged.columns if c not in {"Country"}]

    rows = []
    for metric in ["Confirmed", "Deaths", "Recovered"]:
        pass

    # Re-read each source into tidy form to avoid fragile column suffix logic.
    tidy = None
    for metric in ["Confirmed", "Deaths", "Recovered"]:
        df = pd.read_csv(raw_dir / f"{metric.lower()}_global.csv")
        df = df.groupby("Country/Region")[df.columns[4:]].sum()
        df.index.name = "Country"
        long = df.reset_index().melt(id_vars="Country", var_name="Date", value_name=metric)
        tidy = long if tidy is None else tidy.merge(long, on=["Country", "Date"], how="outer")
    return tidy
