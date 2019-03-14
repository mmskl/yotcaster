from flask import request, render_template, Flask, redirect, url_for, send_file
from re import match
import feedparser
import youtube_dl
from os import path

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/channel', methods=['POST'])
def channel():
    url = request.form['url']
    
    matches = match('.*\/(.+)$', url)
    if matches is not None:
        channel_id = matches.groups()[0]

    return redirect(url_for('feed', channel_id=channel_id))

@app.route('/video', methods=['POST'])
def video():
    url = request.form['url']
    
    matches = match('.*v=(.*)', url)
    if matches is not None:
        video_id = matches.groups()[0]

    return redirect(url_for('download', video_id=video_id))



@app.route('/feed/<channel_id>', methods=['GET'])
def feed(channel_id):

    channel_rss = 'https://www.youtube.com/feeds/videos.xml?channel_id={}'.format(channel_id)

    # https://www.youtube.com/channel/UCoXxgqIOTa8qCM7Hd7RiURw
    feed = feedparser.parse(channel_rss)
    data = feed['feed']

    channel = {
            'title': data['title'],
            'link': data['link'],
            'author': data['author'],
            }

    
    
    items = []
    for item in feed['items']:

        download_url = '{}download/{}'.format(request.url_root, item['yt_videoid'])

        items.append({
            'title': item['title'],
            'audio_url': download_url,
            'author': item['author'],
            'link': item['link'],
            'pub_date': item['published'],
            'summary': item['summary']
            })

    channel['items'] = items
    return render_template('rss.xml', channel=channel)


@app.route('/download/<video_id>', methods=['GET'])
def download(video_id):

    file_path = 'data/{}.m4a'.format(video_id)

    if not path.exists('data/' + file_path):

        ydl_opts = {
            'outtmpl': file_path,
            'format': 'm4a/worstaudio/worst',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                'preferredquality': '128',
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(['https://www.youtube.com/watch?v={}'.format(video_id)])


    return send_file(open(file_path, 'rb'), mimetype='application/octet-stream')

if __name__ == '__main__':
      app.run(host='localhost', port=5000, debug=True)
