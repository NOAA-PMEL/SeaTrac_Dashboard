import dash_design_kit as ddk
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, Input, Output, callback, dcc, no_update
import plotly.express as px

app = Dash(__name__)
server = app.server

# Get colors from color pallets 
colors = px.colors.qualitative.Plotly

url = 'http://auk.pmel.noaa.gov:8080/erddap/tabledap/TELOST01_ATRH_12345.csv?time%2CAir_Temp%2CAir_Temp_Std%2CRH%2CRH_Std&time%3E=2026-07-04T03%3A00%3A00Z&time%3C=2026-07-06T09%3A00%3A00Z&orderBy(%22time%22)'
df = pd.read_csv(url, skiprows=[1])
var_options = df.columns #variables for graph selector dropdown

app.layout = ddk.App(
    [
        ddk.Header(
            [
                ddk.Logo(src=app.get_asset_url("logo.png")),
                ddk.Title("Engineering Data"),
            ]
        ),
        #ddk.ControlCard(ddk.ControlItem(dcc.Dropdown(id="variable",options=var_options,multi=True))),
        ddk.ControlCard(ddk.ControlItem(dcc.Dropdown(id="variable",options=var_options,multi=True))),
        ddk.Card(
            children=ddk.Graph(id="graph"),
        ),
    ],
    show_editor=True,
)

@app.callback(
    [Output("graph","figure")],
    [Input("variable","value")]
)

def update_plot(in_variable):
    if not in_variable:
        return no_update
        
    #print(in_variable)
    
    # Create figure with secondary y-axis
    fig = make_subplots(cols=1,rows=len(in_variable))
    count = 1
    
    for var in in_variable:    
        # Add traces, setting one to the secondary axis
        fig.add_trace(
            go.Scatter(x=df['time'], y=df[var], name=var, line=dict(color=colors[count % len(colors)])),
            secondary_y=False, col=1, row=count
        )
        
        fig.update_yaxes(title_text=var, row=count, col=1)
        
        fig.update_layout(
            title_text="Data from TELOST01",
            height = 200*(count+1),
            yaxis=dict(
                #title=var, #Only adds over top subplot
                title_font_color="#1f77b4",
                tickfont_color="#1f77b4",
                gridcolor="#1f77b4",
                showgrid=True,
                linecolor="#1f77b4", # Colors the actual vertical axis line
            )
        )
        count += 1

    return [fig]


if __name__ == "__main__":
    app.run(debug=True,port = 8050)
    