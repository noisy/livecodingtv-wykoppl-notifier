# -*- coding: utf-8 -*-
import os
import wykop
import requests
################################################
# TODO:
# v bigger thumbnails (1024_576)
# - simple database (SQLite?)
# - custom tags per author, transmission, project to subscribe or ignore
# - proper authorization
# - stats

################################################
api = wykop.WykopAPI(
    appkey=os.environ['WYKOP_API_KEY'],
    secretkey=os.environ['WYKOP_SECRET_KEY'],
    login=os.environ['WYKOP_LOGIN'],
    password=os.environ['WYKOP_PASS']
)
################################################
cookies = {'sessionid': os.environ['LIVECODING_SESSION_ID']}
programming_languages = [
    'javascript', 'java', 'python', 'ruby', 'css', 'php',
    'c++', 'c', 'shell', 'csharp', 'objectivec', 'r',
    'viml', 'go', 'perl', 'coffeescript', 'tex',
    'scala', 'haskell', 'emacs', 'lisp'
]
################################################

# TODO: figure out how to authorize without cookie
json = requests.get('https://www.livecoding.tv/api/livestreams/onair/', cookies=cookies).json()

onair_streams = json['results']

pl_streams = [
    stream
    for stream in onair_streams
    if requests.get(stream['user'], cookies=cookies).json()['country'] == 'PL'
]

for stream in pl_streams:

    tags = stream['tags']
    tags = [tag.lower() for tag in tags.replace(',', '').split()]
    tags = [tag for tag in tags if tag in programming_languages]

    thumb_url = stream['thumbnail_url'].replace('_250_140/', '_1024_576/')
    final_thumb_url = requests.get(thumb_url).url  # resolve redirect

    response = api.add_entry("""
        Livestream: [{title}]({stream_url})
        Autor: {author}
        #livecodingtv {programming_tags}

        """.format(
            title=stream['title'],
            stream_url='https://www.livecoding.tv/{user}/'.format(user=stream['user__slug']),
            author=stream['user__slug'],
            programming_tags=' '.join(
                ['#[{tag}](http://www.wykop.pl/tag/{tag}/)'.format(tag=tag) for tag in tags]
            )
        ),
        embed=final_thumb_url
    )

    print str(response)


print "end"