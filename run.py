# -*- coding: utf-8 -*-
import os
import wykop
import requests
from database import User, Stream

################################################
# TODO:
# v bigger thumbnails (1024_576)
# v simple database (SQLite?)
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


def is_user_from_country(stream_data, code):
    user = User.get_user(stream_data['user__slug'].lower())
    if not user:
        user_data = requests.get(stream_data['user'], cookies=cookies).json()
        user = User(username=user_data['username'].lower(), country_code=user_data['country'])

    return user.country_code == code


def should_notify(stream_data):
    user = User.get_user(stream_data['user__slug'])
    stream = Stream.selectBy(user=user, title=stream_data['title']).getOne(default=None)

    if stream:
        if stream.ended:
            stream.ended = False
            return True
        else:
            print '{}\'s stream "{}" still in progress...'.format(stream_data['user__slug'], stream.title)
            return False
    else:
        Stream(user=user, title=stream_data['title'], url=stream_data['url'])
        return True


def mark_inactive_streams_as_ended():
    for stream in list(Stream.selectBy(ended=False)):
        response = requests.get(stream.url, cookies=cookies).json()

        if not response['is_live'] or stream.title != response['title']:
            stream.ended = True


def main():

    mark_inactive_streams_as_ended()

    # TODO: figure out how to authorize without cookie
    json = requests.get('https://www.livecoding.tv/api/livestreams/onair/', cookies=cookies).json()
    onair_streams = json['results']

    pl_streams = [
        stream_data
        for stream_data in onair_streams
        if is_user_from_country(stream_data, 'PL')
    ]

    for stream_data in pl_streams:

        if not should_notify(stream_data):
            continue

        tags = stream_data['tags']
        tags = [tag.lower() for tag in tags.replace(',', '').split()]
        tags = [tag for tag in tags if tag in programming_languages]

        thumb_url = stream_data['thumbnail_url'].replace('_250_140/', '_1024_576/')
        final_thumb_url = requests.get(thumb_url).url  # resolve redirect

        response = api.add_entry("""
            Livestream: [{title}]({stream_url})
            Autor: {author}
            #livecodingtv {programming_tags}

            """.format(
                title=stream_data['title'],
                stream_url='https://www.livecoding.tv/{user}/'.format(user=stream_data['user__slug']),
                author=stream_data['user__slug'],
                programming_tags=' '.join(
                    ['#[{tag}](http://www.wykop.pl/tag/{tag}/)'.format(tag=tag) for tag in tags]
                )
            ),
            embed=final_thumb_url
        )

        print str(response)

    print "End"


if __name__ == '__main__':
    main()
