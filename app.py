"""
app.py
Flask application template for the warm-up assignment

Students need to implement the API endpoints as specified in the assignment.
"""

from flask import Flask, request, jsonify, render_template
from starter_preprocess import TextPreprocessor
import traceback

app = Flask(__name__)
preprocessor = TextPreprocessor()

@app.route('/')
def home():
    """Render a simple HTML form for URL input"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Text preprocessing service is running"
    })

@app.route('/api/clean', methods=['POST'])
def clean_text():
    try:
        data = request.get_json(silent=True)
        if not data or "url" not in data:
            return jsonify({"success": False, "error": "Missing JSON body or 'url' field."}), 400

        url = str(data["url"]).strip()
        if not url:
            return jsonify({"success": False, "error": "URL must be a non-empty string."}), 400

        raw_text = preprocessor.fetch_from_url(url)
        cleaned = preprocessor.clean_gutenberg_text(raw_text)

        # NOTE: Do NOT call normalize_text here (it contains a bad regex).
        stats = preprocessor.get_text_statistics(cleaned)           # does safe normalization inside
        summary = preprocessor.create_summary(cleaned, 3)           # does safe normalization inside

        return jsonify({
            "success": True,
            "cleaned_text": cleaned,   # first 500 chars shown in UI per spec
            "statistics": stats,
            "summary": summary
        }), 200

    except Exception as e:
        app.logger.error("Error in /api/clean\n" + traceback.format_exc())
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """
    API endpoint that accepts raw text and returns statistics only

    Expected JSON input:
        {"text": "Your raw text here..."}

    Returns JSON:
        {
            "success": true/false,
            "statistics": {...},
            "error": "..." (if applicable)
        }
    """
    try:
        # Get JSON data from request
        data = request.get_json(silent=True)
        if not data or "text" not in data:
            return jsonify({"success": False, "error": "Missing JSON body or 'text' field."}), 400

        # Extract text from the JSON
        text = str(data["text"])
        if not text.strip():
            return jsonify({"success": False, "error": "Text must be a non-empty string."}), 400

        # Normalize so sentence/word detection is consistent
        normalized = preprocessor.normalize_text(text, preserve_sentences=True)

        # Compute statistics only
        stats = preprocessor.get_text_statistics(normalized)

        # Return JSON response
        return jsonify({
            "success": True,
            "statistics": stats
        }), 200

    except Exception as e:
        app.logger.error("Error in /api/analyze\n" + traceback.format_exc())
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Text Preprocessing Web Service...")
    print("📖 Available endpoints:")
    print("   GET  /           - Web interface")
    print("   GET  /health     - Health check")
    print("   POST /api/clean  - Clean text from URL")
    print("   POST /api/analyze - Analyze raw text")
    print()
    print("🌐 Open your browser to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    
    app.run(debug=True, port=5000, host='0.0.0.0')