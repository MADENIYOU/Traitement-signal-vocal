from flask import Blueprint, render_template, request, jsonify, current_app
import os
from app.services.enregistrement import sauvegarder_audio
from app.services.segmentation import segmenter_audio

partie1_bp = Blueprint('partie1', __name__)

@partie1_bp.route('/')
def interface():
    """Affiche l'interface de numérisation et segmentation."""
    return render_template('partie1.html')

@partie1_bp.route('/sauvegarder', methods=['POST'])
def sauvegarder():
    """
    Endpoint pour recevoir l'audio du client et le sauvegarder.
    Attend : blob audio, locuteur, session, parametres.
    """
    if 'audio' not in request.files:
        return jsonify({"error": "Aucun fichier audio reçu"}), 400
    
    audio_file = request.files['audio']
    locuteur = request.form.get('locuteur', 'inconnu')
    session = request.form.get('session', 'session_01')
    params = {
        'freq': request.form.get('frequence'),
        'bits': request.form.get('codage')
    }
    
    chemin_complet = sauvegarder_audio(audio_file, locuteur, session, params)
    
    return jsonify({
        "message": "Enregistrement sauvegardé",
        "path": chemin_complet
    })

@partie1_bp.route('/segmenter', methods=['POST'])
def segmenter():
    """
    Endpoint pour lancer la segmentation automatique.
    """
    data = request.json
    filepath = data.get('filepath')
    top_db = float(data.get('seuil', 40))
    min_silence_len_ms = int(data.get('duree_min', 300))
    
    try:
        # Appel au service mis à jour
        segments = segmenter_audio(
            filepath, 
            top_db=top_db, 
            min_silence_len_ms=min_silence_len_ms
        )
        
        return jsonify({
            "message": f"{len(segments)} segments détectés",
            "segments": segments
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
