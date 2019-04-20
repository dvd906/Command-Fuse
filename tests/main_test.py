import unittest
import os 
import sys

from ..modules import data_parser

class CommandParserTest(unittest.TestCase):

    def test_not_supported(self):
        with self.assertRaises(TypeError):
            dp = data_parser.RawDataParser('testpath')

    def test_empty_data_for_valid_regex(self):
        valid_extensions = ['.csv', '.tsv', '.xlsx']
        for extension in valid_extensions:
            dp = data_parser.RawDataParser(extension)
            self.assertEqual([], dp.data)

if __name__ == '__main__':
    unittest.main()
