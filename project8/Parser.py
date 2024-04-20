"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        self._file = input_file
        self._current_command = ''

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        self._current_command = self._file.readline()
        if self._current_command:
            return True
        return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        if '//' in self._current_command:
            self._current_command = \
                self._current_command.split('//', 1)[0]
        self._current_command = self._current_command.strip()

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        if not self._current_command:
            return ''
        elif 'call' == self._current_command.split()[0]:
            return 'C_CALL'
        elif 'function' == self._current_command.split()[0]:
            return 'C_FUNCTION'
        elif 'return' == self._current_command.split()[0]:
            return 'C_RETURN'
        elif 'if-goto' == self._current_command.split()[0]:
            return 'C_IF'
        elif 'goto' == self._current_command.split()[0]:
            return 'C_GOTO'
        elif 'label' == self._current_command.split()[0]:
            return 'C_LABEL'
        elif 'push' == self._current_command.split()[0]:
            return 'C_PUSH'
        elif 'pop' == self._current_command.split()[0]:
            return 'C_POP'

        elif 'add' == self._current_command.split()[0] or \
                'sub' == self._current_command.split()[0] or \
                'neg' == self._current_command.split()[0] or \
                'eq' == self._current_command.split()[0] or \
                'gt' == self._current_command.split()[0] or \
                'lt' == self._current_command.split()[0] or \
                'and' == self._current_command.split()[0] or \
                'or' == self._current_command.split()[0] or \
                'not' == self._current_command.split()[0] or \
                'shiftleft' == self._current_command.split()[0] or \
                'shiftright' == self._current_command.split()[0]:
            return 'C_ARITHMETIC'

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        command_type = self.command_type()
        if command_type == 'C_ARITHMETIC':
            return self._current_command
        else:
            return self._current_command.split()[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        return int(self._current_command.split()[2])
