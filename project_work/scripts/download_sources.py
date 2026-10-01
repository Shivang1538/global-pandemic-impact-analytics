from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from covid_impact.ingestion import download_jhu, download_world_bank

raw = ROOT / "data" / "raw"
print("Downloading COVID-19 source data...")
download_jhu(raw)
print("Downloading World Bank indicators...")
download_world_bank(raw / "world_bank.csv")
print("Source download complete.")
