import inspect
import sys
import numbers
from functools import wraps


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
        if self.value in env:
            return env[self.value]
        else:
            raise SyntaxError('Unknown symbol: "%s"' % self.value)


class Nil(Lispval):
    pass


class List(Lispval):
    def display(self):
        return '(%s)' % ' '.join([x.display() for x in self.value])

    def write(self):
        return '(%s)' % ' '.join([x.write() for x in self.value])


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
    if isinstance(value, bool):
        return Bool(value)
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
        return String(value[1:-1])
    else:
        return Symbol(value)
