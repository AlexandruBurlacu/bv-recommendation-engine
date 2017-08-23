"""Domain Logic module

This module contains both logic for fetching data from
database and for mesuring similarity between books.
"""

# Author: Alexandru Burlacu
# Email:  alexandru-varacuta@bookvoyager.org

from math import sqrt
from .utils import compose


def reshape_transform(objs):
    """Reshapes an iterable of 4-tuple to a dict of lists

    Parameters
    ----------
    obj : iterable of (int, str, str, int)

    Returns
    -------
    sentiment_timeline : dict of str to list of (int, int)
        A dictionary of indexed magnitudes of 6 different basic emotions.
    """

    get = lambda key, x: x[
        {
            "sentiment_score": 0,
            "sentiment_cat": 1,
            "index": 3
        }[key]
    ]

    sentiment_timeline = {
        "sadness": [],
        "fear": [],
        "joy": [],
        "surprise": [],
        "anger": [],
        "love": []
    }

    for obj in objs:
        data = (get("sentiment_score", obj), get("index", obj))
        sentiment_timeline[get("sentiment_cat", obj)].append(data)

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
    """
    max_lens = []
    for timeline in timelines:
        for val in timeline.values():
            max_lens += max(val) if val else [-1]

    return max(max_lens)

def fill(sentiment_range, length, memo={}):
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
    """
    if not length in memo:
        memo[length] = [0 for _ in range(length)]

    new_range = memo[length]
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

def _validate_input_vector(func):
    def __inner(vector, *args, **kwargs):
        vector_len = len(vector)
        if vector_len < 100: # 'vector' should be at least 100 elements long
            valid_vector = [*vector, *[0 for _ in range(100 - vector_len)]]
            result = func(valid_vector, *args, **kwargs)
        else:
            result = func(vector, *args, **kwargs)

        return result
    return __inner

@_validate_input_vector
def chunk_sum(vector):
    """It is safe given that the len(vector) >= 100.

    Parameters
    ----------
    vector : iterable of Numbers

    Returns
    -------
    list of Numbers
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
    {base_name : [{"score" : score, "title": candidate_obj}]}
        base_name, candidate_obj is str and score is float
    """
    get_title = lambda o: o["metadata"]["title"]
    def __inner(base, matches, *args, **kwargs):
        base_name = get_title(base)

        scores = func(base, matches, *args, **kwargs)

        return {
            base_name: [{"score": score,
                         "title": title} for score, title in
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
