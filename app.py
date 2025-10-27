from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import json
import instaloader

app = Flask(__name__, template_folder='.')  # القوالب في نفس المجلد

def get_followers_html(username):
    """محاولة جلب عدد المتابعين عبر تحليل الـ HTML"""
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

def get_followers_instaloader(username):
    """محاولة جلب المتابعين باستخدام instaloader"""
    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        return profile.followers
    except Exception:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username'].strip()

        # 1. محاولة عبر HTML
        followers = get_followers_html(username)
        if followers is not None:
            return render_template('result.html', username=username, followers=followers)

        # 2. محاولة عبر instaloader
        followers = get_followers_instaloader(username)
        if followers is not None:
            return render_template('result.html', username=username, followers=followers)

        # إذا فشلت كل الطرق
        error_message = "لم نتمكن من جلب البيانات، يرجى التحقق من إسم المستخدم أو جرب مرة أخرى."
        return render_template('index.html', error=error_message)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
