from flask import render_template, jsonify, request
from . import create_app
from .analyzer import EnhancedMusicAnalyzer

app = create_app()
analyzer = EnhancedMusicAnalyzer()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        spotify_url = data.get('spotify_url')
        
        if not spotify_url:
            return jsonify({'error': 'No Spotify URL provided'}), 400
            
        results = analyzer.analyze_from_spotify(spotify_url)
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)