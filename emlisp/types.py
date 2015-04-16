import inspect
import re
import numbers
import readline

from functools import wraps


class Env(dict):
    def __init__(self, parms=None, args=None, outer=None):
        self.outer = outer
        if isinstance(parms, Symbol):
            self.update({parms.value: args})
        else:
            if parms or args:
                if not (parms and args) or (len(parms.value) != len(args.value)):
                    raise TypeError('expected %s, given %s' % (
                        parms.display(), args.display()))
                adds = zip([x.value for x in parms.value],
                           [x for x in args.value])
                self.update(adds)

    def find(self, var):
        if var in self:
            return self
        elif self.outer is None:
            raise LookupError(var)
        else:
            return self.outer.find(var)


class Lispval(object):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return self

    def display(self):
        return self.write()

    def write(self):
        return '%s' % self.value

    def __str__(self):
        return self.display()


class Numeric(Lispval):
    pass


class Bool(Lispval):
    def write(self):
        if self.value:
            return '#t'
        else:
            return '#f'


class String(Lispval):
    def display(self):
        return '"%s"' % self.value


class Symbol(Lispval):
    def eval(self, env):
        return env.find(self.value)[self.value]


class Nil(Lispval):
    def display(self):
        return '()'


class List(Lispval):
    def display(self):
        return '(%s)' % ' '.join([x.display() for x in self.value])

    def write(self):
        return '(%s)' % ' '.join([x.write() for x in self.value])


class Lambda(Lispval):
    def __init__(self, parms, exp, env):
        self.parms = parms
        self.exp = exp
        self.env = env

    def write(self):
        return '<lambda: %s>' % id(self)

    def __call__(self, *args, **kwargs):
        return eval(self.exp, Env(self.parms, List(args), self.env))


class InPort(Lispval):
    matcher = r'''\s*(,@|[('`,)]|"(?:[\\].|[^\\"])*"|;.*|[^\s('"`,;)]*)(.*)'''

    def __init__(self, fileio, prompt='emlisp>'):
        self.value = fileio
        self.line = ''
        self.prompt = prompt
        self.continuation = False

    def display(self):
        if self.value is None:
            return 'Port: readline'
        else:
            return 'Port: %s' % self.value

    def read_line(self):
        if self.value is None:
            try:
                if self.continuation is False:
                    self.line = raw_input(self.prompt)
                else:
                    self.line = raw_input(self.prompt.replace('>', '-'))

            except EOFError:
                self.line = ''
        else:
            self.line = self.value.readline()

    def next_token(self):
        while True:
            if self.line == '':
                self.read_line()
            if self.line == '':
                return eof_object
            token, self.line = re.match(InPort.matcher, self.line).groups()
            if token != '' and not token.startswith(';'):
                return token


def unboxedfn(fn):
    needs_env = False
    try:
        fn_args = inspect.getargspec(fn)
        if fn_args[0] and 'env' in fn_args[0]:
            needs_env = True
    except TypeError:
        # build-in or c function
        pass

    @wraps(fn)
    def wrapped(*args, **kwargs):
        args = unbox(args)
        if needs_env:
            retval = fn(*args, env=kwargs['env'])
        else:
            retval = fn(*args)
        return box(retval)

    return wrapped


def unbox(value):
    """unbox a lisp type"""
    if isinstance(value, Numeric) or \
       isinstance(value, Bool) or \
       isinstance(value, String):
        return value.value

    if isinstance(value, Nil):
        return None

    if isinstance(value, List):
        return [unbox(x) for x in value.value]

    if isinstance(value, tuple) or isinstance(value, list):
        return [unbox(x) for x in value]

    raise SyntaxError('Cannot unbox type "%s"' % value.__class__.__name__)


def unboxenv(env, key):
    if env.get(key) is None:
        return Nil()

    return env.get(key).value


def box(value):
    """ box a python native type """
    if value is None:
        return nil_object
    if isinstance(value, bool):
        if value:
            return true_object
        return false_object
    elif isinstance(value, numbers.Number):
        return Numeric(value)
    elif isinstance(value, list):
        return List([box(x) for x in value])
    elif isinstance(value, basestring):
        return String(value)
    else:
        raise SyntaxError('Cannot box value "%s"' % value)


def atomize(value):
    """turn a string representation of a lisp type into a boxed type"""
    try:
        return Numeric(int(value))
    except:
        pass

    try:
        return Numeric(float(value))
    except:
        pass

    if value == '#t':
        return Bool(True)

    if value == '#f':
        return Bool(False)

    if value[0] == '"' and value[-1] == '"':
        return String(value[1:-1].decode('string_escape'))
    else:
        return Symbol(value)


def is_sym(var, what):
    return isinstance(var, Symbol) and var.value == what


def eval(expr, env):
    if not isinstance(expr, List):
        return expr.eval(env)
    if is_sym(expr.value[0], 'quote'):
        (_, exp) = expr.value
        return exp
    if is_sym(expr.value[0], 'if'):
        (_, test, conseq, otherwise) = expr.value
        exp = (conseq if eval(test, env) else otherwise)
        return eval(exp, env)
    if is_sym(expr.value[0], 'set!'):
        (_, var, exp) = expr.value
        if not isinstance(var, Symbol):
            raise SyntaxError('Not a symbol: "%s"' % var)
        env.find(var.value)[var.value] = eval(exp, env)
        return nil_object
    if is_sym(expr.value[0], 'define'):
        (_, var, exp) = expr.value
        if not isinstance(var, Symbol):
            raise SyntaxError('Not a symbol: "%s"' % var)
        env[var.value] = eval(exp, env)
        return nil_object
    if is_sym(expr.value[0], 'lambda'):
        (_, vars, exp) = expr.value
        return Lambda(vars, exp, env)
        return nil_object
    else:
        args = [eval(arg, env) for arg in expr.value]
        fn = args.pop(0)
        return fn(*args, env=env)


eof_object = Symbol('#eof')
true_object = Bool(True)
false_object = Bool(False)
nil_object = Nil(None)
