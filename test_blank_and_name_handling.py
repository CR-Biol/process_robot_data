import unittest

import blank_and_name_handling as module


class TestBlankAndNameHandling(unittest.TestCase):
    def test_process_well_input(self):
        self.assertEqual(
            module.process_well_input("H1, H2, H3"),
            ["H1", "H2", "H3"]
        )
        self.assertEqual(
            module.process_well_input("A1, B2, C3, D4, E5, F6, G7, H8"),
            ["A1", "B2", "C3", "D4", "E5", "F6", "G7", "H8"]
        )
        self.assertEqual(
            module.process_well_input("H1:H4"),
            ["H1", "H2", "H3", "H4"]
        )
        self.assertEqual(
            module.process_well_input("12"),
            ["A12", "B12", "C12", "D12", "E12", "F12", "G12", "H12"]
        )
        with self.assertRaises(ValueError):
            module.process_well_input("X19")
            module.process_well_input("A1:A13")
            module.process_well_input("22")
            module.process_well_input("")
        

    def test_get_wrappers(self):
        pass


    def test_write_blank_corrected(self):
        pass

    def test_baptize(self):
        pass

    def test_merge(self):
        pass

    def test_match_iterable(self):
        pass

    def test_sort_df(self):
        pass


if __name__ == "__main__":
    unittest.main()
