"""logic module

This module contains both logic for fetching data from
database and for mesuring similarity between books.
"""

# Author: Alexandru Burlacu
# Email:  alexandru-varacuta@bookvoyager.org

from math import sqrt
import json

from utils import get_config, db_fetch, compose



def reshape_transform(objs):
    """Reshapes an iterable of 4-tuple to a dict of lists

    Parameters
    ----------
    obj : iterable of (int, str, str, int)

    Returns
    -------
    sentiment_timeline : dict of str to list of (int, int)
        A dictionary of indexed magnitudes of 6 different basic emotions.

    Example
    -------
    >>> data = [(-1, 'fear', "tok", 0),
    ...         (-1, 'sadness', "tok", 1),
    ...         (1, 'surprise', "tok", 2),
    ...         (-1, 'fear', "tok", 3),
    ...         (1, 'surprise', "tok", 4)]
    >>> reshape_transform(data) == {'anger': [],
    ...                             'fear': [(-1, 0), (-1, 3)],
    ...                             'joy': [],
    ...                             'love': [],
    ...                             'sadness': [(-1, 1)],
    ...                             'surprise': [(1, 2), (1, 4)]}
    True

    """
    get_sentiment_cat = lambda x: x[1]
    get_sentiment_score = lambda x: x[0]
    get_index = lambda x: x[3]

    sentiment_timeline = {
        "sadness": [],
        "fear": [],
        "joy": [],
        "surprise": [],
        "anger": [],
        "love": []
    }

    for obj in objs:
        data = (get_sentiment_score(obj), get_index(obj))
        sentiment_timeline[get_sentiment_cat(obj)].append(data)

    return sentiment_timeline


def cosine_similarity(x, y):
    """Computes cosine similarity between 2 vectors.

    Parameters
    ----------
    x : iterable of numeric values
    y : iterable of numeric values

    Returns
    -------
    float
        The value of the cosine between 2 vectors.
    """
    square_rooted = lambda x: sqrt(sum(a * a for a in x))
    numerator = sum(a * b for a, b in zip(x, y))
    denominator = square_rooted(x) * square_rooted(y)

    return numerator / (denominator or 1e-5)

def get_max_len(timelines):
    """Find the bigest index of sentiment timelines.

    Parameters
    ----------
    timelines : list of dict of str to list of (int, int)

    Returns
    -------
    int
        The bigest index value.

    Example
    -------
    >>> tmls = [{"k1": [(1, 1), (1, 3), (1, 5)], "k2": [(3, 4), (4, 20)]}, {"k1": [(3, 15)]}]
    >>> get_max_len(tmls)
    20
    """
    max_len = -1
    for timeline in timelines:
        for key in timeline.keys():
            try:
                local_max = max(timeline[key], key=lambda x: x[1])[1]
                if local_max > max_len:
                    max_len = local_max
            except ValueError:
                continue

    return max_len

def fill(sentiment_range, length):
    """Fills unindexed entries with 0s

    Parameters
    ----------
    sentiment_range : list of (int, int)
        A list of 2-tuples, first value is the magnitude of the sentiment,
        second is the index of it.

    length : int
        Length of the resulting list.

    Returns
    -------
    new_range : list of int
        List of magnitudes of sentiments in chronological order.

    Example
    -------
    >>> my_range = [(1, 0), (-1, 3), (1, 5), (-1, 6)]
    >>> fill(my_range, 8)
    [1, 0, 0, -1, 0, 1, -1, 0]
    """
    new_range = [0 for _ in range(length)]
    for val, i in sentiment_range:
        new_range[i] = val

    return new_range

def fill_obj(obj, length):
    for key in obj.keys():
        obj[key] = fill(obj[key], length)

    return obj

def similarity(base, vector):
    ret_obj = {}
    for key in base.keys():
        ret_obj[key] = cosine_similarity(base[key], vector[key])

    return ret_obj

def compute_score(similar_books):
    for book in similar_books:
        yield sum(book.values())

def get_top_candidates(raw_base, raw_fetched_objs, top_n=5):
    get_timeline = compose(reshape_transform, lambda o: o["sentiment"]["timeline"])

    print(raw_base)

    base_sentiment = get_timeline(raw_base)
    fetched_objs_sentiment = list(map(get_timeline, raw_fetched_objs))

    max_len = get_max_len([base_sentiment, *fetched_objs_sentiment]) + 1

    base = fill_obj(base_sentiment, max_len)
    fetched_objs = [fill_obj(o, max_len) for o in fetched_objs_sentiment]

    scores = list(similarity(base, obj) for obj in fetched_objs)

    return sorted(compute_score(scores), reverse=True)[:top_n]

def _main():
    config = get_config()
    data = json.loads(db_fetch(config["mongo_rest_interface_addr"], {}))["resp"]
    base, candidates = data[0], data[1:]

    top_15 = get_top_candidates(base, candidates, top_n=15)

    # print(top_15)

if __name__ == '__main__':
    _main()
