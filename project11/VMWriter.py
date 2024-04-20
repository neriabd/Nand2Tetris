"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class VMWriter:
    """
    Writes VM commands into a file. Encapsulates the VM command syntax.
    """

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Creates a new file and prepares it for writing VM commands."""

        self._output_file = output_stream
        self._segment_dict = {"CONSTANT": "constant", "ARG": "argument",
                              "LOCAL": "local", "STATIC": "static",
                              "THIS": "this", "THAT": "that",
                              "POINTER": "pointer", "TEMP": "temp",
                              "FIELD": 'this', 'VAR': 'local'}

    def write_push(self, segment: str, index: int) -> None:
        """Writes a VM push command.

        Args:
            segment (str): the segment to push to, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"
            index (int): the index to push to.
        """
        negative = index < 0
        index = str(index)[1:] if negative else str(index)
        self._output_file.write("push " + self._segment_dict[segment] +
                                " " + index + "\n")
        if negative:
            self.write_arithmetic("neg")

    def write_pop(self, segment: str, index: int) -> None:
        """Writes a VM pop command.

        Args:
            segment (str): the segment to pop from, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP".
            index (int): the index to pop from.
        """

        self._output_file.write("pop " + self._segment_dict[segment] +
                                " " + str(index) + "\n")

    def write_arithmetic(self, command: str) -> None:
        """Writes a VM arithmetic command.

        Args:
            command (str): the command to write, can be "ADD", "SUB", "NEG", 
            "EQ", "GT", "LT", "AND", "OR", "NOT", "SHIFTLEFT", "SHIFTRIGHT".
        """
        self._output_file.write(command + "\n")

    def write_label(self, label: str) -> None:
        """Writes a VM label command.

        Args:
            label (str): the label to write.
        """

        self._output_file.write("label " + label + "\n")

    def write_goto(self, label: str) -> None:
        """Writes a VM goto command.

        Args:
            label (str): the label to go to.
        """

        self._output_file.write("goto " + label + "\n")

    def write_if(self, label: str) -> None:
        """Writes a VM if-goto command.

        Args:
            label (str): the label to go to.
        """

        self._output_file.write("if-goto " + label + "\n")

    def write_call(self, name: str, n_args: int) -> None:
        """Writes a VM call command.

        Args:
            name (str): the name of the function to call.
            n_args (int): the number of arguments the function receives.
        """

        self._output_file.write("call " + name + " " + str(n_args) + "\n")

    def write_function(self, name: str, n_locals: int) -> None:
        """Writes a VM function command.

        Args:
            name (str): the name of the function.
            n_locals (int): the number of local variables the function uses.
        """

        self._output_file.write(
            "function " + name + " " + str(n_locals) + "\n")

    def write_return(self) -> None:
        """Writes a VM return command."""

        self._output_file.write("return" + "\n")
