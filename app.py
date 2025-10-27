from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_followers(username):
    url = f'https://www.instagram.com/{username}/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script', type='text/javascript')
        for script in scripts:
            if script.string and 'window._sharedData' in script.string:
                json_text = script.string.split(' = ', 1)[1].rstrip(';')
                import json
                data = json.loads(json_text)
                try:
                    followers = data['entry_data']['ProfilePage'][0]['graphql']['user']['followers']['count']
                    return followers
                except Exception:
                    return None
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        followers = get_followers(username)
        return render_template('result.html', username=username, followers=followers)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
