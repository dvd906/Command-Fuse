import unittest
import os 
import sys

import modules as m

class TestCommandParser(unittest.TestCase):

    def test_not_supported(self):
        with self.assertRaises(TypeError):
            dp = m.data_parser.RawDataParser('testpath')

    def test_empty_data_for_valid_regex(self):
        valid_extensions = ['.csv', '.tsv', '.xlsx']
        for extension in valid_extensions:
            dp = m.data_parser.RawDataParser(extension)
            self.assertEqual([], dp.data)

class TestOneCommand(unittest.TestCase):

    def test_successful_generation(self):
        cmd_id = 'test_id'
        cmd_str = "test_command --my_input Column --my_static \'StaticValue\' "
        required_columns = ['Column']
        data_dict = {'Column' : 5}

        one_command = m.command_parser.OneCommand(cmd_id, cmd_str, required_columns)
        command_str = one_command.generate(data_dict)
        self.assertNotEqual(command_str, '')

    def test_cannot_generate_error(self):
        cmd_id = 'test_id'
        cmd_str = "test_command --my_imput Column --my_static \'StaticValue\' "
        required_columns = ['Column', 'SomeColumn']
        data_dict = {'Column' : 3}
       
        one_command = m.command_parser.OneCommand(cmd_id, cmd_str, required_columns)
        with self.assertRaises(m.cmd_fuse_exception.CannotGenerateCommandError):
            one_command.generate(data_dict)

    def test_cannot_generate_columns_count(self):
        cmd_id = 'test_id'
        cmd_str = "test_command --my_imput Column --my_static \'StaticValue\' "
        required_columns = ['Column', 'SomeColumn', 'Rofl']
        data_dict = {'Rofl' : 234}

        keys = list(data_dict.keys())
        columns_not_in_dict = [col for col in required_columns if col not in keys]

        try:
            one_command = m.command_parser.OneCommand(cmd_id, cmd_str, required_columns)
            one_command.generate(data_dict)
        except m.cmd_fuse_exception.CannotGenerateCommandError as error:
           count_missing_columns = len(columns_not_in_dict)
           count_error_columns = len(error.missing_columns)
           self.assertEqual(count_missing_columns, count_error_columns)

class TestCommandPackage(unittest.TestCase):

    def test_column_syntax_error(self):
        missing_second_line_str = '\n'.join([
            "command_id : -input [Column]",
            "command_id_2 : -input Column]"
            ])
        with self.assertRaises(m.cmd_fuse_exception.CommandParseError):
            command_package = m.command_parser.CommandPackage(missing_second_line_str)

    def test_duplicated_id_error(self):
        duplicated_id_str = '\n'.join([
            "command_id_2 : -input no_input",
            "command_id_2 : -input test"
            ])
        with self.assertRaises(m.cmd_fuse_exception.CommandParseError):
            command_package = m.command_parser.CommandPackage(duplicated_id_str)

if __name__ == '__main__':
    unittest.main()
