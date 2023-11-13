import dash_bootstrap_components as dbc
import os
from datetime import datetime as dt

class Config():

    styles = [dbc.themes.DARKLY]
    today = dt.today()
    strtoday = today.strftime('%Y-%m-%d')
    wd_path = 'work/'
    collections = 'collections/'
