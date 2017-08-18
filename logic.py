"""logic module

This module contains both logic for fetching data from
database and for mesuring similarity between books.
"""

# Author: Alexandru Burlacu
# Email:  alexandru-varacuta@bookvoyager.org

from math import sqrt
import json
from utils import compose

def _reshape_timeline(checkpoints):
    return map(lambda x: x, checkpoints)

def preprocess_resp(raw_resp):
    """Transforma the sentiment timeline dict of the response body.

    It's ugly as hell, sorry.

    Parameters
    ----------
    raw_resp : dict of {"resp": [dict]}
        The response dictionary fetched, and optionaly preprocessed, from database.

    Returns
    -------
    resp : list
        List with dictionaries with modified structure of the value under
        the `timeline` key of the `sentiment` dictionary
    dict
        {"Content-Type": "application/json"}

    Example
    -------
    >>> obj =  \"""{"resp":
    ...    [{"sentiment":
    ...       {"timeline":
    ...            [
    ...                [1, "joy", "hope", 1936],
    ...                [1, "joy", "hope", 3597]
    ...           ]}
    ...    }]}\"""
    >>> preprocess_resp(obj)[0]
    '[{"sentiment": {"timeline": [[1, "joy", "hope", 1936], [1, "joy", "hope", 3597]]}}]'
    >>> preprocess_resp(obj)[1]
    {'Content-Type': 'application/json'}
    """
    resp = json.loads(raw_resp)["resp"]
    condition = len(resp)
    if condition == 1:
        timeline = _reshape_timeline(resp[0]["sentiment"]["timeline"])
        resp[0]["sentiment"].update({"timeline": list(timeline)}) # [WARNING] change in-place
    elif condition > 1:
        timelines = [_reshape_timeline(r["sentiment"]["timeline"]) for r in resp]
        [r["sentiment"].update({"timeline": list(timeline)}) # [WARNING] change in-place
         for r, timeline in zip(resp, timelines)]
    return json.dumps(resp), {"Content-Type": "application/json"}

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
    """Applies `fill` to all values of a given object"""
    for key in obj.keys():
        obj[key] = chunk_sum(fill(obj[key], length))

    return obj

def cosine_similarity(x_vector, y_vector):
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
    numerator = sum(a * b for a, b in zip(x_vector, y_vector))
    denominator = square_rooted(x_vector) * square_rooted(y_vector)

    return numerator / (denominator or 1e-5)

def chunk_sum(vector):
    """It is safe given that the len(vector) >= 100.

    Parameters
    ----------
    vector : iterable of Numbers

    Returns
    -------
    list of Numbers

    Example
    -------
    >>> x = range(1000)
    >>> chunk_sum(x) == [x * 100 + 45 for x in range(100)]
    True
    >>> chunk_sum(range(100)) == list(range(100))
    True
    """

    def _chunks(vector):
        size, counter = len(vector), 0
        chunk_size = int(size / 100)
        while counter < size:
            yield vector[counter : counter + chunk_size]
            counter += chunk_size

    return [sum(piece) for piece in _chunks(vector)]

def similarity(base, vector):
    """Returns the cosine similarity over all fields of 2 dict objects"""
    ret_obj = {}
    for key in base.keys():
        ret_obj[key] = cosine_similarity(base[key], vector[key])

    return ret_obj

def compute_score(similar_books):
    """Yields the sum of matched books' cosine similarity
    values over 6 basic sentiments"""
    for book in similar_books:
        yield sum(book.values())

def reshape_output(func):
    """Reshapes the output of the function `func`.

    Parameters
    ----------
    func : binary function
    base : dict
    matches : list of dict

    Returns
    -------
    {base_name : [{candidate_name : score}]}
        base_name, candidate_name is str and score is float
    """
    get_title = lambda o: o["metadata"]["title"]
    def __inner(base, matches, *args, **kwargs):
        base_name = get_title(base)

        scores = func(base, matches, *args, **kwargs)

        return {
            base_name : [{title: score} for score, title in
                         zip(scores, map(get_title, matches))]
        }

    return __inner

@reshape_output
def get_candidates(raw_base, raw_fetched_objs):
    """

    Parameters
    ----------
    raw_base : dict
        Base book
    raw_fetched_objs : [dict]
        Matching books

    Returns
    -------
    [float]
        The similarity scores of books compared to the base book.
    """
    get_timeline = compose(reshape_transform, lambda o: o["sentiment"]["timeline"])

    base_sentiment = get_timeline(raw_base)
    fetched_objs_sentiment = list(map(get_timeline, raw_fetched_objs))

    max_len = get_max_len([base_sentiment, *fetched_objs_sentiment]) + 1
    base = fill_obj(base_sentiment, max_len)
    fetched_objs = (fill_obj(o, max_len) for o in fetched_objs_sentiment)

    return compute_score(similarity(base, obj) for obj in fetched_objs)

