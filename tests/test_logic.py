import unittest
import src.logic as M

class TestLogicModule(unittest.TestCase):

    def test_reshape_transform_valid_data(self):
        data = [(-1, 'fear', "tok", 0), (-1, 'sadness', "tok", 1),
                (1, 'surprise', "tok", 2), (-1, 'fear', "tok", 3),
                (1, 'surprise', "tok", 4)]
        self.assertEqual(M.reshape_transform(data), {'anger': [], 'fear': [(-1, 0), (-1, 3)],
                                                     'joy': [], 'love': [], 'sadness': [(-1, 1)],
                                                     'surprise': [(1, 2), (1, 4)]})

    def test_get_max_len_valid_data(self):
        tmls = [{"k1": [(1, 1), (1, 3), (1, 5)], "k2": [(3, 4), (4, 20)]}, {"k1": [(3, 15)]}]
        self.assertEqual(M.get_max_len(tmls), 20)

    def test_get_max_len_data_contains_empty_lists(self):
        tmls = [{"k1": [(1, 1), (1, 3), (1, 5)], "k2": [(3, 4), (4, 20)]}, {"k1": []}]
        self.assertEqual(M.get_max_len(tmls), 20)

    def test_fill_valid_data(self):
        my_range = [(1, 0), (-1, 3), (1, 5), (-1, 6)]
        self.assertEqual(M.fill(my_range, 8), [1, 0, 0, -1, 0, 1, -1, 0])

    def test_fill_empty_data(self):
        my_range = []
        self.assertEqual(M.fill(my_range, 8), [0, 0, 0, 0, 0, 0, 0, 0])

    def test_chunk_sum_valid_data(self):
        x = range(1000)
        self.assertEqual(M.chunk_sum(x), [x * 100 + 45 for x in range(100)])

    def test_chunk_sum_100_data(self):
        self.assertEqual(M.chunk_sum(range(100)), list(range(100)))

    def test_chunk_sum_invalid_data(self):
        self.assertEqual(M.chunk_sum(range(10)), [*range(10), *[0 for _ in range(90)]])
