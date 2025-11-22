# Interactive Streamlit Dashboard of Cash Pot results from 2017 to 2021
# Geezam.com
# https://cashpotdashboard.streamlit.app/

import streamlit as st
from functions import (load_data, render_overview, render_details)
from constants import EMOJI_LIST, NUM_MEANINGS

st.set_page_config(page_title="Cash Pot Draw Analyzer 2017-2021",
                   page_icon="💰", layout="wide")
# Pandas function for data frame using CSV files
df = load_data()
# Mapping numbers 1-36 to meanings and emojis
meaning_map = {}
for num, meaning in NUM_MEANINGS.items():
    emoji = EMOJI_LIST[num - 1] if (num - 1) < len(EMOJI_LIST) else ""
    meaning_map[num] = f"{meaning} {emoji}"
# Dynamic years in case dataset is expanded in the future
if not df.empty:
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    st.title(f"📊 Cash Pot Draw Analyzer {min_year}-{max_year}")
else:
    st.title("📊 Cash Pot Draw Analyzer")
    st.stop()

# Sidebar with info and disclaimer
with st.sidebar:
    st.header("ℹ️ Guide")
    st.markdown(f"""
    Welcome to the **Cash Pot Analyzer**. "Cash Pot" is a daily lottery game
                popular in Jamaica.

    **How to use:**
    1. **💾 ALL DATA OVERVIEW:** Click the top button to see the frequency of
                all numbers combined.
    2. **🔢 Specific Numbers:** Click any button in the grid (1-36) to see
                details for that specific number.
    3. **💡 Tip:** Use the tabs on the main screen to switch between
                'All Time' data and specific years."

    **Data Details:**
    - **Range:** {min_year} to {max_year}
    - **Total Draws:** {len(df):,}
    """)

    st.divider()
    st.caption("Created by [Geezam](https://geezam.com), coded in Python"
               " and delivered using Streamlit")

    st.caption("""
    **⚠️ Disclaimer:** This application is designed for educational purposes
               to demonstrate data analysis techniques. The data provided
               here is not guaranteed to be accurate or complete. The creator
               (Geezam) accepts no liability for any errors, omissions, or
               decisions made based on this information. This is not a
               gambling tool.
    """)

# Default view is of all numbers data
if 'selected_view' not in st.session_state:
    st.session_state.selected_view = "Global Overview"


# For changing views
def set_view(view_name):
    st.session_state.selected_view = view_name


st.write("### Select a View")


if st.session_state.selected_view == "Global Overview":
    btn_style = "primary"
else:
    btn_style = "secondary"

if st.button("💾 ALL DATA OVERVIEW",
             type=btn_style,
             use_container_width=True,
             on_click=set_view,
             args=("Global Overview",)):
    pass

st.write("Or select a specific number:")

all_numbers = sorted(df['drawn_number'].unique())

# Number buttons in 12 columns thus 3 rows. 12 x 3 = 36 numbers
cols = st.columns(12)

for i, number in enumerate(all_numbers):
    col_index = i % 12

    emoji = EMOJI_LIST[number - 1] if (number - 1) < len(EMOJI_LIST) else ""
    button_label = f"{number} {emoji}"

    if st.session_state.selected_view == number:
        btn_style = "primary"
    else:
        btn_style = "secondary"

    with cols[col_index]:
        if st.button(button_label,
                     key=f"btn_{number}",
                     type=btn_style,
                     use_container_width=True,
                     on_click=set_view,
                     args=(number,)):
            pass

st.divider()

# Logic for rendering charts depending on selection
selection = st.session_state.selected_view

if selection == "Global Overview":
    render_overview(df, meaning_map)

else:
    selected_number = selection
    current_meaning = meaning_map.get(selected_number, "")

    st.header(f"Detailed Analysis for: {selected_number} ({current_meaning})")

    years = sorted(df['year'].unique(), reverse=True)
    tab_labels = ["All Time"] + [str(y) for y in years]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        subset = df[df['drawn_number'] == selected_number]
        render_details(subset, "All Time", len(df),
                       current_meaning)

    for i, year in enumerate(years):
        with tabs[i+1]:
            subset_year = df[
                (df['drawn_number'] == selected_number) &
                (df['year'] == year)
            ]
            total_draws_in_year = len(df[df['year'] == year])
            render_details(subset_year, str(year),
                           total_draws_in_year,
                           current_meaning)

st.divider()

st.caption("""
    **⚠️ Disclaimer:** This application is designed for educational purposes
               to demonstrate data analysis techniques. The data provided
               here is not guaranteed to be accurate or complete. The creator
               (Geezam) accepts no liability for any errors, omissions, or
               decisions made based on this information. This is not a
               gambling tool.
    """)
