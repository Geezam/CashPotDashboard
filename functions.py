# functions.py

import streamlit as st
import pandas as pd
import plotly.express as px
import glob
from constants import SLOT_LABELS


@st.cache_data
def load_data():
    all_files = glob.glob("csv/cashpot_*.csv")

    if not all_files:
        st.error("No files found! Please make sure your CSV files start "
                 "with 'cashpot_' and are in the same folder.")
        return pd.DataFrame()

    df_list = []
    for filename in all_files:
        try:
            temp_df = pd.read_csv(filename)
            df_list.append(temp_df)
        except Exception as e:
            st.error(f"Error reading file {filename}: {e}")
            continue

    if df_list:
        df = pd.concat(df_list, ignore_index=True)
    else:
        return pd.DataFrame()

    df = df.rename(columns={
        "WinningNumber": "drawn_number",
        "Date": "timestamp"})

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    df['year'] = df['timestamp'].dt.year

    df['Draw Time'] = df['Draw Time'].astype(str).str.strip()

    time_map_csv = {
        'Earlybird - 8:30 am': 1,
        'Morning - 10:30 am': 2,
        'Midday - 1 pm': 3,
        'Mid Afternoon - 3 pm': 4,
        'Drivetime - 5 pm': 5,
        'Evening - 8:25 pm': 6
    }

    df['draw_slot'] = df['Draw Time'].map(time_map_csv)
    df['draw_slot'] = df['draw_slot'].fillna(0).astype(int)

    return df


def render_overview(data, meaning_map):
    st.header("🎲 CASH POT Number Frequency Overview")
    st.markdown("Below is the frequency distribution of all drawn numbers "
                "from 2017 to 2021.")

    if data.empty:
        st.warning("No data loaded.")
        return

    global_counts = data['drawn_number'].value_counts().reset_index()
    global_counts.columns = ['Number', 'Count']
    global_counts = global_counts.sort_values('Number')

    global_counts['Meaning'] = global_counts['Number'].map(meaning_map)

    fig = px.bar(
        global_counts,
        x='Number',
        y='Count',
        color='Count',
        color_continuous_scale='Greens',
        text='Count',
        hover_data=['Meaning'],
        title="Total Appearances by Number (2017 to 2021)"
    )

    fig.update_layout(xaxis=dict(tickmode='linear', dtick=1))
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Most Drawn")
        top_5 = global_counts.sort_values('Count', ascending=False).head(5)
        st.dataframe(top_5[['Number', 'Meaning', 'Count']],
                     hide_index=True, use_container_width=True)

    with c2:
        st.subheader("Least Drawn")
        bot_5 = global_counts.sort_values('Count', ascending=True).head(5)
        st.dataframe(bot_5[['Number', 'Meaning', 'Count']],
                     hide_index=True, use_container_width=True)


def render_details(data, title_suffix, total_dataset_size, meaning):
    """Renders the specific stats for a selected number."""
    if len(data) == 0:
        st.warning("No data available for this period.")
        return

    # Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Draws", len(data))
    with m2:
        if total_dataset_size > 0:
            prob = (len(data) / total_dataset_size) * 100
        else:
            prob = 0
        st.metric("Appearance Rate", f"{prob:.2f}%")
    with m3:
        last_seen = data['date'].max()
        st.metric("Last Seen", str(last_seen))

    st.markdown("---")

    # Charts
    c1, c2 = st.columns(2)
    with c1:

        counts = data['draw_slot'].value_counts().reset_index()
        counts.columns = ['Draw Slot', 'Count']

        all_slots = pd.DataFrame({'Draw Slot': [1, 2, 3, 4, 5, 6]})
        final_counts = all_slots.merge(counts, on='Draw Slot',
                                       how='left').fillna(0)

        slot_map = SLOT_LABELS
        final_counts['Draw Name'] = final_counts['Draw Slot'].map(slot_map)

        # 4. Plot with specific Sort Order
        fig_bar = px.bar(final_counts, x='Draw Name', y='Count',
                         title=f"Luckiest Draw Time for {meaning}",
                         color_discrete_sequence=['#217C36'],
                         category_orders={"Draw Name": ["Earlybird",
                                                        "Morning", "Midday",
                                                        "Mid Afternoon",
                                                        "Drivetime", "Evening"]
                                          })
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        ts_data = data.set_index('timestamp')
        monthly_trend = ts_data.resample('ME').size().reset_index(name='Count')

        fig_line = px.line(monthly_trend, x='timestamp', y='Count',
                           color_discrete_sequence=['#217C36'],
                           markers=True, title=f"Trend ({title_suffix})")
        st.plotly_chart(fig_line, use_container_width=True)
