import os
from flask import Flask, render_template
from flask_cors import CORS
from app.routes.partie1 import partie1_bp

def create_app():
    """
    Crée et configure l'instance de l'application Flask.
    """
    app = Flask(__name__)
    CORS(app)

    # Configuration des dossiers de stockage
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'database')
    app.config['SEGMENTS_FOLDER'] = os.path.join(os.getcwd(), 'segments')

    # Création des dossiers s'ils n'existent pas
    for folder in [app.config['UPLOAD_FOLDER'], app.config['SEGMENTS_FOLDER']]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Enregistrement des Blueprints (routes)
    app.register_blueprint(partie1_bp, url_prefix='/partie1')

    @app.route('/')
    def index():
        """Route principale pointant vers l'accueil."""
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    # Debug activé pour faciliter le développement étape par étape
    app.run(debug=True, host='0.0.0.0', port=5000)
