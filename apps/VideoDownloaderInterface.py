# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 14:58:55 2021

@author: guido
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
#home made libraries
from videoDownloader import *
#multipage app
from app import app

def loadDownloadPath():
    global path
    pathFile = str(Path(__file__).parent.absolute())
    try:
        file2write=open(pathFile+"/downloadPath.txt",'r')
        path = str(file2write.read())
        file2write.close()
    except:
        path = pathFile+'/Videos/'
    return path

def saveDownloadPath():
    global path
    pathFile = str(Path(__file__).parent.absolute())
    makeDir(path)
    file2write=open(""+pathFile+"/downloadPath.txt",'w')
    file2write.write(str(path))
    file2write.close()

def makeDir(path):
    try:
        os.makedirs(path)
    except:
        None     

df = pd.DataFrame()
busy = False
#load the external stylesheet
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#initialise the app
# app = dash.Dash(__name__,title="LoL stats")
#define the app
path = loadDownloadPath()
layout = html.Div(children=[
                      html.Div(className='row',  # Define the row element
                               children=[
                                  #the left side
                                            html.H2('Video downloader', style = {'padding': '5px', 'fontSize': '30px', 'color': 'blue'}),
                                            html.Div([
                                            html.Span("download-path: ", style = {'padding': '5px', 'fontSize': '20px', 'color': 'white'}),
                                            dcc.Input(id='vid-path', value=path, type='text', style={'width': '15%'}),
                                            html.Button(id='pathUpdate-button', n_clicks=0, children='Update', style={'color': 'white'}),
                                            ]),
                                            html.Div(id='path-update'),
                                            html.Div([
                                            html.Span("Video-Link:", style = {'padding': '5px', 'fontSize': '20px', 'color': 'white'}),
                                            dcc.Input(id='vid-link', value='', type='text', style={'width': '17.3%'}),
                                            html.Button(id='vidUpdate-button', n_clicks=0, children='GO', style={'color': 'white'}),
                                            ]),
                                            html.Div(id='vidUpdate-loading'),
                                            html.Div(id='vidUpdate-done')
                                  ])
                                ])
#update the download path
@app.callback(
    Output('path-update', 'children'),
    Input('pathUpdate-button', 'n_clicks'),
    State('vid-path', 'value'),
    prevent_initial_call=True
)
def update_videoPath(n, downloadPath):
    global path
    path = downloadPath
    saveDownloadPath()
    status = 'Done'
    return [html.Span('{}'.format(status), style={'color': 'white'})]

@app.callback(
    Output('vid-path', 'value'),
    Input('path-update', 'children'),
    prevent_initial_call=False
)
def update_textField(n):
    global path
    return loadDownloadPath()

@app.callback(
    Output('vidUpdate-loading', 'children'),
    Input('vidUpdate-button', 'n_clicks'),
    State('vid-link', 'value'),
    prevent_initial_call=True
)
def update_statusText(n, vidLinkTemp):
    global vidLink
    global path
    vidLink = vidLinkTemp
    status = 'starting'
    return [html.Span('{}'.format(status), style={'color': 'white'})]

@app.callback(
    Output('vidUpdate-done', 'children'),
    Input('vidUpdate-loading', 'children'),
    prevent_initial_call=True
)
def update_stats(status):
    global vidLink
    global path
    succes, failed, existed = downloadTheLink(vidLink, path)
    status = 'succes: ' + str(succes) + ' failed: ' + str(failed) + ' existed: '+ str(existed)
    return [html.Span('{}'.format(status), style={'color': 'white'})]