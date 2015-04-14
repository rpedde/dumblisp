import numbers
import math
import operator as op

from emlisp import types


def standard_environment():
    env = {}
    env.update({k: v for k, v in vars(math).iteritems() if callable(v)})
    env.update({
        '+': op.add,
        '-': op.sub,
        '*': op.mul,
        '/': op.div,
        '>': op.gt,
        '<': op.lt,
        '>=': op.ge,
        '<=': op.le,
        '=': op.eq,
        'abs': abs,
        'append': op.add,
        'apply': apply,
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'cons': lambda x, y: [x] + y,
        'eq?': op.is_,
        'equal?': op.eq,
        'length': len,
        'list': lambda *x: list(x),
        'list?': lambda x: isinstance(x, list),
        'map': map,
        'max': max,
        'min': min,
        'not': op.not_,
        'null?': lambda x: x == [],
        'number?': lambda x: isinstance(x, numbers.Number),
        'procedure?': callable,
        'round': round,
        # 'symbol?': lambda x: isinstance(x, types.Symbol)
    })

    env = {k: types.unboxedfn(v) for k, v in env.iteritems()}

    env['pi'] = types.box(math.pi)
    env['e'] = types.box(math.e)

    retval = types.Env()
    retval.update(env)
    return retval


global_env = standard_environment()
