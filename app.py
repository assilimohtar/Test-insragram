from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__, template_folder='.')  # نخبر Flask أن القوالب في نفس المجلد

def get_followers(username):
    url = f'https://www.instagram.com/{username}/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script', type='text/javascript')
        for script in scripts:
            if script.string and 'window._sharedData' in script.string:
                json_text = script.string.split(' = ', 1)[1].rstrip(';')
                data = json.loads(json_text)
                followers = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']
                return followers
    except Exception:
        return None
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username'].strip()
        followers = get_followers(username)
        return render_template('result.html', username=username, followers=followers)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
