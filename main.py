import streamlit as st
import pandas as pd
import json
import requests
from datetime import datetime, timedelta, time
import altair as alt

# CONSTANTS
FIDELITY = 5
CHART_TITLE_COLOR = 'navyblue'
CITIES = ["London", "Paris", "Helsinki", "Moscow", "Tokyo"]

# Page Config
st.set_page_config(page_title="Temperature History", page_icon="🌡️")

st.title('Maximum Temperature History')

# Date format converter (compantible with event urls)
def format_date_string(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{dt.strftime('%B').lower()}-{dt.day}-{dt.year}"

def excract_number_from_temp_str(temp_str):
    return int(temp_str.split('°C')[0])

# Helper function to excract temperature ranges of a particular date and city
def extract_temperatures_results(city, date):
    # event_url_sample = f'https://gamma-api.polymarket.com/events/slug/highest-temperature-in-london-on-august-2-2026'
    formatted_date = format_date_string(str(date))
    event_url = f'https://gamma-api.polymarket.com/events/slug/highest-temperature-in-{city}-on-{formatted_date}'
    response = requests.get(event_url).json()
    markets = response["markets"]

    lowest_temp_item = [item for item in markets if 'below' in item.get('groupItemTitle').lower()][0]
    highest_temp_item = [item for item in markets if 'higher' in item.get('groupItemTitle').lower()][0]

    lowest_temp_str = lowest_temp_item.get('groupItemTitle')
    highest_temp_str = highest_temp_item.get('groupItemTitle')

    # Exctract the data needed
    temperatares_list = []
    verdict = None
    for item in markets:
        temp_str = item.get('groupItemTitle')
        temp_val = excract_number_from_temp_str(temp_str)

        outcomePrices = json.loads(item.get('outcomePrices'))

        temp_slug = item.get("slug")

        if 'below' in temp_str:
            lowest_temp_str = temp_str
            lowest_temp_val = temp_val
            
        elif 'higher' in temp_str:
            highest_temp_str = temp_str
            highest_temp_val = temp_val
            

        # Check if that's the correct temperature (verdict)
        # Fix: Convert price to float before checking against 1
        if float(outcomePrices[0]) >= 0.99:  # Handles both 1 and floating point 0.99+
            verdict_val = temp_val
            verdict_str = temp_str

        temperatares_list.append({
            'temp_str': temp_str,
            'temp_val': temp_val,
            'temp_slug': temp_slug
        })

    temperatures_range = [range(lowest_temp_val, highest_temp_val)]

    return {
        'verdict_str': verdict_str,
        'verdict_val': verdict_val,
        'lowest_temp_str': lowest_temp_str,
        'highest_temp_str': highest_temp_str,
        'lowest_temp_val': lowest_temp_val,
        'highest_temp_val': highest_temp_val,
        'temperatures_range': temperatures_range,
        'temperatares_list': temperatares_list,
        'event_url': event_url,
    }


def generate_df(temperature):
     MARKET_SLUG = [
          temp_item.get('temp_slug') for temp_item in temperatures_results.get('temperatares_list') if temp_item.get('temp_val') == temperature
          ][0]

     market_url = f"https://gamma-api.polymarket.com/markets/slug/{MARKET_SLUG}"

     # st.markdown(f":small[**API URL: {market_url}**]")
     
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
            "fidelity": FIDELITY,     # data resolution in minutes
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

        return df

     except Exception as e:
        raise Exception('No dataframe return')

    
def plot_temperature(temperature):
    try:
        df = generate_df(temperature)

        # Draw altair interactive chart
        chart = (
            alt.Chart(
                df,
                title=alt.TitleParams(
                    text=f"Temperature: {temperature}°",
                    fontSize=20,  # Change font size here
                    color='blue',
                    anchor="middle",  # Options: 'start', 'middle', 'end'
                    ),
            )
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


def plot_temperatures_in_single_chart(temperatures_list):
    try:
        df_list = []
        for temp in temperatures_list:
            df = generate_df(temp)
            if df is not None and not df.empty:
                # Add a column so Altair knows which line this data belongs to
                df['temperature'] = f"{temp}°C"
                df_list.append(df)
        
        if not df_list:
            st.warning("No price history returned for these temperatures.")
            return

        # Combine all individual dataframes into a single dataframe
        combined_df = pd.concat(df_list, ignore_index=True)

        chart = (
            alt.Chart(
                combined_df,
                title=alt.TitleParams(
                    text="Temperature Comparisons",
                    fontSize=20, 
                    color='blue',
                    anchor="middle",  
                ),
            )
            .mark_line(point=False)
            .encode(
                x=alt.X("time:T", title="Time"),
                y=alt.Y("price:Q", title="Price (%)"),
                # Add color encoding to separate the lines and create a legend
                color=alt.Color("temperature:N", title="Temperature"),
                tooltip=[
                    alt.Tooltip("time_str:N", title="Exact Time"),
                    alt.Tooltip("temperature:N", title="Temperature"),
                    alt.Tooltip("price:Q", title="Price (%)", format=".2f"),
                ],
            )
            .interactive() 
        )
        st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.warning(f"Error plotting data: {e}")


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

    city = st.selectbox('City', options=CITIES).lower()

    # Date Picker (Restricted between 5 days ago and today)
    selected_date = st.date_input(
        label="Select Target Event Date",
        value=one_day_ago.date(),  # Default to current date
        min_value=five_days_ago.date(),
        max_value=one_day_ago.date(),
    )

    selected_date_time = datetime.combine(selected_date, time.min)

    # default start time: 2 days ago at 5AM
    default_start_time = selected_date_time - timedelta(days=2) + timedelta(hours=5)

    # default end time: same day at 8PM
    default_end_time = selected_date_time + timedelta(hours=20)

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

    temperatures_results = extract_temperatures_results(city=city, date=selected_date)

    verdict_str = temperatures_results.get('verdict_str')
    verdict_val = temperatures_results.get('verdict_val')
    min_temp = temperatures_results.get('lowest_temp_val')
    max_temp = temperatures_results.get('highest_temp_val')

    st.write(" ")

    single_plot = st.checkbox('Single Plot', value=True)

    col1, col2 = st.columns(2)

    with col1:
        num_temp_plots = st.number_input(
            'Number of Plots', value=1, min_value=1, max_value=len(temperatures_results.get('temperatares_list'))
    )

    if not single_plot:
        with col2:
            # The maximum number of plots per row should not exceed the maximum number of plots and the maximum number would be 4
            max_plots_per_row = min(4, num_temp_plots)
            num_plots_per_row = st.number_input('Plots per Row', value=1, min_value=1, max_value=max_plots_per_row)
            
    

    st.write(" ")

    plotting_temperatures_list = []

    for i in range(num_temp_plots):
        
        input_temperature = st.slider(
            label=f"Select temperature {i + 1}",
            value=verdict_val,
            min_value=min_temp,
            max_value=max_temp,
            key=f"temp_slider_{i}",
        )

        plotting_temperatures_list.append(input_temperature)


st.markdown(f"## :rainbow[{city.title()}] :thermometer:")
st.success(f'Verdict: {verdict_str}')

# Extract min and max from output tuple
start_time, end_time = selected_range

st.write("**Selected Start Time:**", start_time)
st.write("**Selected End Time:**", end_time)

st.write(" ")

formatted_month_year = selected_date.strftime("%B")  # e.g., 'August'
formatted_day = str(selected_date.day)  # e.g., '2' or '3'
formatted_year = selected_date.strftime("%Y")  # e.g., '2026'


if single_plot:
    plot_temperatures_in_single_chart(plotting_temperatures_list)
else:
    for i in range(0, len(plotting_temperatures_list), num_plots_per_row):
        # Slice the temperatures for the current row
        row_temps = plotting_temperatures_list[i: i + num_plots_per_row]

        # Create columns
        cols = st.columns(num_plots_per_row)

        for col, temp in zip(cols, row_temps):
            with col:
                plot_temperature(temp)
