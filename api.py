"""API module

Here are implemented all the resources of the `Recommendation` service.
"""

# Author: Alexandru Burlacu
# Email:  alexandru-varacuta@bookvoyager.org


import json
import logging
import falcon

import utils
# from logic import <smth/>

def parse(stream):
    """Parses bytestring to dict"""
    kv_list = stream.decode("utf-8").replace("=", ":").split("&")
    data = [xy.split(":") for xy in kv_list]

    return {x: y for x, y in data}


class DummyStorage:
    """DummyStorage"""
    def __init__(self, addr):
        self._db_proxy = "It's a server, running at {}".format(addr)

    def fetch_with_contraints(self, contraints):
        """fetch_with_contraints"""
        pass

class DummyStorageException(Exception):
    """DummyStorageException"""

    @staticmethod
    def handle(ex, req, resp, params):
        """Error handler"""
        raise falcon.HTTPError(falcon.HTTP_404, "Some generic shit happen")

#########################################################################################

class RecommenderResource:
    def __init__(self):
        self._logger = logging.getLogger("test.logger")
        # self._db = DummyStorage("localhost:27017")

    def on_get(self, req, resp):
        """GET method handler"""
        book_name = req.get_param("book_name")
        filters = parse(req.stream.read())


        resp.content_type = "application/json"
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(utils.db_fetch({"book_name": book_name,
                                               "filters": filters}))



api = falcon.API()
api.add_route("/", RecommenderResource())
api.add_error_handler(DummyStorageException, DummyStorageException.handle)
