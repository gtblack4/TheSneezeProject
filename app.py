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
#MAPBOXKEY = os.environ['MAPBOXKEY']
MAPBOXKEY = 'pk.eyJ1IjoiZ3RibGFjazQiLCJhIjoiY2txdmdkdW9lMDk3MDJ2bnp0MzVhazM2cCJ9.-i6gkNqdpDeZ-NIrdiYjvA'





mf.checkLastRun()
#reads the separate year csv's
sneezeData2020 =pd.read_csv('data/2020Sneezes.csv',sep=";")
sneezeData2021 =pd.read_csv('data/2021Sneezes.csv',sep=";")
sneezeData2022 =pd.read_csv('data/2022Sneezes.csv',sep=";")


#dataBreakdown does a number of operations to get more information from the spreadsheet. Creating separate columns for cumulative data, time data (day,week,month). This probably isn't needed anymore. I created this
#before I fully understood plotly
mf.dataBreakdown(sneezeData2020)
mf.dataBreakdown(sneezeData2021)
mf.dataBreakdown(sneezeData2022)


dataTotal = sneezeData2020.append(sneezeData2021).append(sneezeData2022)

headers = list(dataTotal.columns.values.tolist())

#gets the total amount for the counter on the top of the page
totalSum = sneezeData2021['Cumulative'].tail(1)







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
                id = "LED2021",
                children=[
                    html.H6("2021 Sneeze Count"),
                    daq.LEDDisplay(
                        id="operator-led",
                        value=mf.totalSum(sneezeData2021),

                        color="rgb(0, 153, 51)",
                        backgroundColor="#1e2130",
                        size=40,
                    ),
                ],
            ), html.Div(
                id="LED2022",
                children=[
                    html.H6("2022 Sneeze Count"),
                    daq.LEDDisplay(
                        id="operator-led2",

                        value=mf.totalSum(sneezeData2022),
                        color="#C49102",
                        backgroundColor="#1e2130",
                        size=40,
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
                        #html.Img(id="logo", src=app.get_asset_url("favicon.png")),
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
                generate_section_banner("Fun Information About Gage's Sneezes"),
                html.Div(
                    id="stats-table-div",
                    children=[
                        html.Div(
                            id="stats-table-rows",
                            children=[
                                build_sneeze_stats_table(),
                            ]
                        )
                    ]
                ),
                html.Div(
                    id="facts-div",
                    children=[
                        #                           
                        html.Div(
                            id="sneeze-facts-rows",
                            children=[
                                #build_sneeze_facts_rows("What day had the most sneezes?", sneeziestDay(), 1),
                                #build_sneeze_facts_rows("What is the daily average number of sneezes?", averageSneezeDay(),2),
                                build_sneeze_facts_rows("What percent of days did Gage sneeze?", sneezeLessDays(), 3),
                                build_sneeze_facts_rows("What percent of people think Gage tracking his sneezes is weird?", "99.8% of people.",4),
                                build_sneeze_facts_rows("What holiday had the most sneezes?","Veterans Day 2021: 10 sneezes.",5),
                                build_sneeze_facts_rows("How many sneezes were blessed by strangers?","24 sneezes.",6)
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ]
def buildSneezeTable(sneezes):

    sneezeEvents = mf.sneezeFitCount(sneezes)
    sneezeSum= mf.totalSum(sneezes)
    sneezeLessDays = mf.sneezeLessDays(sneezes)
    sneeziestDate = sneeziestDay(sneezes)
    sneezeTable = [sneezeEvents,sneezeSum,sneeziestDate,round(sneezeSum/sneezeEvents,2),round(sneezeSum/365,2),365-sneezeLessDays,sneezeLessDays]
    return sneezeTable
def build_sneeze_stats_table():

    sneezeTable2020 = buildSneezeTable(sneezeData2020)
    sneezeTable2021 = buildSneezeTable(sneezeData2021)

    data=[go.Table(
        header=dict(values=["","2020","2021"],
                    line_color='white',
                    font=dict(color='white',size=28),
                    fill_color='#1e2130',
                    height=35),
        cells=dict(values=[
            ["Total Number of Sneezing Events","Total Number of Sneezes","Date with the Most Sneezes","Average Sneezes per Sneezing Event","Average Sneezes per Day",
             "Number of Days with Sneezes","Number of Days without Sneezes",],#Fact Title
            sneezeTable2020,#2020
            sneezeTable2021#2021
                   ],
        fill_color='#161a28',
        font=dict(color='white',size=20),
        height = 70,
        align='left')

    )]
    layout = go.Layout(
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       showlegend=True,
                       autosize=True,
                       height=600,
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
                       margin=dict(t=20, b=20, l=3, r=3),

                       )
    config = {'displayModeBar': False}
    return dcc.Graph(id = "stats_table",figure=go.Figure(data=data,layout=layout))

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
                        ###### What is this project all about?

                        In late 2019 I noticed that I was sneezing more frequently than my coworkers. In an effort to find out the truth, I began tracking every sneeze. 
                        It quickly evolved from a simple notepad into spreadsheets and further into the website you see now. Development is ongoing to discover the dirty truth behind why I sneeze so frequently.
                        

                        ###### But why?
                        To be determined at a later date.


                        ###### Source Code

                        You can find the source code of this app on my [Github repository](https://github.com/gtblack4/TheSneezeProject).
                       
                        ###### Business Inquiries, Job offers, and Suggestions
                        Email: gtblack4@gmail.com
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
                html.P("Cumulative Comparison"),
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
                    generate_section_banner("2021 Quick Stats"),
                    html.Div(
                        id="quick-graph-div",
                        children=[
#                            generate_metric_list_header(),
                            html.Div(
                                id="bar-graph-rows",
                                children=[

                                    build_sneeze_stats_row("How Many Sneezes go Unblessed?",generate_blessed_sneezes(),1),
                                    build_sneeze_stats_row("Is Gage Allergic to People?",generate_fit_count(),2),
                                    build_sneeze_stats_row("Where are the Sneezes?",generate_location_graph(),3),
                                    #build_sneeze_stats_row("Time of Day ",generate_time_plot(),4),
                                
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Piechart
            html.Div(
                id="piechart-outer",
                className="four columns",
                children=[
                   generate_section_banner("Weekday Breakdown"),
                    
                    
                    html.Div(id='weekday-pie-chart-div', children = generate_piechart()),
                ],
            ),
        ],
    )


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

#***********Functions for the Fun Facts Panel*********
def sneeziestDay(sneezes):
    byDay = sneezes.groupby(pd.Grouper(key='Timestamp',freq='D')).sum()
    highestDay = byDay['Number of Sneezes'].max()
    highestCount = byDay['Number of Sneezes'].idxmax().strftime('%B %d, %Y')
    #text = '{} had the most sneezes at {}'.format(highestCount,highestDay)
    return highestCount



def sneezeLessDays():
    uniqueDays = dataTotal["Timestamp"].map(pd.Timestamp.date).unique()
    totalDays = projectLength()
    sneezeDays = len(uniqueDays)
    percentDays =  round((sneezeDays/ totalDays) * 100,2)
    text = 'Gage sneezed on {} out of {} days, which is {}% of days.'.format(sneezeDays,totalDays,percentDays)
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
    hovertemplate='Blessed Sneezes: %{x}<extra></extra>',
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
        hovertemplate='Unblessed Sneezes: %{x}<extra></extra>',
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
      


        yaxis = dict(showticklabels=False,fixedrange=True),
        xaxis = dict(tickvals=[int(0),int(blessedSum['Blessed']),int(blessedSum['Unblessed']+blessedSum['Blessed'])], ticktext=[int(0),int(blessedSum['Blessed']),int(blessedSum['Unblessed'])],
            showgrid = True, tickangle = 0, color = 'white',ticklabelposition='outside left',ticklabeloverflow='hide past div',fixedrange=True),
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
    return dcc.Graph(id="blessed-chart", figure = go.Figure(data=data,layout=layout),config=config)


class Sneeze:
    pass


def generate_location_graph():
    sneezeLocationSum = dataTotal.groupby(['Location']).sum()
    sneezeLocation = pd.DataFrame(columns=["Location", "Sneezes"])
    data = []
    tickvalues = [0]
    ticktext = [0]
    count = 0
    sum = 0
    sneezeLocationSum = sneezeLocationSum['Number of Sneezes']

    # add the different locations together
    #In a car
    sneezeLocation.loc[len(sneezeLocation.index)] = ['Car', int(sneezeLocationSum['Car (Driving)']) + int(sneezeLocationSum['Car (Passenger)'])]
    #Indoors
    sneezeLocation.loc[len(sneezeLocation.index)] = ['Inside', int(sneezeLocationSum["Someone else's house"]) +  int(sneezeLocationSum['Office']) + int(sneezeLocationSum['Bar/Restaurant'])  + int(sneezeLocationSum['Hotel']) + int(sneezeLocationSum['Public Store']) + int(sneezeLocationSum['Hospital'])+ int(sneezeLocationSum['Parking Garage'])+ int(sneezeLocationSum['Your Home'])]
    #Outdoors
    sneezeLocation.loc[len(sneezeLocation.index)] = ['Outside', int(sneezeLocationSum['City Street']) + int(sneezeLocationSum['Park'])+ int(sneezeLocationSum['Parking Lot'])+ int(sneezeLocationSum['Sports Facility']+ int(sneezeLocationSum['Waterfront']) + int(sneezeLocationSum['Backyard']))]



    for row in sneezeLocation.index:


        sum = sneezeLocation['Sneezes'][row] + sum
        ticktext.append(int(int(sneezeLocation['Sneezes'][row])+int(ticktext[count])))

        tickvalues.append(sum)
        # data.append(
        # go.Bar(
        # y=['Sneezes'],
        # x=[sneezeLocation['Sneezes'][row]],
        # name=row,
        # orientation='h',
        # ))
        # count = count+1
    fig = go.Figure(data=[go.Bar(
                        y=['Sneezes'],
                        x=[sneezeLocation['Sneezes'][0]],
                        width=[1, 1],
                        name='Car',
                        orientation='h',
                        hovertemplate='Number of Car Sneezes: %{x}<extra></extra>',
                        marker_color='#0b1d78',


                    ),
                        go.Bar(
                            y=['Sneezes'],
                            x=[sneezeLocation['Sneezes'][1]],
                            width=[1, 1],
                            name='Indoors',
                            orientation='h',
                            marker_color='#0069c0',
                            hovertemplate='Number of Indoor Sneezes: %{x}<extra></extra>',
                        ),
                        go.Bar(
                            y=['Sneezes'],
                            x=[sneezeLocation['Sneezes'][2]],
                            width=[1, 1],
                            name='Outdoors',
                            orientation='h',
                            marker_color='#00c698',
                            hovertemplate='Number of Outdoor Sneezes: %{x}<extra></extra>',

                        ),
                    ],
    layout = go.Layout(barmode='stack',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor= 'rgba(0,0,0,0)',
            showlegend=True,
            autosize=True,
            yaxis = dict(showticklabels=False,fixedrange=True),
            xaxis = (dict(tickmode= 'array',tickvals=tickvalues, ticktext=ticktext,showgrid = True, tickangle = 0,color='white',ticklabelposition='outside left',ticklabeloverflow='hide past div',fixedrange=True)),
            #xaxis=dict(tickformat="%m/%d")
            legend=dict(
                traceorder ='normal',
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

                       ),
        )
    #fig.update_traces(hovertemplate='Number of %{y} Sneezes: %{x}')
    # fig.update_layout(
    #     hoverlabel=dict(
    #         bgcolor="black",
    #         font_size=16,
    #         font_family="Open Sans, sans-serif"
    #     )
    # )
    #fig.update_layout(hovermode="y")
    config = {'displayModeBar': False}

    return dcc.Graph(id="location-count-chart", figure = fig,config=config)

def generate_fit_count():
    sneezeAlone = dataTotal.groupby(['Number of Nearby People']).sum()

    #np.savetxt("data/dataTotal.csv", dataTotal, delimiter=";", fmt='%s')
    sneezeFriends = pd.DataFrame(columns=["Friends", "Sneezes"])

    sneezeFriends.loc[len(sneezeFriends.index)] = ['Alone', sneezeAlone['Number of Sneezes'][0]]
    sneezeFriends.loc[len(sneezeFriends.index)] = ['With Nearby People', int(sneezeAlone['Number of Sneezes'].sum())-int(sneezeAlone['Number of Sneezes'][0])]

    tickvalues =[0,sneezeFriends['Sneezes'][1],sneezeFriends['Sneezes'].sum()]
    ticktext =[0,int(sneezeAlone['Number of Sneezes'].sum())-int(sneezeAlone['Number of Sneezes'][0]),sneezeAlone['Number of Sneezes'][0],]
    fig = go.Figure(data=[
        go.Bar(
            y=['Sneezes'],
            x=[sneezeFriends['Sneezes'][1]],
            width=[1, 1],
            name='With Others',
            orientation='h',
            marker_color='#C49102',
            hovertemplate='Sneezes Near Others: %{x}<extra></extra>',
        ),
        go.Bar(
            y=['Sneezes'],
            x=[sneezeFriends['Sneezes'][0]],
            width=[1, 1],
            name='Alone',
            orientation='h',
            hovertemplate='Sneezes While Alone: %{x}<extra></extra>',
            marker_color='#FFC30B',

        ),

    ],
    layout = go.Layout(barmode='stack',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor= 'rgba(0,0,0,0)',
            showlegend=True,
            autosize=True,
            yaxis = dict(showticklabels=False,fixedrange=True),
            xaxis = (dict(tickmode= 'array',tickvals=tickvalues, ticktext=ticktext,showgrid = True, tickangle = 0,color = 'white',ticklabelposition='outside left',ticklabeloverflow='hide past div',fixedrange=True)),
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
    )
    config = {'displayModeBar': False}
    return dcc.Graph(id="fit-count-chart", figure = fig,config=config)

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
            generate_section_banner("More Graphs for Your Viewing Pleasure"),
            html.P("Time of Day Heat Map"),
            html.Div(
                id="heatmap-div",
                children=[
                    generate_time_plot()
                ]
            ),
            html.Div(
                id="year-line-div",
                children=[html.P("Running 14 Day Average"),
                    generate_month_line_graph()

                ]
            )
        ],
    )
def build_bottom_panel():
    return html.Div(
            id="bottom-panel",
            className="bottom-panel-container",
            children=[html.Div(
                          id="sneeze-fit-size",
                          children=[html.P("Number of Sneezes per Sneezing Fit"),
                              generate_sneeze_fit_size_graph()
                          ]
                      ),
                      html.Div(
                          id="monthly-comparison",
                          children=[html.P("Number of Sneezes in a Day"),
                                   generate_sneeze_day_count()
                                        ]
                        )
        ]
    )
def generate_sneeze_day_count():
    sneezeSize2020 = sneezeData2020.groupby(pd.to_datetime(sneezeData2020['Timestamp']).dt.strftime('%y-%m-%d'))['Number of Sneezes'].sum().reset_index(
        name='Number of Sneezes').sort_values(['Timestamp'], ascending=True)
    sneezeSize2021 = sneezeData2021.groupby(pd.to_datetime(sneezeData2021['Timestamp']).dt.strftime('%y-%m-%d'))['Number of Sneezes'].sum().reset_index(
        name='Number of Sneezes').sort_values(['Timestamp'], ascending=True)
    sneezeSize2022 = sneezeData2022.groupby(pd.to_datetime(sneezeData2022['Timestamp']).dt.strftime('%y-%m-%d'))['Number of Sneezes'].sum().reset_index(
        name='Number of Sneezes').sort_values(['Timestamp'], ascending=True)
    #These three lines create a dataframe of the number of days with x number of sneezes
    #Then add in the number of days without sneezes and then sort that data

    daySum2020 = sneezeSize2020['Number of Sneezes'].value_counts().rename_axis('Number of Sneezes').reset_index(name="Count")
    daySum2020.loc[len(daySum2020.index)] = [0, 366-daySum2020['Count'].sum()]
    daySum2020 = daySum2020.sort_values(by="Number of Sneezes",ascending=True)

    daySum2021 = sneezeSize2021['Number of Sneezes'].value_counts().rename_axis('Number of Sneezes').reset_index(name="Count")
    daySum2021.loc[len(daySum2021.index)] = [0, 365-daySum2021['Count'].sum()]
    daySum2021 = daySum2021.sort_values(by="Number of Sneezes",ascending=True)

    daySum2022 = sneezeSize2022['Number of Sneezes'].value_counts().rename_axis('Number of Sneezes').reset_index(name="Count")
    daySum2022.loc[len(daySum2022.index)] = mf.sneezeLessDays(sneezeData2022)
    daySum2022 = daySum2022.sort_values(by="Number of Sneezes", ascending=True)
    colorArray = ['#3ddbd9', '#08bdba', '#009d9a', '#007d79', '#004144', '#022b30']


    data=[

        go.Bar(name='2020',

               x=daySum2020['Number of Sneezes'],
               y=daySum2020['Count'],

               marker=dict(color='rgb(102, 255, 102)'),
               hovertemplate='Year: 2020 <br>There are %{y} days with %{x} sneezes<extra></extra>',
               hoverinfo='x+y+text',
               hoverlabel=dict(
                   bgcolor="black",
                   font_size=16,
                   font_family="Open Sans, sans-serif"
               ),

               ),
        go.Bar(name='2021',

               x=daySum2021['Number of Sneezes'],
               y=daySum2021['Count'],
               marker=dict(color='rgb(0, 153, 51)'),
               hovertemplate='Year: 2021 <br>There are %{y} days with %{x} sneezes<extra></extra>',
               hoverinfo='x+y+text',
               hoverlabel=dict(
                   bgcolor="black",
                   font_size=16,
                   font_family="Open Sans, sans-serif"
               ),

               ),
        go.Bar(name='2022',

               x=daySum2022['Number of Sneezes'],
               y=daySum2022['Count'],
               marker=dict(color='#C49102'),
               hovertemplate='Year: 2022 <br>There are %{y} days with %{x} sneezes<extra></extra>',
               hoverinfo='x+y+text',
               hoverlabel=dict(
                   bgcolor="black",
                   font_size=16,
                   font_family="Open Sans, sans-serif"
               ),

               )

    ]
    # Change the bar mode
    layout = go.Layout(barmode='group',
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)',
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

                      margin=dict(t=0, b=0, l=0, r=15),
                      xaxis=dict(color="white",tickmode="linear",tick0=0,dtick=1,fixedrange=True),
                      yaxis=dict(color="white",fixedrange=True ),
                       xaxis_title="Number of Sneezes per Day",
                       yaxis_title="Number of Days",

                       )
    config = {'displayModeBar': False,}
    return html.Div(dcc.Graph(figure=go.Figure(data=data,layout=layout),config=config))


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
            hovertemplate='Time: %{x}<br>Sneezing Fits: %{z}<extra></extra>',
            hoverinfo='x+y+text',
            hoverlabel=dict(
                    bgcolor="black",
                    font_size=16,
                    font_family="Open Sans, sans-serif"
                )
            )
        ]

    layout = go.Layout(
        title = "fart",
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
        
        margin=dict(t=0, b=6, l=0, r=15),

        xaxis=dict(tickformat="%I:00",color="white",nticks=4,fixedrange=True),
        yaxis=dict(tickformat='Y',color="white",nticks=4,fixedrange=True),

        )

    config = {'displayModeBar': True}
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
        ),
        go.Scatter(
            x=sneezeData2022['Month Day'],
            y=sneezeData2022['Cumulative'],
            mode='lines',
            name="2022",
            line=dict(
                color='#C49102',
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

        xaxis=dict(tickformat="%b",color="white",nticks=12,fixedrange=True),
        yaxis=dict(color="white",fixedrange=True)
        ),

   )

    fig.update_traces(hovertemplate='%{x|%b %d} Number of Sneezes: %{y}<extra></extra>')
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
    week2022 = pd.DataFrame(mf.buildWeekSums(sneezeData2022))

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
    fig.add_trace(
    go.Scatter(
        x=pd.to_datetime(week2022['Month Day']),
        y=week2022['7 Day Average'],
        mode= 'lines',
        name="2021",
        line=dict(
            color='#C49102',
            width=3
            )
        ),
        #secondary_y=False,
    )


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
        xaxis=dict(tickformat="%b",color="white",nticks=12,fixedrange=True),
        yaxis=dict(tickvals = [0,1,2,3,4, 5,6,7,8,9,10,11],color="white",nticks=20,fixedrange=True),
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
        hovertemplate='%{hovertext| %b %d %Y}<br>%{hovertext| %I:%M %p}<br>Sneezes: %{customdata}<extra></extra>',
        marker=go.scattermapbox.Marker(
            size=6,
            color = '#34eb74'
        ),

    ))
    fig.add_trace(go.Scattermapbox(
        name = "2021",
        lat=sneezeData2021['Latitude'],
        lon=sneezeData2021['Longitude'],
        hovertext=sneezeData2021["Timestamp"],
        customdata=sneezeData2021['Number of Sneezes'],
        #customdata2=sneezeData2021['Location'],
        hovertemplate='%{hovertext| %b %d %Y}<br>%{hovertext| %I:%M %p}<br>Sneezes: %{customdata}<extra></extra>',
        marker=go.scattermapbox.Marker(
            size=6,
            color = 'green'
            ),
    ))
    fig.add_trace(go.Scattermapbox(
        name="2022",
        lat=sneezeData2022['Latitude'],
        lon=sneezeData2022['Longitude'],
        hovertext=sneezeData2022["Timestamp"],
        customdata=sneezeData2022['Number of Sneezes'],
        # customdata2=sneezeData2021['Location'],
        hovertemplate='%{hovertext| %b %d %Y}<br>%{hovertext| %I:%M %p}<br>Sneezes: %{customdata}<extra></extra>',
        marker=go.scattermapbox.Marker(
            size=6,
            color='#C49102'
        ),
    ))
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
        zoom=4,

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
    with open('data/counties-fips.json') as response:
            counties = json.load(response)
    #print(counties["features"][0]["properties"]["COUNTY"])
    df = pd.read_csv("data/allFips.csv",
                       dtype={"fips": str})
    fig = go.Figure(go.Choroplethmapbox(
        geojson=counties,
        locations=df.fips,
        z=np.log10(df.sneezes),
        text=df.sneezes,
        colorscale="Greens",
        #featureidkey="properties.COUNTY",
        marker_line_width=0,
        #customdata='counties.properties.COUNTY',
        hovertext=df.sneezes,
        #hoverdata="County",
        colorbar=dict(
            tickvals=[0, .5, 1, 1.5, 2, 2.5,3],
            ticktext=['1', '10', '15', '20', '50', '100','1000'],
            thickness=20,
        ),
        hovertemplate='%{hovertext} Sneezes<extra></extra>',
    ),)
    fig.update_layout(mapbox_zoom=4,
                        mapbox_center = {"lat": 40, "lon": -81.5},
                        margin={"r":0,"t":0,"l":0,"b":0},
                        mapbox_style="dark",
                        mapbox_accesstoken=MAPBOXKEY,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        autosize=True,
                        coloraxis_showscale=False,
                      )




    return html.Div(dcc.Graph(figure=fig))    

def generate_sneeze_fit_size_graph():

    sneezeSize2020 = sneezeData2020.groupby(['Number of Sneezes'])['Number of Sneezes'].count().reset_index(
  name='Count').sort_values(['Number of Sneezes'], ascending=True)
    sneezeSize2021 = sneezeData2021.groupby(['Number of Sneezes'])['Number of Sneezes'].count().reset_index(
        name='Count').sort_values(['Number of Sneezes'], ascending=True)
    sneezeSize2022 = sneezeData2022.groupby(['Number of Sneezes'])['Number of Sneezes'].count().reset_index(
        name='Count').sort_values(['Number of Sneezes'], ascending=True)


    colorArray = ['#3ddbd9','#08bdba','#009d9a','#007d79','#004144','#022b30']
    #print(sneezeSize)



    data=[


        go.Bar(name='Sneeze Fit Size: 2020',

               x=sneezeSize2020['Number of Sneezes'],
               y=sneezeSize2020['Count'],

               marker=dict(color='rgb(102, 255, 102)'),
               hovertemplate='Year: 2020 <br>Sneeze Fit Size: %{x}<br>Number of Fits: %{y}<extra></extra>',
               hoverinfo='x+y+text',
               hoverlabel=dict(
                   bgcolor="black",
                   font_size=16,
                   font_family="Open Sans, sans-serif"
               ),

               ),
        go.Bar(name='Sneeze Fit Size: 2021',

               x=sneezeSize2021['Number of Sneezes'],
               y=sneezeSize2021['Count'],
               marker=dict(color='rgb(0, 153, 51)'),
               hovertemplate='Year: 2021 <br>Sneeze Fit Size: %{x}<br>Number of Fits: %{y}<extra></extra>',
               hoverinfo='x+y+text',
               hoverlabel=dict(
                   bgcolor="black",
                   font_size=16,
                   font_family="Open Sans, sans-serif"
               ),

               ),
        go.Bar(name='Sneeze Fit Size: 2022',

               x=sneezeSize2022['Number of Sneezes'],
               y=sneezeSize2022['Count'],
               marker=dict(color='#C49102'),
               hovertemplate='Year: 2022 <br>Sneeze Fit Size: %{x}<br>Number of Fits: %{y}<extra></extra>',
               hoverinfo='x+y+text',
               hoverlabel=dict(
                   bgcolor="black",
                   font_size=16,
                   font_family="Open Sans, sans-serif"
               ),

               )

        ]
    # Change the bar mode
    layout = go.Layout (barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
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
        xaxis=dict( color="white",fixedrange=True ),
        yaxis=dict( color="white",fixedrange=True),
        xaxis_title="Number of Sneezes per Fit",
        yaxis_title="Number of Sneezing Fits",

    )
    config = {'displayModeBar': False}
    return html.Div(dcc.Graph(figure=go.Figure(data=data,layout=layout),config=config))

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
app._favicon = ("favicon.png")
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
                    children=[build_top_panel(), build_chart_panel(),],
                ),
                build_bottom_panel(),
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
        return "Switch to Scatter Plot",generate_sneeze_heat_map()
    else:
        return "Switch to Heat Map (Slow loading)",generate_sneeze_map()
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
