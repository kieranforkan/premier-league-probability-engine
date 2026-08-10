# Premier League Probability Engine — Streamlit Showcase

A public-facing Streamlit layer for the existing `premier-league-probability-engine` repository.

## Visual direction

- Deep Premier-League-inspired purple (`#37003C`)
- Green / mint accents (`#00C875`, `#00FF85`)
- Off-white background (`#F7F5F2`)
- White fixture cards and clean probability bars
- No official league logo or club crests are bundled
- Independent-project disclaimer included

## Install into your existing repository

Copy these into the repository root:

```text
app/
.streamlit/
requirements-streamlit.txt
```

The app expects your existing project structure:

```text
premier-league-probability-engine/
├── app/
│   ├── streamlit_app.py
│   └── demo_forecasts.csv
├── .streamlit/
│   └── config.toml
├── outputs/
│   └── forecasts/
│       └── 2026_27/
│           ├── current_live_forecasts.csv
│           └── opening_round_final_forecast_table.csv
└── ...
```

## Install

```powershell
pip install -r requirements-streamlit.txt
```

## Run

From the repository root:

```powershell
streamlit run app/streamlit_app.py
```

The app automatically prefers data in this order:

1. `outputs/forecasts/2026_27/current_live_forecasts.csv`
2. `outputs/forecasts/2026_27/opening_round_final_forecast_table.csv`
3. `app/demo_forecasts.csv`

So the showcase runs immediately with bundled demo forecasts, but switches to your real live outputs once copied into the main repo.

## Pages

- **Fixtures** — responsive fixture cards, xG, H/D/A probabilities, filters and confidence labels.
- **Match Analysis** — fixture-level explanation with optional model-v-market comparison when those columns are available.
- **The Model** — plain-English explanation of the Poisson engine plus technical specification.
- **About** — explains the live-season update workflow and how to interpret probabilities.

## Confidence thresholds

- **Strong:** favourite >= 60% and margin over second outcome >= 25 percentage points.
- **Moderate:** favourite >= 45% and margin >= 12 percentage points.
- **Low:** everything else.

These are descriptive presentation labels, not statistical confidence intervals.

## Deployment

For Streamlit Community Cloud, push the app to GitHub, ensure the main repo requirements include `streamlit`, `pandas`, and `numpy`, and set the entrypoint to:

```text
app/streamlit_app.py
```

The app deliberately reads forecast artefacts instead of fitting the model on every page load. That keeps the public interface fast and preserves the frozen production-model design.
