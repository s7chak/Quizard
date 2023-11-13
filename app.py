import dash
from flask_session import Session
from config import Config
external_stylesheets = Config.styles

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)
app.server.secret_key = 'quizard_s7chak'
Session(app)
server = app.server
app.config.suppress_callback_exceptions = True