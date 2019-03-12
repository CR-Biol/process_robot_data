import unittest
import datetime

import get_raw_data_asc


class TestRawDataAsc(unittest.TestCase):
    def test_get_time(self):
        # Test usual cases.
        self.assertEqual(get_raw_data_asc.time_from_asc("Date: 2018-12-04, Time: 16:50:46\n"),
                          datetime.datetime(2018, 12, 4, 16, 50, 46)
                          )
        self.assertEqual(get_raw_data_asc.time_from_asc("Date: 3123-04-22, Time: 16:50:46\n"),
                          datetime.datetime(3123, 4, 22, 16, 50, 46)
                          )
        self.assertEqual(get_raw_data_asc.time_from_asc("Date: 918-12-04, Time: 16:50:46\n"),
                          datetime.datetime(918, 12, 4, 16, 50, 46)
                          )

        # Test without line break.
        self.assertEqual(get_raw_data_asc.time_from_asc("Date: 2018-12-04, Time: 16:50:46"),
                          datetime.datetime(2018, 12, 4, 16, 50, 46)
                          )

        # Test input that does not satisfy TECAN reader time stemp format.
        self.assertRaises(ValueError, get_raw_data_asc.time_from_asc, "any string")
      



if __name__ == "__main__":
    unittest.main()
  