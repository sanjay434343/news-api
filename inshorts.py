# Coded by Sumanjay on 29th Feb 2020
import datetime
import uuid
import requests
import pytz


headers = {
    'authority': 'inshorts.com',
    'accept': '*/*',
    'accept-language': 'en-GB,en;q=0.5',
    'content-type': 'application/json',
    'referer': 'https://inshorts.com/en/read',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
}

params = (
    ('category', 'top_stories'),
    ('max_limit', '10'),
    ('include_card_data', 'true')
)


def getNews(category):
    import flask
    # Support offset and limit for batching
    offset = int(flask.request.args.get('offset', 0))
    limit = int(flask.request.args.get('limit', 10))
    current_year = datetime.datetime.now().year
    all_news = []
    fetched = 0
    api_offset = offset
    api_limit = limit

    # Map 'all' to 'all_news' for the API
    api_category = category
    if category == "all":
        api_category = "all_news"

    while len(all_news) < limit:
        url = f'https://inshorts.com/api/en/news?category={api_category}&max_limit={api_limit}&include_card_data=true&offset={api_offset}'
        response = requests.get(url)
        try:
            news_data = response.json()['data']['news_list']
        except Exception as e:
            print(response.text)
            break

        if not news_data:
            break

        for entry in news_data:
            try:
                news = entry['news_obj']
                timestamp = news['created_at'] / 1000
                dt_utc = datetime.datetime.utcfromtimestamp(timestamp)
                if dt_utc.year != current_year:
                    break
                # Map to raw structure as requested
                newsObject = {
                    'id': uuid.uuid4().hex,
                    'title': news.get('title', ''),
                    'imageUrl': news.get('image_url', ''),
                    'url': news.get('shortened_url', ''),
                    'content': news.get('content', ''),
                    'author': news.get('author_name', ''),
                    'date': dt_utc.strftime('%A, %d %B, %Y'),
                    'time': datetime.datetime.fromtimestamp(timestamp, pytz.timezone('Asia/Kolkata')).strftime('%I:%M %p').lower(),
                    'readMoreUrl': news.get('source_url', '')
                }
                all_news.append(newsObject)
                if len(all_news) >= limit:
                    break
            except Exception:
                print(entry)

        if len(news_data) < api_limit:
            break
        api_offset += api_limit

    newsDictionary = {
        'success': True if all_news else False,
        'category': category,
        'data': all_news
    }

    if not all_news:
        newsDictionary['error'] = 'No news found for this year'
    return newsDictionary
