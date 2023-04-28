# -*- coding: utf-8 -*-
#
# by: Guido Kok
import dash
from dash import html #HTML
from dash import dcc  #Interactive
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
from pathlib import Path
import time
from datetime import date
import os
from plotly.subplots import make_subplots
import plotly.graph_objects as go
#multipage app
from app import app
global locationStart
#the confort borders for humidity and temperature
humiBorder = [30.,50.]
tempBorder = [18.,22.]
#lookup table for the different iaq ranges
iaqTab = pd.DataFrame([
                    [0.,50.,'Excellent', 'Nothing','Nothing', 'darkgreen'],
                    [50.,100.,'Good', 'Nothing','Nothing', 'green'],
                    [100.,150.,'Lightly polluted', 'reduction of well-being possible','ventilation', 'yellow'],
                    [150.,200.,'Moderately polluted', 'significant irritation possible','increase ventilation', 'orange'],
                    [200.,250.,'Heavily polluted', 'Headache terretory','optimize ventilation', 'red'],
                    [250.,300.,'Severely polluted', 'Big problem','maximize ventilation and reduce people', 'purple'],
                    [300.,510.,'Heavily polluted', 'Headache terretory','maximize ventilation and scidadle', 'brown']
                    ],
                  columns = ['Lower range','Upper range','Quality','Impact','Action','Colour'])
#dict for iaq accuracy values
iaqAccTab = {0: 'Stabilizing',
             1: 'No clear reference',
             2: 'Calibrating',
             3: 'Calibrated'}
#lookup table for the different co2 ranges
co2Tab = pd.DataFrame([ #https://www.kane.co.uk/knowledge-centre/what-are-safe-levels-of-co-and-co2-in-rooms
                    [0.,400.,'Normal outdoor', 'darkgreen'],
                    [400.,1000.,'Normal indoor, good air', 'green'],
                    [1000.,2000.,'Complaints of drowsiness and poor air', 'yellow'],
                    [2000.,5000.,'Headaches, sleepiness and stagnant, stale, stuffy air. Poor concentration, loss of attention, increased heart rate and slight nausea may also be present.', 'red'],
                    [5000.,40000.,'Workplace exposure limit (as 8-hour TWA) in most jurisdictions.', 'purple'],
                    [40000.,99999.,'Exposure may lead to serious oxygen deprivation resulting in permanent brain damage, coma, even death.', 'brown']
                    ],
                  columns = ['Lower range','Upper range','Effect','Colour'])

#lookup table for the different pm2.5 dust particals ranges
pm25Tab = pd.DataFrame([
                    [0.,99999.,'Unknown', 'darkgreen'],
                    ],
                  columns = ['Lower range','Upper range','Effect','Colour'])
#lookup table for the different pm2.5 dust particals ranges
pm100Tab = pd.DataFrame([
                    [0.,99999.,'Unknown', 'darkgreen'],
                    ],
                  columns = ['Lower range','Upper range','Effect','Colour'])
#retreives the columns names for the different options
def getOptions():
    options = []
    for i in df.columns[2:]:
        row = {}
        row['label'] = i
        row['value'] = i
        options.append(row)
    return options

#checks in which range the value belongs, returns an dict with all the properties of that range
def chkIAQ(val):
    for i in range(0, len(iaqTab), 1):
        if val >= iaqTab.iloc[i]['Lower range'] and val <  iaqTab.iloc[i]['Upper range']:
            iaqDict = {'Quality' : iaqTab.iloc[i]['Quality'],
                       'Action' : iaqTab.iloc[i]['Action'],
                       'Colour' : iaqTab.iloc[i]['Colour']
                }
            return iaqDict
#checks in which range the value belongs, returns an dict with all the properties of that range
def chkCO2(val):
    for i in range(0, len(co2Tab), 1):
        if val >= co2Tab.iloc[i]['Lower range'] and val <  co2Tab.iloc[i]['Upper range']:
            co2Dict = {'Effect' : co2Tab.iloc[i]['Effect'],
                       'Colour' : co2Tab.iloc[i]['Colour']
                }
            return co2Dict
#checks in which range the value belongs, returns an dict with all the properties of that range
def chkpm25(val):
    for i in range(0, len(pm25Tab), 1):
        if val >= pm25Tab.iloc[i]['Lower range'] and val <  pm25Tab.iloc[i]['Upper range']:
            pm25Dict = {'Effect' : pm25Tab.iloc[i]['Effect'],
                       'Colour' : pm25Tab.iloc[i]['Colour']
                }
            return pm25Dict
#checks in which range the value belongs, returns an dict with all the properties of that range
def chkpm100(val):
    for i in range(0, len(pm100Tab), 1):
        if val >= pm100Tab.iloc[i]['Lower range'] and val <  pm100Tab.iloc[i]['Upper range']:
            pm100Dict = {'Effect' : pm100Tab.iloc[i]['Effect'],
                       'Colour' : pm100Tab.iloc[i]['Colour']
                }
            return pm100Dict
#selects the data of past given hours
def readCSV(tempDf, dfName):
    global pathLoc
    file = pathLoc+'/'+dfName+'.csv'
    try:
        tempDf = pd.read_csv(file)
    except:
        tempDf = pd.DataFrame()
    return tempDf
def date2int(date):
    date = date.split('-')
    date = int(date[2]) + int(date[1])*100 + int(date[0])*10000
    return date

def time2int(time):
    time = time.split(':')
    #makes one huge time value, easy to detect if current time is higher or lower than given time
    time = int(time[0])*10000 + int(time[1])*100 + int(time[2])
    return time

def getTimeDate(hoursBack):
    beginTime = time.time() - hoursBack*60.*60.
    beginTimeDate = time.strftime('%Y-%m-%d', time.localtime(beginTime))
    beginTimeDate = date2int(beginTimeDate)
    beginTimeHMS = time.strftime('%H:%M:%S', time.localtime(beginTime))
    beginTimeHMS = time2int(beginTimeHMS)
    return beginTimeDate, beginTimeHMS

def addFromTimeStamp(selection, fileName, beginHMS):
    df = readCSV(selection, fileName)
    tempDf = pd.DataFrame()
    for i in range(0,df.shape[0]-1,1):
        tempHMS = df['timeStamp'][i]
        tempHMS = time2int(tempHMS)
        if tempHMS >= beginHMS:
            tempDf = df[i:].copy(deep=False)
            tempDf = tempDf.reset_index(drop=True)
            break
    df = mergeDf(selection, tempDf)
    return df

def addDf(selection, fileName):
    df = readCSV(selection, fileName)
    df = mergeDf(selection,df)
    return df

def mergeDf(df1, df2):
    frames = [df1, df2]
    mergedDf = pd.concat(frames)
    return mergedDf

def selectTimeFrame(hoursBack):
    global pathLoc
    selection = pd.DataFrame()
    #calculates on which date and time to begin
    beginTimeDate, beginTimeHMS = getTimeDate(hoursBack)
    for file in sorted(os.listdir(pathLoc)):
        file_path = f'{pathLoc}/{file}'
        if os.path.isfile(file_path) and file.endswith(".csv"):
            fileName = file.split('.')[0]
            if len(fileName.split('-')) == 3:
                fileDate = date2int(fileName)
                if fileDate == beginTimeDate:
                    selection = addFromTimeStamp(selection,fileName, beginTimeHMS)
                elif fileDate > beginTimeDate:
                    selection = addDf(selection,fileName)
                    
    selection = selection.reset_index(drop=True)
    selection = selection.sort_values(by=['date','timeStamp'], ascending=True) 
    return selection

def selectDate(dateBegin, dateEnd = -1):
    global pathLoc
    if type(dateEnd) != str:
        dateEnd = dateBegin
    dateBeginInt = date2int(dateBegin)
    dateEndInt = date2int(dateEnd)
    selection = pd.DataFrame()
    for file in sorted(os.listdir(pathLoc)):
        file_path = f'{pathLoc}/{file}'
        if os.path.isfile(file_path) and file.endswith(".csv"):
            fileName = file.split('.')[0]
            if len(fileName.split('-')) == 3:
                fileNameInt = date2int(fileName)
                if fileNameInt >= dateBeginInt and fileNameInt <= dateEndInt:
                    selection = addDf(selection,fileName)
            
            
    selection = selection.reset_index(drop=True)
    selection = selection.sort_values(by=['date','timeStamp'], ascending=True) 
    return selection

#get rid of all the columns that are not used
def filterDf(tempDf, toKeep):
    tempDf = tempDf[toKeep]
    return tempDf

def calcDt(tempDf, keep):
    if tempDf.shape[1] == 2:
        tempDf = calcOneLineDt(tempDf, keep)
    elif tempDf.shape[1] == 3:
        tempDf = calcTwoLinesDt(tempDf, keep)
    return tempDf

def calcOneLineDt(tempDf, keep):
    tempDf['diff'] = tempDf[keep[1]].diff()
    return tempDf
    
def calcTwoLinesDt(tempDf, keep):
    tempDf['diff'] = tempDf[keep[1]] - tempDf[keep[2]]
    return tempDf

#load the begin data in
path = str(Path(__file__).parent.absolute())+"/database_roomAnalyzer"
startDate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
#update starting values for temperature compensation and measurement interval
try:
    dfParam = pd.read_csv(path+'/parameters.csv')
    tempCompStart = dfParam['temperature compensation'][0]
    timeIntervalStart = dfParam['time interval'][0]
    locationStart = dfParam['location'][0]
except:
    tempCompStart = -2
    timeIntervalStart = 5
    locationStart = 'home'

pathLoc = path+'/'+str(locationStart)
if os.path.isdir(pathLoc) == False:
    os.mkdir(pathLoc)

file = pathLoc+'/'+startDate+'.csv'
try:
    df = pd.read_csv(file)
except:
    df = pd.DataFrame(columns=['date', 'timeStamp', 'temperature', 'outside temperature', 'humidity', 'pressure','gasResistance'])

#define the app
layout = html.Div(children=[
                      html.Div(className='row',  # Define the row element
                               children=[
                                  #the left side
                                  html.Div(className='four columns div-user-controls',
                                           children = [
                                            html.H2('Room Analyzer', style = {'padding': '5px', 'fontSize': '30px', 'color': 'blue'}),
                                            #shows the different current values
                                            html.Div(id='last-update'),
                                            html.Div(id='cur-temp'),
                                            html.Div(id='cur-outsideTemp'),
                                            html.Div(id='cur-humi'),
                                            html.Div(id='cur-co2'),
                                            html.Div(id='cur-pm25'),
                                            html.Div(id='cur-pm100'),
                                            html.Div(id='cur-iaq'),
                                            html.Div(id='cur-voc'),
                                            html.Div(id='cur-press'),
                                            html.Div(id='cur-gasRes'),
                                            html.Br(),
                                            html.Div([
                                                html.Span("Temperature compensation (°C): ", style = {'padding': '5px', 'fontSize': '20px', 'color': 'white'}),
                                                dcc.Input(id='temp-comp', value=str(tempCompStart), type='number', style={'width': '15%', 'float': 'right'})
                                            ]),
                                            html.Br(),
                                            html.Div([
                                                html.Span("Measurement interval (min): ", style = {'padding': '5px', 'fontSize': '20px', 'color': 'white'}),
                                                dcc.Input(id='time-interval', value=str(timeIntervalStart), type='number', style={'width': '15%', 'float': 'right'})    
                                            ]),
                                            html.Br(),
                                            html.Div([
                                                html.Span("Location: ", style = {'padding': '5px', 'fontSize': '20px', 'color': 'white'}),
                                                dcc.Input(id='cur-location', value=str(locationStart), type='text', style={'width': '15%', 'float': 'right'})
                                            ]),

                                            html.Button(id='update-button', n_clicks=0, children='Update', style={'color': 'white', 'float': 'middle'}),
                                            html.Div(id='update-txt')

                                        ]),
                                  #the right side
                                  html.Div(className='eight columns div-for-charts bg-grey',
                                           children=[
                                            #the hours back box and the dropdown menu
                                            html.Div(children = [
                                                #the Hours back input box
                                                html.Div(["Hours back: ",
                                                          dcc.Input(id='Hours-back', value='24', type='number', style={'width': '10%', 'float': 'middle'}),
                                                #dropdown menu for the different options
                                                dcc.Dropdown(
                                                    id='choose-graph',
                                                    options= getOptions(),
                                                    value=[getOptions()[0]['value']],
                                                    multi=True,
                                                    clearable=False,
                                                    style={'width': '80%', 'float': 'right'}
                                            )])
                                            ]),
                                            html.Div(id='date-selecter'),
                                            #adds an checkbox to turn overlay of y-axes on or off
                                            html.Div(children = [
                                            dcc.Checklist(
                                                        id='chk-overlap',
                                                        options=[
                                                            {'label': 'Overlap', 'value': 'Overlp'}
                                                        ],
                                                        value=['Overlp'],
                                                        style={'width': '10%', 'float': 'left'}
                                                    ),
                                            dcc.Checklist(
                                                        id='to-zero',
                                                        options=[
                                                            {'label': 'To zero', 'value': 'toZero'}
                                                        ],
                                                        value=[],
                                                        style={'width': '10%', 'float': 'left'}
                                                    ),
                                            dcc.Checklist(
                                                        id='calc-diff',
                                                        options=[
                                                            {'label': 'difference', 'value': 'diffDt'}
                                                        ],
                                                        value=[],
                                                        style={'width': '10%', 'float': 'left'}
                                                    ),
                                            dcc.Checklist(
                                                        id='diff-only',
                                                        options=[
                                                            {'label': 'only difference', 'value': 'showDtOnly'}
                                                        ],
                                                        value=[],
                                                        style={'width': '10%', 'float': 'left'}
                                                    )
                                            ]),
                                            #the graph
                                            dcc.Graph(id='live-update-graph'),
                                            #the update element
                                            dcc.Interval(
                                                id='interval-component',
                                                interval=1*60*1000, # in milliseconds
                                                n_intervals=0
                                            )
                                        ])

                                  ])
                                ])

# Update the graph when interval hits, different Hours back value or new selection in the option
@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'),
              Input('Hours-back', 'value'),
              Input('choose-graph', 'value'),
              Input('chk-overlap', 'value'),
              Input('to-zero', 'value'),
              Input('calc-diff', 'value'),
              Input('diff-only', 'value'),
              Input('Date-select', 'start_date'),
              Input('Date-select', 'end_date'),
              
              )
def update_graph_live(n, hours, options, overlap, toZero, diffDt, showDtOnly, dateBegin, dateEnd):
    global df
    global locationStart
    global pathLoc
    if type(dateBegin) == str:    
        df = selectDate(dateBegin,dateEnd)
    else:
        hours = float(hours)
        if hours == None:
            hours = 24.
        #selects the timeframe
        df = selectTimeFrame(hours)
    df['timeStamp'] = df['timeStamp'] + ' ' + df['date']
    #if only one option is selected, put the option in a list
    if isinstance(options, str) == True:
        options = [options]
    keep = ['timeStamp'] + options
    filteredDf = filterDf(df, keep)    
    
    #create template figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    fig.update_layout(template="plotly_dark")
    i = 0
    #checks if overlap is selected
    if len(overlap) == 0:
        overlap = ['None']
    if len(toZero) == 0:
        toZero = ['None']
    if len(diffDt) == 0:
        diffDt = ['None']
    if len(showDtOnly) == 0:
        showDtOnly = ['None']
    
    if diffDt[0] == 'diffDt':
        filteredDf = calcDt(filteredDf, keep)[1:]
    
    if showDtOnly[0] == 'showDtOnly' and diffDt[0] == 'diffDt':
        filteredDf = filterDf(filteredDf, ['timeStamp', 'diff'])
    
    dfColumns = []
    for col in filteredDf.columns[1:]:
        dfColumns.append(col)
    #loop through all the selected options
    for option in dfColumns:
        if i == 1 and overlap[0] == 'Overlp':
            secondY = True
            modus = 'lines'
            dashOpt = 'dash'
            widthOpt = 1
        else:
            secondY = False
            modus = 'lines'
            dashOpt = None
            widthOpt = 2
        #change the borders to the correct border for the option
        if option == 'humidity':
            borders = humiBorder
        elif option == 'temperature':
            borders = tempBorder
        else:
            borders = ['none','none']

        if option == 'bsec iaq':
            for i in range(0, len(iaqTab), 1):
                fig.add_trace(go.Scatter(x=filteredDf['timeStamp'], y=filteredDf[option].where(filteredDf[option] >= iaqTab.iloc[i]['Lower range']), mode=modus, line = dict(color=iaqTab.iloc[i]['Colour'], width=widthOpt, dash=dashOpt), name= option), secondary_y= secondY)
        elif option == 'co2' or option == 'bsec co2_equivalent':
            for i in range(0, len(co2Tab), 1):
                fig.add_trace(go.Scatter(x=filteredDf['timeStamp'], y=filteredDf[option].where(filteredDf[option] >= co2Tab.iloc[i]['Lower range']), mode=modus, line = dict(color=co2Tab.iloc[i]['Colour'], width=widthOpt, dash=dashOpt), name= option), secondary_y= secondY)
        elif option == 'pm25':
            for i in range(0, len(pm25Tab), 1):
                fig.add_trace(go.Scatter(x=filteredDf['timeStamp'], y=filteredDf[option].where(filteredDf[option] >= pm25Tab.iloc[i]['Lower range']), mode=modus, line = dict(color=pm25Tab.iloc[i]['Colour'], width=widthOpt, dash=dashOpt), name= option), secondary_y= secondY)
        elif option == 'pm100' :
            for i in range(0, len(pm100Tab), 1):
                fig.add_trace(go.Scatter(x=filteredDf['timeStamp'], y=filteredDf[option].where(filteredDf[option] >= pm100Tab.iloc[i]['Lower range']), mode=modus, line = dict(color=pm100Tab.iloc[i]['Colour'], width=widthOpt, dash=dashOpt), name= option), secondary_y= secondY)

        else:
            #adds the plot in the green to the template
            fig.add_trace(go.Scatter(x=filteredDf['timeStamp'], y=filteredDf[option], mode=modus, line =dict(color='green', width=widthOpt, dash=dashOpt), name= option), secondary_y= secondY)
            #when under the first border, make the line red
            if borders[0] !='none':
                fig.add_trace(go.Scatter(x=filteredDf['timeStamp'], y=filteredDf[option].where(filteredDf[option] <borders[0]), mode=modus, line =dict(color='red', width=widthOpt, dash=dashOpt), name= option), secondary_y= secondY)
            #when above second border, make line red
            if borders[1] !='none':
                fig.add_trace(go.Scatter(x=filteredDf['timeStamp'], y=filteredDf[option].where(filteredDf[option] >borders[1]), mode=modus, line =dict(color='red', width=widthOpt, dash=dashOpt), name= option), secondary_y= secondY)

        i = i+1
    #hide the legend
    fig.update_layout(showlegend=False)
    #change y axes grid to darkblue to improve the readability
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='darkblue')
    #fig.update_xaxes(tickangle=-45)
    if toZero[0] == 'toZero':
        fig.update_yaxes(rangemode="tozero")
    return fig

@app.callback(Output('temp-comp', 'value'),
              Input('update-txt', 'children'),
              Input('interval-component', 'n_intervals'))
def update_tempComp(value, n):
    global tempCompStart
    dfParam = pd.read_csv(path+'/parameters.csv')
    tempCompStart = dfParam['temperature compensation'][0]
    return tempCompStart

#update time interval field
@app.callback(Output('time-interval', 'value'),
             Input('update-txt', 'children'),
             Input('interval-component', 'n_intervals'))
def update_timeInter(value, n):
    global timeIntervalStart
    dfParam = pd.read_csv(path+'/parameters.csv')
    timeIntervalStart = dfParam['time interval'][0]
    return timeIntervalStart


#update time interval field
@app.callback(Output('cur-location', 'text'),
             Input('update-txt', 'children'),
             Input('interval-component', 'n_intervals'))
def update_timeLoc(value, n):
    global locationStart
    global pathLoc
    dfParam = pd.read_csv(path+'/parameters.csv')
    locationStart = dfParam['location'][0]
    return locationStart
#saves the database into csv
def closeDatabase(df, path, name):
        df.to_csv(path+'/'+name+'.csv', index=False)
#update temperature compensation and update frequency on update button press
@app.callback(Output('update-txt', 'children'),
              Input('update-button', 'n_clicks'),
              State('temp-comp', 'value'),
              State('time-interval', 'value'),
              State('cur-location', 'value'),
              prevent_initial_call=True)

def update_preferences(n_clicks, tempComp, timeInt, location):
    global tempCompStart
    global timeIntervalStart
    global locationStart
    global pathLoc
    
    df = pd.DataFrame()
    row = {}
    if timeInt <=0.:
        timeInt = 0.01
    row['temperature compensation'] = tempComp
    row['time interval'] = timeInt
    row['location'] = location
    
    tempCompStart = tempComp
    timeIntervalStart = timeInt
    locationStart = location
    timeInt = float(timeInt)
    pathLoc = path+'/'+str(location)
    if os.path.isdir(pathLoc) == False:
        os.mkdir(pathLoc)
    df = df.append(row, ignore_index=True)
    closeDatabase(df,path, 'parameters')
    return [html.Span('Updated {} times'.format(n_clicks), style={'color': 'white'})]


#Update the last date
@app.callback(Output('date-selecter', 'children'),
              Input('interval-component', 'n_intervals'))
def update_lastUpdate(n):
    return ["Date Select: ",
              dcc.DatePickerRange(
                    id='Date-select',
                    first_day_of_week = 1,
                    with_portal=False,
                    day_size=50,
                    calendar_orientation= 'horizontal',
                    updatemode = 'singledate',
                    show_outside_days = True,
                    clearable=True,
                    max_date_allowed= date.today(),
                    display_format= 'Y-M-D'
                )]

#Update the text on the leftside when the graph updates
@app.callback(Output('last-update', 'children'),
              Input('live-update-graph', 'figure'))
def update_lastUpdate(n):
    global df
    time = df['timeStamp'][df.shape[0]-1]
    style = {'padding': '5px', 'fontSize': '20px', 'color': 'white'}
    return [html.Span('Last updated: {}'.format(time), style = style)]

@app.callback(Output('cur-temp', 'children'),
              Input('live-update-graph', 'figure'))
def update_temp(n):
    global df
    temp = df['temperature'][df.shape[0]-1]
    if temp >= tempBorder[0] and temp <= tempBorder[1]:
        style = {'padding': '5px', 'fontSize': '20px', 'color': 'green'}
        advice = ""
    else:
        style = {'padding': '5px', 'fontSize': '20px', 'color': 'red'}
        advice = ""
    return [html.Span('Temperature: {0:0.2f} C \t'.format(temp), style = style), html.Span(advice, style = style)]

@app.callback(Output('cur-humi', 'children'),
              Input('live-update-graph', 'figure'))
def update_humi(n):
    global df
    humi = df['humidity'][df.shape[0]-1]
    if humi < 30:
      colour = 'red'
      advice = 'humidity too low!'
    elif humi > 50:
      colour = 'red'
      advice = 'humidity too high!'
    else:
        colour = 'green'
        advice = ''
    style = {'padding': '5px', 'fontSize': '20px', 'color': colour}
    return [html.Span('humidity: {0:0.2f} % \t '.format(humi), style = style), html.Span(advice, style = style)]

@app.callback(Output('cur-outsideTemp', 'children'),
              Input('live-update-graph', 'figure'))
def update_outsideTemp(n):
    global df
    temp = df['outside temperature'][df.shape[0]-1]
    style = {'padding': '5px', 'fontSize': '20px', 'color': 'grey'}
    return [html.Span('Outside temperature: {0:0.2f} C \t'.format(temp), style = style)]

@app.callback(Output('cur-iaq', 'children'),
              Input('live-update-graph', 'figure'))
def update_iaq(n):
    global df
    iaq = df['bsec iaq'][df.shape[0]-1]
    iaqAcc = iaqAccTab[int(df['bsec iaq_accuracy'][df.shape[0]-1])]
    iaqDict = chkIAQ(iaq)
    advice = iaqDict['Action']
    style = {'padding': '5px', 'fontSize': '20px', 'color': iaqDict['Colour']}
    return [html.Span('Indoor air quality(iaq)({}) : {} \t'.format((iaqAcc), round(iaq,2)), style = style), html.Span(advice, style = style)]

@app.callback(Output('cur-voc', 'children'),
              Input('live-update-graph', 'figure'))
def update_voc(n):
    global df
    voc = df['bsec  breath_voc_equivalent '][df.shape[0]-1]
    style = {'padding': '5px', 'fontSize': '20px', 'color': 'grey'}
    return [html.Span('Estimated VOC: {} ppm ({} ppb)\t'.format(round(voc,2), round(voc*1000.,2)), style = style)]

@app.callback(Output('cur-co2', 'children'),
              Input('live-update-graph', 'figure'))
def update_co2(n):
    global df
    co2 = df['co2'][df.shape[0]-1]
    co2Dict = chkCO2(co2)
    style = {'padding': '5px', 'fontSize': '20px', 'color': co2Dict['Colour']}
    effect = co2Dict['Effect']
    return [html.Span('CO2: {0:0.2f} ppm\t'.format(co2), style = style), html.Span(effect, style = style)]

@app.callback(Output('cur-pm25', 'children'),
              Input('live-update-graph', 'figure'))
def update_pm25(n):
    global df
    pm25 = df['pm2.5'][df.shape[0]-1]
    pm25Dict = chkpm25(pm25)
    style = {'padding': '5px', 'fontSize': '20px', 'color': pm25Dict['Colour']}
    effect = pm25Dict['Effect']
    return [html.Span('dust pm2.5: {0:0.2f} ppm\t'.format(pm25), style = style), html.Span(effect, style = style)]

@app.callback(Output('cur-pm100', 'children'),
              Input('live-update-graph', 'figure'))
def update_pm100(n):
    global df
    pm100 = df['pm10'][df.shape[0]-1]
    pm100Dict = chkpm100(pm100)
    style = {'padding': '5px', 'fontSize': '20px', 'color': pm100Dict['Colour']}
    effect = pm100Dict['Effect']
    return [html.Span('dust pm10: {0:0.2f} ppm\t'.format(pm100), style = style), html.Span(effect, style = style)]

@app.callback(Output('cur-press', 'children'),
              Input('live-update-graph', 'figure'))
def update_press(n):
    global df
    press = df['pressure'][df.shape[0]-1]
    style = {'padding': '5px', 'fontSize': '20px', 'color': 'grey'}
    return [html.Span('Pressure: {0:0.2f} hPa \t'.format(press), style = style)]

@app.callback(Output('cur-gasRes', 'children'),
              Input('live-update-graph', 'figure'))
def update_gasRes(n):
    global df
    gasRes = df['gasResistance'][df.shape[0]-1]
    style = {'padding': '5px', 'fontSize': '20px', 'color': 'grey'}
    return [html.Span('Gas resistance: {0:0.2f} Ohm \t'.format(gasRes), style = style)]

# if __name__ == '__main__':
#     app.run_server(host='0.0.0.0', port=8050, debug= False)