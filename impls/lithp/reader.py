"""
"""

import re

mal_re = re.compile("""[\s,]*(~@|[\[\]{}()'`~^@]|"(?:\\.|[^\\"])*"?|;.*|[^\s\[\]{}('"`,;)]*)""")
ctrl_chars = "".join(map(chr, list(range(0x00, 0x20)) + list(range(0x7f, 0xa0))))
ctrl_char_re = re.compile("[{}]".format(ctrl_chars))

class MalType(object):
    def __init__(self):
        return

    def __str__(self):
        return "MalType"


class MalList(MalType):
    def __init__(self):
        self._mal_types = []
        return

    def __str__(self):
        return "({})".format(" ".join([str(t) for t in self._mal_types]))

    def append(self, val):
        self._mal_types.append(val)
        return


class MalArray(MalType):
    def __init__(self):
        self._mal_types = []
        return

    def __str__(self):
        return "[{}]".format(" ".join([str(t) for t in self._mal_types]))

    def append(self, val):
        self._mal_types.append(val)
        return


class MalInt(MalType):
    def __init__(self, token):
        self._value = int(token)
        return

    def __str__(self):
        return str(self._value)


class MalSymbol(MalType):
    def __init__(self, token):
        self._name = str(token)
        return

    def __str__(self):
        return self._name


class MalNil(MalType):
    def __str__(self):
        return "nil"

# States
#   - 

class Reader(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.idx = 0
        return

    def __str__(self):
        return str(self.tokens)

    def peek(self):
        return self.tokens[self.idx]

    def next(self):
        tok = self.tokens[self.idx]
        self.idx += 1
        return tok

    def read_form(self):
        if self.peek() == "(":
            self.next()
            return self.read_list()
        else:
            return self.read_atom()

    def read_list(self):
        mal_list = MalList()
        while True:
            try:
                tok = self.peek()
            except IndexError:
                print("EOF")
                return MalNil()
            
            if tok == ")":
                self.next()
                break

            try:
                mal_list.append(self.read_form())
            except IndexError:
                break

        return mal_list

    def read_atom(self):
        return _parse_token(self.next())
        
    
def _parse_token(token):
    if re.match("\d+", token):
        return MalInt(token)
    else:
        return MalSymbol(token)
    
def tokenize(the_str, mal_re=mal_re):
    return mal_re.findall(the_str)

def read_str(the_str):
    r = Reader(tokenize(ctrl_char_re.sub("", the_str)))
    return r.read_form()

