from __future__ import annotations

from pathlib import Path
import html

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Premier League Probability Engine",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
FORECAST_DIR = PROJECT_ROOT / "outputs" / "forecasts" / "2026_27"
CURRENT_FORECAST_PATH = FORECAST_DIR / "current_live_forecasts.csv"
FINAL_OPENING_PATH = FORECAST_DIR / "opening_round_final_forecast_table.csv"
DEMO_PATH = APP_DIR / "demo_forecasts.csv"

PURPLE = "#37003C"
PURPLE_2 = "#5B1465"
GREEN = "#00C875"
GREEN_BRIGHT = "#00FF85"
OFF_WHITE = "#F7F5F2"
INK = "#19131D"
MUTED = "#746D77"
BORDER = "#E7E0E8"

st.markdown(
    f"""
    <style>
        :root {{
            --pl-purple: {PURPLE}; --pl-purple-2: {PURPLE_2};
            --pl-green: {GREEN}; --pl-green-bright: {GREEN_BRIGHT};
            --pl-off-white: {OFF_WHITE}; --pl-ink: {INK};
            --pl-muted: {MUTED}; --pl-border: {BORDER};
        }}
        .stApp {{
            background:
                radial-gradient(circle at 88% 2%, rgba(0,200,117,.11), transparent 28rem),
                radial-gradient(circle at 0 0, rgba(55,0,60,.08), transparent 28rem),
                var(--pl-off-white);
            color: var(--pl-ink);
        }}
        [data-testid="stHeader"] {{
            background: rgba(247,245,242,.88); backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(55,0,60,.08);
        }}
        [data-testid="stMainBlockContainer"] {{
            padding-top: 2rem; padding-bottom: 4rem; max-width: 1280px;
        }}
        h1,h2,h3 {{ color: var(--pl-purple); letter-spacing: -.025em; }}
        .hero {{
            overflow:hidden; position:relative; padding:2rem 2.1rem; border-radius:28px;
            color:#fff; margin-bottom:1.35rem;
            background:radial-gradient(circle at 88% 20%, rgba(0,255,133,.32), transparent 16rem),
                       linear-gradient(130deg,#37003C 0%,#4C0755 56%,#211326 100%);
            border:1px solid rgba(255,255,255,.12);
        }}
        .hero-kicker,.section-kicker {{
            color:#BFFFD9; font-size:.78rem; font-weight:800; text-transform:uppercase;
            letter-spacing:.12em; margin-bottom:.5rem;
        }}
        .section-kicker {{ color:var(--pl-green); margin-top:.4rem; }}
        .hero-title {{
            font-size:clamp(2.05rem,4vw,4.2rem); line-height:.98; font-weight:850;
            letter-spacing:-.055em; max-width:850px;
        }}
        .hero-copy {{ max-width:720px; margin-top:1rem; font-size:1.02rem; color:rgba(255,255,255,.82); }}
        .status-row {{ display:flex; flex-wrap:wrap; gap:.55rem; margin-top:1.25rem; }}
        .hero-chip {{
            display:inline-flex; gap:.45rem; align-items:center; padding:.5rem .72rem;
            border-radius:999px; background:rgba(255,255,255,.10);
            border:1px solid rgba(255,255,255,.14); color:#fff; font-size:.86rem;
        }}
        .hero-chip-dot {{
            width:.52rem; height:.52rem; border-radius:99px; background:var(--pl-green-bright);
            box-shadow:0 0 0 4px rgba(0,255,133,.12);
        }}
        .fixture-card {{
            background:rgba(255,255,255,.92); border:1px solid var(--pl-border);
            border-radius:24px; padding:1.15rem 1.2rem 1rem;
            box-shadow:0 10px 30px rgba(55,0,60,.055); min-height:100%;
        }}
        .fixture-date {{
            color:var(--pl-muted); font-size:.77rem; font-weight:700; text-transform:uppercase;
            letter-spacing:.08em; margin-bottom:.8rem;
        }}
        .team-row {{ display:grid; grid-template-columns:40px 1fr auto; align-items:center; gap:.72rem; margin:.62rem 0; }}
        .team-badge {{
            width:40px; height:40px; display:grid; place-items:center; border-radius:12px;
            font-weight:850; font-size:.75rem; color:#fff;
            background:linear-gradient(145deg,var(--pl-purple),var(--pl-purple-2));
        }}
        .team-name {{ color:var(--pl-ink); font-weight:750; }}
        .team-xg {{ color:var(--pl-purple); font-weight:850; font-variant-numeric:tabular-nums; }}
        .xg-label {{ color:var(--pl-muted); font-weight:600; font-size:.7rem; margin-left:.15rem; }}
        .prob-list {{ margin-top:1rem; padding-top:.95rem; border-top:1px solid var(--pl-border); }}
        .prob-row {{
            display:grid; grid-template-columns:minmax(78px,1fr) 2.1fr 52px; align-items:center;
            gap:.65rem; margin:.52rem 0; font-size:.82rem;
        }}
        .prob-label {{ color:var(--pl-ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
        .prob-track {{ height:9px; border-radius:999px; background:#ECE7ED; overflow:hidden; }}
        .prob-fill {{ height:100%; border-radius:inherit; background:linear-gradient(90deg,var(--pl-purple),var(--pl-green)); }}
        .prob-value {{ text-align:right; color:var(--pl-purple); font-weight:850; font-variant-numeric:tabular-nums; }}
        .fixture-footer {{ margin-top:1rem; display:flex; justify-content:space-between; align-items:center; gap:.8rem; flex-wrap:wrap; }}
        .confidence {{
            display:inline-flex; align-items:center; gap:.4rem; border-radius:999px; padding:.4rem .62rem;
            font-size:.74rem; font-weight:800; border:1px solid rgba(55,0,60,.10);
        }}
        .confidence-strong {{ color:#063C26; background:#DDF8E9; }}
        .confidence-moderate {{ color:#4C3100; background:#FFF0C7; }}
        .confidence-low {{ color:#5A435F; background:#F0E9F2; }}
        .model-favourite {{ font-size:.77rem; color:var(--pl-muted); }}
        .model-favourite strong {{ color:var(--pl-purple); }}
        .detail-hero,.explain-card {{ background:#fff; border:1px solid var(--pl-border); border-radius:24px; padding:1.35rem; }}
        .detail-team {{ color:var(--pl-purple); font-size:clamp(1.35rem,3vw,2.5rem); font-weight:850; letter-spacing:-.035em; }}
        .versus {{ color:var(--pl-muted); font-size:.82rem; text-transform:uppercase; letter-spacing:.1em; font-weight:800; text-align:center; }}
        .explain-num {{ color:var(--pl-green); font-size:.76rem; font-weight:900; letter-spacing:.08em; text-transform:uppercase; }}
        .market-box {{ border:1px solid rgba(0,200,117,.25); background:#F2FBF6; border-radius:22px; padding:1rem 1.1rem; }}
        .tiny-note {{ color:var(--pl-muted); font-size:.78rem; }}
        .footer-note {{ margin-top:2.2rem; padding-top:1rem; border-top:1px solid var(--pl-border); color:var(--pl-muted); font-size:.75rem; }}
        [data-testid="stMetric"] {{ background:#fff; border:1px solid var(--pl-border); padding:.95rem; border-radius:18px; }}
        div[data-testid="stButton"]>button {{ border-radius:999px; border:1px solid rgba(55,0,60,.18); font-weight:700; }}
        @media(max-width:720px) {{ .hero{{padding:1.45rem;border-radius:22px}} .fixture-card{{border-radius:20px}} .prob-row{{grid-template-columns:82px 1fr 48px}} }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def read_csv_if_exists(path_string: str) -> pd.DataFrame | None:
    path = Path(path_string)
    return pd.read_csv(path, low_memory=False) if path.is_file() else None


def load_forecasts() -> tuple[pd.DataFrame, str]:
    selected = None
    selected_path = None
    for path in (CURRENT_FORECAST_PATH, FINAL_OPENING_PATH, DEMO_PATH):
        frame = read_csv_if_exists(str(path))
        if frame is not None and not frame.empty:
            selected, selected_path = frame.copy(), path
            break
    if selected is None:
        raise FileNotFoundError("No forecast CSV was found.")

    if selected_path == CURRENT_FORECAST_PATH and FINAL_OPENING_PATH.is_file():
        rich = read_csv_if_exists(str(FINAL_OPENING_PATH))
        if rich is not None:
            keys = ["OfficialHomeTeam", "OfficialAwayTeam"]
            extras = [
                "Confidence", "MarketProbability_H", "MarketProbability_D", "MarketProbability_A",
                "MarketFavourite", "TotalVariationDistance", "PrimaryWatchlist",
                "LongshotSensitive", "ModalScoreline",
            ]
            extras = [c for c in extras if c in rich.columns]
            if extras:
                selected = selected.merge(rich[keys + extras], on=keys, how="left")

    if "Kickoff" in selected.columns:
        selected["Kickoff"] = pd.to_datetime(selected["Kickoff"], errors="coerce")

    required = [
        "OfficialHomeTeam", "OfficialAwayTeam", "HomeExpectedGoals", "AwayExpectedGoals",
        "Probability_H", "Probability_D", "Probability_A",
    ]
    missing = [c for c in required if c not in selected.columns]
    if missing:
        raise ValueError(f"Forecast data missing columns: {missing}")
    return selected.reset_index(drop=True), selected_path.name


def confidence_for_row(row: pd.Series) -> str:
    probs = np.sort(np.array([row.Probability_H, row.Probability_D, row.Probability_A], dtype=float))
    favourite, margin = float(probs[-1]), float(probs[-1] - probs[-2])
    if favourite >= .60 and margin >= .25:
        return "Strong"
    if favourite >= .45 and margin >= .12:
        return "Moderate"
    return "Low"


def favourite_for_row(row: pd.Series) -> str:
    probs = [float(row.Probability_H), float(row.Probability_D), float(row.Probability_A)]
    idx = int(np.argmax(probs))
    return row.OfficialHomeTeam if idx == 0 else row.OfficialAwayTeam if idx == 2 else "Draw"


try:
    FORECASTS, DATA_SOURCE_NAME = load_forecasts()
except Exception as exc:
    st.error(f"Could not load forecasts: {exc}")
    st.stop()

fallback_conf = FORECASTS.apply(confidence_for_row, axis=1)
if "Confidence" not in FORECASTS.columns:
    FORECASTS["Confidence"] = fallback_conf
else:
    FORECASTS["Confidence"] = FORECASTS["Confidence"].fillna(fallback_conf)

fallback_fav = FORECASTS.apply(favourite_for_row, axis=1)
if "ModelFavourite" not in FORECASTS.columns:
    FORECASTS["ModelFavourite"] = fallback_fav
else:
    FORECASTS["ModelFavourite"] = FORECASTS["ModelFavourite"].fillna(fallback_fav)

FORECASTS["FixtureLabel"] = FORECASTS["OfficialHomeTeam"].astype(str) + "  vs  " + FORECASTS["OfficialAwayTeam"].astype(str)


def esc(value) -> str:
    return html.escape(str(value))


def abbrev(team: str) -> str:
    words = [w for w in str(team).replace("&", " ").replace("-", " ").split() if w.lower() not in {"and", "of", "the"}]
    return (words[0][:3] if len(words) == 1 else "".join(w[0] for w in words[:3])).upper()


def fixture_datetime(row: pd.Series) -> str:
    kickoff = row.get("Kickoff")
    return "Upcoming fixture" if pd.isna(kickoff) else pd.Timestamp(kickoff).strftime("%a %d %b · %H:%M").upper()


def confidence_class(label: str) -> str:
    return {"Strong":"confidence-strong", "Moderate":"confidence-moderate", "Low":"confidence-low"}.get(str(label), "confidence-low")


def probability_bar(label: str, probability: float) -> str:
    pct = 100 * float(probability)
    return f'''<div class="prob-row"><div class="prob-label">{esc(label)}</div><div class="prob-track"><div class="prob-fill" style="width:{min(max(pct,0),100):.1f}%"></div></div><div class="prob-value">{pct:.1f}%</div></div>'''


def render_fixture_card(row: pd.Series, key: str):
    home, away, confidence = row.OfficialHomeTeam, row.OfficialAwayTeam, str(row.Confidence)
    st.markdown(
        f'''<div class="fixture-card">
        <div class="fixture-date">{esc(fixture_datetime(row))}</div>
        <div class="team-row"><div class="team-badge">{esc(abbrev(home))}</div><div class="team-name">{esc(home)}</div><div class="team-xg">{float(row.HomeExpectedGoals):.2f}<span class="xg-label">xG</span></div></div>
        <div class="team-row"><div class="team-badge">{esc(abbrev(away))}</div><div class="team-name">{esc(away)}</div><div class="team-xg">{float(row.AwayExpectedGoals):.2f}<span class="xg-label">xG</span></div></div>
        <div class="prob-list">{probability_bar(home,row.Probability_H)}{probability_bar('Draw',row.Probability_D)}{probability_bar(away,row.Probability_A)}</div>
        <div class="fixture-footer"><div class="confidence {confidence_class(confidence)}">{esc(confidence)} confidence</div><div class="model-favourite">Model favourite · <strong>{esc(row.ModelFavourite)}</strong></div></div>
        </div>''',
        unsafe_allow_html=True,
    )
    if st.button("View match analysis →", key=f"analyse_{key}", use_container_width=True):
        st.session_state["selected_fixture"] = row.FixtureLabel
        st.switch_page(MATCH_PAGE)


def selected_row() -> pd.Series:
    labels = FORECASTS.FixtureLabel.tolist()
    current = st.session_state.get("selected_fixture", labels[0])
    if current not in labels:
        current = labels[0]
    selected = st.selectbox("Choose a fixture", labels, index=labels.index(current), key="analysis_fixture_picker")
    st.session_state["selected_fixture"] = selected
    return FORECASTS.loc[FORECASTS.FixtureLabel == selected].iloc[0]


def render_footer():
    st.markdown('''<div class="footer-note">Independent probability-modelling project. Not affiliated with or endorsed by the Premier League or any club. Probabilities are model estimates, not guarantees or betting advice.</div>''', unsafe_allow_html=True)


def fixtures_page():
    st.markdown('''<div class="hero"><div class="hero-kicker">2026–27 · Probability Engine</div><div class="hero-title">See the match.<br>See the probabilities.</div><div class="hero-copy">A live Premier League forecasting model translating expected goals, team form and pre-match information into easy-to-read win, draw and loss probabilities.</div><div class="status-row"><div class="hero-chip"><span class="hero-chip-dot"></span> Frozen production model</div><div class="hero-chip">70 pre-match predictors</div><div class="hero-chip">Independent Poisson forecasts</div></div></div>''', unsafe_allow_html=True)

    c1,c2,c3 = st.columns([1.4,1,1])
    teams = ["All clubs"] + sorted(set(FORECASTS.OfficialHomeTeam) | set(FORECASTS.OfficialAwayTeam))
    with c1: team_filter = st.selectbox("Club", teams)
    with c2: conf_filter = st.selectbox("Confidence", ["All","Strong","Moderate","Low"])
    with c3: sort_mode = st.selectbox("Sort", ["Kickoff","Highest confidence"])

    filtered = FORECASTS.copy()
    if team_filter != "All clubs":
        filtered = filtered.loc[(filtered.OfficialHomeTeam == team_filter) | (filtered.OfficialAwayTeam == team_filter)]
    if conf_filter != "All":
        filtered = filtered.loc[filtered.Confidence == conf_filter]
    if sort_mode == "Kickoff" and "Kickoff" in filtered.columns:
        filtered = filtered.sort_values("Kickoff", kind="mergesort")
    else:
        filtered = filtered.assign(_fav=filtered[["Probability_H","Probability_D","Probability_A"]].max(axis=1)).sort_values("_fav", ascending=False)

    st.markdown('<div class="section-kicker">Upcoming fixtures</div>', unsafe_allow_html=True)
    st.subheader(f"{len(filtered)} modelled fixtures")
    rows = list(filtered.iterrows())
    if not rows:
        st.info("No fixtures match the current filters.")
    for i in range(0,len(rows),2):
        cols = st.columns(2, gap="large")
        for j in range(2):
            if i+j < len(rows):
                idx,row = rows[i+j]
                with cols[j]: render_fixture_card(row, f"{idx}_{i}_{j}")
    st.caption(f"Data loaded from: {DATA_SOURCE_NAME}")
    render_footer()


def match_analysis_page():
    st.markdown('<div class="section-kicker">Match analysis</div>', unsafe_allow_html=True)
    st.title("Inside the forecast")
    st.write("Pick a fixture to see what the model is saying without needing to read a notebook.")
    row = selected_row(); home=row.OfficialHomeTeam; away=row.OfficialAwayTeam; confidence=str(row.Confidence)
    st.markdown(f'''<div class="detail-hero"><div class="fixture-date">{esc(fixture_datetime(row))}</div><div style="display:grid;grid-template-columns:1fr auto 1fr;gap:1rem;align-items:center;"><div><div class="detail-team">{esc(home)}</div><div class="tiny-note">Expected goals · {float(row.HomeExpectedGoals):.2f}</div></div><div class="versus">vs</div><div style="text-align:right"><div class="detail-team">{esc(away)}</div><div class="tiny-note">Expected goals · {float(row.AwayExpectedGoals):.2f}</div></div></div></div>''', unsafe_allow_html=True)

    p1,p2,p3 = st.columns(3)
    p1.metric(home, f"{100*float(row.Probability_H):.1f}%")
    p2.metric("Draw", f"{100*float(row.Probability_D):.1f}%")
    p3.metric(away, f"{100*float(row.Probability_A):.1f}%")

    left,right = st.columns([1.15,.85], gap="large")
    with left:
        st.subheader("What the model expects")
        st.markdown(probability_bar(home,row.Probability_H)+probability_bar("Draw",row.Probability_D)+probability_bar(away,row.Probability_A), unsafe_allow_html=True)
        st.markdown(f'''<div class="fixture-footer"><div class="confidence {confidence_class(confidence)}">{esc(confidence)} confidence</div><div class="model-favourite">Model favourite · <strong>{esc(row.ModelFavourite)}</strong></div></div>''', unsafe_allow_html=True)
    with right:
        st.subheader("Expected goals")
        a,b = st.columns(2)
        a.metric(home, f"{float(row.HomeExpectedGoals):.2f} xG")
        b.metric(away, f"{float(row.AwayExpectedGoals):.2f} xG")
        if "ModalScoreline" in row.index and pd.notna(row.get("ModalScoreline")):
            st.metric("Most likely exact score", str(row.ModalScoreline))

    st.divider(); st.subheader("How confident is that?")
    if confidence == "Strong":
        msg = "The favourite is at least 60% and at least 25 percentage points ahead of the next-most-likely outcome."
    elif confidence == "Moderate":
        msg = "The favourite is at least 45% and at least 12 percentage points ahead of the next-most-likely outcome."
    else:
        msg = "The result is relatively open: the leading outcome does not clear the Strong or Moderate separation thresholds."
    st.info(msg)

    market_cols = ["MarketProbability_H","MarketProbability_D","MarketProbability_A"]
    if all(c in row.index and pd.notna(row.get(c)) for c in market_cols):
        st.subheader("Model vs market")
        m1,m2,m3 = st.columns(3)
        for box,label,model_col,market_col in [
            (m1,home,"Probability_H","MarketProbability_H"),
            (m2,"Draw","Probability_D","MarketProbability_D"),
            (m3,away,"Probability_A","MarketProbability_A"),
        ]:
            box.metric(label, f"{100*float(row[model_col]):.1f}%", delta=f"{100*(float(row[model_col])-float(row[market_col])):+.1f}pp vs market")
        if "TotalVariationDistance" in row.index and pd.notna(row.get("TotalVariationDistance")):
            tv=float(row.TotalVariationDistance)
            label="Large disagreement" if tv>=.10 else "Meaningful disagreement" if tv>=.07 else "Some disagreement" if tv>=.03 else "Very similar"
            st.write(f"**Overall probability disagreement:** {label} ({tv:.3f} TV distance)")

    with st.expander("Technical details"):
        st.write("Separate Poisson regressions estimate expected home and away goals. Those rates generate scoreline probabilities from 0–0 through 10–10, which are aggregated into H / D / A probabilities.")
        st.write("The model uses 70 pre-match predictors covering Elo, recent form, venue form, rest, congestion, season progress and league-table state.")
    render_footer()


def model_page():
    st.markdown('<div class="section-kicker">The model</div>', unsafe_allow_html=True)
    st.title("From football data to probabilities")
    st.write("The maths is serious. The interface does not need to be. Here is the model in four steps.")
    cols=st.columns(4,gap="medium")
    steps=[
        ("01 · PRE-MATCH STATE","Know the teams","Elo, form, venue form, rest, congestion and league-table information are reconstructed before kickoff."),
        ("02 · GOAL MODELS","Estimate goals","Separate Poisson regressions estimate expected home and away goals."),
        ("03 · SCORELINES","Map the score space","The expected-goal rates produce probabilities for every scoreline from 0–0 to 10–10."),
        ("04 · MATCH PROBABILITY","Add them up","Scorelines are aggregated into home-win, draw and away-win probabilities."),
    ]
    for col,(num,title,copy) in zip(cols,steps):
        with col: st.markdown(f'''<div class="explain-card"><div class="explain-num">{esc(num)}</div><h3 style="margin-top:.55rem">{esc(title)}</h3><div class="tiny-note" style="font-size:.86rem">{esc(copy)}</div></div>''', unsafe_allow_html=True)
    st.divider(); st.subheader("Production model at a glance")
    a,b,c,d=st.columns(4); a.metric("Training fixtures","4,180"); b.metric("Historical seasons","11"); c.metric("Frozen predictors","70"); d.metric("Output","H / D / A")
    st.subheader("Why Independent Poisson?")
    st.write("Chronological walk-forward testing gave Independent Poisson the best overall balance of predictive performance, stability, interpretability and production suitability. Its advantage over the alternative ensemble was small, so the project does not claim decisive statistical superiority.")
    st.subheader("A credibility check")
    st.markdown('''<div class="market-box"><strong>The market benchmark was stronger historically.</strong><br><br>Closing bookmaker probabilities achieved lower historical log loss than the model. This is a forecasting engine and research showcase, not a claim that a profitable betting edge has been proven.</div>''', unsafe_allow_html=True)
    with st.expander("Technical model specification"):
        st.write("**Model family:** Independent Poisson regression")
        st.write("**Home-goal regularisation:** α = 0")
        st.write("**Away-goal regularisation:** α = 0.001")
        st.write("**Scoreline grid:** 0–10 goals for each team, renormalised")
        st.write("**Probability order:** (H, D, A)")
        st.write("**Production training window:** 2015–16 through 2025–26")
        st.write("**In-season retraining:** None — the production model remains frozen")
    render_footer()


def about_page():
    st.markdown('<div class="section-kicker">About the project</div>', unsafe_allow_html=True)
    st.title("A probability engine, not a score predictor")
    st.write("The point is not to announce that one result *will* happen. It is to quantify uncertainty before kickoff.")
    l,r=st.columns([1.05,.95],gap="large")
    with l:
        st.subheader("What changes during the season?")
        st.write("The model stays frozen. The information going into it changes as matches are completed.")
        st.markdown("""1. Results enter the season ledger.\n2. Elo and team histories update.\n3. Form, rest and congestion are reconstructed.\n4. The pre-match table is rebuilt.\n5. The next eligible fixtures receive new probabilities.""")
    with r:
        st.subheader("What does not change?")
        st.markdown("""- Fitted Poisson estimators\n- Median imputer\n- Scaler\n- Frozen 70-feature schema\n- H / D / A probability definition""")
    st.subheader("How to read a forecast")
    e1,e2,e3=st.columns(3)
    cards=[
        (e1,"Probability","70% is not certainty","A 70% favourite is expected to fail roughly three times in ten if the probability is well calibrated."),
        (e2,"Expected goals","xG is a rate","A team with 1.7 expected goals is not being predicted to score exactly 1.7. It is the model's goal-rate estimate."),
        (e3,"Confidence","Separation matters","Confidence depends on both the favourite's probability and how far it sits ahead of the second-most-likely outcome."),
    ]
    for col,num,title,copy in cards:
        with col: st.markdown(f'''<div class="explain-card"><div class="explain-num">{esc(num)}</div><h3>{esc(title)}</h3><div class="tiny-note" style="font-size:.86rem">{esc(copy)}</div></div>''', unsafe_allow_html=True)
    render_footer()


FIXTURES_PAGE = st.Page(fixtures_page, title="Fixtures", icon="⚽", default=True)
MATCH_PAGE = st.Page(match_analysis_page, title="Match Analysis", icon="🔎")
MODEL_PAGE = st.Page(model_page, title="The Model", icon="🧠")
ABOUT_PAGE = st.Page(about_page, title="About", icon="ℹ️")

page = st.navigation([FIXTURES_PAGE, MATCH_PAGE, MODEL_PAGE, ABOUT_PAGE], position="top")
page.run()
