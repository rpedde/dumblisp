import numbers
import math
import operator as op

from emlisp import types


def standard_environment():
    env = dict()
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

    env['thing'] = thing
    
    env = {k: types.unboxedfn(v) for k, v in env.iteritems()}

    env['pi'] = types.box(math.pi)
    env['e'] = types.box(math.e)

    return env


global_env = standard_environment()


def is_sym(var, what):
    return isinstance(var, types.Symbol) and var.value == what


def eval(expr, env=global_env):
    if not isinstance(expr, types.List):
        return expr.eval(env)
    if is_sym(expr.value[0], 'quote'):
        (_, exp) = expr.value
        return exp
    if is_sym(expr.value[0], 'if'):
        (_, test, conseq, otherwise) = expr.value
        exp = (conseq if eval(test, env) else otherwise)
        return eval(exp, env)
    if is_sym(expr.value[0], 'define'):
        (_, var, exp) = expr.value
        if not isinstance(var, types.Symbol):
            raise SyntaxError('Not a symbol: "%s"' % var)
        env[var.value] = eval(exp, env)
        return None
    else:
        fn = eval(expr.value[0], env)
        args = [eval(arg, env) for arg in expr.value[1:]]
        return fn(*args, env=env)
