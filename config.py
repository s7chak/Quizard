import dash_bootstrap_components as dbc
import os
from datetime import datetime as dt

class Config():
    today = dt.today()
    strtoday = today.strftime('%Y-%m-%d')
    quiz_limit = 5