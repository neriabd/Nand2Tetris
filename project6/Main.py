"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    symbol_table = SymbolTable()
    parser = Parser(input_file)
    counter = 0
    while parser.has_more_commands():
        parser.advance()
        command_type = parser.command_type()
        if command_type == 'L_COMMAND':
            symbol_table.add_entry(parser.symbol(), counter)
        if command_type == 'A_COMMAND' or command_type == 'C_COMMAND':
            counter += 1

    input_file.seek(0)
    n = 16
    while parser.has_more_commands():
        parser.advance()
        symbol = parser.symbol()
        if parser.command_type() == 'A_COMMAND':
            if not symbol_table.contains(symbol):
                if symbol.isdigit():
                    symbol_table.add_entry(symbol, int(symbol))
                else:
                    symbol_table.add_entry(symbol, n)
                    n += 1
            command = str(bin(symbol_table.get_address(symbol)))
            command = command.replace('b', (16 - len(command) + 1) * '0')
        elif parser.command_type() == 'C_COMMAND':
            dest = parser.dest()
            comp = parser.comp()
            jump = parser.jump()
            bin_dest = Code.dest(dest)
            bin_comp = Code.comp(comp)
            bin_jump = Code.jump(jump)
            if '<<' in comp or '>>' in comp:
                command = '101' + bin_comp + bin_dest + bin_jump
            else:
                command = '111' + bin_comp + bin_dest + bin_jump
        else:
            continue
        output_file.write(command + '\n')


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
