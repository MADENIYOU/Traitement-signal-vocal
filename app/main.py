import os
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from app.routes.partie1 import partie1_bp
from app.routes.partie2 import partie2_bp

def create_app():
    """
    Crée et configure l'instance de l'application Flask.
    """
    app = Flask(__name__)
    CORS(app)

    # Configuration des dossiers de stockage
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'database')
    app.config['SEGMENTS_FOLDER'] = os.path.join(os.getcwd(), 'segments')
    # Configuration Partie 2 - Filtrage FFT
    app.config['UPLOAD_PARTIE2'] = os.path.join(os.getcwd(), 'database', 'uploads_partie2')
    app.config['FILTERED_FOLDER'] = os.path.join(os.getcwd(), 'database', 'filtres')

    # Création des dossiers s'ils n'existent pas
    for folder in [
        app.config['UPLOAD_FOLDER'], 
        app.config['SEGMENTS_FOLDER'],
        app.config['UPLOAD_PARTIE2'],
        app.config['FILTERED_FOLDER']
    ]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    # Debug - afficher les chemins (aide au développement)
    print("UPLOAD P2:", app.config['UPLOAD_PARTIE2'])
    print("FILTERED:", app.config['FILTERED_FOLDER'])

    # Route pour servir les segments audio
    @app.route('/segments/<path:filename>')
    def serve_segments(filename):
        return send_from_directory(app.config['SEGMENTS_FOLDER'], filename)

    # Enregistrement des Blueprints (routes)
    app.register_blueprint(partie1_bp, url_prefix='/partie1')
    # Partie 2 - Filtrage FFT
    app.register_blueprint(partie2_bp, url_prefix='/partie2')

    @app.route('/')
    def index():
        """Route principale pointant vers l'accueil."""
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    # Debug activé pour faciliter le développement étape par étape
    app.run(debug=True, host='0.0.0.0', port=5000)
