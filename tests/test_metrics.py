import pandas as pd

from covid_impact.metrics import prepare_timeseries, country_summary, continent_summary


def sample():
    return pd.DataFrame({
        "Date": ["2020-01-01", "2020-01-02", "2020-01-01", "2020-01-02"],
        "Country": ["Exampleland", "Exampleland", "Diamond Princess", "Otherland"],
        "Confirmed": [100, 130, 500, 50],
        "Deaths": [5, 7, 10, 2],
        "Recovered": [20, 40, 400, 10],
    })


def test_prepare_timeseries_removes_excluded_entities_and_calculates_metrics():
    raw = sample()
    result = prepare_timeseries(raw)
    assert "Diamond Princess" not in set(result["Country"])
    row = result[result["Country"].eq("Exampleland")].iloc[-1]
    assert row["Active"] == 83
    assert round(row["Mortality_Rate_Pct"], 2) == round(7 / 130 * 100, 2)


def test_country_summary_applies_case_threshold():
    result = country_summary(prepare_timeseries(sample()), min_confirmed=100)
    assert list(result["Country"]) == ["Exampleland"]


def test_continent_aggregation():
    daily = prepare_timeseries(sample())
    mapping = pd.DataFrame({"Country": ["Exampleland"], "Continent": ["Testland"]})
    result = continent_summary(daily, mapping)
    assert result["Confirmed"].max() == 130
