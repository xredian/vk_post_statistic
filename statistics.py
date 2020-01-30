from collections import Counter
from datetime import datetime


def post_statistics(ymdh: str, posts: list):
    """
    Statistics of the number of posts in certain periods
    :param ymdh: period
    :param posts: list of posts
    :return: dict with number of posts per period
    """
    count = [getattr(datetime.fromtimestamp(post['date']), ymdh)
             for post in posts]
    return dict(Counter(count))


def average_statistics(ymdh: str, tag: str, posts: list):
    """
    Statistics of the average number of likes, comments or reposts
    in certain periods
    :param ymdh: period
    :param tag: on of the following - likes, comments, reposts
    :param posts: list of posts
    :return: dict with average numbers per period
    """
    data = post_statistics(ymdh, posts)
    tags = Counter()
    for post in posts:
        tags[getattr(datetime.fromtimestamp(post['date']), ymdh)] += post[tag][
            'count']
    try:
        average = {k: round(tags[k] / data.get(k, 0), 2) for k in tags.keys()}
    except ZeroDivisionError:
        average = 'There are no posts for the specified period'
    return average
