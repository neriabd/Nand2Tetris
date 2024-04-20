"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # A good place to start is to read all the lines of the input:
        # input_lines = input_file.read().splitlines()
        self._file = input_file
        self._current_instruction = ''

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        self._current_instruction = self._file.readline()
        if self._current_instruction:
            return True
        return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current
        command. Should be called only if has_more_commands() is true.
        """
        if '//' in self._current_instruction:
            self._current_instruction = \
                self._current_instruction.split('//', 1)[0]
        self._current_instruction = self._current_instruction.replace(" ", "")
        self._current_instruction = self._current_instruction.strip()

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self._current_instruction.startswith('@'):
            return "A_COMMAND"
        elif self._current_instruction.startswith('('):
            return "L_COMMAND"
        elif self._current_instruction:
            return "C_COMMAND"
        return ''

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if self._current_instruction.startswith('@'):
            return self._current_instruction[1:]
        else:
            return self._current_instruction[1:-1]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if '=' in self._current_instruction:
            ind = self._current_instruction.index('=')
            return self._current_instruction[0:ind].strip()

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        start_ind = 0
        end_ind = len(self._current_instruction)
        if '=' in self._current_instruction:
            start_ind = self._current_instruction.index('=') + 1
        if ';' in self._current_instruction:
            end_ind = self._current_instruction.index(';')
        return self._current_instruction[start_ind:end_ind].strip()

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if ';' in self._current_instruction:
            ind = self._current_instruction.index(';')
            return self._current_instruction[ind + 1:].strip()
