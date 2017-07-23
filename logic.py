"""logic module

This module contains both logic for fetching data from
database and for mesuring similarity between books.
"""

# Author: Alexandru Burlacu
# Email:  alexandru-varacuta@bookvoyager.org


from utils import get_config, db_fetch

CONFIG = get_config()

def reshape_transform(objs):
    """
    Reshapes an iterable of 4-tuple to a dict of lists

    Parameters
    ----------
    obj : iterable of (int, str, str, int)

    Returns
    -------
    dict of str to list of (int, int)
    {str: [(int, int)]}

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


# def pipeline():
#     pass

# def similarity_metric(sim_func):
#     def _inner(base, variant):
#         return {"sim": sim_func(base, variant)}
#     return _inner
