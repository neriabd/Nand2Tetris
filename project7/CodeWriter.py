"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self._output_stream = output_stream
        self._file_name = ''
        self._boolean_counter = 0
        self._push_D_to_stack = 'push_D_to_stack'
        self._pop_stack_to_D = 'pop_stack_to_D'
        self._commands_dict = {self._pop_stack_to_D: '@SP\n'
                                                     'M=M-1\n'
                                                     'A=M\n'
                                                     'D=M\n',
                               self._push_D_to_stack: '@SP\n'
                                                      'A=M\n'
                                                      'M=D\n'
                                                      '@SP\n'
                                                      'M=M+1\n'}

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self._file_name = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """

        if 'add' in command:
            self._output_stream.write(
                self._commands_dict[self._pop_stack_to_D] +
                '@R14\n'
                'M=D\n' +
                self._commands_dict[self._pop_stack_to_D] +
                '@R14\n'
                'D=D+M\n' +
                self._commands_dict[self._push_D_to_stack])

        elif 'sub' in command:
            self._output_stream.write(
                self._commands_dict[self._pop_stack_to_D] +
                '@R14\n'
                'M=D\n' +
                self._commands_dict[self._pop_stack_to_D] +
                '@R14\n'
                'D=D-M\n' +
                self._commands_dict[self._push_D_to_stack])

        elif 'neg' in command:
            self._output_stream.write(
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=-M\n"
                "@SP\n"
                "M=M+1\n")

        elif 'not' in command:
            self._output_stream.write(
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=!M\n"
                "@SP\n"
                "M=M+1\n")

        elif 'shiftleft' in command:
            self._output_stream.write(
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=M<<\n"
                "@SP\n"
                "M=M+1\n")

        elif 'shiftright' in command:
            self._output_stream.write(
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=M>>\n"
                "@SP\n"
                "M=M+1\n")

        elif 'and' in command:
            self._output_stream.write(
                self._commands_dict[self._pop_stack_to_D] +
                '@R14\n'
                'M=D\n' +
                self._commands_dict[self._pop_stack_to_D] +
                '@R14\n'
                'D=D&M\n' +
                self._commands_dict[self._push_D_to_stack])

        elif 'or' in command:
            self._output_stream.write(
                self._commands_dict[self._pop_stack_to_D] +
                '@R14\n'
                'M=D\n' +
                self._commands_dict[self._pop_stack_to_D] +
                '@R14\n'
                'D=D|M\n' +
                self._commands_dict[self._push_D_to_stack])

        elif 'gt' in command or 'lt' in command or 'eq' in command:
            self._output_stream.write(
                self._commands_dict[self._pop_stack_to_D] +
                '@R14\n'
                'M=D\n'
                '@tmp1\n'
                'M=D\n' +
                self._commands_dict[self._pop_stack_to_D] +
                '@R13\n'
                'M=D\n'
                '@tmp2\n'
                'M=D\n'

                '@R13\n'
                'D=M\n'
                f'@POSA{self._boolean_counter}\n'
                'D;JGT\n'
                '@R15\n'
                'M=0\n'
                f'@CONTINUEA{self._boolean_counter}\n'
                '0;JMP\n'
                f'(POSA{self._boolean_counter})\n'
                '@R15\n'
                'M=1\n'
                f'(CONTINUEA{self._boolean_counter})\n'
                '@R14\n'
                'D=M\n'
                f'@POSB{self._boolean_counter}\n'
                'D;JGT\n'
                '@R13\n'
                'M=0\n'
                f'@CONTINUEB{self._boolean_counter}\n'
                '0;JMP\n'
                f'(POSB{self._boolean_counter})\n'
                '@R13\n'
                'M=1\n'
                f'(CONTINUEB{self._boolean_counter})\n'
                '@R13\n'
                'D=M\n'
                '@R15\n'
                'D=D-M\n'
                f'@SAME{self._boolean_counter}\n'
                'D;JEQ\n')

            if 'eq' in command:
                self._output_stream.write(
                    f'@FALSE{self._boolean_counter}\n'
                    '0;JMP\n')

            elif 'gt' in command:
                self._output_stream.write(
                    '@R15\n'
                    'D=M\n'
                    f'@TRUE{self._boolean_counter}\n'
                    'D;JGT\n'
                    f'@FALSE{self._boolean_counter}\n'
                    '0;JMP\n')

            elif 'lt' in command:
                self._output_stream.write(
                    '@R15\n'
                    'D=M\n'
                    f'@TRUE{self._boolean_counter}\n'
                    'D;JEQ\n'
                    f'@FALSE{self._boolean_counter}\n'
                    '0;JMP\n')

            self._output_stream.write(
                f'(SAME{self._boolean_counter})\n'
                '@tmp2\n'
                'D=M\n'
                '@tmp1\n'
                'D=D-M\n'
                f'@TRUE{self._boolean_counter}\n')
            if 'eq' in command:
                self._output_stream.write('D;JEQ\n')
            elif 'gt' in command:
                self._output_stream.write('D;JGT\n')
            elif 'lt' in command:
                self._output_stream.write('D;JLT\n')
            self._output_stream.write(
                f'(FALSE{self._boolean_counter})\n'
                '@SP\n'
                'A=M\n'
                'M=0\n'
                f'@END{self._boolean_counter}\n'
                '0;JMP\n'
                f'(TRUE{self._boolean_counter})\n'
                '@SP\n'
                'A=M\n'
                'M=-1\n'
                f'(END{self._boolean_counter})\n'
                '@SP\n'
                'M=M+1\n')

            if 'gt' in command or 'lt' in command or 'eq' in command:
                self._boolean_counter += 1

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        new_segment = ''
        if segment == 'local':
            new_segment = 'LCL'
        elif segment == 'argument':
            new_segment = 'ARG'
        elif segment == 'this':
            new_segment = 'THIS'
        elif segment == 'that':
            new_segment = 'THAT'

        if command == 'C_PUSH':
            if new_segment == 'LCL' or new_segment == 'ARG' or \
                    new_segment == 'THIS' or new_segment == 'THAT' or segment \
                    == 'temp':
                if segment != 'temp':
                    self._output_stream.write(f'@{new_segment}\n'
                                              'D=M\n')
                else:
                    self._output_stream.write('@5\n'
                                              'D=A\n')
                self._output_stream.write(
                    f'@{index}\n'
                    'A=D+A\n'
                    'D=M\n' +
                    self._commands_dict[self._push_D_to_stack])

            elif segment == 'constant':
                self._output_stream.write(
                    f'@{index}\n'
                    f'D=A\n' +
                    self._commands_dict[self._push_D_to_stack])

            elif segment == 'static':
                self._output_stream.write(
                    f'@{self._file_name}.{index}\n'
                    'D=M\n' +
                    self._commands_dict[self._push_D_to_stack])

            elif segment == 'pointer':
                if index == 0:
                    self._output_stream.write(
                        '@THIS\n'
                        'D=M\n' +
                        self._commands_dict[self._push_D_to_stack])
                else:
                    self._output_stream.write(
                        '@THAT\n'
                        'D=M\n' +
                        self._commands_dict[self._push_D_to_stack])

        elif command == 'C_POP':
            if new_segment == 'LCL' or new_segment == 'ARG' or \
                    new_segment == 'THIS' or new_segment == 'THAT' or segment \
                    == 'temp':
                self._output_stream.write(
                    self._commands_dict[
                        self._pop_stack_to_D] +  # D = item popped
                    '@R13\n'
                    'M=D\n')

                if segment != 'temp':
                    self._output_stream.write(
                        f'@{new_segment}\n'
                        'D=M\n')
                else:
                    self._output_stream.write(
                        '@5\n'
                        'D=A\n')

                self._output_stream.write(
                    f'@{index}\n'
                    'A=D+A\n'
                    'D=A\n'
                    '@R14\n'
                    'M=D\n'
                    '@R13\n'
                    'D=M\n'
                    '@R14\n'
                    'A=M\n'
                    'M=D\n')

            elif segment == 'static':
                self._output_stream.write(
                    self._commands_dict[
                        self._pop_stack_to_D] +
                    f'@{self._file_name}.{index}\n'
                    'M=D\n')

            elif segment == 'pointer':
                if index == 0:
                    self._output_stream.write(
                        self._commands_dict[self._pop_stack_to_D] +
                        '@THIS\n'
                        'M=D\n')
                else:
                    self._output_stream.write(
                        self._commands_dict[self._pop_stack_to_D] +
                        '@THAT\n'
                        'M=D\n')

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command.
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        pass

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        pass

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command.

        Args:
            label (str): the label to go to.
        """
        pass

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command.
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        pass

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command.
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        pass

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        pass
