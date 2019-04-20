import os

import modules.cmd_fuse_exception as cmd_fuse_exception
import modules.command_parser     as command_parser
import modules.data_parser        as data_parser

class CommandSeparationType:
    sequential = 'seq'
    group = 'group'

class CommandFuse:

    BASE_COMMAND_COLUMN = 'CMD'
    BASE_COMMAND_SEP = ';'
    _DATA_START_IDX = 1
    # windows using \r\n for endline only use \n
    _NEW_LINE = '\n' 

    def __init__(self, data, commands, 
       command_column=BASE_COMMAND_COLUMN,
       cmd_id_sep=BASE_COMMAND_SEP,
       separation_type=CommandSeparationType.sequential):
        self._data = data
        self._commands = commands
        self._command_column = command_column
        self._command_id_sep = cmd_id_sep
        self._separation_type = separation_type

        self._fuse_functions = {
           CommandSeparationType.group : self._group_fuse,
           CommandSeparationType.sequential : self._seq_fuse
        }

    def fuse(self):
        """
        Generates the commands

        Returns
        -------
        generated_commands : []
            One element is str
        """
        generated_commands = []
        fuse_function = self._fuse_functions.get(self._separation_type)
        if not fuse_function:
            raise cmd_fuse_exception.NotSupportedSeparationError(self._separation_type)
        generated_commands = fuse_function()
        return generated_commands

    def fuse_to_file(self, path):
        """
        Saves the generated output to the provided path
        """
        generated_commands = self.fuse()
        
        with open(path, 'w') as to_save:
            command_str = CommandFuse._NEW_LINE.join(generated_commands)
            to_save.write(command_str)

    def _group_fuse(self):
        """
        Implements the group command generation

        Retunrs
        -------
        generated_commands : []
            One element is str
        """
        command_dict = {}
        index = CommandFuse._DATA_START_IDX
        for row in self._data:
            command_str = row.get(self._command_column)
            if command_str:
                commands = self._extract_commands(command_str)
                for command_id in commands:
                    one_command = self._commands.get(command_id)
                    if not one_command:
                       raise cmd_fuse_exception.UnknownCommandIdError(command_id, index)
                    if not command_dict.get(command_id):
                        command_dict[command_id] = []
                    try:
                        command_dict[command_id].append(one_command.generate(row))
                    except cmd_fuse_exception.CannotGenerateCommandError as generated_error:
                        message = str(generated_error)
                        raise cmd_fuse_exception.FuseExecutionError(message, index)
            index = index + 1
        generated_commads = []
        for cmd_id in command_dict:
            generated_commads = generated_commads + command_dict[cmd_id]
        return generated_commads

    def _seq_fuse(self):
        """
        Implements the sequential fuse 
        
        Returns
        -------
        generated_commands : []
            One element is str
        """
        generated_commands = []
        index = CommandFuse._DATA_START_IDX
        for row in self._data:
            command_str = row.get(self._command_column)
            if command_str:
                commands = self._extract_commands(command_str)
                for command_id in commands:
                    command_id = command_id.strip()
                    one_command = self._commands.get(command_id)
                    if not one_command:
                       raise cmd_fuse_exception.UnknownCommandIdError(command_id, index)
                    try:
                        generated_commands.append(one_command.generate(row))
                    except cmd_fuse_exception.CannotGenerateCommandError as generated_error:
                        message = str(generated_error)
                        raise cmd_fuse_exception.FuseExecutionError(message, index)
            index = index + 1
        return generated_commands

    def _extract_commands(self, command_str):
        commands = command_str.split(self._command_id_sep)
        formatted_command_ids = []
        for cmd_id in commands:
            formatted_command_ids.append(cmd_id.strip())
        return formatted_command_ids
            
        