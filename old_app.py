# Dash app demonstrating periodic data refresh using Celery and Redis
import json
import os

import dash_ag_grid as dag
import dash_design_kit as ddk
import pandas as pd
import plotly.express as px
import redis
from dash import Dash, Input, Output, callback, dcc, html

import tasks

# Initialize Dash app
app = Dash(__name__,suppress_callback_exceptions=True)
server = app.server  # expose server variable for Procfile

# Initialize data on startup
tasks.update_data()

# app.config.suppress_callback_exceptions = True

# Connect to Redis for data retrieval
redis_instance = redis.StrictRedis.from_url(
    os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")
)


def get_dataframe():
    # In this function, we retrieve the data from redis using redis command hget ("hash get").
    # The data is stored as a JSON-ified string. We load it into memory with `json.loads`.

    # This data is periodically getting updated via a separate Celery Process in tasks.py.
    # "DATASET" is the name of the key that we're storing in the Redis.
    # This name can be anything, but it should match the name that we
    # use to save the dataset in `tasks.py`
    data = json.loads(redis_instance.hget("app-data", "DATASET"))
    return pd.DataFrame(data=data)


app.layout = ddk.App(
    [
        # Trigger updates every 1 second
        #dcc.Interval(id="interval", interval=1000),  # in milliseconds
        html.Div(id="dummy"),
        ddk.Header(
            [
                ddk.Logo(src=app.get_asset_url("logo.png")),
                ddk.Title("Periodic Data Refresh"),
            ]
        ),
        ddk.Card([
            dcc.Markdown(
                """
                This demo periodically refreshes data using a Celery worker and Redis.

                - A Celery task generates random data and saves it to Redis every second.
                - A dcc.Interval in the app (1000 ms) refreshes the view every second and pulls the latest data from Redis, updating the chart and table automatically.
                """
            )
        ]),
        ddk.Row(
            [
                # Bar chart visualization
                ddk.Card(
                    children=[
                        ddk.CardHeader(title="Timeseries Analysis latitude"),
                        ddk.Graph(id="graph"),
                    ]
                ),
                # Data table with pagination
                ddk.Card(
                    children=[
                        ddk.CardHeader(title="Raw Data"),
                        dag.AgGrid(
                            id="table",
                            columnDefs=[{"field": i} for i in ["time", "latitude"]],
                            columnSize="autoSize",
                            dashGridOptions={
                                "pagination": True,
                                "paginationPageSize": 20,
                            },
                        ),
                    ]
                ),
            ]
        ),
        ddk.Row(
            [
                # Bar chart visualization
                ddk.Card(
                    children=[
                        ddk.CardHeader(title="Timeseries Analysis longitude"),
                        ddk.Graph(id="graph"),
                    ]
                ),
                # Data table with pagination
                ddk.Card(
                    children=[
                        ddk.CardHeader(title="Raw Data"),
                        dag.AgGrid(
                            id="table",
                            columnDefs=[{"field": i} for i in ["time", "longitude"]],
                            columnSize="sizeToFit",
                            dashGridOptions={
                                "pagination": True,
                                "paginationPageSize": 20,
                            },
                        ),
                    ]
                ),
            ]
        ),
    ],
    show_editor=True,
)


# Callback to update chart and table every 5 seconds
@callback(
    Output("graph", "figure"),
    Output("table", "rowData"),
    Input("dummy", "n_clicks"),
)
def update_data(n_intervals):
    """Refresh dashboard with latest data from Redis"""
    #df = get_dataframe()
    df = pd.read_csv("https://data.pmel.noaa.gov/pmel/erddap/tabledap/sd1043.csv?time%2Clatitude%2Clongitude%2CTEMP_AIR_MEAN&time%3E=2020-10-22T00%3A00%3A00Z&time%3C=2020-10-29T04%3A45%3A00Z",skiprows=[1])
    figure = px.line(df, x="time", y="latitude")
    data = df.to_dict("records")
    return figure, data


if __name__ == "__main__":
    app.run(debug=True)
