import unittest
import datetime

import get_raw_data_asc


class TestRawDataAsc(unittest.TestCase):
    def test_get_time(self):

        self.assertEquals(get_raw_data_asc.time_from_asc("Date: 2018-12-04, Time: 16:50:46\n"),
                          datetime.datetime(2018, 12, 04, 16, 50, 46)
                          )



if __name__ == "__main__":
    unittest.main()
