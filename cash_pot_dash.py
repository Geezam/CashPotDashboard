# cash_pot_dash.py
import streamlit as st
from functions import (load_data, render_global_overview,
                       render_detail_dashboard)
from constants import EMOJI_LIST, NUM_MEANINGS

st.set_page_config(page_title="Cash Pot Draw Analyzer 2017-2021",
                   layout="wide")
df = load_data()

meaning_map = {}
for num, meaning in NUM_MEANINGS.items():
    emoji = EMOJI_LIST[num - 1] if (num - 1) < len(EMOJI_LIST) else ""
    meaning_map[num] = f"{meaning} {emoji}"

st.title("🎱 Cash Pot Draw Analyzer 2017-2021")

if df.empty:
    st.stop()

all_numbers = sorted(df['drawn_number'].unique())
options = ["Global Overview"] + list(all_numbers)


def format_func(option):
    if option == "Global Overview":
        return "2017 to 2021 Numbers Overview"
    else:
        meaning = meaning_map.get(option, "Unknown")
        return f"{option} - {meaning}"


selection = st.selectbox("Select a View:", options, format_func=format_func)

st.divider()

if selection == "Global Overview":
    render_global_overview(df, meaning_map)

else:
    selected_number = selection
    current_meaning = meaning_map.get(selected_number, "")

    st.header(f"Detailed Analysis for: {selected_number} ({current_meaning})")

    years = sorted(df['year'].unique(), reverse=True)
    tab_labels = ["All Time"] + [str(y) for y in years]
    tabs = st.tabs(tab_labels)

    # Tab 0: All Time
    with tabs[0]:
        subset = df[df['drawn_number'] == selected_number]
        render_detail_dashboard(subset, "All Time", len(df),
                                current_meaning)

    # Remaining Tabs: Individual Years
    for i, year in enumerate(years):
        with tabs[i+1]:
            subset_year = df[
                (df['drawn_number'] == selected_number) &
                (df['year'] == year)
            ]
            total_draws_in_year = len(df[df['year'] == year])
            render_detail_dashboard(subset_year, str(year),
                                    total_draws_in_year,
                                    current_meaning)
