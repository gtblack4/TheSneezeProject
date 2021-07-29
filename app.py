import os
import pathlib

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import plotly.graph_objs as go
import plotly.express as px
import dash_daq as daq
import numpy as np
import functions as mf
import pandas as pd
import math
from plotly.subplots import make_subplots

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "The Sneeze Project"
server = app.server
app.config["suppress_callback_exceptions"] = True

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
df = pd.read_csv(os.path.join(APP_PATH, os.path.join("data", "spc_data.csv")))

#BEGIN DATA LOADING 
MAPBOXKEY = os.getenv('MAPBOXKEY')
MAPBOXKEY = 'pk.eyJ1IjoiZ3RibGFjazQiLCJhIjoiY2txdmdkdW9lMDk3MDJ2bnp0MzVhazM2cCJ9.-i6gkNqdpDeZ-NIrdiYjvA'


sneezeData2020 =pd.read_csv('data/2020Sneezes.csv',sep=";")
sneezeData2021 =pd.read_csv('data/2021Sneezes.csv',sep=";")
mf.dataBreakdown(sneezeData2020)
mf.dataBreakdown(sneezeData2021)
dataTotal = sneezeData2021.append(sneezeData2020)
headers = list(dataTotal.columns.values.tolist())

currentSneezeCount = sneezeData2021['Cumulative'].tail(1)

params = list(df)
max_length = len(df)

suffix_row = "_row"
suffix_button_id = "_button"
suffix_sparkline_graph = "_sparkline_graph"
suffix_count = "_count"
suffix_ooc_n = "_OOC_number"
suffix_ooc_g = "_OOC_graph"
suffix_indicator = "_indicator"

totalSum = currentSneezeCount


def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Gage's Live Sneeze Dashboard"),
                    html.H6("Gesundheit"),

                ],
            ),
            html.Div(
                
                children=[
                    html.H6("Total Sneezes This Year"),
                    daq.LEDDisplay(
                        id="operator-led",
                        value=totalSum,
                        color="#32c95b",
                        backgroundColor="#1e2130",
                        size=50,
                    ),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    # html.A(
                    #     html.Button(children="ENTERPRISE DEMO"),
                    #     href="https://plotly.com/get-demo/",
                    # ),
                    html.Button(
                        id="learn-more-button", children="LEARN MORE", n_clicks=0
                    ),
                    html.A(
                        html.Img(id="logo", src=app.get_asset_url("sneezeLogo.png")),
                        href="https://plotly.com/dash/",
                    ),
                ],
            ),
        ],
    )


def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Specs-tab",
                        label="Specification Settings",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Control-chart-tab",
                        label="Data Visualizations",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
            )
        ],
    )


def init_df():
    ret = {}
    for col in list(df[1:]):
        data = df[col]
        stats = data.describe()

        std = stats["std"].tolist()
        ucl = (stats["mean"] + 3 * stats["std"]).tolist()
        lcl = (stats["mean"] - 3 * stats["std"]).tolist()
        usl = (stats["mean"] + stats["std"]).tolist()
        lsl = (stats["mean"] - stats["std"]).tolist()

        ret.update(
            {
                col: {
                    "count": stats["count"].tolist(),
                    "data": data,
                    "mean": stats["mean"].tolist(),
                    "std": std,
                    "ucl": round(ucl, 3),
                    "lcl": round(lcl, 3),
                    "usl": round(usl, 3),
                    "lsl": round(lsl, 3),
                    "min": stats["min"].tolist(),
                    "max": stats["max"].tolist(),
                    "ooc": populate_ooc(data, ucl, lcl),
                }
            }
        )

    return ret


def populate_ooc(data, ucl, lcl):
    ooc_count = 0
    ret = []
    for i in range(len(data)):
        if data[i] >= ucl or data[i] <= lcl:
            ooc_count += 1
            ret.append(ooc_count / (i + 1))
        else:
            ret.append(ooc_count / (i + 1))
    return ret


state_dict = init_df()


def init_value_setter_store():
    # Initialize store data
    state_dict = init_df()
    return state_dict


def build_tab_1():
    return [
        # Manually select metrics
        html.Div(
            id="set-specs-intro-container",
            # className='twelve columns',
            children=html.P(
                "Use historical control limits to establish a benchmark, or set new values."
            ),
        ),
        html.Div(
            id="settings-menu",
            children=[
                html.Div(
                    id="metric-select-menu",
                    # className='five columns',
                    children=[
                        html.Label(id="metric-select-title", children="Select Metrics"),
                        html.Br(),
                        dcc.Dropdown(
                            id="metric-select-dropdown",
                            options=list(
                                {"label": param, "value": param} for param in params[1:]
                            ),
                            value=params[1],
                        ),
                    ],
                ),
                html.Div(
                    id="value-setter-menu",
                    # className='six columns',
                    children=[
                        html.Div(id="value-setter-panel"),
                        html.Br(),
                        html.Div(
                            id="button-div",
                            children=[
                                html.Button("Update", id="value-setter-set-btn"),
                                html.Button(
                                    "View current setup",
                                    id="value-setter-view-btn",
                                    n_clicks=0,
                                ),
                            ],
                        ),
                        html.Div(
                            id="value-setter-view-output", className="output-datatable"
                        ),
                    ],
                ),
            ],
        ),
    ]


ud_usl_input = daq.NumericInput(
    id="ud_usl_input", className="setting-input", size=200, max=9999999
)
ud_lsl_input = daq.NumericInput(
    id="ud_lsl_input", className="setting-input", size=200, max=9999999
)
ud_ucl_input = daq.NumericInput(
    id="ud_ucl_input", className="setting-input", size=200, max=9999999
)
ud_lcl_input = daq.NumericInput(
    id="ud_lcl_input", className="setting-input", size=200, max=9999999
)


def build_value_setter_line(line_num, label, value, col3):
    return html.Div(
        id=line_num,
        children=[
            html.Label(label, className="four columns"),
            html.Label(value, className="four columns"),
            html.Div(col3, className="four columns"),
        ],
        className="row",
    )


def generate_modal():
    return html.Div(
        id="markdown",
        className="modal",
        children=(
            html.Div(
                id="markdown-container",
                className="markdown-container",
                children=[
                    html.Div(
                        className="close-container",
                        children=html.Button(
                            "Close",
                            id="markdown_close",
                            n_clicks=0,
                            className="closeButton",
                        ),
                    ),
                    html.Div(
                        className="markdown-text",
                        children=dcc.Markdown(
                            children=(
                                """
                        ###### What is this dashboard all about?

                        I built this dashboard for real-time monitoring of my sneezes.

                        ###### But why?



                        ###### Source Code

                        You can find the source code of this app on my [Github repository](https://github.com/gtblack4/TheSneezeProject).

                    """
                            )
                        ),
                    ),
                ],
            )
        ),
    )


def build_quick_stats_panel():
    return html.Div(
        id="quick-stats",
        className="row",
        children=[
            html.Div(
                id="card-1",
                children=[
                html.Div(id = "graph-label",
                    children=[
                html.Button('Cumulative',id="switch-button", n_clicks=0,style=dict(color='white')),
                  ]),
                html.Div(id="line-graphs"),
                ],
            ),
           

            html.Div(
                id="card-2",
                children=[
                    html.P("Where in the World has Gage Sneezed?"),
                    html.Div(
                    id="map-graph",
                    children=[
                    generate_sneeze_map()
                    ]
                    )
                ],
            ),
           
        ],
    )


def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)


def build_top_panel(stopped_interval):
    return html.Div(
        id="top-section-container",
        className="row",
        children=[
            # Metrics summary
            html.Div(
                id="metric-summary-session",
                className="eight columns",
                children=[
                    generate_section_banner("Quick Stats"),
                    html.Div(
                        id="metric-div",
                        children=[
#                            generate_metric_list_header(),
                            html.Div(
                                id="metric-rows",
                                children=[
                                    build_sneeze_stats_row("How many sneezes go unblessed?",generate_blessed_sneezes(),1),
                                    build_sneeze_stats_row("Sneeze fit size",generate_fit_count(),1),
                                    build_sneeze_stats_row("Sneeze fit location",generate_location_graph(),1),
                                    #build_sneeze_stats_row("Time of Day ",generate_time_heat_graph(),1),
                                    
                                    # generate_metric_row_helper(stopped_interval, 4),
                                    # generate_metric_row_helper(stopped_interval, 5),
                                    # generate_metric_row_helper(stopped_interval, 6),
                                    # generate_metric_row_helper(stopped_interval, 7),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Piechart
            html.Div(
                id="ooc-piechart-outer",
                className="four columns",
                children=[
                   generate_section_banner("Weekday Breakdown"),
                    
                    
                    html.Div(id='weekday-pie-chart-div', children =  generate_piechart()),
                ],
            ),
        ],
    )
def generate_time_heat_graph():
    sneezeHours = []
    for x in range(0,24):
        sneezeHours.append(x)
    
    fig = go.Figure(data=go.Heatmap(
                    x=pd.to_datetime(dataTotal['Timestamp']).dt.strftime('%h'),
                    z=dataTotal['Number of Sneezes']))
    config = {'displayModeBar': False}
    return dcc.Graph(id="fit-count-chart", figure = fig,config=config)

def build_sneeze_stats_row(text,graph,position):
      return html.Div(
        id="sneeze-stats-row",
        className="row metric-row",

        children=[
            html.Div(
                id="sneeze-stats-title",
                children=[
              html.P(
                id="sneeze-stats-title-text",
                children=[text])
              ]
            ),
            html.Div(
                id="sneeze-stats-graph",
                children=[
                graph
                ]
            )
         
            ])

def generate_sneeze_time():
    print('fart')
def generate_location_graph():
    sneezeLocation = pd.DataFrame(dataTotal['Location'].value_counts())
    data = []
    tickvalues = [0]
    count = 0
    sneezeLocation = sneezeLocation.sort_index()

    sneezeLocation = sneezeLocation.sort_values('Location',ascending=False)


    for row in sneezeLocation.index:


        tickvalues.append(int(int(sneezeLocation['Location'][row])+int(tickvalues[count])))
        data.append(
        go.Bar(
        y=['Sneezes'],
        x=[sneezeLocation['Location'][row]],
        name=row,
        orientation='h',
        ))
        count = count+1
   
    layout = go.Layout(barmode='stack',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor= 'rgba(0,0,0,0)',
            showlegend=False,
            autosize=True,
            yaxis = dict(showticklabels=False),
            xaxis = (dict(tickmode= 'array',tickvals=tickvalues, ticktext=tickvalues,showgrid = True, tickangle = 0)),
            #xaxis=dict(tickformat="%m/%d")
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(
                    color="white"
                ),
            ),
            margin=dict(t=0, b=0, l=0, r=0),
        )
    config = {'displayModeBar': False}
    return dcc.Graph(id="location-count-chart", figure = go.Figure(data=data,layout=layout),config=config)

def generate_fit_count():
    sneezeFit = pd.DataFrame(dataTotal['Number of Sneezes'].value_counts())
    data = []
    tickvalues = [0]
    count = 0
    sneezeFit = sneezeFit.sort_index()
   
    for row in sneezeFit.index:
        tickvalues.append(int(int(sneezeFit['Number of Sneezes'][row])+int(tickvalues[count])))
        data.append(
        go.Bar(
        y=['Sneezes'],
        x=[sneezeFit['Number of Sneezes'][row]],
        name=row,
        orientation='h',
        ))
        count = count+1
   
    layout = go.Layout(barmode='stack',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor= 'rgba(0,0,0,0)',
            showlegend=True,
            autosize=True,
            yaxis = dict(showticklabels=False),
            xaxis = (dict(tickmode= 'array',tickvals=tickvalues, ticktext=tickvalues,showgrid = True,
 
  tickangle = 0)),
            #xaxis=dict(tickformat="%m/%d")
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                traceorder='normal',
                font=dict(
                    color="white"
                ),
            ),
            margin=dict(t=0, b=0, l=0, r=0),
        )
    config = {'displayModeBar': False}
    return dcc.Graph(id="fit-count-chart", figure = go.Figure(data=data,layout=layout),config=config)


def generate_blessed_sneezes():
    
    blessedSum = dataTotal.groupby(dataTotal['Blessed'])['Number of Sneezes'].sum()
    #blessedSum.rename(columns = {'Blessed':'Count'})

    data = [go.Bar(
    y=['Sneezes'],
    x=[blessedSum[0]],
    name='Blessed',
    orientation='h',
    marker=dict(
        color='rgba(246, 78, 139, 0.6)',
        line=dict(color='rgba(246, 78, 139, 1.0)', width=3)
        )
    ),
    go.Bar(
        y=['Sneezes'],
        x=[blessedSum[1]],
        name='Unblessed',
        orientation='h',
        marker=dict(
            color='rgba(58, 71, 80, 0.6)',
            line=dict(color='rgba(58, 71, 80, 1.0)', width=3)
            )
        ),

    ]
    layout = go.Layout(barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor= 'rgba(0,0,0,0)',
        showlegend=True,
        autosize=True,
      

        #xaxis=dict(tickformat="%m/%d")
        yaxis = dict(showticklabels=False),
        xaxis = (dict(tickvals=[int(0),int(blessedSum['Blessed']),int(blessedSum['Unblessed']+blessedSum['Blessed'])], ticktext=[int(0),int(blessedSum['Blessed']),int(blessedSum['Unblessed'])],
            showgrid = True, tickangle = 0)),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(
                color="white"
            ),
        ),
        margin=dict(t=0, b=0, l=0, r=0),
    )
    config = {'displayModeBar': False}
    return dcc.Graph(id="blessed-chart", figure = go.Figure(data=data,layout=layout),config=config)

def generate_piechart():
    # value == "All Years":
    #     value = [2020,2021] 
    # else:
    #     value = [int(value)]
    # df = dataTotal[dataTotal['Year'].isin(value)]
  
    data = [
        go.Pie(
            labels=dataTotal['Day of Week'],
            values=dataTotal['Number of Sneezes'],
            name="WeekDay Breakdown",   
            
           )
    ,]
    layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        
        showlegend=True,
        autosize=True,

        legend=dict(
            font= dict(color = 'white'),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=0, b=100, l=0, r=0),
    )
    config = {'displayModeBar': False}
    return dcc.Graph(id ='weekday-pie-chart',figure =go.Figure(data=data,layout=layout),config=config)

def generate_piechart2():
    return dcc.Graph(

        id="piechart",
        figure={
            "data": [
                {
                    "labels": [],
                    "values": [],
                    "type": "pie",
                    "marker": {"line": {"color": "white", "width": 1}},
                    "hoverinfo": "label",
                    "textinfo": "label",
                }
            ],
            "layout": {
                "margin": dict(l=20, r=20, t=20, b=20),
                "showlegend": True,
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "white"},
                "autosize": True,
            },
        },
    )


# Build header
def generate_sneeze_header():
    return generate_metric_row(
        "metric_header",
        {"height": "3rem", "margin": "1rem 0", "textAlign": "center"},
        {"id": "m_header_1", "children": html.Div("Parameter")},
        {"id": "m_header_2", "children": html.Div("Count")},
        {"id": "m_header_3", "children": html.Div("Sparkline")},
        {"id": "m_header_4", "children": html.Div("OOC%")},
        {"id": "m_header_5", "children": html.Div("%OOC")},
        {"id": "m_header_6", "children": "Pass/Fail"},
    )

def generate_rows(graphType,index):
    return generate
    item = params[index]
def generate_metric_row_helper(stopped_interval, index):
    item = params[index]

    div_id = item + suffix_row
    button_id = item + suffix_button_id
    sparkline_graph_id = item + suffix_sparkline_graph
    count_id = item + suffix_count
    ooc_percentage_id = item + suffix_ooc_n
    ooc_graph_id = item + suffix_ooc_g
    indicator_id = item + suffix_indicator

    return generate_metric_row(
        div_id,
        None,
        {
            "id": item,
            "className": "metric-row-button-text",
            "children": html.Button(
                id=button_id,
                className="metric-row-button",
                children=item,
                title="Click to visualize live SPC chart",
                n_clicks=0,
            ),
        },
        {"id": count_id, "children": "0"},
        {
            "id": item + "_sparkline",
            "children": dcc.Graph(
                id=sparkline_graph_id,
                style={"width": "100%", "height": "95%"},
                config={
                    "staticPlot": False,
                    "editable": False,
                    "displayModeBar": False,
                },
                figure=go.Figure(
                    {
                        "data": [
                            {
                                "x": state_dict["Batch"]["data"].tolist()[
                                    :stopped_interval
                                ],
                                "y": state_dict[item]["data"][:stopped_interval],
                                "mode": "lines+markers",
                                "name": item,
                                "line": {"color": "#f4d44d"},
                            }
                        ],
                        "layout": {
                            "uirevision": True,
                            "margin": dict(l=0, r=0, t=4, b=4, pad=0),
                            "xaxis": dict(
                                showline=False,
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                            ),
                            "yaxis": dict(
                                showline=False,
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                            ),
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                        },
                    }
                ),
            ),
        },
        {"id": ooc_percentage_id, "children": "0.00%"},
        {
            "id": ooc_graph_id + "_container",
            "children": daq.GraduatedBar(
                id=ooc_graph_id,
                color={
                    "ranges": {
                        "#92e0d3": [0, 3],
                        "#f4d44d ": [3, 7],
                        "#f45060": [7, 15],
                    }
                },
                showCurrentValue=False,
                max=15,
                value=0,
            ),
        },
        {
            "id": item + "_pf",
            "children": daq.Indicator(
                id=indicator_id, value=True, color="#91dfd2", size=12
            ),
        },
    )


def generate_metric_row(id, style, col1, col2, col3, col4, col5, col6):
    if style is None:
        style = {"height": "8rem", "width": "100%"}

    return html.Div(
        id=id,
        className="row metric-row",
        style=style,
        children=[
            html.Div(
                id=col1["id"],
                className="one column",
                style={"margin-right": "2.5rem", "minWidth": "50px"},
                children=col1["children"],
            ),
            html.Div(
                id=col2["id"],
                style={"textAlign": "center"},
                className="one column",
                children=col2["children"],
            ),
            html.Div(
                id=col3["id"],
                style={"height": "100%"},
                className="four columns",
                children=col3["children"],
            ),
            html.Div(
                id=col4["id"],
                style={},
                className="one column",
                children=col4["children"],
            ),
            html.Div(
                id=col5["id"],
                style={"height": "100%", "margin-top": "5rem"},
                className="three columns",
                children=col5["children"],
            ),
            html.Div(
                id=col6["id"],
                style={"display": "flex", "justifyContent": "center"},
                className="one column",
                children=col6["children"],
            ),
        ],
    )


def build_chart_panel():
    return html.Div(
        id="control-chart-container",
        className="twelve columns",
        children=[
            generate_section_banner("Live SPC Chart"),
            dcc.Graph(
                id="control-chart-live",
                figure=go.Figure(
                    {
                        "data": [
                            {
                                "x": [],
                                "y": [],
                                "mode": "lines+markers",
                                "name": params[1],
                            }
                        ],
                        "layout": {
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                            "xaxis": dict(
                                showline=False, showgrid=False, zeroline=False
                            ),
                            "yaxis": dict(
                                showgrid=False, showline=False, zeroline=False
                            ),
                            "autosize": True,
                        },
                    }
                ),
            ),
        ],
    )

def generate_year_line_graph():


    data = [
        go.Scatter(
            x=sneezeData2020['Month Day'],
            y=sneezeData2020['Cumulative'], 
            mode= 'lines',
            name="2020",
            line=dict(
                color='rgb(102, 255, 102)',
                width=3
            )
        ),
        go.Scatter(
            x=sneezeData2021['Month Day'], 
            y=sneezeData2021['Cumulative'], 
            mode= 'lines',
            name="2021", 
            line=dict(
                color='rgb(0, 153, 51)',
                width=3
            ),
        )
    ]
    layout = go.Layout(
      
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor= 'rgba(0,0,0,0)',
        showlegend=True,
        autosize=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(
                color="white"
            ),

        ),
        margin=dict(t=0, b=0, l=0, r=0),

        xaxis=dict(tickformat="%m/%d",color="white"),
        yaxis=dict(color="white")
        )
   
    config = {'displayModeBar': False}
    return dcc.Graph(figure=go.Figure(data=data,layout=layout),config=config)
   
def day_length(day_of_year, latitude):
    P = math.asin(0.39795 * math.cos(0.2163108 + 2 * math.atan(0.9671396 * math.tan(.00860 * (day_of_year - 186)))))
    pi = math.pi
    day_light_hours = 24 - (24 / pi) * math.acos((math.sin(0.8333 * pi / 180) + math.sin(latitude * pi / 180) * math.sin(P)) / (math.cos(latitude * pi / 180) * math.cos(P)))
    return day_light_hours


def build_daylight_array():
    min_light = 24.0
    max_light = 0.0
    latitude = 42.3605
    dayLightHour = pd.DataFrame()
  
    for day in range(1,365):
        length_hours = day_length(day,latitude)
        length_hours = [pd.to_datetime(day-1, unit='D',origin=str(1900)),length_hours]
 
        dayLightHour = dayLightHour.append([length_hours])
     
   
    return dayLightHour

def generate_month_line_graph():
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    dayLightHours = pd.DataFrame(build_daylight_array())
    week2020 = pd.DataFrame(mf.buildWeekSums(sneezeData2020))
    week2021 = pd.DataFrame(mf.buildWeekSums(sneezeData2021))
  
    fig.add_trace(
        go.Scatter(
        x=pd.to_datetime(week2020['Month Day']).dt.strftime('%Y/%-m/%d'),
        y=week2020['7 Day Average'],
        mode= 'lines',
        name="2020",
        line=dict(
            color='rgb(102, 255, 102)',
            width=2
        ),
        
    ),
        secondary_y=False,
    )
   
   
    fig.add_trace(
    go.Scatter(
        x=pd.to_datetime(week2021['Month Day']).dt.strftime('%Y/%-m/%d'), 
        y=week2021['7 Day Average'], 
        mode= 'lines',
        name="2021",
        line=dict(
            color='rgb(0, 153, 51)',
            width=3
            )
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
        x=pd.to_datetime(dayLightHours[0]).dt.strftime('%Y/%-m/%d'),
        y=dayLightHours[1],
        mode= 'lines',
        name="Cleveland DayLight hours",
        line=dict(
            color='rgb(255,255,0)',
            width=2
        ),
        yaxis='y2',

    ),
        
        secondary_y=True,

    )
    #regression = pd.ols(y=week2021['date'], x=week2021['sum'])
    #print(regression)


    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor= 'rgba(0,0,0,0)',
        showlegend=True,
        autosize=True,
      

        #xaxis=dict(tickformat="%m/%d")
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(

            color="white"
        ),
        ),

        margin=dict(t=0, b=0, l=0, r=0),
        xaxis=dict(tickformat="%b",color="white",nticks=12),
        yaxis=dict(tickvals = [0, 1,2, 3,4, 5,6, 7,8, 9,10, 11],color="white",nticks=20),
        yaxis2=dict(color="blue",nticks=0, anchor="free",overlaying="y2", side="right",showgrid=False, showticklabels=False,),
        
        )
    fig.update_layout(autotypenumbers='convert types')
    config = {'displayModeBar': False}


    return dcc.Graph(figure=fig,config=config)
# def generate_month_line_graph2():

#     dayLightHours = pd.DataFrame(build_daylight_array())

#     week2020 = pd.DataFrame(mf.buildWeekSums(sneezeData2020))
#     week2021 = pd.DataFrame(mf.buildWeekSums(sneezeData2021))

#     data = [
   
#     go.Scatter(
#         x=week2020['Week Number'],
#         y=week2020['sum'],
#         mode= 'lines',
#         name="2020",
#         line=dict(
#             color='rgb(102, 255, 102)',
#             width=3
#         )
#     ),
#     go.Scatter(
#         x=week2021['Week Number'], 
#         y=week2021['sum'], 
#         mode= 'lines',
#         name="2021",
#         line=dict(
#             color='rgb(0, 153, 51)',
#             width=3
#             )
#         )
#     ]
#     layout = go.Layout(
#         paper_bgcolor='rgba(0,0,0,0)',
#         plot_bgcolor= 'rgba(0,0,0,0)',
#         showlegend=True,
#         autosize=True,
      

#         #xaxis=dict(tickformat="%m/%d")
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.02,
#             xanchor="right",
#             x=1,
#             font=dict(

#             color="white"
#         ),
#         ),

#         margin=dict(t=0, b=0, l=0, r=0),
#         )
#     config = {'displayModeBar': False}


#     return dcc.Graph(figure=go.Figure(data=data,layout=layout),config=config)
   

def generate_sneeze_map():
    
    fig = go.Figure(go.Scattermapbox(
        lat=dataTotal['Latitude'],
        lon=dataTotal['Longitude'],
        hovertext=dataTotal["Timestamp"],
        marker=go.scattermapbox.Marker(
        size=9,

        ),

    )
    )
    fig.update_layout(mapbox_style="dark",
    mapbox_accesstoken=MAPBOXKEY,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor= 'rgba(0,0,0,0)',
    autosize=True,
    margin=dict(t=0, b=0, l=0, r=0),
    )
    fig.update_layout(

    autosize=True,
    hovermode='closest',
    showlegend=False,
    mapbox=dict(
        accesstoken=MAPBOXKEY,
        bearing=0,
        center=dict(
            lat=40,
            lon=-84
        ),
        pitch=0,
        zoom=4,

    ),
    )
    return html.Div(dcc.Graph(figure=fig))

def generate_graph(interval, specs_dict, col):
    stats = state_dict[col]
    col_data = stats["data"]
    mean = stats["mean"]
    ucl = specs_dict[col]["ucl"]
    lcl = specs_dict[col]["lcl"]
    usl = specs_dict[col]["usl"]
    lsl = specs_dict[col]["lsl"]

    x_array = state_dict["Batch"]["data"].tolist()
    y_array = col_data.tolist()

    total_count = 0

    if interval > max_length:
        total_count = max_length - 1
    elif interval > 0:
        total_count = interval

    ooc_trace = {
        "x": [],
        "y": [],
        "name": "Out of Control",
        "mode": "markers",
        "marker": dict(color="rgba(210, 77, 87, 0.7)", symbol="square", size=11),
    }

    for index, data in enumerate(y_array[:total_count]):
        if data >= ucl or data <= lcl:
            ooc_trace["x"].append(index + 1)
            ooc_trace["y"].append(data)

    histo_trace = {
        "x": x_array[:total_count],
        "y": y_array[:total_count],
        "type": "histogram",
        "orientation": "h",
        "name": "Distribution",
        "xaxis": "x2",
        "yaxis": "y2",
        "marker": {"color": "#f4d44d"},
    }

    fig = {
        "data": [
            {
                "x": x_array[:total_count],
                "y": y_array[:total_count],
                "mode": "lines+markers",
                "name": col,
                "line": {"color": "#f4d44d"},
            },
            ooc_trace,
            histo_trace,
        ]
    }

    len_figure = len(fig["data"][0]["x"])

    fig["layout"] = dict(
        margin=dict(t=40),
        hovermode="closest",
        uirevision=col,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend={"font": {"color": "darkgray"}, "orientation": "h", "x": 0, "y": 1.1},
        font={"color": "darkgray"},
        showlegend=True,
        xaxis={
            "zeroline": False,
            "showgrid": False,
            "title": "Batch Number",
            "showline": False,
            "domain": [0, 0.8],
            "titlefont": {"color": "darkgray"},
        },
        yaxis={
            "title": col,
            "showgrid": False,
            "showline": False,
            "zeroline": False,
            "autorange": True,
            "titlefont": {"color": "darkgray"},
        },
        annotations=[
            {
                "x": 0.75,
                "y": lcl,
                "xref": "paper",
                "yref": "y",
                "text": "LCL:" + str(round(lcl, 3)),
                "showarrow": False,
                "font": {"color": "white"},
            },
            {
                "x": 0.75,
                "y": ucl,
                "xref": "paper",
                "yref": "y",
                "text": "UCL: " + str(round(ucl, 3)),
                "showarrow": False,
                "font": {"color": "white"},
            },
            {
                "x": 0.75,
                "y": usl,
                "xref": "paper",
                "yref": "y",
                "text": "USL: " + str(round(usl, 3)),
                "showarrow": False,
                "font": {"color": "white"},
            },
            {
                "x": 0.75,
                "y": lsl,
                "xref": "paper",
                "yref": "y",
                "text": "LSL: " + str(round(lsl, 3)),
                "showarrow": False,
                "font": {"color": "white"},
            },
            {
                "x": 0.75,
                "y": mean,
                "xref": "paper",
                "yref": "y",
                "text": "Targeted mean: " + str(round(mean, 3)),
                "showarrow": False,
                "font": {"color": "white"},
            },
        ],
        shapes=[
            {
                "type": "line",
                "xref": "x",
                "yref": "y",
                "x0": 1,
                "y0": usl,
                "x1": len_figure + 1,
                "y1": usl,
                "line": {"color": "#91dfd2", "width": 1, "dash": "dot"},
            },
            {
                "type": "line",
                "xref": "x",
                "yref": "y",
                "x0": 1,
                "y0": lsl,
                "x1": len_figure + 1,
                "y1": lsl,
                "line": {"color": "#91dfd2", "width": 1, "dash": "dot"},
            },
            {
                "type": "line",
                "xref": "x",
                "yref": "y",
                "x0": 1,
                "y0": ucl,
                "x1": len_figure + 1,
                "y1": ucl,
                "line": {"color": "rgb(255,127,80)", "width": 1, "dash": "dot"},
            },
            {
                "type": "line",
                "xref": "x",
                "yref": "y",
                "x0": 1,
                "y0": mean,
                "x1": len_figure + 1,
                "y1": mean,
                "line": {"color": "rgb(255,127,80)", "width": 2},
            },
            {
                "type": "line",
                "xref": "x",
                "yref": "y",
                "x0": 1,
                "y0": lcl,
                "x1": len_figure + 1,
                "y1": lcl,
                "line": {"color": "rgb(255,127,80)", "width": 1, "dash": "dot"},
            },
        ],
        xaxis2={
            "title": "Count",
            "domain": [0.8, 1],  # 70 to 100 % of width
            "titlefont": {"color": "darkgray"},
            "showgrid": False,
        },
        yaxis2={
            "anchor": "free",
            "overlaying": "y",
            "side": "right",
            "showticklabels": False,
            "titlefont": {"color": "darkgray"},
        },
    )

    return fig


def update_sparkline(interval, param):
    x_array = state_dict["Batch"]["data"].tolist()
    y_array = state_dict[param]["data"].tolist()

    if interval == 0:
        x_new = y_new = None

    else:
        if interval >= max_length:
            total_count = max_length
        else:
            total_count = interval
        x_new = x_array[:total_count][-1]
        y_new = y_array[:total_count][-1]

    return dict(x=[[x_new]], y=[[y_new]]), [0]


def update_count(interval, col, data):
    if interval == 0:
        return "0", "0.00%", 0.00001, "#92e0d3"

    if interval > 0:

        if interval >= max_length:
            total_count = max_length - 1
        else:
            total_count = interval - 1

        ooc_percentage_f = data[col]["ooc"][total_count] * 100
        ooc_percentage_str = "%.2f" % ooc_percentage_f + "%"

        # Set maximum ooc to 15 for better grad bar display
        if ooc_percentage_f > 15:
            ooc_percentage_f = 15

        if ooc_percentage_f == 0.0:
            ooc_grad_val = 0.00001
        else:
            ooc_grad_val = float(ooc_percentage_f)

        # Set indicator theme according to threshold 5%
        if 0 <= ooc_grad_val <= 5:
            color = "#92e0d3"
        elif 5 < ooc_grad_val < 7:
            color = "#f4d44d"
        else:
            color = "#FF0000"

    return str(total_count + 1), ooc_percentage_str, ooc_grad_val, color


app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        dcc.Interval(
            id="interval-component",
            interval=2 * 1000,  # in milliseconds
            n_intervals=50,  # start at batch 50
            disabled=True,
        ),
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(id="app-content"),
            ],
        ),
        dcc.Store(id="value-setter-store", data=init_value_setter_store()),
        dcc.Store(id="n-interval-stage", data=50),
        generate_modal(),
    ],
)


@app.callback(
    [Output("app-content", "children"), Output("interval-component", "n_intervals")],
    [Input("app-tabs", "value")],
    [State("n-interval-stage", "data")],
)
def render_tab_content(tab_switch, stopped_interval):
    if tab_switch == "tab1":
        return build_tab_1(), stopped_interval
    return (
        html.Div(
            id="status-container",
            children=[
                build_quick_stats_panel(),
                html.Div(
                    id="graphs-container",
                    children=[build_top_panel(stopped_interval), build_chart_panel()],
                ),
            ],
        ),
        stopped_interval,
    )


# Update interval
@app.callback(
    Output("n-interval-stage", "data"),
    [Input("app-tabs", "value")],
    [
        State("interval-component", "n_intervals"),
        State("interval-component", "disabled"),
        State("n-interval-stage", "data"),
    ],
)
def update_interval_state(tab_switch, cur_interval, disabled, cur_stage):
    if disabled:
        return cur_interval

    if tab_switch == "tab1":
        return cur_interval
    return cur_stage


# Callbacks for stopping interval update


@app.callback(
    [Output("year-graph", "style"), 
    Output('month-graph', "style"),
    Output("time-button", "children")],
    #dash.dependencies.Output('year-graph', 'style'),
    [dash.dependencies.Input('time-button', 'n_clicks')],
    )
def button_toggle(n_clicks):
    if n_clicks % 2 == 1:
        return {'display': 'block'},{'display':'none'},"14 Day Moving Average"

    else:
        return {'display':'none'},{'display': 'block'},"Yearly Cumulative"


@app.callback(

    [Output("switch-button","children"),Output("line-graphs","children")],
    [dash.dependencies.Input('switch-button','n_clicks')]
)
def line_graph_switch(n_clicks):
    if n_clicks % 2 == 1:
        return "Yearly Cumulative",generate_year_line_graph()
    else:
        return "14 Day Moving Average",generate_month_line_graph()
    #switchback
        


def stop_production(n_clicks, current):
    if n_clicks == 0:
        return True, "start"
    return not current, "stop" if current else "start"


# ======= Callbacks for modal popup =======
@app.callback(
    Output("markdown", "style"),
    [Input("learn-more-button", "n_clicks"), Input("markdown_close", "n_clicks")],
)



def update_click_output(button_click, close_click):
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "learn-more-button":
            return {"display": "block"}

    return {"display": "none"}


# ======= update progress gauge =========
@app.callback(
    output=Output("progress-gauge", "value"),
    inputs=[Input("interval-component", "n_intervals")],
)
def update_gauge(interval):
    if interval < max_length:
        total_count = interval
    else:
        total_count = max_length

    return int(total_count)


# ===== Callbacks to update values based on store data and dropdown selection =====
@app.callback(
    output=[
        Output("value-setter-panel", "children"),
        Output("ud_usl_input", "value"),
        Output("ud_lsl_input", "value"),
        Output("ud_ucl_input", "value"),
        Output("ud_lcl_input", "value"),
    ],
    inputs=[Input("metric-select-dropdown", "value")],
    state=[State("value-setter-store", "data")],
)
def build_value_setter_panel(dd_select, state_value):
    return (
        [
            build_value_setter_line(
                "value-setter-panel-header",
                "Specs",
                "Historical Value",
                "Set new value",
            ),
            build_value_setter_line(
                "value-setter-panel-usl",
                "Upper Specification limit",
                state_dict[dd_select]["usl"],
                ud_usl_input,
            ),
            build_value_setter_line(
                "value-setter-panel-lsl",
                "Lower Specification limit",
                state_dict[dd_select]["lsl"],
                ud_lsl_input,
            ),
            build_value_setter_line(
                "value-setter-panel-ucl",
                "Upper Control limit",
                state_dict[dd_select]["ucl"],
                ud_ucl_input,
            ),
            build_value_setter_line(
                "value-setter-panel-lcl",
                "Lower Control limit",
                state_dict[dd_select]["lcl"],
                ud_lcl_input,
            ),
        ],
        state_value[dd_select]["usl"],
        state_value[dd_select]["lsl"],
        state_value[dd_select]["ucl"],
        state_value[dd_select]["lcl"],
    )


# ====== Callbacks to update stored data via click =====
@app.callback(
    output=Output("value-setter-store", "data"),
    inputs=[Input("value-setter-set-btn", "n_clicks")],
    state=[
        State("metric-select-dropdown", "value"),
        State("value-setter-store", "data"),
        State("ud_usl_input", "value"),
        State("ud_lsl_input", "value"),
        State("ud_ucl_input", "value"),
        State("ud_lcl_input", "value"),
    ],
)
def set_value_setter_store(set_btn, param, data, usl, lsl, ucl, lcl):
    if set_btn is None:
        return data
    else:
        data[param]["usl"] = usl
        data[param]["lsl"] = lsl
        data[param]["ucl"] = ucl
        data[param]["lcl"] = lcl

        # Recalculate ooc in case of param updates
        data[param]["ooc"] = populate_ooc(df[param], ucl, lcl)
        return data


@app.callback(
    output=Output("value-setter-view-output", "children"),
    inputs=[
        Input("value-setter-view-btn", "n_clicks"),
        Input("metric-select-dropdown", "value"),
        Input("value-setter-store", "data"),
    ],
)
def show_current_specs(n_clicks, dd_select, store_data):
    if n_clicks > 0:
        curr_col_data = store_data[dd_select]
        new_df_dict = {
            "Specs": [
                "Upper Specification Limit",
                "Lower Specification Limit",
                "Upper Control Limit",
                "Lower Control Limit",
            ],
            "Current Setup": [
                curr_col_data["usl"],
                curr_col_data["lsl"],
                curr_col_data["ucl"],
                curr_col_data["lcl"],
            ],
        }
        new_df = pd.DataFrame.from_dict(new_df_dict)
        return dash_table.DataTable(
            style_header={"fontWeight": "bold", "color": "inherit"},
            style_as_list_view=True,
            fill_width=True,
            style_cell_conditional=[
                {"if": {"column_id": "Specs"}, "textAlign": "left"}
            ],
            style_cell={
                "backgroundColor": "#1e2130",
                "fontFamily": "Open Sans",
                "padding": "0 2rem",
                "color": "darkgray",
                "border": "none",
            },
            css=[
                {"selector": "tr:hover td", "rule": "color: #91dfd2 !important;"},
                {"selector": "td", "rule": "border: none !important;"},
                {
                    "selector": ".dash-cell.focused",
                    "rule": "background-color: #1e2130 !important;",
                },
                {"selector": "table", "rule": "--accent: #1e2130;"},
                {"selector": "tr", "rule": "background-color: transparent"},
            ],
            data=new_df.to_dict("rows"),
            columns=[{"id": c, "name": c} for c in ["Specs", "Current Setup"]],
        )


# decorator for list of output
def create_callback(param):
    def callback(interval, stored_data):
        count, ooc_n, ooc_g_value, indicator = update_count(
            interval, param, stored_data
        )
        spark_line_data = update_sparkline(interval, param)
        return count, spark_line_data, ooc_n, ooc_g_value, indicator

    return callback


for param in params[1:]:
    update_param_row_function = create_callback(param)
    app.callback(
        output=[
            Output(param + suffix_count, "children"),
            Output(param + suffix_sparkline_graph, "extendData"),
            Output(param + suffix_ooc_n, "children"),
            Output(param + suffix_ooc_g, "value"),
            Output(param + suffix_indicator, "color"),
        ],
        inputs=[Input("interval-component", "n_intervals")],
        state=[State("value-setter-store", "data")],
    )(update_param_row_function)


#  ======= button to choose/update figure based on click ============
@app.callback(
    output=Output("control-chart-live", "figure"),
    inputs=[
        Input("interval-component", "n_intervals"),
        Input(params[1] + suffix_button_id, "n_clicks"),
        Input(params[2] + suffix_button_id, "n_clicks"),
        Input(params[3] + suffix_button_id, "n_clicks"),
        Input(params[4] + suffix_button_id, "n_clicks"),
        Input(params[5] + suffix_button_id, "n_clicks"),
        Input(params[6] + suffix_button_id, "n_clicks"),
        Input(params[7] + suffix_button_id, "n_clicks"),
    ],
    state=[State("value-setter-store", "data"), State("control-chart-live", "figure")],
)
def update_control_chart(interval, n1, n2, n3, n4, n5, n6, n7, data, cur_fig):
    # Find which one has been triggered
    ctx = dash.callback_context

    if not ctx.triggered:
        return generate_graph(interval, data, params[1])

    if ctx.triggered:
        # Get most recently triggered id and prop_type
        splitted = ctx.triggered[0]["prop_id"].split(".")
        prop_id = splitted[0]
        prop_type = splitted[1]

        if prop_type == "n_clicks":
            curr_id = cur_fig["data"][0]["name"]
            prop_id = prop_id[:-7]
            if curr_id == prop_id:
                return generate_graph(interval, data, curr_id)
            else:
                return generate_graph(interval, data, prop_id)

        if prop_type == "n_intervals" and cur_fig is not None:
            curr_id = cur_fig["data"][0]["name"]
            return generate_graph(interval, data, curr_id)

# Update piechart

@app.callback(
    Output(component_id="weekday-pie-chart", component_property="figure"),
    [Input(component_id="weekday-dropdown", component_property="value")]
)

def update_weekday_piechart(value):
  
    if value == "All Years":
        value = [2020,2021] 
    else:
        value = [int(value)]
    df = dataTotal[dataTotal['Year'].isin(value)]

    data = [
        go.Pie(
           labels=df['Day of Week'],
           values=df['Number of Sneezes'],
           name="WeekDay Breakdown",   
           )
    ,]
    layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor= 'rgba(0,0,0,0)',
        showlegend=True,
        autosize=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=0, b=0, l=0, r=0),
    )
    #layout =[]
    config = {'displayModeBar': False}
    return go.Figure(data=data,layout=layout,config=config)







# Running the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
