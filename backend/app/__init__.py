from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import config

# Initialisation des extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name='default'):
    # 1. Créer l'application Flask
    app = Flask(__name__)

    # 2. Charger la configuration (MySQL, JWT, etc.)
    app.config.from_object(config[config_name])

    # 3. Relier les extensions à l'application
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # 4. Enregistrer les routes
    from .routes.auth import auth_bp
    from .routes.tournois import tournois_bp
    from .routes.equipes import equipes_bp
    from .routes.matchs import matchs_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tournois_bp, url_prefix='/api/tournois')
    app.register_blueprint(equipes_bp, url_prefix='/api/equipes')
    app.register_blueprint(matchs_bp, url_prefix='/api/matchs')

    return app