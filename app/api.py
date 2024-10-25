from flask import jsonify, current_app, request
from . import api_bp
from .analyzer import EnhancedMusicAnalyzer

@api_bp.route('/analyze', methods=['POST'])
def analyze_track():
    try:
        data = request.get_json()
        spotify_url = data.get('spotify_url')
        
        if not spotify_url:
            return jsonify({'error': 'No Spotify URL provided'}), 400
            
        analyzer = EnhancedMusicAnalyzer()
        results = analyzer.analyze_from_spotify(spotify_url)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        current_app.logger.error(f"API error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'api_version': '1.0.0'
    })