from datetime import datetime
from dotenv import load_dotenv
import os
import requests
import time

load_dotenv()
token = os.getenv('ACCESS_TOKEN')
api_v = os.getenv('API_VERSION')


def get_data(user_id, offset=0):
    """
    Returns a list of user or community posts
    :param user_id: user or community id
    :param offset: offset, required to select more then 100 posts
    :param count: number of posts
    :return: list of posts
    """
    user_id = str(user_id)
    if user_id.isdigit():
        response = requests.get(f'https://api.vk.com/method/wall.get?owner_id='
                                f'{user_id}&offset={offset}&'
                                f'access_token={token}&v={api_v}')
    else:
        response = requests.get(f'https://api.vk.com/method/wall.get?domain='
                                f'{user_id}&offset={offset}&'
                                f'access_token={token}&v={api_v}')

    data = response.json()
    return data


def get_wall(user_id, date, selected_posts=None, offset=0):
    if selected_posts is None:
        selected_posts = []
    date_f = datetime.strptime(date, '%Y-%m-%d')
    data = get_data(user_id, offset)
    for elem in data['response']['items']:
        for key in elem:
            if key == 'date':
                post_date = datetime.fromtimestamp(elem['date'])
                if post_date >= date_f:
                    selected_posts.append(elem)
                else:
                    break
    if offset > len(selected_posts):
        return selected_posts
    offset += 100
    time.sleep(0.3)
    return get_wall(user_id, date, selected_posts, offset)


def ids_parse(posts: list):
    """
    Parses the resulting list of posts on ids
    :param posts: list of posts
    :return: post ids
    """
    ids = []
    for post in posts:
        ids.append(post['id'])
    return ids


def text_parse(posts: list):
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
            attach.append(f'https://vk.com/id{owner_id}?z=album'
                          f'{owner_id}_{album_id}')
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


def attachments_parse(posts: list):
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


def num_attachments_parse(posts: list):
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


def parse(posts: list, item: str):
    """
    Parses the resulting list of posts on likes, reposts or comments
    :param posts: list of posts
    :param item: likes, reposts or commens
    :return: number of likes
    """
    items = [post[item]['count'] for post in posts]
    return items
