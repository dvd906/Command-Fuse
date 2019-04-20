from collections import OrderedDict
import json
import re
import os

import modules.data_parser        as data_parser
import modules.cmd_fuse_exception as cmd_fuse_exception

class OneCommand:
    """
    Represents a single command which can be generated
    """
    def __init__(self, cmd_id, cmd_str, required_cols):
        """
        Params
        ------
        cmd_id : str
            The command name to refer later in datasheet
        cmd_str : str
            The raw string command
        required_cols : []
            The required columns to substitute for generating
        """
        self._cmd_id = cmd_id
        self._cmd_str = cmd_str
        self._requried_columns = required_cols

    def __repr__(self):
        sep = ', '
        represent = __class__.__name__ 
        represent += '(' + str(self._cmd_id) + sep
        represent += str(self._cmd_str) + sep
        represent += str(self._requried_columns) + ')'             
        return represent

    @property
    def cmd_id(self):
        return self._cmd_id

    @property
    def required_columns(self):
        return self._requried_columns
    @property
    def command_str(self):
        return self._cmd_str

    def generate(self, data:dict):
        """
        Returns
        -------
        str
            the generated command or the missing column(s)
        """
        if self._is_data_avialable(data):
            generated_cmd = self._cmd_str
            for col in self._requried_columns:
                generated_cmd = re.sub(col, data[col], generated_cmd)
            return generated_cmd.strip()
        else:
            missing_cols = self._get_missing_columns(data)
            raise cmd_fuse_exception.CannotGenerateCommandError(self._cmd_id, missing_cols)

    def _is_data_avialable(self, data):
        is_avialable = True
        for col in self._requried_columns:
            if col not in data.keys():
                is_avialable = False
                break
        return is_avialable

    def _get_missing_columns(self, data):
        missing_cols = []
        for key in self._requried_columns:
            if key not in data.keys():
                missing_cols.append(key)
        return missing_cols

class CommandPackage(data_parser.DataParser):
    """
    Creates a command package from the given text file
    One row hold one command, which must meet the following syntax:
    cmd_id : command [to_substitute]
    """
    BASE_SEPARATOR = ':'
    COL_SUB_LEFT = '['
    COL_SUB_RIGHT = ']'
    TO_REPLACE = ''
    _SPLITTED_COMMAND_LENGTH = 2
    _BASE_PACKAGE_NAME = 'package'
    _JSON_INDENT = 4
    _VALID_PARENTHESIS = 1

    def __init__(self, path=None, package_name=_BASE_PACKAGE_NAME, separator=BASE_SEPARATOR,
       col_sub_left=COL_SUB_LEFT, col_sub_right=COL_SUB_RIGHT,
       to_replace=TO_REPLACE):
        """
        Params
        ------
        path : str
            The file path
        package_name : str
            The command's package name
        separator : str
            The command id and command row separator
        col_sub_left : str
            The left id of the column which to replace later
        col_sub_right : right
            The right id of the column which to replace later
        to_replace : str
            The col_sub-s to replace in the command
        """
        self._separator = separator
        self._package_name = package_name
        self._col_sub_left = col_sub_left
        self._col_sub_right = col_sub_right
        self._to_replace = to_replace
        return super().__init__(path)

    @property
    def package_name(self):
        return self._package_name

    def deploy(self):
        """
        Creates the package
        Returns
        -------
        dict
            JSON ready object
        """
        json_ready_dict = {}
        for command in self.data:
            key = command.cmd_id
            current_command = {}
            current_command['required_columns'] = command.required_columns
            current_command['command'] = command.command_str
            json_ready_dict[key] = current_command.copy()
        return json_ready_dict

    def deploy_package(self, path):
        """
        Writes the package into the path
        Params
        ------
        path : str
            The file to write
        """
        json_ready_commands = self.deploy()
        if os.path.isdir(path):
            path = path + os.sep + self._package_name
        with open(path, 'w') as package_file:
            package_file.write(json.dumps(json_ready_commands, 
                    indent=CommandPackage._JSON_INDENT))

    def load_package(self, path):
        """
        Loads the package from the provided path
        Params
        ------
        path : str
            To load the package file
        Returns
        -------
        commands : []
            One element is a OneCommand
        """
        commands = {}
        with open(path) as package_file:
            lines_str = ''.join(package_file.readlines())
            json_commands = json.loads(lines_str)
            for cmd_id in json_commands:
                command_prop = json_commands[cmd_id]
                one_command = OneCommand(cmd_id, 
                   command_prop['command'],
                   command_prop['required_columns'])
                commands[cmd_id] = one_command
        return commands

    def _get_data(self, path):
        """
        Returns
        -------
        commands : []
            Where one element is an OneCommand
        """
        rows = None
        with open(path) as cmd_file:
            rows = cmd_file.read().splitlines()
        cmds = []
        index = 0
        for one_row in rows:
            split_cmd = one_row.split(self._separator)

            if len(split_cmd) == CommandPackage._SPLITTED_COMMAND_LENGTH:
                cmd = OrderedDict()
                cmd_id = split_cmd[0].strip()
                required_cols = None
                try:
                    required_cols = self._get_required_cols(split_cmd[1])
                except cmd_fuse_exception.ColumnSyntaxError as syntax_err:
                    error_str = str(syntax_err)
                    raise cmd_fuse_exception.CommandParseError(index, error_str)
                command = split_cmd[1].replace(self._col_sub_left, self._to_replace)
                command = command.replace(self._col_sub_right, self._to_replace)
                cmds.append(OneCommand(cmd_id, command, required_cols))
            else:
                raise cmd_fuse_exception.CommandParseError(index)
            index = index + 1
        return cmds
    
    def _get_required_cols(self, raw_command):
        """
        Gets the required columns for the command

        Params
        ------
        raw_command : str
            The raw command string
        Returns
        -------
        columns : []
            The required columns in an array
            One element is a str
        Raises
        ------
        ColumnSyntaxError
            When the open/closing parenthesis does not match
        """
        cols = []
        left_split_sep = raw_command.split(self._col_sub_left)
        split_left_num = len(left_split_sep)
        for possible_column in left_split_sep:
            if self._col_sub_right in possible_column:
                cols.append(possible_column.split(self._col_sub_right)[0])
                split_left_num = split_left_num - 1

        if split_left_num != CommandPackage._VALID_PARENTHESIS:
            if split_left_num < CommandPackage._VALID_PARENTHESIS:
                raise cmd_fuse_exception.ColumnSyntaxError(self._col_sub_left)
            else:
                raise cmd_fuse_exception.ColumnSyntaxError(self._col_sub_right)
        return cols
