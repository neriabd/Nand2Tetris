"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

import SymbolTable
import VMWriter
from typing import List

OP_DICT = {'+': 'add', '-': 'sub', '&': 'and', '|': 'or', '<': 'lt',
           '>': 'gt', '=': 'eq', '*': 'call Math.multiply 2',
           '/': 'call Math.divide 2'}

UNARY_OP_DICT = {'-': 'neg', '~': 'not', '^': 'shiftleft', '#': 'shiftright'}

KEYWORD_DICT = {'true': ("CONSTANT", -1), 'false': ("CONSTANT", 0),
                'this': ("POINTER", 0), 'null': ("CONSTANT", 0)}


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self._symbol_table = SymbolTable.SymbolTable()
        self._vm_writer = VMWriter.VMWriter(output_stream)
        self._tokenizer = input_stream.get_token()
        self.ind = 0
        self.label_counter = 0
        self.end_counter = 0
        self._length_token = len(self._tokenizer)
        self._class_name = ""
        self.compile_class()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.ind += 1
        self._class_name = self._tokenizer[self.ind]
        self.ind += 2
        while '}' != self._tokenizer[self.ind]:
            if 'field' in self._tokenizer[self.ind] or 'static' in \
                    self._tokenizer[self.ind]:
                self.compile_class_var_dec()
            if 'function' in self._tokenizer[self.ind] or 'constructor' in \
                    self._tokenizer[self.ind] or 'method' in \
                    self._tokenizer[self.ind]:
                self.compile_subroutine()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        """Compiles a var declaration."""
        kind = self._tokenizer[self.ind]
        self.ind += 1
        type = self._tokenizer[self.ind]
        self.ind += 1
        names = []
        while ';' != self._tokenizer[self.ind]:
            names.append(self._tokenizer[self.ind])
            self.ind += 1
            if self._tokenizer[self.ind] == ',':
                self.ind += 1
        self.ind += 1
        for name in names:
            self._symbol_table.define(name, type, kind.upper())

    def compile_var_dec(self) -> int:
        """Compiles a var declaration."""
        kind = 'VAR'
        self.ind += 1
        type = self._tokenizer[self.ind]
        self.ind += 1
        names = []
        while ';' != self._tokenizer[self.ind]:
            names.append(self._tokenizer[self.ind])
            self.ind += 1
            if self._tokenizer[self.ind] == ',':
                self.ind += 1
        self.ind += 1
        for name in names:
            self._symbol_table.define(name, type, kind)
        return len(names)

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self._symbol_table.start_subroutine()
        function_type = self._tokenizer[self.ind]
        self.ind += 2
        name = self._tokenizer[self.ind]
        self.ind += 2
        if function_type == 'method':
            self._symbol_table.define("this", self._class_name, "ARG")
        self.compile_parameter_list()
        var = 0
        while 'var' in self._tokenizer[self.ind]:
            var += self.compile_var_dec()
        self._vm_writer.write_function(self._class_name + '.' + name, var)
        if function_type == 'constructor':
            self._vm_writer.write_push("CONSTANT",
                                       self._symbol_table.var_count(
                                           'FIELD') + 1)
            self._vm_writer.write_call('Memory.alloc', 1)
            self._vm_writer.write_pop('POINTER', 0)
        elif function_type == 'method':
            self._vm_writer.write_push('ARG', 0)
            self._vm_writer.write_pop('POINTER', 0)
        self.compile_statements()
        self.ind += 1

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        kind = 'ARG'
        while ')' != self._tokenizer[self.ind]:
            if self._tokenizer[self.ind] != ',':
                self._symbol_table.define(self._tokenizer[self.ind + 1],
                                          self._tokenizer[self.ind], kind)
                self.ind += 2
            else:
                self.ind += 1
        self.ind += 2

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        while self._tokenizer[self.ind] != '}':
            command = self._tokenizer[self.ind]
            if command == 'let':
                self.compile_let()
            elif command == 'if':
                self.compile_if()
            elif command == 'while':
                self.compile_while()
            elif command == 'do':
                self.compile_do()
            elif command == 'return':
                self.compile_return()

    def compile_call_in_exp(self, func: List[str]) -> None:
        """ compiles a function call that is in the expressions """
        name = ''
        flag = 0
        i = 0
        func.pop()
        while '(' != func[i]:
            name += func[i]
            i += 1
        arg_lst = []
        if name[0].islower() and '.' in name:
            arg_lst.append([name.split(".", 1)[0]])
            name1, name2 = name.split(".", 1)
            name1 = self._symbol_table.type_of(name1)
            name = name1 + "." + name2
        elif '.' not in name:
            name = self._class_name + "." + name
            self._vm_writer.write_push("POINTER", 0)
            flag = 1
        i += 1
        while i < len(func):
            now = []
            if ',' == func[i]:
                i += 1
            while i < len(func) and func[i] != ',':
                now.append(func[i])
                i += 1
            i += 1
            arg_lst.append(now)
        for arg in arg_lst:
            self.compile_expression(arg)
        self._vm_writer.write_call(name, len(arg_lst) + flag)

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.ind += 1
        func = []
        while ';' != self._tokenizer[self.ind]:
            func.append(self._tokenizer[self.ind])
            self.ind += 1
        self.compile_call_in_exp(func)
        self._vm_writer.write_pop('TEMP', 0)
        self.ind += 1

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.ind += 1
        first = []
        while '=' != self._tokenizer[self.ind]:
            first.append(self._tokenizer[self.ind])
            self.ind += 1
        self.ind += 1
        second = []
        while ';' != self._tokenizer[self.ind]:
            second.append(self._tokenizer[self.ind])
            self.ind += 1
        self.ind += 1
        self.compile_expression(second)
        if '[' in first:
            name = [first[0]]
            start = first.index('[') + 1
            end = len(first) - 1
            self.compile_expression(first[start:end])  # index of array
            self.compile_expression(name)  # array start address
            self._vm_writer.write_arithmetic("add")
            self._vm_writer.write_pop("POINTER", 1)
            self._vm_writer.write_pop("THAT", 0)
        else:
            self._vm_writer.write_pop(self._symbol_table.kind_of(first[0]),
                                      self._symbol_table.index_of(first[0]))

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.label_counter += 1
        self.end_counter += 1
        my_label = self.label_counter
        my_end = self.end_counter
        self.ind += 1
        self._vm_writer.write_label(self._class_name + str(my_label))
        exp = []
        while '{' != self._tokenizer[self.ind]:
            exp.append(self._tokenizer[self.ind])
            self.ind += 1
        self.ind += 1
        self.compile_expression(exp)
        self._vm_writer.write_arithmetic('not')
        self._vm_writer.write_if(
            self._class_name + "END" + str(my_end))
        self.compile_statements()
        self._vm_writer.write_goto(self._class_name + str(my_label))
        self._vm_writer.write_label(
            self._class_name + "END" + str(my_end))
        self.ind += 1

    def compile_return(self) -> None:
        """Compiles a return statement."""
        exp = []
        self.ind += 1
        if self._tokenizer[self.ind] == ';':
            self._vm_writer.write_push('CONSTANT', 0)
            self._vm_writer.write_return()
            self.ind += 1
            return
        while ';' != self._tokenizer[self.ind]:
            exp.append(self._tokenizer[self.ind])
            self.ind += 1
        self.compile_expression(exp)
        self._vm_writer.write_return()
        self.ind += 1

    def compile_if(self) -> None:
        """Compiles an if statement, possibly with a trailing else clause."""
        self.label_counter += 1
        self.end_counter += 1
        my_label = self.label_counter
        my_end = self.end_counter
        self.ind += 1
        exp = []
        while '{' != self._tokenizer[self.ind]:
            exp.append(self._tokenizer[self.ind])
            self.ind += 1
        self.compile_expression(exp)
        self._vm_writer.write_arithmetic('not')
        self._vm_writer.write_if(
            self._class_name + "ELSE" + str(my_label))
        self.ind += 1
        self.compile_statements()
        self.ind += 1
        self._vm_writer.write_goto(
            self._class_name + "END" + str(my_end))
        self._vm_writer.write_label(
            self._class_name + "ELSE" + str(my_label))
        if self._tokenizer[self.ind] == 'else':
            self.ind += 2
            self.compile_statements()
            self.ind += 1
        self._vm_writer.write_label(
            self._class_name + "END" + str(my_end))

    def compile_expression(self, exp: List[str]) -> None:
        """Compiles an expression."""
        exp = self.check_for_function(exp)
        symbol_lst = []
        for i, x in enumerate(exp):
            if type(x) == list:
                self.compile_call_in_exp(x)

            elif x == '(' or x == '[':
                symbol_lst.append(x)

            elif x == ')':
                self.close_parenthesis(symbol_lst)

            elif x == ']':
                self.push_array_index(symbol_lst)

            elif x.startswith('"'):
                self.compile_string(x)

            elif x.isdigit():
                self.push_number(x, symbol_lst)

            elif self._symbol_table.type_of(x):
                self.push_from_symbol_table(x, i, exp, symbol_lst)

            elif x in KEYWORD_DICT:
                self.push_keyword(x, symbol_lst)

            elif x in OP_DICT:
                if x == '-':
                    if i > 0 and '(' != exp[i - 1] and exp[i - 1] != '[':
                        symbol_lst.append(OP_DICT[x])
                    else:
                        symbol_lst.append(UNARY_OP_DICT[x])
                else:
                    symbol_lst.append(OP_DICT[x])

            elif x in UNARY_OP_DICT:
                symbol_lst.append(UNARY_OP_DICT[x])

    def close_parenthesis(self, symbol_lst: List[str]) -> None:
        """ deletes the parenthesis """
        while '(' != symbol_lst[-1]:
            self._vm_writer.write_arithmetic(symbol_lst.pop())
        symbol_lst.pop()
        while symbol_lst and '(' != symbol_lst[-1] and '[' != \
                symbol_lst[-1]:
            self._vm_writer.write_arithmetic(symbol_lst.pop())

    def push_array_index(self, symbol_lst: List[str]) -> None:
        """ pushes the array's index """
        while '[' != symbol_lst[-1]:
            self._vm_writer.write_arithmetic(symbol_lst.pop())
        symbol_lst.pop()
        self._vm_writer.write_arithmetic("add")
        self._vm_writer.write_pop("POINTER", 1)
        self._vm_writer.write_push("THAT", 0)
        while symbol_lst and symbol_lst[-1] != '(' and \
                symbol_lst[-1] != '[':
            self._vm_writer.write_arithmetic(symbol_lst.pop())

    def push_keyword(self, x: str, symbol_lst: List[str]) -> None:
        """ pushes the keyword """
        segment, index = KEYWORD_DICT.get(x)
        self._vm_writer.write_push(segment, index)
        if symbol_lst and \
                (symbol_lst[-1] != '(' and symbol_lst[-1] != '['):
            self._vm_writer.write_arithmetic(symbol_lst.pop())

    def push_from_symbol_table(self, x: str, i: int, exp: List[str],
                               symbol_lst: List) -> None:
        """ pushes the element that is in the symbol table """
        self._vm_writer.write_push(self._symbol_table.kind_of(x),
                                   self._symbol_table.index_of(x))
        if (i + 1) < len(exp) and exp[i + 1] == '[':
            return
        if symbol_lst and (
                symbol_lst[-1] != '(' and symbol_lst[-1] != '['):
            self._vm_writer.write_arithmetic(symbol_lst.pop())

    def push_number(self, x: str, symbol_lst: List[str]) -> None:
        """ pushes a number """
        self._vm_writer.write_push('CONSTANT', int(x))
        if symbol_lst and (
                symbol_lst[-1] != '(' and symbol_lst[-1] != '['):
            self._vm_writer.write_arithmetic(symbol_lst.pop())

    def compile_string(self, x: str) -> None:
        """ compiles a single string """
        x = x[1:-1]
        self._vm_writer.write_push("CONSTANT", len(x))
        self._vm_writer.write_call('String.new', 1)
        for i in range(len(x)):
            self._vm_writer.write_push("CONSTANT", ord(x[i]))
            self._vm_writer.write_call('String.appendChar', 2)

    def check_for_function(self, exp: List[str]) -> List:
        """ for each function in expression -> puts it into list in order to
         easily handle function later on """
        updated = []
        i = 0
        while i < len(exp):
            if i < len(exp) - 1 and exp[i + 1] == ".":
                name = []
                while exp[i] != "(":
                    name.append(exp[i])
                    i += 1
                name.append(exp[i])
                i += 1
                counter = 1
                while counter != 0:
                    name.append(exp[i])
                    if exp[i] == "(":
                        counter += 1
                    elif exp[i] == ")":
                        counter -= 1
                    i += 1
                updated.append(name)
            else:
                updated.append(exp[i])
                i += 1
        return updated
