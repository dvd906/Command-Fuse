class CommandFuseError(Exception):
    pass

class CommandParseError(CommandFuseError):

    def __init__(self, index, message=None):
        self._line = index + 1
        self._message = "Cannot parse command "
        self._message += "at line: {} ".format(self._line)
        if message:
            self._message += message

    def __str__(self):
        return self._message

class CannotGenerateCommandError(CommandFuseError):

    def __init__(self, command_name, missing_columns):
        self._message = "Cannot generate \'{}\' ".format(command_name)
        self._message += "the following column(s) missing: {}".format(
            missing_columns
        )

    def __str__(self):
        return self._message

class NotSupportedSeparationError(CommandFuseError):

    def __init__(self, separation):
        self._message = 'Not supported fuse procedure: {}'.format(
                separation
            )

    def __str__(self):
        return self._message

class UnknownCommandIdError(CommandFuseError):

    def __init__(self, cmd_id, index):
        self._message = 'Cannot resolve command id \'{}\' '.format(cmd_id)
        self._message += 'at line: {}'.format(index + 1)

    def __str__(self):
        return self._message

class FuseExecutionError(CommandFuseError):

    def __init__(self, raised_message, index):
        self._message = raised_message
        self._message += 'at line: {}'.format(index + 1)

    def __str__(self):
        return self._message

class ColumnSyntaxError(CommandFuseError):

    def __init__(self, missing_col):
        self._message = 'Missing column parenthesis \'{}\''.format(missing_col)

    def __str__(self):
        return self._message