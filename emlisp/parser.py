from emlisp import types


def parse(program):
    retval = read_from_tokens(tokenize(program))
    return retval


def read_from_tokens(tokens):
    if len(tokens) == 0:
        raise SyntaxError('Unexpected EOF')
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)
        return types.List(L)
    elif token == ')':
        raise SyntaxError('Unexpected )')
    else:
        return types.atomize(token)


def tokenize(chars):
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()
