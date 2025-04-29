#!/usr/bin/env python3

from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import random
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def gendata():
    maxval=100.0
    dates=pd.date_range('2023-01-01', periods=1000)
    bias=0.00
    df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close',])
    for d in dates: 
        vallist = []
        for i in range(0,4):
           vallist.append(random.random() * maxval) 
        logger.debug(f"Vallist: {vallist} {type(vallist)}")

        openval = vallist[random.randint(0,3)] + bias
        highval = max(vallist) + bias
        lowval = min(vallist) + bias
        closeval = vallist[random.randint(0,3)] + bias
        new_row = {
            'date': d, 
            'open': openval, 
            'high': highval,
            'low': lowval,
            'close': closeval,
        }
        try:
            new_row_df = pd.DataFrame([new_row])
            df = pd.concat([df, new_row_df], ignore_index=True)
            logger.debug(df)
        except Exception as e:
            print(f"Error adding row: {e}")
        bias = bias + 1.0

    return df

def create_stock_chart():
    df = gendata()
    # Create OHLC chart
    fig = go.Figure(data=go.Ohlc(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    ))
    

    return df, fig

# Initialize the Dash app
app = Dash(__name__)


# App layout
app.layout = html.Div([
    html.H3("OHLC Stock Chart with Adjustable Viewport"),
    dcc.RangeSlider(
      id='viewport-slider',
      min=0,
      max=len(df) - 1 if not df.empty else 100,
      step = 1,
      value = [0, len(df) - 1] if not df.empty else [0,100],
      marks = {i: str(i) for i in range(0, len(df), len(df)//5)},
      tooltip = {'placement': 'bottom', 'always_visible': True},
    ),
    dcc.Graph(id='ohlc-chart'),
])

# Callback to update the OHLC chart and dynamically scale y-axis
@app.callback(
    Output('ohlc-chart', 'figure'),
    [   Input('stock-chart', 'relayoutData'),
        Input('viewport-slider', 'value'),
    ],
)
def update_chart(relayout_data, viewport_range):
    # Filter data based on viewport slider (index-based)
    start_idx, end_idx = viewport_range
    if start_idx < 0 or end_idx >= len(df):
      logger.warning("Invalid viewport range")
      start_idx = end_idx = 0, len(df) - 1
    filtered_df = df.iloc[start_idx:end_idx]

    if filtered_df.empty:
      logger.warning("No data in selected viewport")
      return go.Figure(
        layout=dict(
          title="No data in selected viewport",
          xaxis=dict(title="Date"),
          yaxis=dict(title="Price (USD)"),
          annotations=[dict(text="No data for selected viewport", x=0.5, y=0.5, showarrow=False)]
        )
      )
    
    # Create OHLC chart
    fig = go.Figure(data=go.Ohlc(
        x=filtered_df['date'],
        open=filtered_df['open'],
        high=filtered_df['high'],
        low=filtered_df['low'],
        close=filtered_df['close']
    ))
    
    # Dynamically scale y-axis based on visible data
    y_min = filtered_df['Low'].min() * 0.95  # Add 5% padding below
    y_max = filtered_df['High'].max() * 1.05  # Add 5% padding above
    logger.debug(f"y_min: {y_min} y_max: {y_max}")
    
    # Update layout
    fig.update_layout(
        title='AAPL OHLC Chart',
        xaxis_title='Date',
        xaxis_rangeslider = dict(
            visible = True,
        ),
        xaxis = dict(
        ),
        yaxis_title='Price (USD)',
        yaxis=dict(range=[y_min, y_max]),  # Set dynamic y-axis range
        margin=dict(l=50, r=50, t=50, b=50),
        height=500,
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
