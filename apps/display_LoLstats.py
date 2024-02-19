# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 14:58:55 2021

@author: guido

TO DO:
 - met all moeten de databases gemerged worden!
 stappenplan:
 1. choose_maps verzamelt alle databases als version all is
 2. update_statsDropdown merged gewenste databases
"""

# -*- coding: utf-8 -*-
#
# by: Guido Kok

import os
from pathlib import Path
import dash
from dash import html #HTML
from dash import dcc  #Interactive
from dash.dependencies import Input, Output, State
import pandas as pd
from dash import dash_table
#home made libraries
from account_statsV4 import *
from dfCombiner import *
from curGame import *
#multipage app
from app import app
#load the begin data in
path = str(Path(__file__).parent.absolute())

path = path+'/databaseLoL/'
df = pd.DataFrame()
busy = False
csvDB = []
#load the external stylesheet
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#initialise the app
# app = dash.Dash(__name__,title="LoL stats")
#define the app
layout = html.Div(children=[
                      html.Div(className='row',  # Define the row element
                               children=[
                                  #the left side
                                            html.H2('LoL Stats', style = {'padding': '5px', 'fontSize': '30px', 'color': 'blue'}),
                                            html.Div(children=[
                                            html.Span("Summoners Name: ", style = {'padding': '5px', 'fontSize': '20px', 'color': 'white'}),
                                            dcc.Input(id='sum-name', value='ironsuperhulk', type='text', style={'width': '15%'}),
                                            html.Button(id='update-button', n_clicks=0, children='GO', style={'color': 'white'}),
                                            html.Div(id='played-with'),
                                            html.Div(id='update-loading'),
                                            html.Div(id='update-done')
                                            ]),
                                            html.Div([
                                                dcc.Dropdown(
                                                    id='choose-version',
                                                    multi=False,
                                                    clearable=False,
                                                    ),
                                                    ],style={'width': '5%', 'float': 'left'}
                                                ),
                                            html.Div([
                                                dcc.Dropdown(
                                                    id='choose-subversion',
                                                    multi=False,
                                                    clearable=False,
                                                    ),
                                                    ],style={'width': '5%', 'float': 'left'}
                                                ),
                                            html.Div([
                                                dcc.Dropdown(
                                                    id='choose-map',
                                                    multi=False,
                                                    clearable=False,
                                                    ),
                                                    ],style={'width': '15%', 'float': 'left'}
                                                ),
                                            html.Div([
                                                dcc.Dropdown(
                                                    id='choose-stats',
                                                    multi=False,
                                                    clearable=False,
                                                    ),
                                                    ],style={'width': '15%', 'float': 'left'}
                                                ),
                                            html.Div([
                                                dcc.Dropdown(
                                                    id='choose-columns',
                                                    multi=True,
                                                    clearable=False,
                                                    ),
                                                    ],style={'width': '60%', 'float': 'right'}
                                            ),
                                  #the right side
                                  html.Br(),
                                  html.Br(),
                                    dash_table.DataTable(
                                                     id='stats-table',
                                                     sort_action='custom',
                                                     sort_mode='single',
                                                     sort_by=[],
                                                     style_header={'backgroundColor': 'rgb(30, 30, 30)'},
                                                     style_data_conditional=[
                                                         {
                                                             'if': {'row_index': 'odd'},
                                                             'backgroundColor': 'rgb(20, 20, 20)'
                                                         }
                                                     ],
                                                     style_cell={
                                                         'backgroundColor': 'rgb(50, 50, 50)',
                                                         'fontWeight': 'bold',
                                                         'color': 'white'
                                                     },
                                                 ),
                                dcc.Interval(
                                id='interval-component',
                                interval=1*60*1000, # in milliseconds
                                n_intervals=0
                                            )
                                  ])
                                ])

#load the csv file in. if this is not possible return the given dataframe
def readCSV(dfName):
    global path
    file = path+dfName
    try:
        tempDf = pd.read_csv(file)
    except:
        tempDf = pd.DataFrame()
    return tempDf
#show if currently in game with a known player
@app.callback(
    Output('played-with', 'children'),
    Input('update-button', 'n_clicks'),
    Input('interval-component', 'n_intervals'),
    State('sum-name', 'value'),
    prevent_initial_call=True
)
def update_playedWithText(n_clicks, n_interval, sumName):
    global summonerName
    global path
    global busy
    show = []
    summonerName = sumName
    ctx = dash.callback_context
    updateTrigger = ctx.triggered[0]['prop_id'].split('.')[0]
    if updateTrigger == 'interval-component' and busy == False and n_clicks > 0:
        busy = True
        getStats(summonerName)
        busy = False

    if busy == False:
        inGamePlayers = checkInGamePlayers(sumName)
        for x in inGamePlayers:
            show.append(html.Span('{}'.format(x), style={'color': 'white'}))
            show.append(html.Br())
        return show

@app.callback(
    Output('update-loading', 'children'),
    Input('update-button', 'n_clicks'),
    State('sum-name', 'value'),
    prevent_initial_call=True
)
def update_statusText(n, sumName):
    global summonerName
    global path
    summonerName = sumName
    status = 'Loading...'
    return [html.Span('{}'.format(status), style={'color': 'white'})]

@app.callback(
    Output('update-done', 'children'),
    Input('update-loading', 'children'),
    prevent_initial_call=True
)
def update_stats(status):
    global summonerName
    global path
    global busy
    while busy == True:
        None
    busy = True
    getStats(summonerName)
    busy = False
    status = 'Done'
    return [html.Span('{}'.format(status), style={'color': 'white'})]

@app.callback(
    Output('choose-version', 'options'),Output('choose-version', 'value'),
    Input('update-done', 'children'),
    prevent_initial_call=True
)
def choose_version(n):
    path = str(Path(__file__).parent.absolute())
    path = path+'/databaseLoL/'+summonerName+'/'
    versions = []
    for folder in sorted(os.listdir(path), reverse = True):
      # Instantiating the path of the file
        file_path = f'{path}/{folder}'
        # Checking whether the given file is a directory or not
        if os.path.isdir(file_path):
            try:
                # Printing the file pertaining to file_path
                row = {}
                row['label'] = folder
                row['value'] = folder
                versions.append(row)
            except:
                None
    return versions, versions[0]['value']

def folderScan(givenPath, csvDB):
    """
    scans through the given path and do tasks
    """
    try:
        for file in os.listdir(givenPath):
            # Inisiating the path of the file
            file_path = f"{givenPath}/{file}"
            # Check if file is a folder, if so go in that folder
            if os.path.isdir(file_path):
                newPath = givenPath + "/" + file
                csvDB = folderScan(newPath, csvDB)

            # check if file is a file, if so copy that file
            elif (file.endswith(".csv")):
                csvDB.append(file_path)
    #if there is an error, save it in txt file
    except Exception as error:
        print("path problem: ", str(error))
    return csvDB

@app.callback(
    Output('choose-subversion', 'options'),Output('choose-subversion', 'value'),
    Input('choose-version', 'value'),
    prevent_initial_call=True
)
def choose_subversion(version):
    global csvDB
    path = str(Path(__file__).parent.absolute())
    path = path+'/databaseLoL/'+summonerName+'/'
    if version == "all":
        csvDB = folderScan(path,csvDB)
    
    path = path+version+'/'
    subversions = []
    for folder in sorted(os.listdir(path), reverse = True):
      # Instantiating the path of the file
        file_path = f'{path}/{folder}'
        # Checking whether the given file is a directory or not
        if os.path.isdir(file_path):
            try:
                # Printing the file pertaining to file_path
                row = {}
                row['label'] = folder
                row['value'] = folder
                subversions.append(row)
            except:
                None
    return subversions, subversions[0]['value']

@app.callback(
    Output('choose-map', 'options'),Output('choose-map', 'value'),
    Input('choose-version', 'value'),
    Input('choose-subversion', 'value'),
    prevent_initial_call=True
)
def choose_maps(version, subversion):
    global csvDB
    maps = []
    path = str(Path(__file__).parent.absolute())
    path = path+'/databaseLoL/'+summonerName+'/'+version+'/'
    if version != "all" and subversion == 'all':
        csvDB = folderScan(path,csvDB)
    else:
        path = path+subversion+'/'
        csvDB = folderScan(path,csvDB)
    for file_path in sorted(csvDB):
    # Instantiating the path of the file
        file = file_path.split("/")[-1]
        # Checking whether the given file is a directory or not
        if os.path.isfile(file_path) and file.endswith(".csv"):
            try:
                # Printing the file pertaining to file_path
                fileName = file.split('.')[0]
                mapType = fileName.split('_')[1]
                found = False
                for i in range(0,len(maps),1):
                    if maps[i]['label'] == mapType:
                        found = True
                        break

                if found == False:
                    row = {}
                    row['label'] = mapType
                    row['value'] = mapType
                    maps.append(row)
            except:
                None
    return maps, maps[0]['value']
@app.callback(
    Output('choose-stats', 'options'),Output('choose-stats', 'value'),
    Input('choose-version', 'value'),
    Input('choose-subversion', 'value'),
    Input('choose-map', 'value'),
    
    prevent_initial_call=True
)
def update_database_dropdown(version, subversion, chosenMap):
    global summonerName
    global path
    global options
    global csvDB
    path = str(Path(__file__).parent.absolute())
    path = path+'/databaseLoL/'+summonerName+'/'+version+'/'+subversion+'/'
    # Iterating over all the files
    options = []
    for file_path in sorted(csvDB) :
      # Instantiating the path of the file
        file = file_path.split("/")[-1]

        # Checking whether the given file is a directory or not
        if os.path.isfile(file_path) and file.endswith(".csv"):
            try:
                # Printing the file pertaining to file_path
                fileName = file.split('.')[0]
                mapType = fileName.split('_')[1]
                fileName = fileName.split('_')[1:]
                sep = " "
                fileName = sep.join(fileName)
                if mapType == chosenMap:

                    found = False
                    for i in range(0,len(options),1):
                        if options[i]['label'] == fileName:
                            found = True
                            break

                    if found == False:

                        row = {}
                        row['label'] = fileName
                        row['value'] = file
                        options.append(row)
            except:
                None
    # print("options: ", options)
    return options, options[0]['value']

def getOptions(dfTemp):
    options = []
    for i in dfTemp.columns:
        row = {}
        row['label'] = i
        row['value'] = i
        options.append(row)
    return options

def mapStatsPercent(oldDf):
    ignoreCols = ['map', 'played', 'winrate']
    newDf = oldDf.copy()
    #for statement that goes through every column
    for column in oldDf.columns:
        #checks if column is in ignore Cols
        if (column in ignoreCols) == False:
            colSplit = column.split('_')
            newDf[column] = newDf[column].astype(str)
        #for statement that goes through every row
            for row in range(0, oldDf.shape[0]):
                #if col is won
                if colSplit[0] == 'won' and len(colSplit) == 1:
                    played = float(oldDf.at[row, 'played'])
                    wins = float(oldDf.at[row, column])
                    winRate = wins/played * 100.
                    winRate = round(winRate,2)
                    winRate = str(winRate)+'%'
                    newDf.at[row, column] = winRate

                elif colSplit[0] == 'won':
                    value = float(oldDf.at[row, column])
                    wins = float(oldDf.at[row, 'won'])
                    if wins == 0:
                        percent = 0.
                    else:
                        percent = value/wins * 100.
                    percent = round(percent,2)
                    percent = str(percent)+'%'
                    newDf.at[row, column] = percent

                elif colSplit[0] == 'lost':
                    value = float(oldDf.at[row, column])
                    lost = float(oldDf.at[row, 'played'] - oldDf.at[row, 'won'])
                    if lost == 0:
                        percent = 0
                    else:
                        percent = value/lost * 100.
                    percent = round(percent,2)
                    percent = str(percent)+'%'
                    newDf.at[row, column] = percent
    del newDf['winrate']
    return newDf

@app.callback(
    Output('choose-columns', 'options'),Output('choose-columns', 'value'),
    Input('choose-stats', 'value'),
    Input('choose-map', 'value'),
    Input('choose-version', 'value'),
    Input('choose-subversion', 'value'),
    prevent_initial_call=True
)
def update_statsDropdown(database, map, version, subversion):
    global df, csvDB
    if version == "all" or subversion == "all":
        df = dfCombiner(csvDB, map, database)
    else:
        df = readCSV(database)
    if database.split('.')[0].split('_')[1] == 'mapStats':
        df = mapStatsPercent(df)
    options = getOptions(df)
    return options, options[0]['value']

@app.callback(
    Output('stats-table', 'data'), Output('stats-table', 'columns'),
    Input('stats-table', 'sort_by'),
    Input('choose-columns', 'value'),
    prevent_initial_call=True
    )
def update_table(sort_by, cols):
    try:
        dff = df.sort_values(
            sort_by[0]['column_id'],
            ascending=sort_by[0]['direction'] == 'asc',
            inplace=False
        )
    except:
        # No sort is applied
        dff = df
    if isinstance(cols, str) == True:
        cols = [cols]
    if len(cols) < 2:
        cols = df.columns
    colsDict = []
    for i in cols:
        row = {'name': i, 'id': i, 'deletable': True}
        colsDict.append(row)

    return dff.to_dict('records'), colsDict