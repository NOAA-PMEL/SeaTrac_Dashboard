from dash.html import Label
import dash_design_kit as ddk
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, Input, Output, callback, dcc, no_update
import plotly.express as px
from urllib.parse import quote

app = Dash(__name__)
server = app.server

row_height = 350
# Get colors from color pallets 
colors = px.colors.qualitative.Plotly
url_df = pd.read_csv('http://auk.pmel.noaa.gov:8080/erddap/search/index.csv?page=1&itemsPerPage=1000&searchFor=ST01')
urls = url_df['tabledap'].to_list()

var_dict = {}
var_options = []
unit_dict = {}

for url in urls:
    info_url = url.replace('tabledap','info')
    info_url = info_url+'/index.csv'
    info_df = pd.read_csv(info_url)
    var_df = info_df.loc[info_df['Row Type']=='variable']
    ## Build dictionary - relationship between the variables and the urls
    for var in var_df['Variable Name'].to_list():
        var_units = info_df.loc[(info_df['Row Type']=='attribute') & (info_df['Variable Name']==var) & (info_df['Attribute Name']=='units')]
        #units = var_units['Value'].astype(str)
        if not var_units.empty:
            units = str(var_units['Value'].iloc[0])
            unit_dict[var] = units
            
        var_dict[var] = url
        if var.lower() != 'time':
            var_options.append({'label': var, 'value': var}) # Drop down options

### Example from google ########################
#new_columns = {}
#for i in range(len(urls)):
#    col_name = f"New_Col_{i}"
#    # Example logic: multiply column A by the loop index
#    new_columns[col_name] = df["A"] * i
    
#df_new_cols = pd.DataFrame(new_columns)
#df = pd.concat([df, df_new_cols], axis=1)
####################################################

app.layout = ddk.App(
    [
        ddk.Header(
            [
                ddk.Logo(src=app.get_asset_url("logo.png")),
                ddk.Title("Engineering Data"),
            ]
        ),
        #ddk.ControlCard(ddk.ControlItem(dcc.Dropdown(id="variable",options=var_options,multi=True))),
        ddk.ControlCard(orientation='horizontal', width=1, children=[
            ddk.ControlItem(dcc.Dropdown(id="variable",options=var_options,multi=True), width=0.5),
            ddk.ControlItem(dcc.DatePickerRange(id='datepicker', min_date_allowed='2026-06-01'), width=0.5)   
        ]),
        ddk.Card(
            children=ddk.Graph(id="graph"),
            style={"height":"80vh","overflow-y":"scroll"}
        ),
    ],
    show_editor=False,
)

@app.callback(
    [Output("graph","figure")],
    [Input("variable","value"), Input("datepicker","start_date"), Input("datepicker","end_date")]
)

def update_plot(in_variable,in_start_date,in_end_date):
    if not in_variable or not in_start_date or not in_end_date:
        return no_update
    
    # Create figure with secondary y-axis
    row_heights = [row_height-3]*len(in_variable)
    fig = make_subplots(cols=1,rows=len(in_variable),shared_xaxes=True,row_heights=row_heights)
    #fig = make_subplots(cols=1,rows=len(in_variable),shared_xaxes=True,row_heights=row_heights, vertical_spacing = .1/len(in_variable))
    count = 1
    
    for var in in_variable: 
        url = var_dict[var]
        # Fileter the URL
        url = url + '.csv?time,' + var + quote('&time>=' + in_start_date + '&time<=' + in_end_date + '&orderBy("time")')
        df = pd.read_csv(url, skiprows=[1])
        
        # Add traces
        fig.add_trace(
            go.Scatter(x=df['time'], y=df[var], name=var, line=dict(color=colors[count % len(colors)])),
            secondary_y=False, col=1, row=count
        )
        title = var 
        if var in unit_dict:
            title = title + ' (' + unit_dict[var] + ')'
            
        fig.update_yaxes(title_text=title, row=count, col=1)
        fig.update_xaxes(showticklabels=True)
        fig.update_layout(
            title_text="Data from TELOST01",
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

    fig.update_layout(height = row_height*len(in_variable))
    
    return [fig]

if __name__ == "__main__":
    app.run(debug=True,port = 8050)
    