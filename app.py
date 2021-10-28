import os
import pathlib

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dash_table
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


#Map box key, should probabyl make this private, but its free so *shrug* 
MAPBOXKEY = os.getenv('MAPBOXKEY')
MAPBOXKEY = 'pk.eyJ1IjoiZ3RibGFjazQiLCJhIjoiY2txdmdkdW9lMDk3MDJ2bnp0MzVhazM2cCJ9.-i6gkNqdpDeZ-NIrdiYjvA'






#reads the separate =year csv's
sneezeData2020 =pd.read_csv('data/2020Sneezes.csv',sep=";")
sneezeData2021 =pd.read_csv('data/2021Sneezes.csv',sep=";")

#dataBreakdown does a number of operations to get more information from the spreadsheet. Creating separate columns for cumulative data, time data (day,week,month). This probably isn't needed anymore. I created this
#before I fully understood plotly
mf.dataBreakdown(sneezeData2020)
mf.dataBreakdown(sneezeData2021)

dataTotal = sneezeData2020.append(sneezeData2021)
headers = list(dataTotal.columns.values.tolist())

#gets the total amount for the counter on the top of the page
totalSum = sneezeData2021['Cumulative'].tail(1)
mf.checkLastRun()






#Creates the header for the whole site
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
                    html.Button(
                        id="learn-more-button", children="LEARN MORE ABOUT THE PROJECT", n_clicks=0
                    ),
                    html.A(
                        html.Img(id="logo", src=app.get_asset_url("sneezeLogo.png")),
                        href="https://plotly.com/dash/",
                    ),
                ],
            ),
        ],
    )

#creates the buttons to switch between the
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
                        id="facts-tab",
                        label="Fun Facts",
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


def build_tab_1():
    return [
        html.Div(
            id="fun-facts-container",
           
            children=[
                generate_section_banner("A collection of fun information about my sneezes."),
                html.Div(
                    id="facts-div",
                    children=[
                        #                           
                        html.Div(
                            id="sneeze-facts-rows",
                            children=[
                                build_sneeze_facts_rows("What day had the most sneezes?", sneeziestDay(), 1),
                                build_sneeze_facts_rows("What is the daily average number of sneezes?",averageSneezeDay(),2),
                                build_sneeze_facts_rows("What % of days did Gage sneeze on?", sneezLessDays(), 3),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ]
def build_sneeze_facts_rows(title,value,position):
    position = "sneeze-facts-row-" + str(position)
    return html.Div(
        id=position,
        #className="row metric-row",

        children=[
            html.Div(
                id="sneeze-facts-title",
                children=[
                    html.P(
                        id="sneeze-facts-title-text",
                        children=[title])
                ]
            ),
            html.Div(
                id="sneeze-facts-value",
                children=[
                    html.P(
                        id="sneeze-facts-value-text",
                        children=[value]
                    )

                ]
            )

        ])







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
                html.Div(id = "month-graph",
                    children=[
                generate_year_line_graph()]),
                html.Div(id="line-graphs"),
                ],
            ),
           

            html.Div(
                id="card-2",
                children=[
                html.P("Where in the World has Gage Sneezed?"),
                html.Button('Heatmap',id="switch-button", n_clicks=0,style=dict(color='white',width="100%")),
                    
                    html.Div(
                    id="map-graphs",
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


def build_top_panel():
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
                        id="quick-graph-div",
                        children=[
#                            generate_metric_list_header(),
                            html.Div(
                                id="bar-graph-rows",
                                children=[

                                    build_sneeze_stats_row("How many sneezes go unblessed?",generate_blessed_sneezes(),1),
                                    build_sneeze_stats_row("Sneeze fit size",generate_fit_count(),2),
                                    build_sneeze_stats_row("Sneeze fit location",generate_location_graph(),3),
                                    #build_sneeze_stats_row("Time of Day ",generate_time_plot(),4),
                                
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
                    
                    
                    html.Div(id='weekday-pie-chart-div', children = generate_piechart()),
                ],
            ),
        ],
    )
def generate_time_heat_graph():
    sneezeHours = []
    for x in range(0,24):
        sneezeHours.append(x)
    
    fig = go.Figure(data=go.Heatmap(
                    x=pd.to_datetime(dataTotal['Timestamp']).dt.strftime('%H:%M'),
                    z=dataTotal['Number of Sneezes']))
    config = {'displayModeBar': False}
    return dcc.Graph(id="fit-count-chart", figure = fig,config=config)

def build_sneeze_stats_row(text,graph,position):
      position = "sneeze-stats-row-" + str(position)
      return html.Div(
        
        id=position,
        className="row sneeze-row",

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
#***********Functions for the Fun Facts Panel*********
def sneeziestDay():

    byDay = dataTotal.groupby(pd.Grouper(key='Timestamp',freq='D')).sum()
    highestDay = byDay['Number of Sneezes'].max()
    highestCount = byDay['Number of Sneezes'].idxmax().strftime('%B %d, %Y')
    text = '{} had the most sneezes at {}'.format(highestCount,highestDay)
    return text



def sneezLessDays():
    uniqueDays = dataTotal["Timestamp"].map(pd.Timestamp.date).unique()
    totalDays = projectLength()
    sneezeDays = len(uniqueDays)
    percentDays =  round((sneezeDays/ totalDays) * 100,2)
    text = 'Gage sneezed on {} out of {} days. Which is {}% of days'.format(sneezeDays,totalDays,percentDays)
    return text

def averageSneezeDay():

    average2020 = round((sneezeData2020['Number of Sneezes'].sum()/366),2)
    average2021 = round(sneezeData2021['Number of Sneezes'].sum()/(projectLength()-366),2)
    text = 'Gage averaged {} sneezes per day in 2020, and {} in 2021'.format(average2020,average2021)
    return text

def projectLength():
    f_date = pd.to_datetime('2020, 1, 1').strftime("%Y-%m-%d")
    l_date = dataTotal['Timestamp'].iloc[-1].strftime("%Y-%m-%d")
    numDays = abs(pd.to_datetime(l_date) - pd.to_datetime(f_date)).days
    return numDays

#**************************************************************







#***********QUICK STATS GRAPH FUNCTIONS*******************
def generate_blessed_sneezes():
    
    blessedSum = sneezeData2021.groupby(sneezeData2021['Blessed'])['Number of Sneezes'].sum()
    #blessedSum.rename(columns = {'Blessed':'Count'})

    data = [go.Bar(
    y=['Sneezes'],
    x=[blessedSum[0]],
    width=[1,1],
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
        width=[1,1],
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
        xaxis = dict(tickvals=[int(0),int(blessedSum['Blessed']),int(blessedSum['Unblessed']+blessedSum['Blessed'])], ticktext=[int(0),int(blessedSum['Blessed']),int(blessedSum['Unblessed'])],
            showgrid = True, tickangle = 0, color = 'white',ticklabelposition='outside left',ticklabeloverflow='hide past div'),
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
        margin=dict(t=20, b=20, l=0, r=0),
        #margin=dict(t=0, b=0, l=0, r=0),
    )
    config = {'displayModeBar': False}
    return dcc.Graph(id="blessed-chart", figure = go.Figure(data=data,layout=layout),config=config)


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
            xaxis = (dict(tickmode= 'array',tickvals=tickvalues, ticktext=tickvalues,showgrid = True, tickangle = 0,color='white',ticklabelposition='outside left',ticklabeloverflow='hide past div')),
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
            margin=dict(t=20, b=20, l=0, r=0),
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
        width=[3]

        ))
        count = count+1
   
    layout = go.Layout(barmode='stack',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor= 'rgba(0,0,0,0)',
            showlegend=True,
            autosize=True,
            yaxis = dict(showticklabels=False),
            xaxis = (dict(tickmode= 'array',tickvals=tickvalues, ticktext=tickvalues,showgrid = True, tickangle = 0,color = 'white',ticklabelposition='outside left',ticklabeloverflow='hide past div')),
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
            margin=dict(t=20, b=20, l=0, r=0),
            #margin=dict(t=0, b=0, l=0, r=0),
        )
    config = {'displayModeBar': False}
    return dcc.Graph(id="fit-count-chart", figure = go.Figure(data=data,layout=layout),config=config)

def generate_piechart():

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
#*********************************************************************************************************************


def build_chart_panel():
    return html.Div(
        id="bottom-graph-container",
        className="bottom graphs",
        children=[
            generate_section_banner("Some Other Graphs"),
            html.Div(
                id="heatmap-div",
                children=[
                    generate_time_plot()
                ]
            ),
            html.Div(
                id="year-line-div",
                children=[
                    generate_month_line_graph()

                ]
            )
        ],
    )

def generate_time_plot():
#.dt.strftime('%H')
    timeFrame = dataTotal.sort_values(by='Hour')
    timeFrame['Hour'] = pd.to_datetime(timeFrame['Hour']).dt.strftime("%I:00 %p")
    data = [
    go.Histogram2d(
            x=timeFrame['Hour'],
            z=timeFrame['Number of Sneezes'],
            y=timeFrame['Year'],
            colorscale='blugrn',
            showscale=False,
            )
        ]

    layout = go.Layout(
      
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor= 'rgba(0,0,0,0)',
        showlegend=False,
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
        
        margin=dict(t=0, b=0, l=0, r=15),

        xaxis=dict(tickformat="%I:00",color="white",nticks=4),
        yaxis=dict(tickformat='Y',color="white",nticks=3),
      
        )
    config = {'displayModeBar': False}
    return dcc.Graph(figure=go.Figure(data=data,layout=layout),config=config)


def generate_year_line_graph():
    fig = go.Figure(

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
    ],
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
        hovermode = 'x unified',

        xaxis=dict(tickformat="%b",color="white",nticks=12),
        yaxis=dict(color="white") 
        ),

   )

    fig.update_traces(hovertemplate='%{x|%b %d} Number of Sneezes: %{y}')
    fig.update_layout(
    hoverlabel=dict(
        bgcolor="black",
        font_size=16,
        font_family="Open Sans, sans-serif"
    )
)
    config = {'displayModeBar': False}
    
    return dcc.Graph(figure=fig,config=config)
   
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
    #fig = make_subplots(specs=[[{"secondary_y": True}]])

    dayLightHours = pd.DataFrame(build_daylight_array())
    week2020 = pd.DataFrame(mf.buildWeekSums(sneezeData2020))
    week2021 = pd.DataFrame(mf.buildWeekSums(sneezeData2021))
  
    fig = go.Figure(
        go.Scatter(
        x=pd.to_datetime(week2020['Month Day']),
        y=week2020['7 Day Average'],
        mode= 'lines',
        name="2020",
        line=dict(
            color='rgb(102, 255, 102)',
            width=2
        ),
        
    ),
       # secondary_y=False,
    )
   
   
    fig.add_trace(
    go.Scatter(
        x=pd.to_datetime(week2021['Month Day']),
        y=week2021['7 Day Average'], 
        mode= 'lines',
        name="2021",
        line=dict(
            color='rgb(0, 153, 51)',
            width=3
            )
        ),
        #secondary_y=False,
    )
    # fig.add_trace(
    #     go.Scatter(
    #     x=pd.to_datetime(dayLightHours[0]),
    #     y=dayLightHours[1],
    #     mode= 'lines',
    #     name="Cleveland DayLight hours",
    #     line=dict(
    #         color='rgb(255,255,0)',
    #         width=2
    #     ),
    #     yaxis='y2',

    # ),
        
    #     secondary_y=True,

    # )
    # regression = pd.ols(y=week2021['date'], x=week2021['sum'])
    # print(regression)


    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor= 'rgba(0,0,0,0)',
        showlegend=True,
        autosize=True,
        hovermode = 'x unified',
      

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
        yaxis=dict(tickvals = [0,1,2,3,4, 5,6,7,8,9,10,11],color="white",nticks=20),
        yaxis2=dict(color="blue",nticks=0, anchor="free",overlaying="y2", side="right",showgrid=False, showticklabels=False,),
        
        )
    fig.update_traces(hovertemplate='%{x|%b %e} <br>Running Average: %{y}')
    fig.update_layout(
    hoverlabel=dict(
        bgcolor="black",
        font_size=16,
        font_family="Open Sans, sans-serif"
    ))
    fig.update_layout(autotypenumbers='convert types')
    config = {'displayModeBar': False}


    return dcc.Graph(figure=fig,config=config)

   

def generate_sneeze_map():
    fig = go.Figure(go.Scattermapbox(
        name = "2020",
        lat=sneezeData2020['Latitude'],
        lon=sneezeData2020['Longitude'],
        hovertext=sneezeData2020["Timestamp"],
        customdata=sneezeData2020['Number of Sneezes'],
        hovertemplate='%{hovertext| %b %d %Y} <br>%{hovertext| %I:%M %p} <br>Sneezes: %{customdata}',
        marker=go.scattermapbox.Marker(
        size=9,
        color = '#34eb74'
        ),

    )
    )
    fig.add_trace(go.Scattermapbox(
        name = "2021",
        lat=sneezeData2021['Latitude'],
        lon=sneezeData2021['Longitude'],
        hovertext=sneezeData2021["Timestamp"],
        customdata=sneezeData2021['Number of Sneezes'],
        #customdata2=sneezeData2021['Location'],
        hovertemplate='%{hovertext| %b %d %Y} <br>%{hovertext| %I:%M %p} <br>Sneezes: %{customdata}',
        marker=go.scattermapbox.Marker(
        size=9,
        color = 'green'
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
    showlegend=True,
     legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(

            color="white"
        ),
            ),
    mapbox=dict(
        accesstoken=MAPBOXKEY,
        bearing=0,
        center=dict(
            lat=40,
            lon=-81.5
        ),
        pitch=0,
        zoom=4.5,

    ),
    )
    fig.update_layout(
    hoverlabel=dict(
        #bgcolor="black",
        font_size=16,
       # font_family="Open Sans, sans-serif"
    ))
    return html.Div(dcc.Graph(figure=fig))

def generate_sneeze_heat_map():

    from urllib.request import urlopen
    import json
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
            counties = json.load(response)

    df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                       dtype={"fips": str})
    fig = go.Figure(go.Choroplethmapbox(geojson=counties, locations=df.fips, z=df.unemp,
    colorscale="Viridis", zmin=0, zmax=12, marker_line_width=0))
    fig.update_layout(mapbox_style="light", mapbox_accesstoken=MAPBOXKEY,
                  mapbox_zoom=3, mapbox_center = {"lat": 37.0902, "lon": -95.7129})
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return html.Div(dcc.Graph(figure=fig))    


app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
     
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(id="app-content"),
            ],
        ),
        generate_modal(),
    ],
)

#TODO Strip out unneeded variables
@app.callback(
    [Output("app-content", "children")],
    [Input("app-tabs", "value")],

)
def render_tab_content(tab_switch):
    if tab_switch == "tab1":
        return build_tab_1()
    return (
        html.Div(
            id="status-container",
            children=[
                build_quick_stats_panel(),
                html.Div(
                    id="graphs-container",
                    children=[build_top_panel(), build_chart_panel()],
                ),
            ],
        ),
        
    )


# Update interval



# Callbacks for stopping interval update



@app.callback(
    [Output("switch-button","children"),Output("map-graphs","children")],
    [dash.dependencies.Input('switch-button','n_clicks')]
)

def map_graph_switch(n_clicks):
    if n_clicks % 2 == 1:
        return "Scatter Plot",generate_sneeze_heat_map()
    else:
        return "Heat Map",generate_sneeze_map()
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



# Running the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
