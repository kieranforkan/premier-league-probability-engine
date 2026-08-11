# Premier League Probability Engine

An end-to-end football forecasting system that produces **pre-match Premier League home-win, draw and away-win probabilities**.

The project combines Elo ratings, recent team performance, venue-specific form, rest, fixture congestion, league-table state and other strictly pre-match information with an **Independent Poisson model** to estimate expected goals and full-time result probabilities.

The final production model was trained on **4,180 Premier League fixtures across 11 seasons**, from 2015–16 through 2025–26, and is now being used prospectively for the **2026–27 Premier League season**.

> **Current status:** Production model frozen and 2026–27 forecasting pipeline operational.

---

## Interactive Forecasting App

A Streamlit application provides a non-technical interface to the model.

Users can explore upcoming fixtures and view:

- Expected goals for each team
- Home-win, draw and away-win probabilities
- Model favourite
- Forecast confidence
- Fixture-level model analysis
- Model-vs-market comparisons where available
- A plain-English explanation of how the model works

### Live App

**Streamlit:** 
`https://premier-league-probability-engine.streamlit.app/`

The app uses a Premier-League-inspired visual identity with deep purple, green and off-white styling while remaining an independent project.

---

## Example: Opening 2026–27 Forecasts

The first production forecasts were generated before any 2026–27 Premier League matches had been played.

| Fixture | Home xG | Away xG | Home | Draw | Away | Model Favourite |
|---|---:|---:|---:|---:|---:|---|
| Arsenal vs Coventry | 2.47 | 0.95 | **70.6%** | 16.8% | 12.6% | Arsenal |
| Hull vs Manchester United | 1.01 | 2.04 | 17.9% | 20.8% | **61.3%** | Manchester United |
| Everton vs Crystal Palace | 1.49 | 1.41 | **39.3%** | 24.7% | 35.9% | Everton |
| Ipswich vs Sunderland | 1.17 | 1.62 | 27.6% | 24.6% | **47.8%** | Sunderland |
| Nottingham Forest vs Leeds | 1.55 | 1.35 | **42.0%** | 24.7% | 33.4% | Nottingham Forest |
| Brentford vs Tottenham | 1.69 | 1.24 | **48.1%** | 24.0% | 28.0% | Brentford |
| Brighton vs Aston Villa | 1.42 | 1.60 | 34.0% | 24.1% | **41.8%** | Aston Villa |
| Manchester City vs Bournemouth | 2.02 | 1.22 | **55.8%** | 21.4% | 22.8% | Manchester City |
| Newcastle vs Liverpool | 1.34 | 1.69 | 30.6% | 23.8% | **45.6%** | Liverpool |
| Fulham vs Chelsea | 1.44 | 1.50 | 36.4% | 24.6% | **39.0%** | Chelsea |

These are probability estimates rather than deterministic score predictions. A team assigned a 70% win probability is still expected to fail to win approximately 30% of comparable matches if the probabilities are well calibrated.

---

# Project Overview

The objective of the project is to answer a simple question:

> **Given only information available before kickoff, what is the probability of a home win, draw or away win?**

Rather than predicting only the most likely result, the system produces a complete probability distribution:

\[
P(H),\quad P(D),\quad P(A)
\]

where:

- \(H\) = home win
- \(D\) = draw
- \(A\) = away win

The production output order is always:

```text
(H, D, A)
```

The probabilities are constrained to sum to 1.

---

# Modelling Pipeline

The final system can be summarised as:

```text
Historical match data
        ↓
Pre-match state reconstruction
        ↓
Elo ratings
        ↓
Rolling team and venue form
        ↓
Rest / congestion / table features
        ↓
70-feature frozen production schema
        ↓
Home-goal Poisson model
+
Away-goal Poisson model
        ↓
Expected goals
        ↓
Scoreline probability matrix
        ↓
Home / Draw / Away probabilities
        ↓
Production forecast
        ↓
Streamlit interface
```

The model never uses information from after the fixture being predicted.

---

# Feature Engineering

The production model uses a frozen schema of **70 pre-match predictors**.

These cover several areas.

## Elo Strength

Team strength is tracked dynamically through an Elo rating system.

Features include:

- Home-team Elo
- Away-team Elo
- Elo difference

Ratings are updated chronologically after matches are completed.

New or previously unseen teams can enter the system from a neutral initial rating before subsequent results update their strength estimate.

---

## Recent Form

Rolling team performance is reconstructed from matches completed before kickoff.

The pipeline includes:

- Goals scored
- Goals conceded
- Points
- Wins
- Draws
- Losses
- Goal difference

Rolling calculations use previous completed fixtures only.

---

## Venue-Specific Form

Home and away performance can differ significantly.

The feature pipeline therefore separately tracks:

- Recent home performance for the home team
- Recent away performance for the away team

This allows the model to distinguish general team strength from venue-specific behaviour.

---

## Rest and Congestion

The model incorporates scheduling information including:

- Days since the previous match
- Short-rest indicators
- Recent match congestion
- Number of fixtures played over recent windows

The current fixture itself is never included in congestion calculations.

---

## League-Table State

The league table is reconstructed exactly as it existed **before each match**.

Features include:

- Points
- Goal difference
- Goals scored
- League position
- Position difference
- Top-four status
- Top-six status
- Top-half status
- Bottom-three status

Fixtures played at the same timestamp are evaluated using the same pre-match table state so that results from one simultaneous match cannot leak into another.

---

## Season Context

The model also contains variables describing where each club is within the season, including:

- Matchweek
- Matches already played
- Season progress
- Difference in matches played
- First-half / second-half season context

---

# Model Development

Several model families were evaluated before the production system was selected.

These included:

1. Logistic Regression
2. Random Forest
3. Histogram Gradient Boosting
4. Weighted model ensemble
5. Independent Poisson scoreline model

The objective was not simply to find the model with the highest classification accuracy.

The primary evaluation focused on the **quality of the complete predicted probability distribution**.

---

# Why Probability Quality Matters

Consider two models predicting the same match.

### Model A

```text
Home: 51%
Draw: 25%
Away: 24%
```

### Model B

```text
Home: 90%
Draw: 6%
Away: 4%
```

Both predict a home win.

However, if the away team wins, Model B was dramatically more overconfident.

For this reason, metrics such as **log loss** and **Brier score** are more appropriate for this project than raw accuracy alone.

---

# Chronological Evaluation

Football forecasting is inherently time-dependent.

A random train/test split would allow future football states to influence earlier predictions and would therefore provide an unrealistic estimate of production performance.

The project instead uses **walk-forward evaluation**.

Each test season is predicted using only information that would have been available before that season.

The walk-forward evaluation covered five Premier League seasons from:

```text
2020–21
to
2024–25
```

Each model produced predictions for **380 fixtures per season**.

---

# Walk-Forward Results

Mean log loss across the five test seasons:

| Model | Mean Log Loss |
|---|---:|
| **Independent Poisson** | **0.9850** |
| Ensemble | 0.9880 |
| Random Forest | 0.9883 |
| Histogram Gradient Boosting | 0.9944 |
| Logistic Regression | 0.9945 |

Independent Poisson achieved the best average log loss and was the strongest model in **3 of the 5 evaluated seasons**.

However, the advantage over the ensemble was small:

```text
Poisson advantage ≈ 0.00296 log-loss units
```

A bootstrap comparison estimated approximately an **89% probability that Poisson was better than the ensemble**, but the uncertainty interval still crossed zero.

The evidence therefore supports Poisson as the preferred production model, but **not as decisively superior**.

---

# Final Model Selection

The **Independent Poisson model** was selected for production.

The decision considered:

- Walk-forward probability performance
- Stability across seasons
- Expected-goal interpretability
- Natural scoreline modelling
- Production simplicity
- Ability to generate complete score distributions

The choice was therefore based on the overall balance of evidence rather than a claim that Poisson overwhelmingly dominated every alternative.

---

# Independent Poisson Model

The model estimates two expected-goal parameters:

\[
\lambda_H
\]

for the home team and

\[
\lambda_A
\]

for the away team.

Goals are modelled as:

\[
X_H \sim \text{Poisson}(\lambda_H)
\]

\[
X_A \sim \text{Poisson}(\lambda_A)
\]

For each possible scoreline:

\[
P(X_H=i, X_A=j)
=
P(X_H=i)P(X_A=j)
\]

The production implementation evaluates scorelines from:

```text
0–0
through
10–10
```

The scoreline probabilities are then aggregated into:

\[
P(H)
=
\sum_{i>j}
P(X_H=i,X_A=j)
\]

\[
P(D)
=
\sum_{i=j}
P(X_H=i,X_A=j)
\]

\[
P(A)
=
\sum_{i<j}
P(X_H=i,X_A=j)
\]

The resulting probabilities are renormalised to ensure:

\[
P(H)+P(D)+P(A)=1
\]

---

# Calibration

Additional calibration methods were tested after model development.

The project evaluated:

- Original probabilities
- Sigmoid calibration
- Isotonic calibration

Neither calibration method improved the selected model sufficiently.

The final production system therefore retains the **original Poisson probabilities**.

This is important because calibration was evaluated rather than automatically applied.

---

# Bookmaker Benchmark

A forecasting model should not only be compared with weaker machine-learning alternatives.

Betting markets provide an extremely strong real-world probability benchmark.

The project therefore evaluated the model against **Pinnacle closing probabilities**.

Historical mean log loss:

| Predictor | Mean Log Loss |
|---|---:|
| Pinnacle Closing Market | **0.9524** |
| Production Poisson Model | 0.9850 |

The market was materially stronger historically.

This result is central to the interpretation of the project.

The system therefore **does not claim to have demonstrated a persistent profitable betting edge**.

Instead, market probabilities are treated as an external benchmark against which the model's forecasts can be evaluated.

---

# Model vs Market Analysis

For current fixtures, bookmaker decimal odds can be converted into implied probabilities:

\[
q_i = \frac{1}{\text{odds}_i}
\]

Because bookmaker probabilities typically sum to more than 1, the quoted market margin is removed using proportional normalisation:

\[
p_i^{market}
=
\frac{q_i}{\sum_j q_j}
\]

This produces a comparable market probability distribution.

Model-market disagreement can then be measured.

One metric used in the project is **Total Variation Distance**:

\[
TV
=
\frac{1}{2}
\sum_i
\left|
p_i^{model}
-
p_i^{market}
\right|
\]

A larger value represents greater disagreement between the complete model and market probability distributions.

---

# Opening-Round Market Comparison

For the initial 2026–27 market snapshot:

```text
Model / market favourite agreement: 9 / 10 fixtures
Mean Total Variation distance:      0.074
Maximum Total Variation distance:   0.116
```

The only opening-round favourite disagreement was:

```text
Brighton vs Aston Villa

Market favourite: Brighton
Model favourite:  Aston Villa
```

Some of the largest probability disagreements included:

- Sunderland away at Ipswich
- Aston Villa away at Brighton
- Bournemouth away at Manchester City
- Crystal Palace away at Everton
- Brentford at home to Tottenham
- Fulham at home to Chelsea

These are treated as **forecast disagreements**, not automatically as betting opportunities.

---

# Disagreement Watchlist

A descriptive watchlist was created to make model-market differences easier to analyse.

An outcome qualifies as a primary disagreement when:

```text
Model probability - market probability >= 5 percentage points
```

and:

```text
Model probability >= 20%
```

Longer-shot outcomes can be separated because very large quoted odds can create extreme theoretical expected returns from relatively small probability-estimation errors.

The opening-round primary watchlist contained six outcomes:

| Outcome | Model Probability | Market Probability | Difference |
|---|---:|---:|---:|
| Sunderland win at Ipswich | 47.8% | 36.9% | +10.9pp |
| Aston Villa win at Brighton | 41.8% | 32.3% | +9.5pp |
| Bournemouth win at Manchester City | 22.8% | 14.8% | +7.9pp |
| Crystal Palace win at Everton | 35.9% | 28.4% | +7.6pp |
| Brentford win vs Tottenham | 48.1% | 40.6% | +7.5pp |
| Fulham win vs Chelsea | 36.4% | 30.3% | +6.1pp |

Coventry away at Arsenal was classified separately as a longshot-sensitive disagreement.

Again, these differences are **not evidence of proven betting profitability**.

---

# Forecast Confidence

To make forecasts easier to interpret in the Streamlit interface, model outputs are assigned descriptive confidence categories.

### Strong

```text
Favourite probability >= 60%
AND
Favourite lead over second-most-likely outcome >= 25 percentage points
```

### Moderate

```text
Favourite probability >= 45%
AND
Favourite lead >= 12 percentage points
```

### Low

Everything else.

For the opening 2026–27 round:

```text
Strong:   2 fixtures
Moderate: 4 fixtures
Low:      4 fixtures
```

These are **presentation categories**, not statistical confidence intervals.

---

# Production Model

After model selection, the full production system was refitted using every available Premier League fixture through the end of 2025–26.

Production training sample:

```text
Fixtures: 4,180
Seasons:  11
From:     2015–16
To:       2025–26
```

The production feature schema contains:

```text
70 predictors
```

The production bundle stores the complete frozen transformation and modelling pipeline required to reproduce forecasts.

---

# Numerical Production Specification

The final fitted models use:

### Home Goals

```text
Regularisation alpha: 0
Numerical predictor basis: 55 columns
Solver: newton-cholesky
```

The full 70-column home design matrix contains linear dependencies, so a deterministic full-rank numerical basis is used for the unregularised home model.

This is a numerical parameterisation decision rather than predictive feature selection.

### Away Goals

```text
Regularisation alpha: 0.001
Predictors: 70
Solver: lbfgs
```

---

# Production Validation

Before release, the exported production bundle was reloaded and tested independently.

Validation included:

- Frozen feature schema
- Model dimensions
- Predictor ordering
- Probability ordering
- Expected-goal reproduction
- Probability reproduction
- Deterministic repeated predictions
- Probability sums
- Artifact hashes
- Reference fixtures

The final production implementation reproduced its reference outputs within the specified numerical tolerances.

---

# 2026–27 Forecasting System

The production model itself remains frozen during the season.

What changes is the **pre-match football state** supplied to the model.

After results occur, the system reconstructs:

- Current Elo ratings
- Rolling team form
- Venue-specific form
- Rest
- Fixture congestion
- Current league-table state
- Matchweek and season progress

The same fitted model is then used to forecast the next eligible fixtures.

There is **no automatic in-season model refitting**.

---

# Why Future Fixtures Cannot All Be Forecast Immediately

Some predictors are dynamic.

For example, the model cannot know a team's five-match form before Matchweek 10 until the earlier matches have actually occurred.

The system therefore uses a sequential forecasting frontier.

Before the season begins:

```text
Exact forecasts currently available: 10
Future fixtures requiring state updates: 370
```

The next group of matches becomes forecastable as preceding results are completed.

---

# Live-Season Runner

The live forecasting system:

1. Reads the official fixture schedule
2. Reads completed 2026–27 results
3. Validates fixture identities
4. Reconstructs the current pre-match state
5. Updates Elo ratings
6. Rebuilds rolling features
7. Reconstructs the league table
8. Produces the frozen 70-feature input
9. Runs the production Poisson model
10. Exports the next set of forecasts

At the pre-season state, the live runner reproduced the original opening-round feature matrix and predictions with:

```text
Feature reproduction error:    0.0
Prediction reproduction error: 0.0
```

This provides a regression test that the operational pipeline matches the validated pre-season implementation.

---

# Streamlit Application

The project includes a public-facing Streamlit interface designed to make the forecasting engine accessible to people without a technical background.

The application includes:

### Fixtures

Upcoming matches displayed using responsive fixture cards containing:

- Expected goals
- Win / draw / loss probabilities
- Model favourite
- Confidence category

### Match Analysis

A deeper fixture view displaying:

- Home probability
- Draw probability
- Away probability
- Expected goals
- Confidence explanation
- Model-vs-market comparison where available

### The Model

A non-technical explanation of:

```text
Pre-match data
      ↓
Goal models
      ↓
Scoreline probabilities
      ↓
Match probabilities
```

### About

An explanation of:

- How forecasts update
- What remains frozen
- How probabilities should be interpreted
- Why expected goals are rates rather than literal score predictions

---

# Repository Structure

```text
premier-league-probability-engine/
│
├── app/
│   ├── streamlit_app.py
│   └── demo_forecasts.csv
│
├── .streamlit/
│   └── config.toml
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_...
│   ├── 02_feature_engineering.ipynb
│   ├── ...
│   ├── 10_production_refit.ipynb
│   └── 11_2026_27_forecasts.ipynb
│
├── outputs/
│   ├── forecasts/
│   │   └── 2026_27/
│   └── tables/
│
├── models/
│
├── requirements-streamlit.txt
├── README.md
└── .gitignore
```

The notebooks document the research and validation process, while the production outputs and Streamlit application expose the final forecasting system.

---

# Running the Streamlit App Locally

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/premier-league-probability-engine.git
```

Move into the project:

```bash
cd premier-league-probability-engine
```

Create and activate a virtual environment if required.

Then install the Streamlit dependencies:

```bash
python -m pip install -r requirements-streamlit.txt
```

Run the application:

```bash
python -m streamlit run app/streamlit_app.py
```

Streamlit will then open the application locally in the browser.

---

# Forecast Data Loading

The Streamlit application prefers forecast files in the following order:

```text
1. outputs/forecasts/2026_27/current_live_forecasts.csv
2. outputs/forecasts/2026_27/opening_round_final_forecast_table.csv
3. app/demo_forecasts.csv
```

This allows the same frontend to display live production outputs during the season while retaining bundled demonstration data for portability.

---

# Updating Forecasts During the Season

The operational workflow is:

```text
Match results occur
        ↓
Results ledger updated
        ↓
Current football state reconstructed
        ↓
70 pre-match features generated
        ↓
Frozen Poisson model applied
        ↓
New fixture probabilities exported
        ↓
Streamlit reads updated forecast file
```

This separation keeps the public interface lightweight.

The Streamlit application does **not** retrain the model every time a user loads the page.

---

# Key Design Principles

## No Target Leakage

Only information available before kickoff is permitted.

---

## Chronological Evaluation

Future matches cannot influence historical predictions.

---

## Probability First

The objective is high-quality probability distributions rather than simply maximising classification accuracy.

---

## Reproducibility

The production package contains a frozen:

- Feature schema
- Transformation pipeline
- Model bundle
- Prediction convention
- Scoreline range
- Reference inputs
- Reference predictions

---

## Model / Market Separation

The model is evaluated against bookmaker markets rather than presented as automatically superior to them.

---

## Production Stability

Once released for the 2026–27 season, the fitted model remains frozen.

This allows its prospective performance to be evaluated cleanly.

---

# Limitations

The current model deliberately remains relatively structured and interpretable.

Potential limitations include:

### Independent goal assumption

The Independent Poisson framework assumes conditional independence between home and away goals.

Real football scores may contain dependencies not completely captured by the features.

---

### No player-level modelling

The model does not directly model:

- Starting line-ups
- Injuries
- Suspensions
- Transfers
- Individual player quality
- Tactical matchups

Some of these effects may indirectly appear through team performance and Elo ratings, but they are not explicitly represented.

---

### Newly promoted teams

Clubs with limited or no recent Premier League history have less directly comparable historical information.

---

### Market information

The production football model does not use bookmaker odds as predictive inputs.

Market probabilities are deliberately reserved for external comparison.

---

### Structural change

Football evolves.

Managerial changes, tactical changes, rule changes and transfer activity can cause historical relationships to shift over time.

---

# Future Work

The most important next stage is **prospective evaluation during the 2026–27 season**.

Planned analysis includes:

- Recording every pre-match forecast
- Measuring live log loss
- Measuring Brier score
- Monitoring calibration
- Comparing model and market forecasts
- Evaluating performance by confidence category
- Evaluating promoted teams separately
- Tracking model-market disagreement over time
- Testing whether apparent historical patterns persist out of sample

Possible future modelling extensions include:

- Dixon-Coles score dependence
- Bivariate Poisson models
- Dynamic team-strength models
- Player availability features
- Transfer-window adjustments
- Expected-goals-based historical team performance
- Bayesian team-strength estimation
- Explicit uncertainty around expected goals
- Additional market-comparison methods

Any future model changes would be evaluated separately rather than silently modifying the frozen 2026–27 production model.

---

# Project Philosophy

A football model should not be judged by whether one favourite wins.

It should be judged by whether its probabilities are useful across a large number of genuinely unseen matches.

The central question for the 2026–27 season is therefore not:

> *Did the model predict this match correctly?*

but:

> **Were events assigned probabilities consistent with how often they actually occurred?**

That distinction is what turns a score-prediction exercise into a probability-modelling project.

---

# Disclaimer

This is an independent quantitative modelling project.

It is **not affiliated with, sponsored by or endorsed by the Premier League, any Premier League club, Pinnacle or any bookmaker**.

The forecasts are model-generated probability estimates produced for research, educational and portfolio purposes.

They do not constitute financial or betting advice, and the historical analysis does not demonstrate a persistent profitable betting strategy.

---

## Author

**Kieran Forkan**  
MMath Mathematics, University of Sheffield

Quantitative modelling · probability · financial mathematics

GitHub: `ADD_GITHUB_PROFILE_URL`

---

## Current Project Status

```text
✓ Feature engineering complete
✓ Baseline models evaluated
✓ Non-linear models evaluated
✓ Poisson scoreline model developed
✓ Walk-forward evaluation complete
✓ Calibration analysis complete
✓ Bookmaker benchmark complete
✓ Final model selected
✓ Production model refitted
✓ Production package validated
✓ 2026–27 fixture pipeline complete
✓ Opening forecasts generated
✓ Live-season update runner operational
✓ Streamlit interface built

→ Next: prospective 2026–27 evaluation
```