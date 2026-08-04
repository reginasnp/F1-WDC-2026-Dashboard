import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================
# Page Config
# ==========================================

st.set_page_config(
    page_title="Formula 1 World Drivers Championship 2026",
    page_icon="🏎️",
    layout="wide",
)

# ==========================================
# Dark Theme CSS
# ==========================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0B0D17;
        color: white;
    }
    h1, h2, h3 {
        color: white;
    }
    [data-testid="stMetricValue"] {
        color: #FF1801;
        font-size: 34px;
    }
    [data-testid="stMetricLabel"] {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# Team Colors
# ==========================================

TEAM_COLORS = {
    "Red Bull": "#3671C6",
    "Ferrari": "#E80020",
    "McLaren": "#FF8000",
    "Mercedes": "#27F4D2",
    "Williams": "#005AFF",
    "Alpine": "#2293D1",
    "Aston Martin": "#006F62",
    "Sauber": "#52E252",
    "RB": "#6692FF",
    "Haas": "#B6BABD",
}


def style_fig(fig, height=500):
    """Terapkan tema dark + hover style yang konsisten ke semua chart."""
    fig.update_traces(
    hovertemplate="<b>%{x}</b><br>Value: %{y}<extra></extra>"
)
    fig.update_layout(
        template="plotly_dark",
        title_x=0.5,
        height=height,
        legend_title="",
        font=dict(size=14),
        margin=dict(l=30, r=30, t=60, b=30),
    )
    return fig


# ==========================================
# Load Data
# ==========================================

project_path = Path(__file__).resolve().parent
wdc = pd.read_csv(project_path / "data" / "processed" / "WDC_clean.csv")

# ==========================================
# Header
# ==========================================

st.image("https://upload.wikimedia.org/wikipedia/commons/3/33/F1.svg", width=180)
st.title("🏁 Formula 1 World Drivers Championship 2026")
st.caption("Interactive Dashboard • Season 2026")
st.markdown("---")

# ==========================================
# Sidebar
# ==========================================

# ==========================================
# Sidebar
# ==========================================

with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/3/33/F1.svg",
        width=120,
    )

    st.title("Navigation")

    st.markdown("---")

    st.markdown("### Dashboard Info")

    st.write("""
Formula 1 Season 2026

Visual Analytics Dashboard

Built using Streamlit + Plotly
""")

    st.markdown("---")

    st.success("Data Source\n\nWDC_clean.csv")

    st.markdown("---")

    st.header("Filter Dashboard")

    teams = ["All Teams"] + sorted(wdc["TeamName"].unique())
    selected_team = st.selectbox("Select Team", teams)

    if selected_team != "All Teams":
        filtered = wdc[wdc["TeamName"] == selected_team].copy()
    else:
        filtered = wdc.copy()

    drivers = ["All Drivers"] + sorted(filtered["FullName"].unique())
    selected_driver = st.selectbox("Select Driver", drivers)

    if selected_driver != "All Drivers":
        filtered = filtered[
            filtered["FullName"] == selected_driver
        ]

    st.markdown("---")

    st.download_button(
        label="📥 Download Dataset",
        data=filtered.to_csv(index=False),
        file_name="WDC_2026.csv",
        mime="text/csv",
    )

# Team Filter
teams = ["All Teams"] + sorted(wdc["TeamName"].unique())
selected_team = st.selectbox("Select Team", teams)

# Buat filtered dulu
if selected_team != "All Teams":
    filtered = wdc[wdc["TeamName"] == selected_team].copy()
else:
    filtered = wdc.copy()

# Driver Filter
drivers = ["All Drivers"] + sorted(filtered["FullName"].unique())
selected_driver = st.selectbox("Select Driver", drivers)

if selected_driver != "All Drivers":
    filtered = filtered[
        filtered["FullName"] == selected_driver
    ]

# ==========================================
# KPI Cards
# ==========================================

driver_points = (
    filtered.groupby("FullName", as_index=False)["Points"]
    .sum()
    .sort_values("Points", ascending=False)
)

leader = driver_points.iloc[0]["FullName"]
leader_points = driver_points.iloc[0]["Points"]

total_races = filtered["GrandPrix"].nunique()
total_points = filtered["Points"].sum()
total_drivers = filtered["FullName"].nunique()
total_teams = filtered["TeamName"].nunique()

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric(
    "🏆 Championship Leader",
    leader,
)

k2.metric(
    "⭐ Leader Points",
    int(leader_points),
)

k3.metric(
    "🏁 Total Races",
    total_races,
)

k4.metric(
    "👥 Drivers",
    total_drivers,
)

k5.metric(
    "🏎️ Teams",
    total_teams,
)

k6.metric(
    "📊 Total Points",
    int(total_points),
)

st.markdown("---")

# ==========================================
# Driver Championship
# ==========================================

driver = driver_points.merge(
    filtered[["FullName", "TeamName"]].drop_duplicates(), on="FullName"
)

driver_fig = px.bar(
    driver,
    x="FullName",
    y="Points",
    color="TeamName",
    color_discrete_map=TEAM_COLORS,
    title="Driver Championship Standings",
    text_auto=True,
)
driver_fig.update_layout(xaxis_title="Driver", yaxis_title="Points")
style_fig(driver_fig)

# ==========================================
# Constructor Championship
# ==========================================

constructor = (
    filtered.groupby("TeamName", as_index=False)["Points"]
    .sum()
    .sort_values("Points", ascending=False)
)

constructor_fig = px.bar(
    constructor,
    x="TeamName",
    y="Points",
    color="TeamName",
    color_discrete_map=TEAM_COLORS,
    title="Constructor Championship Standings",
    text_auto=True,
)
constructor_fig.update_layout(xaxis_title="Team", yaxis_title="Points", showlegend=False)
style_fig(constructor_fig)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(driver_fig, use_container_width=True)
with col2:
    st.plotly_chart(constructor_fig, use_container_width=True)

st.markdown("---")

# ==========================================
# Championship Progression
# ==========================================

# Urutan race diambil dari urutan kemunculan di data (asumsi CSV sudah kronologis),
# bukan di-hardcode, supaya otomatis mengikuti kalender yang ada di file sumber.
race_order = list(pd.unique(wdc["GrandPrix"]))

progression = filtered.copy()
progression["GrandPrix"] = pd.Categorical(
    progression["GrandPrix"], categories=race_order, ordered=True
)
progression = progression.sort_values(["FullName", "GrandPrix"])
progression["CumulativePoints"] = progression.groupby("FullName")["Points"].cumsum()

progression_fig = px.line(
    progression,
    x="GrandPrix",
    y="CumulativePoints",
    color="FullName",
    markers=True,
    title="Championship Progression",
)
progression_fig.update_layout(
    xaxis_title="Grand Prix",
    yaxis_title="Cumulative Points",
    legend_title="Driver",
    xaxis_tickangle=-45,
)
style_fig(progression_fig, height=600)

st.plotly_chart(progression_fig, use_container_width=True)
st.markdown("---")

# ==========================================
# Race Wins & Podium Finishes
# ==========================================

wins = (
    filtered[filtered["Position"] == 1]
    .groupby("FullName", as_index=False)
    .size()
    .rename(columns={"size": "Wins"})
    .sort_values("Wins", ascending=False)
)
wins_fig = px.bar(
    wins, x="FullName", y="Wins", color="Wins", title="Race Wins by Driver", text_auto=True
)
wins_fig.update_layout(xaxis_title="Driver", yaxis_title="Wins", showlegend=False)
style_fig(wins_fig)

podiums = (
    filtered[filtered["Position"] <= 3]
    .groupby("FullName", as_index=False)
    .size()
    .rename(columns={"size": "Podiums"})
    .sort_values("Podiums", ascending=False)
)
podium_fig = px.bar(
    podiums, x="FullName", y="Podiums", color="Podiums", title="Podium Finishes", text_auto=True
)
podium_fig.update_layout(xaxis_title="Driver", yaxis_title="Podiums", showlegend=False)
style_fig(podium_fig)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(wins_fig, use_container_width=True)
with col4:
    st.plotly_chart(podium_fig, use_container_width=True)

st.markdown("---")

# ==========================================
# Average Finish Position
# ==========================================

average_finish = (
    filtered.groupby("FullName", as_index=False)["Position"]
    .mean()
    .rename(columns={"Position": "Average Finish"})
    .sort_values("Average Finish", ascending=True)
)

average_fig = px.bar(
    average_finish,
    x="FullName",
    y="Average Finish",
    color="Average Finish",
    title="Average Finish Position",
    text_auto=".2f",
)

average_fig.update_layout(
    xaxis_title="Driver",
    yaxis_title="Average Finish Position",
    showlegend=False,
)

average_fig.update_yaxes(autorange="reversed")

style_fig(average_fig)

st.plotly_chart(average_fig, use_container_width=True)

# ==========================================
# Dataset Preview
# ==========================================

with st.expander("📋 Preview Dataset"):
    st.dataframe(filtered, use_container_width=True)

# ==========================================
# GitHub Repository
# ==========================================

st.markdown(
    """
### 🌐 GitHub Repository

[View Source Code on GitHub](https://github.com/reginasnp/F1-WDC-2026)
"""
)

# ==========================================
# Footer
# ==========================================

st.markdown("---")

st.caption(
    "🏎️ Formula 1 WDC 2026 Dashboard | Built with Streamlit & Plotly | © Regina Syahda Nabia Putri"
)