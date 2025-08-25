# app/__init__.py
# Este ficheiro cria e configura a aplicação Flask.

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# 1. Cria as instâncias principais
app = Flask(__name__)
app.config.from_object(Config)

# 2. Cria as instâncias das extensões
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

# 3. Diz ao Flask-Login qual é a página de login
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça o login para aceder a esta página.'
login_manager.login_message_category = 'info' # Categoria para o Bootstrap

# 4. Importa as rotas e os modelos no final.
# Isto é crucial para evitar erros de importação circular.
from app import routes, models
