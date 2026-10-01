"""High-level analytics pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .ingestion import load_jhu_wide
from .metrics import prepare_timeseries, country_summary, growth_metrics, continent_summary, enrich_with_world_bank


def build_outputs(raw_dir: Path, processed_dir: Path) -> dict[str, pd.DataFrame]:
    processed_dir.mkdir(parents=True, exist_ok=True)
    raw = load_jhu_wide(raw_dir)
    daily = prepare_timeseries(raw)

    summary = country_summary(daily)
    growth = growth_metrics(daily)

    mapping_path = raw_dir / "country_continent.csv"
    if mapping_path.exists():
        mapping = pd.read_csv(mapping_path)
        continent = continent_summary(daily, mapping)
    else:
        continent = pd.DataFrame()

    wb_path = raw_dir / "world_bank.csv"
    socioeconomic = pd.DataFrame()
    if wb_path.exists():
        wb = pd.read_csv(wb_path)
        socioeconomic = enrich_with_world_bank(summary, wb)

    outputs = {
        "country_daily_metrics": daily,
        "country_summary": summary,
        "growth_analysis": growth,
        "continent_daily_metrics": continent,
        "socioeconomic_summary": socioeconomic,
    }
    for name, frame in outputs.items():
        if not frame.empty:
            frame.to_csv(processed_dir / f"{name}.csv", index=False)
    return outputs
