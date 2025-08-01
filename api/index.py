from flask import Flask, request, jsonify
from flask_cors import CORS
from inshorts import getNews
from main import app as main_app
from vercel_python_wsgi import make_lambda_handler

app = Flask(__name__)
app.secret_key = "i_am_not_feeling_sleepy_so_i_am_coding_this"
CORS(app)

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Inshorts News API.",
        "usage": {
            "news_endpoint": "/news?category=<category>&offset=<offset>&limit=<limit>",
            "docs": "/docs"
        },
        "repository": "https://github.com/sanjay434343/news-api"
    })

@app.route('/api/news')
def news():
    if request.method == 'GET':
        category = request.args.get("category")
        if not category:
            return jsonify({
                "error": "please add category in query params"
            }), 404
        return jsonify(getNews(category)), 200

# Add API prefix to routes for Vercel
@app.route('/api/healthz')
def healthz():
    return jsonify({"status": "ok"})

handler = make_lambda_handler(app)
