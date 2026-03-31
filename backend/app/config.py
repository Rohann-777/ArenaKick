import os

class Config:
    # Clé secrète pour JWT et sessions Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'arenakick-secret-key-2024'

    # Connexion MySQL via WampServer
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/arenakick'

    # Désactive le suivi des modifications (économise de la mémoire)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clé secrète pour JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'arenakick-jwt-secret-2024'

    # Durée de validité du token JWT (1 jour)
    JWT_ACCESS_TOKEN_EXPIRES = 86400

class DevelopmentConfig(Config):
    # Mode développement : affiche les erreurs détaillées
    DEBUG = True

class ProductionConfig(Config):
    # Mode production — cache les erreurs
    DEBUG = False

# Configuration active
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}