from dash import html #HTML
from dash import dcc  #Interactive
from dash.dependencies import Input, Output

from app import app
from apps import display_LoLstats, roomAnalyzerDashboardV2, home, VideoDownloaderInterface
import logging

logging.getLogger('werkzeug').setLevel(logging.ERROR)


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/display_LoLstats' or pathname == '/lol':
        return display_LoLstats.layout
    elif pathname == '/roomAnalyzerDashboardV2' or pathname == '/room2':
        return roomAnalyzerDashboardV2.layout
    elif pathname == '/VideoDownloaderInterface' or pathname == '/viddown':
        return VideoDownloaderInterface.layout
    else:
        return home.layout



if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=False, port=8050)