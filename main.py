import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import requests
from datetime import datetime, timezone, timedelta, time
import altair as alt

st.title('Maximum Temperature History - London')


# 1. Define date bounds
# --- FIX: Store reference time in session_state so it remains stable during script reruns ---
if "ref_now" not in st.session_state:
    # Rounding to current minute/hour or capturing once keeps min/max fixed
    st.session_state.ref_now = datetime.now()

now = st.session_state.ref_now
one_day_ago = now - timedelta(days=1)
two_days_ago = now - timedelta(days=2)
five_days_ago = now - timedelta(days=5)
ten_days_ago = now - timedelta(days=10)

with st.sidebar:
    st.header("Settings")

    # Date Picker (Restricted between 5 days ago and today)
    selected_date = st.date_input(
        label="Select Target Event Date",
        value=one_day_ago.date(),  # Default to current date
        min_value=five_days_ago.date(),
        max_value=one_day_ago.date(),
    )

    # default start time: 2 days ago at 5AM
    selected_date_time = datetime.combine(selected_date, time.min)
    st.write(selected_date_time)
    default_start_time = selected_date_time - timedelta(days=2) + timedelta(hours=5)

    # default end time: same day at 8PM
    default_end_time = selected_date_time + timedelta(hours=20)

    temperature = st.slider(
        label="Select temperature",
        value=28,
        min_value=23,
        max_value=32,
    )

    st.write(default_start_time)
    st.write(default_end_time)


    selected_range = st.slider(
        label="Select Date & Time Range",
        min_value=ten_days_ago,
        max_value=now,
        value=(default_start_time, default_end_time),
        step=timedelta(hours=1),
        format="YYYY-MM-DD HH:mm",
    )

    # Optional: Add a button to manually refresh the 5-day window to 'right now'
    if st.button("Reset Time Bounds to Now"):
        st.session_state.ref_now = datetime.now()
        st.rerun()

# 3. Extract min and max from output tuple
start_time, end_time = selected_range

st.write("**Selected Start Time:**", start_time)
st.write("**Selected End Time:**", end_time)

# TEST PARAMETERS
test_temp = '28c'
test_fidelity = 5
# test_start_time = datetime(2026, 8, 2, 0, 0, 0, tzinfo=timezone.utc)
# test_end_time = datetime(2026, 8, 3, 0, 0, 0, tzinfo=timezone.utc)

formatted_month_year = selected_date.strftime("%B")  # e.g., 'August'
formatted_day = str(selected_date.day)  # e.g., '2' or '3'
formatted_year = selected_date.strftime("%Y")  # e.g., '2026'

date_slug_str = f"{formatted_month_year}-{formatted_day}-{formatted_year}".lower()

# 1. Fetch details directly for this specific market
MARKET_SLUG = f"highest-temperature-in-london-on-{date_slug_str}-{temperature}c"
market_url = f"https://gamma-api.polymarket.com/markets/slug/{MARKET_SLUG}"
st.write(market_url)
response = requests.get(market_url).json()

try:
    # Parse the token IDs (clobTokenIds comes back as a JSON-encoded string)
    clob_token_ids = json.loads(response["clobTokenIds"])
    # Typically, index 0 = YES, index 1 = NO
    yes_token_id = clob_token_ids[0]
    no_token_id = clob_token_ids[1]

    # print(f"YES Token ID: {yes_token_id}")

    # 2. Query price history for the YES token
    history_url = "https://clob.polymarket.com/prices-history"
    params = {
        "market": yes_token_id,
        "fidelity": test_fidelity,     # data resolution in minutes
        "startTs": int(start_time.timestamp()),
        "endTs": int(end_time.timestamp())
        # "interval": "1d",  # or "1d", "1w", "1m"
    }

    history_response = requests.get(history_url, params=params).json()
    history = history_response.get('history', [])

    # Convert raw output to Pandas Dataframe
    df = pd.DataFrame(history)

    # Convert Unix timestamp to UTC datetime objects
    df["time"] = pd.to_datetime(df["t"], unit="s", utc=True)

    # Format time string column
    df["time_str"] = df["time"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Convert price to percentage
    df["price"] = df["p"] * 100

    # st.line_chart(df, x="time_str", y="price")

    # Draw altair interactive chart
    chart = (
        alt.Chart(df)
        .mark_line(point=False)  # point=True gives visible hover targets
        .encode(
            x=alt.X("time:T", title="Time"),
            y=alt.Y("price:Q", title="Price (%)"),
            tooltip=[
                alt.Tooltip("time_str:N", title="Exact Time"),
                alt.Tooltip("price:Q", title="Price (%)", format=".2f"),
            ],
        )
        .interactive()  # Enables zoom & pan
    )
    # st.altair_chart(chart, use_container_width=True)
    st.altair_chart(chart, width='stretch')
    
except:
    st.warning("No price history returned for this timeframe and temperature.")



# history_standard = [{'time': datetime.fromtimestamp(_hist['t']).strftime('%Y-%m-%d, %H:%M:%S'), 'price': _hist['p'] * 100} for _hist in history]

# st.write(history_standard)

# st.line_chart(x=history_standard['time'], y=history_standard['price'])



