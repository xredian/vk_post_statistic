from collections import defaultdict
from datetime import datetime


def post_stat(ymdh: str, posts: list):
    """
    Statistics of the number of posts in certain periods
    :param ymdh: period
    :param posts: list of posts
    :return: dict with number of posts per period
    """
    data = defaultdict(int)
    count = []
    for post in posts:
        if ymdh == 'year':
            count.append(datetime.fromtimestamp(post["date"]).year)
        elif ymdh == 'month':
            count.append(datetime.fromtimestamp(post['date']).month)
        elif ymdh == 'day':
            count.append(datetime.fromtimestamp(post['date']).day)
        elif ymdh == 'hour':
            count.append(datetime.fromtimestamp(post['date']).hour)
    for elem in count:
        data[elem] += 1
    return dict(data)


def stat(ymdh: str, tag: str, posts: list):
    """
    Statistics of the average number of likes, comments or reposts
    in certain periods
    :param ymdh: period
    :param tag: on of the following - likes, comments, reposts
    :param posts: list of posts
    :return: dict with average numbers per period
    """
    data = post_stat(ymdh, posts)
    tags = defaultdict(int)
    for post in posts:
        score = post[tag]['count']
        if ymdh == 'year':
            tags[datetime.fromtimestamp(post['date']).year] += score
        elif ymdh == 'month':
            tags[datetime.fromtimestamp(post['date']).month] += score
        elif ymdh == 'day':
            tags[datetime.fromtimestamp(post['date']).day] += score
        elif ymdh == 'hour':
            tags[datetime.fromtimestamp(post['date']).hour] += score
    try:
        average = {k: round(tags[k] / data.get(k, 0), 2) for k in tags.keys()}
    except ZeroDivisionError:
        average = 'There are no posts for the specified period'
    return average
