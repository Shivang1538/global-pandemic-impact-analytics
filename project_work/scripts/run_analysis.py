from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from covid_impact.analytics import build_outputs
from covid_impact.charts import plot_global_trend, plot_top_countries, plot_mortality

raw = ROOT / "data" / "raw"
processed = ROOT / "data" / "processed"
figures = ROOT / "outputs" / "figures"

outputs = build_outputs(raw, processed)
summary = outputs["country_summary"]
daily = outputs["country_daily_metrics"]

if not daily.empty:
    plot_global_trend(daily, figures)
if not summary.empty:
    plot_top_countries(summary, figures)
    plot_mortality(summary, figures)

print(f"Processed {len(daily):,} country-date rows.")
print(f"Generated {len(summary):,} country summary rows.")
print(f"Outputs: {processed}")
print(f"Charts:  {figures}")
