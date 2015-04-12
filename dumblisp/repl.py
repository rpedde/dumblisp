import logging
from dumblisp import environment, parser


LOGGER = logging.getLogger('dumblisp.repl')


def repl(prompt='dumblisp> '):
    env = environment.standard_environment()

    while True:
        val = None

        try:
            val = environment.eval(parser.parse(raw_input(prompt)), env)

        except EOFError:
            print
            break

        except Exception as e:
            LOGGER.exception(e)
            print e

        if val is not None:
            print val.display()


if __name__ == '__main__':
    repl()
