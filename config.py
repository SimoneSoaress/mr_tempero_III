import os

# Encontra o caminho absoluto da pasta onde este ficheiro está.
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Chave secreta para proteger os formulários e as sessões
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'TOLEDO'
    
    # Configuração da base de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
