from flask import Flask, request, jsonify
from flask_cors import CORS
from inshorts import getNews

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Welcome to the Inshorts News API.",
        "usage": {
            "news_endpoint": "/api/news?category=<category>&offset=<offset>&limit=<limit>"
        }
    })

@app.route('/api/news', methods=['GET'])
def news():
    category = request.args.get("category")
    if not category:
        return jsonify({"error": "please add category in query params"}), 404
    return jsonify(getNews(category)), 200

@app.route('/api/healthz', methods=['GET'])
def healthz():
    return jsonify({"status": "ok"})
