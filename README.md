# Polymarket Maximum Temperature History Tracker

A Streamlit-based web application that visualizes historical prediction market odds for highest temperature events on **Polymarket**. The app fetches market data via Polymarket’s Gamma API and Central Limit Order Book (CLOB) API to display real-time probability trends over configurable timeframes.

Live Demo: [polymarket-temperature-history.streamlit.app](https://polymarket-temperature-history.streamlit.app/)

---

## Preview

| Dashboard Overview | Multi-Temperature Comparison Chart |
|---|---|
| ![Dashboard Overview](image_05f8ba.png) | ![Chart View](2026-08-12T17-26_chart.png) |

---

## Features

* **Supported Cities:** Tracks daily maximum temperature market events for major cities including London, Paris, Helsinki, Moscow, and Tokyo.
* **Winning Outcome Resolution:** Automatically identifies and highlights the market verdict (winning outcome with outcome price $\ge 0.99$).
* **Historical Price Visualizations:** Plots historical market prices as probability percentages ($0\% - 100\%$) over time.
* **Flexible Visualization Layouts:**
  * **Single Chart Overlay:** View multiple temperature outcomes on a single interactive Altair line chart.
  * **Grid Layout:** Toggle off single-chart mode to split temperature outcomes into custom grid rows and columns.
* **Customizable Controls:** Adjust date range sliders, target dates, y-axis scaling, and granular temperature sliders in real time.

---

## Technical Stack

* **Frontend UI:** [Streamlit](https://streamlit.io/)
* **Data Visualization:** [Altair](https://altair-viz.github.io/)
* **Data Processing:** [Pandas](https://pandas.pydata.org/)
* **API Integration:** [Polymarket Gamma API & CLOB API](https://docs.polymarket.com/)

---

## Installation & Local Setup

### Prerequisites

Ensure you have Python 3.8+ installed on your machine.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/polymarket-temperature-history.git
cd polymarket-temperature-history
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install streamlit pandas requests altair
```

### 4. Run the Streamlit App

```bash
streamlit run app.py
```

The application will automatically launch in your default web browser at `http://localhost:8501`.

---

## API Endpoints Used

* **Gamma API Event Endpoint:** Fetch event markets for a given city and target date:
  `https://gamma-api.polymarket.com/events/slug/highest-temperature-in-{city}-on-{formatted_date}`
* **Gamma API Market Details:** Fetch market details and token IDs:
  `https://gamma-api.polymarket.com/markets/slug/{market_slug}`
* **CLOB API Price History:** Query granular historical pricing for specific YES tokens:
  `https://clob.polymarket.com/prices-history`
