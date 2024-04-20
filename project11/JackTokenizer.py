"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

KEYWORD_DICT = {
    'class': 'keyword', 'constructor': 'keyword',
    'function': 'keyword', 'method': 'keyword',
    'field': 'keyword', 'static': 'keyword',
    'var': 'keyword', 'int': 'keyword',
    'char': 'keyword', 'boolean': 'keyword',
    'void': 'keyword', 'true': 'keyword',
    'false': 'keyword', 'null': 'keyword',
    'this': 'keyword', 'let': 'keyword',
    'do': 'keyword', 'if': 'keyword',
    'else': 'keyword', 'while': 'keyword',
    'return': 'keyword',

}

SYMBOL_DICT = {'{': 'symbol', '}': 'symbol', '(': 'symbol', ')': 'symbol',
               '[': 'symbol', ']': 'symbol', '.': 'symbol', ',': 'symbol',
               ';': 'symbol', '+': 'symbol', '-': 'symbol', '*': 'symbol',
               '/': 'symbol', '&': 'symbol', '|': 'symbol', '<': 'symbol',
               '>': 'symbol', '=': 'symbol', '~': 'symbol', '^': 'symbol',
               '#': 'symbol'}


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self._file = input_stream
        self._input_lst = input_stream.read().splitlines()
        self._token_lst = []
        self.simplify_text()
        self._commands_ind = -1
        self._current_line = ''
        self._current_command = ''
        self.fill_token()

    def fill_token(self) -> None:
        """adds tags to the current command"""
        tag, token = '', ''
        while self.has_more_tokens():
            self.advance()
            while len(self._current_line):
                token_type = self.token_type()

                if token_type == "SYMBOL":
                    tag = self.symbol()

                elif token_type == "IDENTIFIER":
                    tag = self.identifier()

                elif token_type == "INT_CONST":
                    tag = self.int_val()

                elif token_type == "STRING_CONST":
                    tag = self.string_val()

                elif token_type == "KEYWORD":
                    tag = self.keyword().lower()
                if tag != '':
                    self._token_lst.append(tag)

    def get_token(self) -> typing.List[str]:
        """
        @return: tokenizer commands
        """
        return self._token_lst

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        self._commands_ind += 1
        return True if self._commands_ind < len(self._input_lst) else False

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true.
        Initially there is no current token.
        """
        self._current_line = self._input_lst[self._commands_ind]

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        self._current_line = self._current_line.strip()

        is_string = self._current_line.startswith('"')
        is_symbol = self._current_line[0] in SYMBOL_DICT
        is_number = self._current_line[0].isdigit()

        if is_string:
            return self.get_string_const()

        elif is_number:
            return self.get_int_const()

        elif is_symbol:
            return self.get_symbol()

        is_keyword = self.check_for_keyword()
        if is_keyword:
            return is_keyword

        return self.get_identifier()

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO",
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self._current_command.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        return self._current_command

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        return self._current_command

    def int_val(self) -> str:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        return self._current_command

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        return self._current_command

    def get_int_const(self) -> str:
        """
        slice the line from the current command and check if it's a string
        @return: the token type
        """
        k = 0
        while k < len(self._current_line) and \
                self._current_line[k].isdigit():
            k += 1
        if int(self._current_line[:k]) < 32767:
            self._current_command = self._current_line[:k]
        self._current_line = self._current_line[len(self._current_command):]
        return "INT_CONST"

    def get_string_const(self) -> str:
        """
        slice the command of the current command and check if it's a string
        @return: the token type
        """
        without_quotation_marks = self._current_line[1:].split('"', 1)[0]
        self._current_command = '"' + without_quotation_marks + '"'
        self._current_line = self._current_line[len(self._current_command):]
        return "STRING_CONST"

    def get_symbol(self) -> str:
        """
        slice the command of the current command and check if it's a symbol
        @return: the token type
        """
        self._current_command = self._current_line[0]
        self._current_line = self._current_line[1:]
        return "SYMBOL"

    def check_for_keyword(self) -> str:
        """
        slice the command of the current command and check if it's a keyword
        @return: the token type
        """
        keyword = ''
        for i, letter in enumerate(self._current_line):
            keyword += letter
            if keyword in KEYWORD_DICT:
                if len(keyword) < len(self._current_line):
                    letter_to_check = self._current_line[i + 1]
                    if letter_to_check.isalpha() or letter_to_check.isdigit() \
                            or letter_to_check == "_":
                        return ''
                self._current_command = keyword
                self._current_line = self._current_line[
                                     len(self._current_command):]
                return KEYWORD_DICT[keyword].upper()

    def get_identifier(self) -> str:
        """
        slice the command of the current command and check if its identifier
        @return: the token type
        """
        slice_line = 0
        for i, letter in enumerate(self._current_line):
            if letter == '_' or letter not in SYMBOL_DICT and letter != ' ':
                slice_line += 1
            else:
                break

        self._current_command = self._current_line[:slice_line]
        self._current_line = self._current_line[slice_line:]

        return "IDENTIFIER"

    def simplify_text(self) -> None:
        """
        remove comments, tabs and keeping the strings as they are
        """
        is_string, is_comment = False, False
        without_comments = []
        for i in range(len(self._input_lst)):
            command = ''
            line = self._input_lst[i].strip()
            line = line.replace('\t', ' ')
            j = 0
            while j < len(line):
                # start of strings
                if line[j] == '"':
                    is_string = not is_string

                # start of comment
                elif not is_string and line[j] == '/':
                    if j < len(line) - 1:
                        comment_type = line[j + 1]
                        if comment_type == '/':
                            j += 1
                            break
                        elif comment_type == '*':
                            is_comment = not is_comment

                if not is_comment:
                    command += line[j]

                # end of comment
                elif not is_string and line[j] == '*':
                    if j < len(line) - 1:
                        comment_type = line[j + 1]
                        if comment_type == '/':
                            is_comment = not is_comment
                            j += 1
                j += 1

            if command and not is_comment:
                without_comments.append(command.strip())

        self._input_lst = without_comments

