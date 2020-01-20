from datetime import datetime
from dotenv import load_dotenv
import os
import requests

load_dotenv()
token = os.getenv('ACCESS_TOKEN')
api_v = os.getenv('API_VERSION')


def get_posts(user_id, date):
    """
    Returns a list of user or community posts
    :param user_id: user or community id
    :param date: date starting from which data is taken into account
    :return: list of posts
    """
    date = datetime.strptime(date, '%Y-%m-%d')
    user_id = str(user_id)
    if user_id.isdigit():
        response = requests.get(f'https://api.vk.com/method/wall.get?owner_id='
                                f'{user_id}&access_token={token}&v={api_v}')
    else:
        response = requests.get(f'https://api.vk.com/method/wall.get?domain='
                                f'{user_id}&access_token={token}&v={api_v}')
    data = response.json()
    selected_posts = []
    for elem in range(len(data['response']['items'])):
        for key in data['response']['items'][elem]:
            if key == 'date':
                post_date = datetime.fromtimestamp(
                    data['response']['items'][elem]['date'])
                if post_date >= date:
                    selected_posts.append(data['response']['items'][elem])
                else:
                    break
    return selected_posts


def attach_parse(nesting):
    """
    Collects attachments to the post
    :param nesting: post (if attachments from user page)
    or post['copy_history'][0] (if attachments from reposted post)
    :return: list of attachments
    """
    attach = []
    for attachment in nesting['attachments']:
        if attachment['type'] == 'photo':
            attach.append(attachment['photo']['photo_604'])
        elif attachment['type'] == 'album':
            owner_id = attachment["album"]["thumb"]["owner_id"]
            album_id = attachment["album"]["thumb"]["album_id"]
            attach.append(f'https://vk.com/id{owner_id}?z=album{owner_id}_{album_id}')
        elif attachment['type'] == 'link':
            attach.append(attachment['link']['url'])
        elif attachment['type'] == 'audio':
            attach.extend([attachment['audio']['id'],
                           attachment['audio']['artist'],
                           attachment['audio']['title']])
        elif attachment['type'] == 'video':
            owner_id = attachment['video']['owner_id']
            id_= attachment['video']['id']
            attach.append(f'https://vk.com/video{owner_id}_{id_}')
    return attach


def parse_posts(posts):
    """
    Parses the resulting list of posts into components
    :param posts: list of posts
    :return: post ids, texts, attachments in the form of codes or links,
    quantity of attachments, likes, reposts and comments
    """
    ids = []
    text = []
    attachments = []
    num_attach = []
    likes = []
    reposts = []
    comments = []
    for post in posts:
        ids.append(post['id'])
        if post['text'] == '':
            if 'copy_history' in post:
                text.append(str(post['copy_history'][0]['text']
                                ).replace('\n', ''))
            else:
                text.append(None)
        else:
            text.append(str(post['text']).replace('\n', ''))
        if 'attachments' in post:
            num_attach.append(len(post['attachments']))
            attachments.append(attach_parse(post))
        elif 'copy_history' in post:
            if 'attachments' in post['copy_history'][0]:
                num_attach.append(len(post['copy_history'][0]['attachments']))
                attachments.append(attach_parse(post['copy_history'][0]))
        likes.append(post['likes']['count'])
        reposts.append(post['reposts']['count'])
        comments.append(post['comments']['count'])
    keys = ('ids', 'text', 'num of attachments', 'list of attachments',
            'num of likes', 'num of reposts', 'number of comments')
    values = (ids, text, num_attach, attachments, likes, reposts, comments)
    parsed_posts = {key: value for key, value in zip(keys, values)}
    return parsed_posts


def ids_parse(posts):
    """
    Parses the resulting list of posts on ids
    :param posts: list of posts
    :return: post ids
    """
    ids = []
    for post in posts:
        ids.append(post['id'])
    return ids


def text_parse(posts):
    """
    Parses the resulting list of posts on texts
    :param posts: list of posts
    :return: post texts
    """
    text = []
    for post in posts:
        if post['text'] == '':
            if 'copy_history' in post:
                text.append(str(post['copy_history'][0]['text']
                                ).replace('\n', ''))
            else:
                text.append(None)
        else:
            text.append(str(post['text']).replace('\n', ''))
    return text


def attachments_parse(posts):
    """
    Parses the resulting list of posts on attachments
    :param posts: list of posts
    :return: attachments in the form of codes or links
    """
    attachments = []
    for post in posts:
        if 'attachments' in post:
            attachments.append(attach_parse(post))
        elif 'copy_history' in post:
            if 'attachments' in post['copy_history'][0]:
                attachments.append(attach_parse(post['copy_history'][0]))
    return attachments


def num_attachments_parse(posts):
    """
    Parses the resulting list of posts on the number of attachments
    :param posts: list of posts
    :return: number of attachments
    """
    num_attach = []
    for post in posts:
        if 'attachments' in post:
            num_attach.append(len(post['attachments']))
        elif 'copy_history' in post:
            if 'attachments' in post['copy_history'][0]:
                num_attach.append(len(post['copy_history'][0]['attachments']))
    return num_attach


def likes_parse(posts):
    """
    Parses the resulting list of posts on likes
    :param posts: list of posts
    :return: number of likes
    """
    likes = []
    for post in posts:
        likes.append(post['likes']['count'])
    return likes


def reposts_parse(posts):
    """
    Parses the resulting list of posts on reposts
    :param posts: list of posts
    :return: number of reposts
    """
    reposts = []
    for post in posts:
        reposts.append(post['reposts']['count'])
    return reposts


def comments_parse(posts):
    """
    Parses the resulting list of posts on comments
    :param posts: list of posts
    :return: number of comments
    """
    comments = []
    for post in posts:
        comments.append(post['comments']['count'])
    return comments
