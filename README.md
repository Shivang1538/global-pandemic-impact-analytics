# Global Pandemic Impact Analytics

A reproducible data analytics project that studies how the COVID-19 pandemic evolved across countries and continents, and how outcomes varied alongside population, income, life expectancy, urbanisation and health-expenditure indicators.

**Author:** Shivang Tiwari  
**Focus:** Data Analytics | Python | SQL-ready data | Statistical analysis | Data visualisation

## What this project does

The project turns public COVID-19 time-series data into an analysis-ready dataset and answers practical questions such as:

- How did confirmed cases, deaths and active cases evolve over time?
- Which countries and continents experienced the largest reported case and death burdens?
- How did mortality rates differ after applying a minimum case threshold?
- How quickly did reported cases grow during the early phase of the pandemic?
- Are pandemic outcomes associated with socioeconomic indicators such as GDP per capita, life expectancy and health expenditure?

## Analytics workflow

```text
Public datasets
     ↓
Data ingestion
     ↓
Validation + country-name standardisation
     ↓
Daily metrics + cumulative metrics
     ↓
Country / continent aggregation
     ↓
Socioeconomic enrichment
     ↓
Statistical analysis
     ↓
CSV outputs + charts
     ↓
Power BI / Excel / SQL-ready analysis
```

## Tech stack

- Python
- Pandas / NumPy
- Matplotlib / SciPy
- Requests
- Pytest
- Jupyter-compatible workflow
- CSV outputs designed for Power BI and Excel

## Project structure

```text
.
├── data/
│   ├── raw/                 # downloaded source data, not committed
│   └── processed/           # generated analysis tables
├── outputs/
│   └── figures/             # generated charts
├── scripts/
│   ├── download_sources.py
│   └── run_analysis.py
├── src/
│   └── covid_impact/
│       ├── analytics.py
│       ├── charts.py
│       ├── ingestion.py
│       └── metrics.py
├── tests/
├── .gitignore
├── LICENSE
├── requirements.txt
└── README.md
```

## Getting started

### 1. Create an environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Download the source data

```bash
python scripts/download_sources.py
```

The downloader retrieves historical COVID-19 time-series data and World Bank indicators used by the analysis. Source files are stored under `data/raw/` and are intentionally ignored by Git because they are external datasets.

### 4. Run the analysis

```bash
python scripts/run_analysis.py
```

Generated tables are written to `data/processed/` and charts to `outputs/figures/`.

## Key analytical outputs

| Output | Purpose |
|---|---|
| `country_daily_metrics.csv` | Country-level daily confirmed, recovered, death and active-case metrics |
| `country_summary.csv` | Country-level cumulative totals and mortality metrics |
| `continent_daily_metrics.csv` | Continent-level daily aggregation |
| `socioeconomic_summary.csv` | Pandemic outcomes enriched with World Bank indicators |
| `growth_analysis.csv` | Early-growth and doubling-time style metrics |

These files can be imported directly into **Power BI**, Excel or a SQL database for further analysis.

## Data quality decisions

The pipeline explicitly handles:

- inconsistent country names across sources
- missing values
- duplicate country/date observations
- non-country records such as cruise ships
- division-by-zero when calculating mortality
- countries with very small case counts when comparing mortality

## Important interpretation note

COVID-19 reporting changed over time and differed substantially between countries. Reported cases and deaths are therefore treated as reported surveillance data, not as a perfect measurement of true infections or deaths. Correlation results in this project are descriptive and should not be interpreted as causal evidence.

## Data sources and attribution

The analysis uses public datasets from the Johns Hopkins University Center for Systems Science and Engineering COVID-19 repository and the World Bank Open Data API. The project code is original to this repository, while the underlying datasets remain owned and licensed by their respective providers.


## Author

**Shivang Tiwari**  
B.Tech Computer Science & Engineering
