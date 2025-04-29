#!/usr/bin/env python3

import logging
import plotly.graph_objects as go
import pandas as pd
from dash import Dash, dcc, html
import pkg_resources
import random

# Configure the logger (with file clearing)
logger = logging.getLogger('StockChartLogger')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('stock_chart.log', mode='w')
console_handler = logging.StreamHandler()
file_handler.setLevel(logging.DEBUG)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("Starting the minimal Dash candlestick application")

# Log package versions
def log_package_versions():
    packages = ['dash', 'plotly', 'pandas', 'dash-core-components', 'dash-html-components', 'dash-renderer']
    for pkg in packages:
        try:
            version = pkg_resources.get_distribution(pkg).version
            logger.info(f"Package {pkg} version: {version}")
        except pkg_resources.DistributionNotFound:
            logger.warning(f"Package {pkg} not installed")

log_package_versions()

def generate_random_list(length, min_val, max_val):
    return [random.randint(min_val, max_val) for _ in range(length)]

def create_minimal_chart():
    try:
        # Create synthetic data
        logger.debug("Creating synthetic data")
        high = 100
        high_med = 80
        low_med = 20
        low = 0
        df = pd.DataFrame({
            'Date': pd.date_range('2023-01-01', periods=100),
            'Open': generate_random_list(100, low, high),
            'High': generate_random_list(100, high_med, high),
            'Low': generate_random_list(100, low, low_med),
            'Close': generate_random_list(100, low, high),
        })
        logger.debug("Synthetic data created: %s rows", len(df))
        logger.debug("Synthetic data sample: %s", df.iloc[0].to_dict())

        # Validate data
        required_columns = ['Open', 'High', 'Low', 'Close']
        missing_columns = [col for col in required_columns if col not in df.columns or df[col].isna().all()]
        if missing_columns:
            logger.error("Missing or empty columns: %s", missing_columns)
            raise ValueError(f"Missing or empty columns: {missing_columns}")
        logger.debug("Data validated: %s", required_columns)
        logger.debug("Data NaN check: %s", df[required_columns].isna().sum().to_dict())

        # Create figure with candlestick and scatter
        fig = go.Figure()
        fig.add_trace(
            go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Candlestick'
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=df['Close'],
                name='Close Price',
                mode='lines',
                line=dict(color='blue')
            )
        )
        fig.update_layout(
            title="Minimal Candlestick and Scatter Test",
            yaxis_title="Price (USD)",
            xaxis_title="Date",
            xaxis=dict(type="date", tickformat="%b %d, %Y"),
            yaxis=dict(fixedrange=False),
            showlegend=True
        )
        logger.debug("Candlestick figure traces: %s", [trace['type'] for trace in fig.data])
        logger.debug("Candlestick figure layout: %s", fig.layout)

        # OHLC figure
        ohlc_fig = go.Figure()
        ohlc_fig.add_trace(
            go.Ohlc(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='OHLC'
            )
        )
        ohlc_fig.update_layout(
            title="Minimal OHLC Test",
            yaxis_title="Price (USD)",
            xaxis_title="Date",
            xaxis=dict(type="date", tickformat="%b %d, %Y"),
            yaxis=dict(fixedrange=False),
            showlegend=True
        )
        logger.debug("OHLC figure traces: %s", [trace['type'] for trace in ohlc_fig.data])

        # Return candlestick figure
        return fig, df
        # To test OHLC: return ohlc_fig

    except Exception as e:
        logger.error("Error in create_minimal_chart: %s", str(e), exc_info=True)
        raise

# Create Dash app
try:
    app = Dash(__name__)

    # Generate chart
    logger.debug("Generating minimal chart")
    fig, df = create_minimal_chart()

    # Test figure with fig.show()
#    logger.debug("Testing figure with fig.show()")
#    try:
#        fig.show()
#    except Exception as e:
#        logger.error("Error rendering figure: %s", str(e), exc_info=True)

    # Minimal layout
    logger.debug("Defining minimal app layout")
    app.layout = html.Div([
        html.H1("Test Candlestick"),
        dcc.Graph(id='test-graph', figure=fig,
                  style={'height': '90vh'},
        ),
        dcc.Store(id='stock-data', data=df.to_dict('records'))
    ])

    logger.info("Dash app configured with minimal layout")

except Exception as e:
    logger.error("Error setting up Dash app: %s", str(e), exc_info=True)
    raise

if __name__ == '__main__':
    try:
        logger.debug("Starting Dash server on port 8050")
        app.run_server(debug=True, use_reloader=False, port=8050)
        logger.info("Dash server started. Open http://127.0.0.1:8050 in a browser.")
    except Exception as e:
        logger.error("Error starting Dash server: %s", str(e), exc_info=True)
        raise
