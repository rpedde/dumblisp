import unittest
import StringIO

from emlisp import types, parser


class ParserTest(unittest.TestCase):
    def test_box(self):
        assert isinstance(types.box(3), types.Numeric)
        assert isinstance(types.box(2.0), types.Numeric)
        assert isinstance(types.box(False), types.Bool)
        assert isinstance(types.box([]), types.List)
        assert isinstance(types.box('foo'), types.String)
        with self.assertRaises(SyntaxError):
            types.box({'foo': 1})

        res = types.box([1, '2', 3.0, False, [1]])
        assert isinstance(res, types.List)
        assert isinstance(res.value[0], types.Numeric)
        assert isinstance(res.value[1], types.String)
        assert isinstance(res.value[2], types.Numeric)
        assert isinstance(res.value[3], types.Bool)
        assert isinstance(res.value[4], types.List)

    def test_display(self):
        assert types.box(3).display() == '3'
        assert types.box(3).write() == '3'
        assert types.box('1').display() == '"1"'
        assert types.box('1').write() == '1'
        assert types.box(True).display() == '#t'
        assert types.box(True).write() == '#t'

    def test_unboxing_decorator(self):
        @types.unboxedfn
        def test_fn(arg):
            assert isinstance(arg, int)
            assert arg == 3

            return True

        val = types.box(3)
        result = test_fn(val)

        assert isinstance(result, types.Bool)
        assert result.value is True

    def test_atomize(self):
        assert isinstance(types.atomize('3'), types.Numeric)
        assert types.atomize('3').value == 3
        assert isinstance(types.atomize('#t'), types.Bool)
        assert isinstance(types.atomize('#f'), types.Bool)
        assert types.atomize('#t').value is True
        assert types.atomize('#f').value is False
        assert isinstance(types.atomize('2.0'), types.Numeric)
        assert types.atomize('2.0').value == 2.0
        assert isinstance(types.atomize('"x"'), types.String)
        assert types.atomize('"x"').value == 'x'
        assert isinstance(types.atomize('x'), types.Symbol)
        assert types.atomize('x').value == 'x'

    def test_symbol_eval(self):
        env = {'x': types.box(3)}
        symbol = types.atomize("x")

        res = symbol.eval(env)
        assert isinstance(res, types.Numeric)
        assert res.value == 3

    # enough types, now test parser
    def test_parser(self):
        def fileio(buffer):
            return types.InPort(StringIO.StringIO(buffer))

        res = parser.read(fileio('3'))
        assert isinstance(res, types.Numeric)
        assert res.value == 3

        res = parser.read(fileio('(quote (1 2 3))'))
        assert isinstance(res, types.List)
        assert len(res.value) == 2
        assert isinstance(res.value[0], types.Symbol)
        assert isinstance(res.value[1], types.List)

        with self.assertRaises(SyntaxError):
            parser.read(fileio('(quote'))

        res = parser.read(fileio(''))
        assert res is types.eof_object

        with self.assertRaises(SyntaxError):
            parser.read(fileio(')'))
