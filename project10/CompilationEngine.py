"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


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
        self._tokenizer = input_stream.get_token()
        self._output_file = output_stream
        self.ind = 0
        self.tabs_counter = 0
        self._length_token = len(self._tokenizer)
        self.compile_class()

    def write_major_tag(self, tag: str) -> None:
        """
        feeds into the output file the command
        @param tag: a string which the command write into the output file
        """
        open_tag = '/' not in tag
        if not open_tag:
            self.tabs_counter -= 1
        self._output_file.write(('  ' * self.tabs_counter) + tag)
        if open_tag:
            self.tabs_counter += 1

    def append_to_file(self) -> None:
        """
        adds a command to the output file
        """
        tag = self._tokenizer[self.ind][0]
        token = self._tokenizer[self.ind][1]
        self._output_file.write(
            ('  ' * self.tabs_counter) + f"<{token}> {tag} </{token}>\n")
        self.ind += 1

    def search_in_command(self, command: str) -> bool:
        """
        @param command: the current command
        @return: True if command in the current line in tokenizer
        """
        if self._tokenizer[self.ind][0] == command:
            return True
        return False

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.write_major_tag("<class>\n")

        while self.ind < self._length_token:
            if self.search_in_command("static") or \
                    self.search_in_command("field"):
                self.compile_class_var_dec()
            elif self.search_in_command("method") or \
                    self.search_in_command("constructor") or \
                    self.search_in_command("function"):
                self.compile_subroutine()
            elif self.search_in_command("var"):
                self.compile_var_dec()
            elif self.search_in_command("let"):
                self.compile_let()
            elif self.search_in_command("if"):
                self.compile_if()
            elif self.search_in_command("while"):
                self.compile_while()
            elif self.search_in_command("do"):
                self.compile_do()
            elif self.search_in_command("return"):
                self.compile_return()
            elif self.search_in_command("("):
                self.append_to_file()
                self.compile_expression_list()
                self.append_to_file()
            else:
                self.append_to_file()

        self.write_major_tag("</class>\n")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        """Compiles a var declaration."""
        self.write_major_tag("<classVarDec>\n")
        while not self.search_in_command(';'):
            self.append_to_file()

        self.append_to_file()
        self.write_major_tag("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.write_major_tag("<subroutineDec>\n")
        while not self.search_in_command("("):
            self.append_to_file()
        self.append_to_file()
        self.compile_parameter_list()
        self.append_to_file()
        self.write_major_tag("<subroutineBody>\n")
        self.append_to_file()
        while self.search_in_command("var"):
            self.compile_var_dec()
        self.compile_statements()
        self.append_to_file()
        self.write_major_tag("</subroutineBody>\n")
        self.write_major_tag("</subroutineDec>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        self.write_major_tag("<parameterList>\n")
        while not self.search_in_command(")"):
            self.append_to_file()
        self.write_major_tag("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.write_major_tag("<varDec>\n")
        while not self.search_in_command(';'):
            self.append_to_file()

        self.append_to_file()
        self.write_major_tag("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        self.write_major_tag("<statements>\n")
        while not self.search_in_command(";"):
            if self.search_in_command("let"):
                self.compile_let()
            elif self.search_in_command("if"):
                self.compile_if()
            elif self.search_in_command("while"):
                self.compile_while()
            elif self.search_in_command("do"):
                self.compile_do()
            elif self.search_in_command("return"):
                self.compile_return()
            else:
                break
        self.write_major_tag("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.write_major_tag("<doStatement>\n")
        while not self.search_in_command('('):
            self.append_to_file()
        self.append_to_file()
        self.compile_expression_list()
        self.append_to_file()
        self.append_to_file()  # ;
        self.write_major_tag("</doStatement>\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.write_major_tag("<letStatement>\n")
        self.append_to_file()  # let
        self.append_to_file()  # varName

        if self.search_in_command('['):
            self.append_to_file()  # (
            self.compile_expression()  # expression
            self.append_to_file()  # )

        self.append_to_file()  # =
        self.compile_expression()  # expression
        self.append_to_file()  # ;

        self.write_major_tag("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.write_major_tag("<whileStatement>\n")

        self.append_to_file()  # while
        self.append_to_file()  # (
        self.compile_expression()  # expression
        self.append_to_file()  # )
        self.append_to_file()  # {
        self.compile_statements()  # statements
        self.append_to_file()  # }

        self.write_major_tag("</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.write_major_tag("<returnStatement>\n")

        self.append_to_file()
        if not self.search_in_command(';'):
            self.compile_expression()

        self.append_to_file()
        self.write_major_tag("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.write_major_tag("<ifStatement>\n")

        self.append_to_file()  # if
        self.append_to_file()  # (
        self.compile_expression()  # expression
        self.append_to_file()  # )
        self.append_to_file()  # {
        self.compile_statements()  # statements
        self.append_to_file()  # }

        if "else" in self._tokenizer[self.ind]:
            self.append_to_file()  # else
            self.append_to_file()  # {
            self.compile_statements()  # statements
            self.append_to_file()  # }

        self.write_major_tag("</ifStatement>\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.write_major_tag("<expression>\n")
        self.compile_term()
        while self.search_in_command("+") or \
                self.search_in_command("-") or \
                self.search_in_command("*") or \
                self.search_in_command("/") or \
                self.search_in_command("&amp;") or \
                self.search_in_command("|") or \
                self.search_in_command("&lt;") or \
                self.search_in_command("&gt;") or \
                self.search_in_command("="):
            self.append_to_file()
            self.compile_term()

        self.write_major_tag("</expression>\n")

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.write_major_tag("<term>\n")

        if self.search_in_command("-") or self.search_in_command("~") \
                or self.search_in_command('^') or self.search_in_command("#"):
            self.append_to_file()
            self.compile_term()

        elif self.search_in_command("("):
            self.append_to_file()
            self.compile_expression()
            self.append_to_file()

        else:
            self.append_to_file()

            if "." in self._tokenizer[self.ind] or '(' in \
                    self._tokenizer[self.ind]:
                while not self.search_in_command('('):
                    self.append_to_file()
                self.append_to_file()
                self.compile_expression_list()
                self.append_to_file()

            elif "[" in self._tokenizer[self.ind]:
                self.append_to_file()
                self.compile_expression()
                self.append_to_file()

        self.write_major_tag("</term>\n")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.write_major_tag("<expressionList>\n")

        while not self.search_in_command(")"):
            self.compile_expression()
            if self.search_in_command(","):
                self.append_to_file()

        self.write_major_tag("</expressionList>\n")
