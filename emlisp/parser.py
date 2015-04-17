import os
import sys
import logging
import readline
import traceback

from emlisp import types, environment

LOGGER = logging.getLogger('emlisp.parser')
HISTORY_FILENAME = '$HOME/.emlisp-history'

quotes = {"'": types.Symbol('quote'),
          '`': types.Symbol('quasiquote'),
          ',': types.Symbol('unquote'),
          ',@': types.Symbol('unquote-splicing')}


def readchar(inport):
    if inport.line != '':
        inport.read_line()
    ch, inport.line = inport.line[0], inport.line[1:]
    return ch


def read(inport):
    def read_ahead(token):
        if token == '(':
            L = []
            while True:
                token = inport.next_token()
                if token == ')':
                    return types.List(L)
                else:
                    L.append(read_ahead(token))
        elif token == ')':
            raise SyntaxError('Unexpected ")"')
        elif token in quotes:
            return types.List([quotes[token], read(inport)])
        elif token is types.eof_object:
            raise SyntaxError('Unexpected EOF in list')
        else:
            return types.atomize(token)

    inport.continuation = False
    token1 = inport.next_token()
    inport.continuation = True

    if token1 is types.eof_object:
        return types.eof_object
    return read_ahead(token1)


def load(filename, env):
    with open(filename, 'r') as f:
        inport = types.InPort(f)
        x = read(inport)
        while x is not types.eof_object:
            types.eval(x, env)
            x = read(inport)


def repl(prompt='emlisp> ', env=None, inport=None, out=sys.stdout):
    if os.path.exists(os.path.expandvars(HISTORY_FILENAME)):
        readline.read_history_file(os.path.expandvars(HISTORY_FILENAME))

    # if env is None:
    #     env = environment.standard_environment()

    if inport is None:
        inport = types.InPort(None, prompt=prompt)

    while True:
        try:
            val = None

            x = read(inport)
            if x is types.eof_object:
                if out:
                    print >> out, '\n'
                readline.write_history_file(os.path.expandvars(
                    HISTORY_FILENAME))
                return

            val = types.eval(x, env)

            if val is not types.nil_object and out:
                print >> out, val.display()

        except Exception as e:
            print '%s: %s' % (type(e).__name__, e)
            if '*debug*' in env:
                traceback.print_exc()

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    repl()
