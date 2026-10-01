"""Publication-style charts for the analytics outputs."""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def _save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_global_trend(daily: pd.DataFrame, output_dir: Path) -> None:
    world = daily.groupby("Date")[["Confirmed", "Deaths", "Active"]].sum().reset_index()
    fig, ax = plt.subplots(figsize=(11, 6))
    for col in ["Confirmed", "Deaths", "Active"]:
        ax.plot(world["Date"], world[col], label=col)
    ax.set_title("Global Reported COVID-19 Burden Over Time")
    ax.set_ylabel("Reported cases")
    ax.legend()
    _save(fig, output_dir / "global_trend.png")


def plot_top_countries(summary: pd.DataFrame, output_dir: Path, n: int = 10) -> None:
    top = summary.head(n).sort_values("Confirmed")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top["Country"], top["Confirmed"])
    ax.set_title(f"Top {n} Countries by Reported Confirmed Cases")
    ax.set_xlabel("Confirmed cases")
    _save(fig, output_dir / "top_countries_confirmed.png")


def plot_mortality(summary: pd.DataFrame, output_dir: Path, n: int = 10) -> None:
    top = summary.sort_values("Mortality_Rate_Pct", ascending=False).head(n).sort_values("Mortality_Rate_Pct")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top["Country"], top["Mortality_Rate_Pct"])
    ax.set_title("Countries with Higher Reported Mortality Rates")
    ax.set_xlabel("Deaths / confirmed cases (%)")
    _save(fig, output_dir / "mortality_rate.png")
