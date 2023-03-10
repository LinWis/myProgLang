from MontelError import *
import string

TT_INT          = 'INT'
TT_FLOAT        = 'FLOAT'
TT_STRING       = 'STRING'
TT_IDENTIFIER   = 'IDENTIFIER' #имя переменной
TT_KEYWORD      = 'KEYWORD' #ключевые слова
TT_EOF          = 'EOF' #конец строки
TT_COMMA        = 'COMMA'
TT_ARROW        = 'ARROW'
TT_NEWLINE      = 'NEWLINE'

TT_PLUS         = 'PLUS'
TT_MINUS        = 'MINUS'
TT_MUL          = 'MUL'
TT_DIV          = 'DIV'
TT_LPAREN       = 'LPAREN' #скобки
TT_RPAREN       = 'RPAREN'
TT_LSQUARE      = 'LSQUARE'
TT_RSQUARE      = 'RSQUARE'
TT_POW          = 'POW'

TT_EQ           = 'EQ' #присвоение
TT_EE           = 'EE' #сравнение
TT_NE           = 'NE' #не равно
TT_LT           = 'LT' #меньше
TT_GT           = 'GT' #больше
TT_LTE          = 'LTE' #меньше или равно
TT_GTE          = 'GTE' #больше или равно

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

KEYWORDS = [
    'var',
    'and',
    'or',
    'not',
    'if',
    'then',
    'elif',
    'else',
    'for',
    'to',
    'step',
    'while',
    'fun',
    'end',
    'return',
    'continue',
    'break'
]


class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == "\n":
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


class Token:

    def __init__(self, type, value=None, pos_start=None, pos_end=None):
        self.type = type
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    def matches(self, type, value):
        return self.type == type and self.value == value

    def __repr__(self):
        if self.value:
            return f"{self.type}:{self.value}"
        return f"{self.type}"


class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, self.fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in (" \t"):
                self.advance()
            elif self.current_char == '#':
                self.skip_comment()
            elif self.current_char in ';\n':
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char == '"':
                tokens.append(self.make_string())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(self.make_minus_or_arrow())
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(TT_POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            elif self.current_char == '!':
                tok, error = self.make_not_equals()
                if error:
                    return [], error
                tokens.append(tok)
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1

            num_str += self.current_char
            self.advance()

        if dot_count > 0:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

        return Token(TT_INT, int(num_str), pos_start, self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

    def make_equals(self):
        tok_type = TT_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_EE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        tok_type = TT_LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_LTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        tok_type = TT_GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_GTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_minus_or_arrow(self):
        tok_type = TT_MINUS
        pos_start = self.pos.copy()

        self.advance()

        if self.current_char == '>':
            self.advance()
            tok_type = TT_ARROW

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_string(self):
        pos_start = self.pos.copy()
        self.advance()
        my_str = ''
        escape_char = False

        escape_chars = {
            'n': '\n',
            't': '\t',
        }

        while self.current_char != '"' and (self.current_char != None or escape_char):
            if escape_char:
                my_str += escape_chars.get(self.current_char, self.current_char)
                escape_char = False

            else:
                if self.current_char == '\\':
                    escape_char = True
                else:
                    my_str += self.current_char

            self.advance()


        self.advance()

        return Token(TT_STRING, my_str, pos_start, self.pos)

    def skip_comment(self):
        self.advance()

        while self.current_char != "\n":
            self.advance()

        self.advance()