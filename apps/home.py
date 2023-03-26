# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 11:30:24 2021

@author: guido
"""

import os
from pathlib import Path
import dash
from dash import html #HTML
from dash import dcc  #Interactive
from dash.dependencies import Input, Output, State
#home made libraries
#multipage app
from app import app
#load the begin data in
path = str(Path(__file__).parent.absolute())

#gets all the possible pages
def getPages():
    global path
    options = []
    for file in sorted(os.listdir(path)) :
      # Instantiating the path of the file
        file_path = f'{path}/{file}'

        # Checking whether the given file is a directory or not
        if os.path.isfile(file_path) and file.endswith(".py"):
            try:
                # Printing the file pertaining to file_path
                fileName = file.split('.')[0]
                if fileName != "__init__" and fileName != "home":
                    row = {}
                    row['label'] = fileName
                    row['value'] = "/"+fileName
                    options.append(row)
            except:
                None
    return options
#initialise the app
# app = dash.Dash(__name__,title="LoL stats")
#define the app
layout = html.Div(children=[
                      html.Div(className='row',  # Define the row element
                               children=[
                                  #the left side
                                      html.H2('Home', style = {'padding': '5px', 'fontSize': '30px', 'color': 'blue'}),
                                      html.Div(id='links'),
                                      dcc.Link('Torrent downloader', href='http://192.168.0.165:8060/', refresh=True),
                                      dcc.Interval(
                                                id='interval-component',
                                                interval=60*60*1000, # in milliseconds
                                                n_intervals=0
                                            )
                                  ])
                                ])

@app.callback(Output('links', 'children'),
              Input('interval-component', 'n_intervals'))
def update_links(n):
    pagesList = []
    pages = getPages()
    for page in pages:
        pagesList.append(dcc.Link(page['label'], href=page['value']))
        pagesList.append(html.Br())
    return pagesList






