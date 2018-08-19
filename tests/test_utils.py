import unittest
import src.utils as M

class TestUtilsModule(unittest.TestCase):

    def test_compose(self):
        f = lambda x: x + 2
        g = lambda x: x * 2
        self.assertEqual(M.compose(f, g)(2), 6)
        self.assertEqual(M.compose(g, f)(2), 8)
        self.assertEqual(M.compose(g, g)(2), 8)
        self.assertEqual(M.compose(f, f)(2), 6)

    def test_make_query_invalid_input(self):
        query_1 = {} # emply query
        query_2 = {"invalid_key": "invalid_value"} # wrong key
        query_3 = {"characters": "no_characters"} # wrong value
        self.assertRaises(KeyError, lambda: M.make_query(query_1))
        self.assertRaises(KeyError, lambda: M.make_query(query_2))
        self.assertRaises(AttributeError, lambda: M.make_query(query_3))

    def test_make_query_valid_input(self):
        query = {'spaceSetting': {'beyondsolarsystem': 0, 'insideearth': 0,
                                  'otherplanets': 0, 'outerspace': 0},
                 'metadata': {'author': {'value': 'Robert A. Heinlein'}},
                 'timeSetting': 'ALTERNATIVE_TIMELINE',
                 'characters': {'dragons': 0, 'robots': 0, 'humanoiddroids': 0,
                                'aliens': 1, 'mutants': 0, 'superintelligence': 0}}
        resp = {"$or": [
            {"metadata.author": {"$regex": r"(Robert A. Heinlein)\w*",
                                 "$options": "i"}},
            {
                "genre.characters.labels.aliens": 1,
                "genre.characters.labels.mutants": {"$in": [0, 1]},
                "genre.characters.labels.robots": {"$in": [0, 1]},
                "genre.characters.labels.humanoiddroids": {"$in": [0, 1]},
                "genre.characters.labels.dragons": {"$in": [0, 1]},
                "genre.characters.labels.superintelligence": {"$in": [0, 1]}
            },
            {
                "genre.spaceSetting.labels.insideearth": {"$in": [0, 1]},
                "genre.spaceSetting.labels.otherplanets": {"$in": [0, 1]},
                "genre.spaceSetting.labels.outerspace": {"$in": [0, 1]},
                "genre.spaceSetting.labels.beyondsolarsystem": {"$in": [0, 1]}
            }
            ]}
        self.assertEqual(M.make_query(query), resp)


    def test_preprocess_resp(self):
        obj = """{"resp": [{"sentiment":
                         {"timeline": [[1, "joy", "hope", 1936],
                                       [1, "joy", "hope", 3597]]}}]}"""
        self.assertEqual(M.preprocess_resp(obj), '[{"sentiment": {"timeline": \
                                                    [[1, "joy", "hope", 1936], \
                                                    [1, "joy", "hope", 3597]]}}]'.replace("  ", ""))
