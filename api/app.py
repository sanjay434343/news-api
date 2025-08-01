#Coded by Sumanjay on 29th Feb 2020
from flask import Flask, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inshorts import getNews
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "i_am_not_feeling_sleepy_so_i_am_coding_this"
CORS(app)

@app.route('/')
def home():
    # Return JSON API info instead of UI
    return jsonify({
        "message": "Welcome to the Inshorts News API.",
        "usage": {
            "news_endpoint": "/news?category=<category>&offset=<offset>&limit=<limit>",
            "docs": "/docs"
        },
        "repository": "https://github.com/sanjay434343/news-api"
    })

@app.route('/news')
def news():
    if request.method == 'GET':
        category = request.args.get("category")
        if not category:
            return jsonify({
                "error": "please add category in query params"
            }), 404
        return jsonify(getNews(category)), 200

@app.route('/ui')
def news_ui():
    # Optimized batch loading and improved image loading UI
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Latest News</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 0; }
            .container { max-width: 500px; margin: 40px auto; background: #fff; padding: 24px; border-radius: 8px; box-shadow: 0 2px 8px #0001; }
            .news-card { margin-bottom: 16px; min-height: 400px; }
            .news-title { font-size: 1.3em; margin: 0 0 8px 0; }
            .news-meta { color: #888; font-size: 0.95em; margin-bottom: 8px; }
            .news-img { max-width: 100%; border-radius: 4px; margin-bottom: 12px; display: block; background: #eee; min-height: 180px; }
            .news-content { margin-bottom: 8px; }
            .nav-btn { background: #007bff; color: #fff; border: none, padding: 10px 18px; border-radius: 4px; cursor: pointer; font-size: 1em; margin: 0 8px; }
            .nav-btn:disabled { background: #ccc; cursor: not-allowed; }
            .reload-btn { background: #28a745; color: #fff; border: none; padding: 8px 14px; border-radius: 4px; cursor: pointer; font-size: 0.95em; margin-bottom: 16px; }
            .reload-btn:hover { background: #218838; }
            .center { text-align: center; }
            .img-spinner {
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 180px;
                background: #eee;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #007bff;
                border-radius: 50%;
                width: 32px;
                height: 32px;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg);}
                100% { transform: rotate(360deg);}
            }
            .img-placeholder {
                width: 100%;
                min-height: 180px;
                background: #ddd;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #aaa;
                font-size: 1.1em;
                border-radius: 4px;
                margin-bottom: 12px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 style="text-align:center;">Latest News</h1>
            <div class="center">
                <button class="reload-btn" onclick="loadNews(true)">Reload News</button>
            </div>
            <div id="news-card" class="news-card"></div>
            <div class="center">
                <button id="prev-btn" class="nav-btn" onclick="showPrev()" disabled>&larr; Previous</button>
                <button id="next-btn" class="nav-btn" onclick="showNext()" disabled>Next &rarr;</button>
            </div>
        </div>
        <script>
            let newsData = [];
            let currentIndex = 0;
            let batchSize = 10;
            let offset = 0;
            let loading = false;
            let allLoaded = false;
            let prefetching = false;
            let prefetchedData = null;

            function renderNews(index) {
                const card = document.getElementById('news-card');
                if (!newsData.length) {
                    card.innerHTML = '<p>No news found.</p>';
                    document.getElementById('prev-btn').disabled = true;
                    document.getElementById('next-btn').disabled = true;
                    return;
                }
                const news = newsData[index];
                let imgHtml = '';
                if (news.imageUrl && news.imageUrl.startsWith('http')) {
                    imgHtml = `
                        <div class="img-spinner" id="img-spinner">
                            <div class="spinner"></div>
                        </div>
                        <img class="news-img" src="${news.imageUrl}" alt="news image"
                            style="display:none;"
                            onload="this.style.display='block';document.getElementById('img-spinner').style.display='none';"
                            onerror="this.style.display='none';document.getElementById('img-spinner').outerHTML='<div class=\\'img-placeholder\\'>Image not available</div>';"
                        />
                    `;
                } else {
                    imgHtml = `<div class="img-placeholder">Image not available</div>`;
                }
                card.innerHTML = `
                    <div class="news-title">${news.title}</div>
                    <div class="news-meta">${news.date} &middot; ${news.time} &middot; By ${news.author}</div>
                    ${imgHtml}
                    <div class="news-content">${news.content}</div>
                    <a href="${news.readMoreUrl}" target="_blank">Read more</a>
                    <div style="margin-top:10px;color:#888;font-size:0.9em;">${index+1} of ${newsData.length}${allLoaded ? '' : ' (loading more...)'}</div>
                `;
                document.getElementById('prev-btn').disabled = (index === 0);
                document.getElementById('next-btn').disabled = (index === newsData.length - 1 && allLoaded);
            }

            function showPrev() {
                if (currentIndex > 0) {
                    currentIndex--;
                    renderNews(currentIndex);
                }
            }

            function showNext() {
                if (currentIndex < newsData.length - 1) {
                    currentIndex++;
                    renderNews(currentIndex);
                    checkAndPrefetch();
                } else if (!allLoaded) {
                    checkAndPrefetch(true);
                }
            }

            async function loadNews(reset=false) {
                if (loading) return;
                loading = true;
                if (reset) {
                    newsData = [];
                    currentIndex = 0;
                    offset = 0;
                    allLoaded = false;
                    prefetching = false;
                    prefetchedData = null;
                }
                const card = document.getElementById('news-card');
                card.innerHTML = '<p>Loading...</p>';
                document.getElementById('prev-btn').disabled = true;
                document.getElementById('next-btn').disabled = true;
                try {
                    const res = await fetch(`/news?category=all&offset=${offset}&limit=${batchSize}`);
                    const data = await res.json();
                    if (!data.success || !data.data.length) {
                        allLoaded = true;
                        if (!newsData.length) card.innerHTML = '<p>No news found.</p>';
                        return;
                    }
                    if (reset) {
                        newsData = data.data;
                        currentIndex = 0;
                    } else {
                        newsData = newsData.concat(data.data);
                    }
                    offset += batchSize;
                    if (data.data.length < batchSize) allLoaded = true;
                    renderNews(currentIndex);
                    // Prefetch next batch for faster experience
                    prefetchNextBatch();
                } catch (e) {
                    card.innerHTML = '<p>Error loading news.</p>';
                }
                loading = false;
            }

            async function prefetchNextBatch() {
                if (prefetching || allLoaded) return;
                prefetching = true;
                try {
                    const res = await fetch(`/news?category=all&offset=${offset}&limit=${batchSize}`);
                    const data = await res.json();
                    if (data.success && data.data.length) {
                        prefetchedData = data.data;
                    } else {
                        allLoaded = true;
                        prefetchedData = null;
                    }
                } catch (e) {
                    prefetchedData = null;
                }
                prefetching = false;
            }

            function checkAndPrefetch(loadIfReady=false) {
                // If user reaches 7th from last loaded, prefetch next batch
                if (!allLoaded && newsData.length - currentIndex <= 3 && !prefetching) {
                    if (prefetchedData) {
                        // Append prefetched data immediately
                        newsData = newsData.concat(prefetchedData);
                        offset += batchSize;
                        if (prefetchedData.length < batchSize) allLoaded = true;
                        prefetchedData = null;
                        if (loadIfReady && currentIndex < newsData.length - 1) {
                            currentIndex++;
                            renderNews(currentIndex);
                        }
                        // Prefetch next batch
                        prefetchNextBatch();
                    } else {
                        // If not prefetched, prefetch now
                        prefetchNextBatch();
                    }
                }
            }

            // Infinite/reel-like scrolling: show next news on scroll down, prev on scroll up
            window.addEventListener('wheel', function(e) {
                if (e.deltaY > 0) {
                    // Scroll down
                    if (currentIndex < newsData.length - 1) {
                        currentIndex++;
                        renderNews(currentIndex);
                        checkAndPrefetch();
                    } else if (!allLoaded) {
                        checkAndPrefetch(true);
                    }
                } else if (e.deltaY < 0) {
                    // Scroll up
                    if (currentIndex > 0) {
                        currentIndex--;
                        renderNews(currentIndex);
                    }
                }
            });

            // Optional: Keyboard navigation (left/right arrow)
            document.addEventListener('keydown', function(e) {
                if (e.key === 'ArrowLeft') showPrev();
                if (e.key === 'ArrowRight') showNext();
            });

            window.onload = function() { loadNews(true); };
        </script>
    </body>
    </html>
    '''

@app.route('/docs')
def docs():
    # Serve the UI as documentation at /docs
    return news_ui()

@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
