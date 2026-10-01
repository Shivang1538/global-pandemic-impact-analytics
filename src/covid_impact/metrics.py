"""Metric engineering for country-level pandemic analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd

EXCLUDED_ENTITIES = {"Diamond Princess", "MS Zaandam"}


def standardize_country_names(df: pd.DataFrame, column: str = "Country") -> pd.DataFrame:
    """Return a copy with common country-name inconsistencies resolved."""
    out = df.copy()
    replacements = {
        "Taiwan*": "Taiwan",
        "Korea, South": "South Korea",
        "North Macedonia": "North Macedonia",
        "Cabo Verde": "Cape Verde",
        "Congo (Brazzaville)": "Congo",
        "Congo (Kinshasa)": "Democratic Republic of the Congo",
    }
    if column in out.columns:
        out[column] = out[column].replace(replacements)
    return out


def prepare_timeseries(df: pd.DataFrame) -> pd.DataFrame:
    """Convert a wide COVID table into a clean country-date table."""
    required = {"Date", "Country", "Confirmed", "Deaths", "Recovered"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    out = standardize_country_names(df)
    out["Date"] = pd.to_datetime(out["Date"], errors="coerce")
    out = out.dropna(subset=["Date", "Country"])
    out = out[~out["Country"].isin(EXCLUDED_ENTITIES)]

    numeric = ["Confirmed", "Deaths", "Recovered"]
    for col in numeric:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0).clip(lower=0)

    out = out.groupby(["Date", "Country"], as_index=False)[numeric].sum()
    out = out.sort_values(["Country", "Date"]).reset_index(drop=True)
    out["Active"] = (out["Confirmed"] - out["Deaths"] - out["Recovered"]).clip(lower=0)
    out["New_Confirmed"] = out.groupby("Country")["Confirmed"].diff().fillna(0).clip(lower=0)
    out["New_Deaths"] = out.groupby("Country")["Deaths"].diff().fillna(0).clip(lower=0)
    out["Mortality_Rate_Pct"] = np.where(
        out["Confirmed"] > 0,
        out["Deaths"] / out["Confirmed"] * 100,
        np.nan,
    )
    return out


def country_summary(daily: pd.DataFrame, min_confirmed: int = 1000) -> pd.DataFrame:
    """Create country-level KPI table with a transparent case threshold."""
    latest_date = daily["Date"].max()
    latest = daily[daily["Date"].eq(latest_date)].copy()
    latest = latest[latest["Confirmed"] >= min_confirmed]
    cols = ["Country", "Confirmed", "Deaths", "Recovered", "Active", "Mortality_Rate_Pct"]
    return latest[cols].sort_values("Confirmed", ascending=False).reset_index(drop=True)


def continent_summary(daily: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    """Aggregate country metrics to continents."""
    required = {"Country", "Continent"}
    if not required.issubset(mapping.columns):
        raise ValueError("mapping must contain Country and Continent")
    merged = daily.merge(mapping[["Country", "Continent"]].drop_duplicates(), on="Country", how="left")
    grouped = (
        merged.groupby(["Date", "Continent"], dropna=False)[["Confirmed", "Deaths", "Recovered", "Active", "New_Confirmed", "New_Deaths"]]
        .sum()
        .reset_index()
    )
    grouped["Mortality_Rate_Pct"] = np.where(
        grouped["Confirmed"] > 0,
        grouped["Deaths"] / grouped["Confirmed"] * 100,
        np.nan,
    )
    return grouped


def growth_metrics(daily: pd.DataFrame, start_threshold: int = 100, end_threshold: int = 10000) -> pd.DataFrame:
    """Estimate early-growth duration and average daily growth for each country."""
    rows = []
    for country, grp in daily.groupby("Country"):
        grp = grp.sort_values("Date")
        start = grp.loc[grp["Confirmed"] >= start_threshold, "Date"]
        end = grp.loc[grp["Confirmed"] >= end_threshold, "Date"]
        if start.empty or end.empty:
            continue
        start_date, end_date = start.iloc[0], end.iloc[0]
        window = grp[(grp["Date"] >= start_date) & (grp["Date"] <= end_date)]
        daily_growth = window["Confirmed"].pct_change().replace([np.inf, -np.inf], np.nan).dropna()
        rows.append({
            "Country": country,
            "Start_Date": start_date,
            "End_Date": end_date,
            "Days_100_to_10000": int((end_date - start_date).days),
            "Average_Daily_Growth_Pct": daily_growth.mean() * 100 if not daily_growth.empty else np.nan,
        })
    return pd.DataFrame(rows).sort_values("Days_100_to_10000") if rows else pd.DataFrame()


def enrich_with_world_bank(summary: pd.DataFrame, wb: pd.DataFrame) -> pd.DataFrame:
    """Join pandemic KPIs to selected socioeconomic indicators."""
    out = summary.merge(wb, on="Country", how="left", validate="one_to_one")
    return out
