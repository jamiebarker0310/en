# Natural Language Toolkit: Logic
#
# Based on church.py, Version 1.0
# Available from http://www.alcyone.com/pyos/church/
# Copyright (C) 2001-2002 Erik Max Francis
# Author: Erik Max Francis <max@alcyone.com>
#
# Modifications by: Steven Bird <sb@csse.unimelb.edu.au>
#                   Peter Wang
#                   Ewan Klein <ewan@inf.ed.ac.uk>
# URL: <http://nltk.sf.net>
# For license information, see LICENSE.TXT
#
# $Iid:$

"""
A version of first order logic, built on top of the untyped lambda calculus.

The class of C{Expression} has various subclasses:

  - C{VariableExpression}

"""

from en.parser.nltk_lite.utilities import Counter


class Error(Exception):
    pass


class Variable:
    """A variable, either free or bound."""

    def __init__(self, name):
        """
        Create a new C{Variable}.

        @type name: C{string}
        @param name: The name of the variable.
        """
        self.name = name

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self.equals(other)

    def equals(self, other):
        """A comparison function."""
        assert isinstance(other, Variable)
        return self.name == other.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Variable('%s')" % self.name

    def __hash__(self):
        return hash(repr(self))


class Constant:
    """A nonlogical constant."""

    def __init__(self, name):
        """
        Create a new C{Constant}.

        @type name: C{string}
        @param name: The name of the constant.
        """
        self.name = name

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self.equals(other)

    def equals(self, other):
        """A comparison function."""
        assert isinstance(other, Constant)
        return self.name == other.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Constant('%s')" % self.name

    def __hash__(self):
        return hash(repr(self))


class Expression:
    """The abstract class of a lambda calculus expression."""

    def __init__(self):
        if self.__class__ is Expression:
            raise NotImplementedError

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self.equals(other)

    def equals(self, other):
        """Are the two expressions equal, modulo alpha conversion?"""
        return NotImplementedError

    def variables(self):
        """Set of all variables."""
        raise NotImplementedError

    def free(self):
        """Set of free variables."""
        raise NotImplementedError

    def subterms(self):
        """Set of all subterms (including self)."""
        raise NotImplementedError

    def replace(self, variable, expression):
        """Replace all instances of variable v with expression E in self,
        where v is free in self."""
        raise NotImplementedError

    def simplify(self):
        """Evaluate the form by repeatedly applying applications."""
        raise NotImplementedError

    def skolemise(self):
        """
        Perform a simple Skolemisation operation.  Existential quantifiers are
        simply dropped and all variables they introduce are renamed so that
        they are unique.
        """
        return self._skolemise(set(), Counter())

    def _skolemise(self, bound_vars, counter):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError


class VariableExpression(Expression):
    """A variable expression which consists solely of a variable."""

    def __init__(self, variable):
        Expression.__init__(self)
        assert isinstance(variable, Variable)
        self.variable = variable

    def equals(self, other):
        """
        Allow equality between instances of C{VariableExpression} and
        C{IndVariableExpression.
        """
        if isinstance(self, VariableExpression) and isinstance(
            other, VariableExpression
        ):
            return self.variable.equals(other.variable)
        else:
            return False

    def variables(self):
        return set([self.variable])

    def free(self):
        return set([self.variable])

    def subterms(self):
        return set([self])

    def replace(self, variable, expression):
        if self.variable.equals(variable):
            return expression
        else:
            return self

    def simplify(self):
        return self

    def infixify(self):
        return self

    def name(self):
        return self.__str__()

    def _skolemise(self, bound_vars, counter):
        return self

    def __str__(self):
        return "%s" % self.variable

    def __repr__(self):
        return "VariableExpression('%s')" % self.variable

    def __hash__(self):
        return hash(repr(self))


def is_indvar(expr):
    """
    Check whether an expression has the form of an individual variable.

    An individual variable matches the following regex:
    C{'^[wxyz](\\d*)'}.

    @rtype: Boolean
    @param expr: String
    """
    result = expr[0] in ["w", "x", "y", "z"]
    if len(expr) > 1:
        return result and expr[1:].isdigit()
    else:
        return result


class IndVariableExpression(VariableExpression):
    """
    An individual variable expression, as determined by C{is_indvar()}.
    """

    def __init__(self, variable):
        Expression.__init__(self)
        assert isinstance(variable, Variable), "Not a Variable: %s" % variable
        assert is_indvar(str(variable)), (
            "Wrong format for an Individual Variable: %s" % variable
        )
        self.variable = variable

    def __repr__(self):
        return "IndVariableExpression('%s')" % self.variable


class ConstantExpression(Expression):
    """A constant expression, consisting solely of a constant."""

    def __init__(self, constant):
        Expression.__init__(self)
        assert isinstance(constant, Constant)
        self.constant = constant

    def equals(self, other):
        if self.__class__ == other.__class__:
            return self.constant.equals(other.constant)
        else:
            return False

    def variables(self):
        return set()

    def free(self):
        return set()

    def subterms(self):
        return set([self])

    def replace(self, variable, expression):
        return self

    def simplify(self):
        return self

    def infixify(self):
        return self

    def name(self):
        return self.__str__()

    def _skolemise(self, bound_vars, counter):
        return self

    def __str__(self):
        return "%s" % self.constant

    def __repr__(self):
        return "ConstantExpression('%s')" % self.constant

    def __hash__(self):
        return hash(repr(self))


class Operator(ConstantExpression):
    """
    A boolean operator, such as 'not' or 'and', or the equality
    relation ('=').
    """

    def __init__(self, operator):
        Expression.__init__(self)
        assert operator in Parser.OPS
        self.constant = operator
        self.operator = operator

    def equals(self, other):
        if self.__class__ == other.__class__:
            return self.constant == other.constant
        else:
            return False

    def simplify(self):
        return self

    def __str__(self):
        return "%s" % self.operator

    def __repr__(self):
        return "Operator('%s')" % self.operator


class VariableBinderExpression(Expression):
    """A variable binding expression: e.g. \\x.M."""

    # for generating "unique" variable names during alpha conversion.
    _counter = Counter()

    def __init__(self, variable, term):
        Expression.__init__(self)
        assert isinstance(variable, Variable)
        assert isinstance(term, Expression)
        self.variable = variable
        self.term = term
        self.prefix = self.__class__.PREFIX.rstrip()
        self.binder = (self.prefix, self.variable.name)
        self.body = str(self.term)

    def equals(self, other):
        r"""
        Defines equality modulo alphabetic variance.

        If we are comparing \x.M  and \y.N, then
        check equality of M and N[x/y].
        """
        if self.__class__ == other.__class__:
            if self.variable == other.variable:
                return self.term == other.term
            else:
                # Comparing \x.M  and \y.N.
                # Relabel y in N with x and continue.
                relabeled = self._relabel(other)
                return self.term == relabeled
        else:
            return False

    def _relabel(self, other):
        """
        Relabel C{other}'s bound variables to be the same as C{self}'s
        variable.
        """
        var = VariableExpression(self.variable)
        return other.term.replace(other.variable, var)

    def variables(self):
        return set([self.variable]).union(self.term.variables())

    def free(self):
        return self.term.free().difference(set([self.variable]))

    def subterms(self):
        return self.term.subterms().union([self])

    def replace(self, variable, expression):
        if self.variable == variable:
            return self
        if self.variable in expression.free():
            v = "z" + str(self._counter.get())
            self = self.alpha_convert(Variable(v))
        return self.__class__(self.variable, self.term.replace(variable, expression))

    def alpha_convert(self, newvar):
        """
        Rename all occurrences of the variable introduced by this variable
        binder in the expression to @C{newvar}.
        """
        term = self.term.replace(self.variable, VariableExpression(newvar))
        return self.__class__(newvar, term)

    def simplify(self):
        return self.__class__(self.variable, self.term.simplify())

    def infixify(self):
        return self.__class__(self.variable, self.term.infixify())

    def __str__(self, continuation=0):
        # Print \x.\y.M as \x y.M.
        if continuation:
            prefix = " "
        else:
            prefix = self.__class__.PREFIX
        if self.term.__class__ == self.__class__:
            return "%s%s%s" % (prefix, self.variable, self.term.__str__(1))
        else:
            return "%s%s.%s" % (prefix, self.variable, self.term)

    def __hash__(self):
        return hash(repr(self))


class LambdaExpression(VariableBinderExpression):
    """A lambda expression: \\x.M."""

    PREFIX = "\\"

    def _skolemise(self, bound_vars, counter):
        bv = bound_vars.copy()
        bv.add(self.variable)
        return self.__class__(self.variable, self.term._skolemise(bv, counter))

    def __repr__(self):
        return "LambdaExpression('%s', '%s')" % (self.variable, self.term)


class SomeExpression(VariableBinderExpression):
    """An existential quantification expression: some x.M."""

    PREFIX = "some "

    def _skolemise(self, bound_vars, counter):
        if self.variable in bound_vars:
            var = Variable("_s" + str(counter.get()))
            term = self.term.replace(self.variable, VariableExpression(var))
        else:
            var = self.variable
            term = self.term
        bound_vars.add(var)
        return term._skolemise(bound_vars, counter)

    def __repr__(self):
        return "SomeExpression('%s', '%s')" % (self.variable, self.term)


class AllExpression(VariableBinderExpression):
    """A universal quantification expression: all x.M."""

    PREFIX = "all "

    def _skolemise(self, bound_vars, counter):
        bv = bound_vars.copy()
        bv.add(self.variable)
        return self.__class__(self.variable, self.term._skolemise(bv, counter))

    def __repr__(self):
        return "AllExpression('%s', '%s')" % (self.variable, self.term)


class ApplicationExpression(Expression):
    """An application expression: (M N)."""

    def __init__(self, first, second):
        Expression.__init__(self)
        assert isinstance(first, Expression)
        assert isinstance(second, Expression)
        self.first = first
        self.second = second

    def equals(self, other):
        if self.__class__ == other.__class__:
            return self.first.equals(other.first) and self.second.equals(other.second)
        else:
            return False

    def variables(self):
        return self.first.variables().union(self.second.variables())

    def free(self):
        return self.first.free().union(self.second.free())

    def _functor(self):
        if isinstance(self.first, ApplicationExpression):
            return self.first._functor()
        else:
            return self.first

    fun = property(_functor, doc="Every ApplicationExpression has a functor.")

    def _operator(self):
        functor = self._functor()
        if isinstance(functor, Operator):
            return str(functor)
        else:
            raise AttributeError

    op = property(_operator, doc="Only some ApplicationExpressions have operators.")

    def _arglist(self):
        """Uncurry the argument list."""
        arglist = [str(self.second)]
        if isinstance(self.first, ApplicationExpression):
            arglist.extend(self.first._arglist())
        return arglist

    def _args(self):
        arglist = self._arglist()
        arglist.reverse()
        return arglist

    args = property(_args, doc="Every ApplicationExpression has args.")

    def subterms(self):
        first = self.first.subterms()

        second = self.second.subterms()
        return first.union(second).union(set([self]))

    def replace(self, variable, expression):
        return self.__class__(
            self.first.replace(variable, expression),
            self.second.replace(variable, expression),
        )

    def simplify(self):
        first = self.first.simplify()
        second = self.second.simplify()
        if isinstance(first, LambdaExpression):
            variable = first.variable
            term = first.term
            return term.replace(variable, second).simplify()
        else:
            return self.__class__(first, second)

    def infixify(self):
        first = self.first.infixify()
        second = self.second.infixify()
        if isinstance(first, Operator) and not str(first) == "not":
            return self.__class__(second, first)
        else:
            return self.__class__(first, second)

    def _skolemise(self, bound_vars, counter):
        first = self.first._skolemise(bound_vars, counter)
        second = self.second._skolemise(bound_vars, counter)
        return self.__class__(first, second)

    def __str__(self):
        # Print ((M N) P) as (M N P).
        strFirst = str(self.first)
        if isinstance(self.first, ApplicationExpression):
            if not isinstance(self.second, Operator):
                strFirst = strFirst[1:-1]
        return "(%s %s)" % (strFirst, self.second)

    def __repr__(self):
        return "ApplicationExpression('%s', '%s')" % (self.first, self.second)

    def __hash__(self):
        return hash(repr(self))


class Parser:
    """A lambda calculus expression parser."""

    # Tokens.
    LAMBDA = "\\"
    SOME = "some"
    ALL = "all"
    DOT = "."
    OPEN = "("
    CLOSE = ")"
    BOOL = ["and", "or", "not", "implies", "iff"]
    EQ = "="
    OPS = BOOL
    OPS.append(EQ)

    def __init__(self, data=None, constants=None):
        if data is not None:
            self.buffer = data
            self.process()
        else:
            self.buffer = ""
        if constants is not None:
            self.constants = constants
        else:
            self.constants = []

    def feed(self, data):
        """Feed another batch of data to the parser."""
        self.buffer += data
        self.process()

    def parse(self, data):
        """
        Provides a method similar to other NLTK parsers.

        @type data: str
        @returns: a parsed Expression
        """
        self.feed(data)
        result = next(self)
        return result

    def process(self):
        """Process the waiting stream to make it trivial to parse."""
        self.buffer = self.buffer.replace("\t", " ")
        self.buffer = self.buffer.replace("\n", " ")
        self.buffer = self.buffer.replace("\\", " \\ ")
        self.buffer = self.buffer.replace(".", " . ")
        self.buffer = self.buffer.replace("(", " ( ")
        self.buffer = self.buffer.replace(")", " ) ")

    def token(self, destructive=1):
        """Get the next waiting token.  The destructive flag indicates
        whether the token will be removed from the buffer; setting it to
        0 gives lookahead capability."""
        if self.buffer == "":
            raise Error("end of stream")
        tok = None
        buffer = self.buffer
        while not tok:
            seq = buffer.split(" ", 1)
            if len(seq) == 1:
                tok, buffer = seq[0], ""
            else:
                assert len(seq) == 2
                tok, buffer = seq
            if tok:
                if destructive:
                    self.buffer = buffer
                return tok
        assert 0  # control never gets here
        return None

    def isVariable(self, token):
        """Is this token a variable (that is, not one of the other types)?"""
        TOKENS = [
            Parser.LAMBDA,
            Parser.SOME,
            Parser.ALL,
            Parser.DOT,
            Parser.OPEN,
            Parser.CLOSE,
            Parser.EQ,
        ]
        TOKENS.extend(self.constants)
        TOKENS.extend(Parser.BOOL)
        return token not in TOKENS

    def __next__(self):
        """Parse the next complete expression from the stream and return it."""
        tok = self.token()

        if tok in [Parser.LAMBDA, Parser.SOME, Parser.ALL]:
            # Expression is a lambda expression: \x.M
            # or a some expression: some x.M
            if tok == Parser.LAMBDA:
                factory = LambdaExpression
            elif tok == Parser.SOME:
                factory = SomeExpression
            elif tok == Parser.ALL:
                factory = AllExpression
            else:
                raise ValueError(tok)

            vars = [self.token()]
            while self.isVariable(self.token(0)):
                # Support expressions like: \x y.M == \x.\y.M
                # and: some x y.M == some x.some y.M
                vars.append(self.token())
            tok = self.token()

            if tok != Parser.DOT:
                raise Error("parse error, unexpected token: %s" % tok)
            term = next(self)
            accum = factory(Variable(vars.pop()), term)
            while vars:
                accum = factory(Variable(vars.pop()), accum)
            return accum

        elif tok == Parser.OPEN:
            # Expression is an application expression: (M N)
            first = next(self)
            second = next(self)
            exps = []
            while self.token(0) != Parser.CLOSE:
                # Support expressions like: (M N P) == ((M N) P)
                exps.append(next(self))
            tok = self.token()  # swallow the close token
            assert tok == Parser.CLOSE
            if isinstance(second, Operator):
                accum = self.make_ApplicationExpression(second, first)
            else:
                accum = self.make_ApplicationExpression(first, second)
            while exps:
                exp, exps = exps[0], exps[1:]
                accum = self.make_ApplicationExpression(accum, exp)
            return accum

        elif tok in self.constants:
            # Expression is a simple constant expression: a
            return ConstantExpression(Constant(tok))

        elif tok in Parser.OPS:
            # Expression is a boolean operator or the equality symbol
            return Operator(tok)

        elif is_indvar(tok):
            # Expression is a boolean operator or the equality symbol
            return IndVariableExpression(Variable(tok))

        else:
            if self.isVariable(tok):
                # Expression is a simple variable expression: x
                return VariableExpression(Variable(tok))
            else:
                raise Error("parse error, unexpected token: %s" % tok)

    # This is intended to be overridden, so that you can derive a Parser class
    # that constructs expressions using your subclasses.  So far we only need
    # to overridde ApplicationExpression, but the same thing could be done for
    # other expression types.
    def make_ApplicationExpression(self, first, second):
        return ApplicationExpression(first, second)


def expressions():
    """Return a sequence of test expressions."""
    a = Variable("a")
    x = Variable("x")
    y = Variable("y")
    z = Variable("z")
    A = VariableExpression(a)
    X = IndVariableExpression(x)
    Y = IndVariableExpression(y)
    Z = IndVariableExpression(z)
    XA = ApplicationExpression(X, A)
    XY = ApplicationExpression(X, Y)
    XZ = ApplicationExpression(X, Z)
    YZ = ApplicationExpression(Y, Z)
    XYZ = ApplicationExpression(XY, Z)
    I = LambdaExpression(x, X)
    K = LambdaExpression(x, LambdaExpression(y, X))
    L = LambdaExpression(x, XY)
    S = LambdaExpression(
        x, LambdaExpression(y, LambdaExpression(z, ApplicationExpression(XZ, YZ)))
    )
    B = LambdaExpression(
        x, LambdaExpression(y, LambdaExpression(z, ApplicationExpression(X, YZ)))
    )
    C = LambdaExpression(
        x, LambdaExpression(y, LambdaExpression(z, ApplicationExpression(XZ, Y)))
    )
    O = LambdaExpression(x, LambdaExpression(y, XY))
    N = ApplicationExpression(LambdaExpression(x, XA), I)
    T = next(Parser("\\x y.(x y z)"))
    return [X, XZ, XYZ, I, K, L, S, B, C, O, N, T]


def main():
    p = Variable("p")
    q = Variable("q")
    P = VariableExpression(p)
    Q = VariableExpression(q)
    for l in expressions():
        print("Expression:", l)
        print("Variables:", l.variables())
        print("Free:", l.free())
        print("Subterms:", l.subterms())
        print("Simplify:", l.simplify())
        la = ApplicationExpression(ApplicationExpression(l, P), Q)
        las = la.simplify()
        print("Apply and simplify: %s -> %s" % (la, las))
        ll = next(Parser(str(l)))
        print("l is:", l)
        print("ll is:", ll)
        assert l.equals(ll)
        print("Serialize and reparse: %s -> %s" % (l, ll))
        print()


def runtests():
    # Test a beta-reduction which used to be wrong
    l = Parser(r"(\x.\x.(x x) 1)").next().simplify()
    id = next(Parser(r"\x.(x x)"))
    assert l == id

    # Test numerals
    zero = next(Parser(r"\f x.x"))
    one = next(Parser(r"\f x.(f x)"))
    two = next(Parser(r"\f x.(f (f x))"))
    three = next(Parser(r"\f x.(f (f (f x)))"))
    four = next(Parser(r"\f x.(f (f (f (f x))))"))
    succ = next(Parser(r"\n f x.(f (n f x))"))
    plus = next(Parser(r"\m n f x.(m f (n f x))"))
    mult = next(Parser(r"\m n f.(m (n f))"))
    pred = next(Parser(r"\n f x.(n \g h.(h (g f)) \u.x \u.u)"))
    v1 = ApplicationExpression(succ, zero).simplify()
    assert v1 == one
    v2 = ApplicationExpression(succ, v1).simplify()
    assert v2 == two
    v3 = ApplicationExpression(ApplicationExpression(plus, v1), v2).simplify()
    assert v3 == three
    v4 = ApplicationExpression(ApplicationExpression(mult, v2), v2).simplify()
    assert v4 == four
    v5 = ApplicationExpression(pred, ApplicationExpression(pred, v4)).simplify()
    assert v5 == two

    # betaConversionTestSuite.pl from
    # _Representation and Inference for Natural Language_
    #
    x1 = Parser(r"(\p.(p mia) \x.(walk x))").next().simplify()
    x2 = Parser(r"(walk mia)").next().simplify()
    assert x1 == x2

    x1 = (
        Parser(r"some x.(and (man x) (\p.some x.(and (woman x) (p x)) \y.(love x y)))")
        .next()
        .simplify()
    )
    x2 = (
        Parser(r"some x.(and (man x) some y.(and (woman y) (love x y)))")
        .next()
        .simplify()
    )
    assert x1 == x2

    x1 = Parser(r"(\a.(sleep a) mia)").next().simplify()
    x2 = Parser(r"(sleep mia)").next().simplify()
    assert x1 == x2

    x1 = Parser(r"(\a.\b.(like b a) mia)").next().simplify()
    x2 = Parser(r"\b.(like b mia)").next().simplify()
    assert x1 == x2

    x1 = Parser(r"\a.(\b.(like b a) vincent)").next().simplify()
    x2 = Parser(r"\a.(like vincent a)").next().simplify()
    assert x1 == x2

    x1 = Parser(r"\a.(and (\b.(like b a) vincent) (sleep a))").next().simplify()
    x2 = Parser(r"\a.(and (like vincent a) (sleep a))").next().simplify()
    assert x1 == x2

    x1 = Parser(r"(\a.\b.(like b a) mia vincent)").next().simplify()
    x2 = Parser(r"(like vincent mia)").next().simplify()
    assert x1 == x2

    x1 = Parser(r"(p (\a.(sleep a) vincent))").next().simplify()
    x2 = Parser(r"(p (sleep vincent))").next().simplify()
    assert x1 == x2

    x1 = Parser(r"\a.(a (\b.(sleep b) vincent))").next().simplify()
    x2 = Parser(r"\a.(a (sleep vincent))").next().simplify()
    assert x1 == x2

    x1 = Parser(r"\a.(a (sleep vincent))").next().simplify()
    x2 = Parser(r"\a.(a (sleep vincent))").next().simplify()
    assert x1 == x2

    x1 = Parser(r"(\a.(a vincent) \b.(sleep b))").next().simplify()
    x2 = Parser(r"(sleep vincent)").next().simplify()
    assert x1 == x2

    x1 = Parser(r"(\a.(believe mia (a vincent)) \b.(sleep b))").next().simplify()
    x2 = Parser(r"(believe mia (sleep vincent))").next().simplify()
    assert x1 == x2

    x1 = Parser(r"(\a.(and (a vincent) (a mia)) \b.(sleep b))").next().simplify()
    x2 = Parser(r"(and (sleep vincent) (sleep mia))").next().simplify()
    assert x1 == x2

    x1 = (
        Parser(
            r"(\a.\b.(and (\c.(c (a vincent)) \d.(probably d)) (\c.(c (b mia)) \d.(improbably d))) \e.(walk e) \e.(talk e)))"
        )
        .next()
        .simplify()
    )
    x2 = (
        Parser(r"(and (probably (walk vincent)) (improbably (talk mia)))")
        .next()
        .simplify()
    )
    assert x1 == x2

    x1 = Parser(r"(\a.\b.(\c.(c a b) \d.\e.(love d e)) jules mia)").next().simplify()
    x2 = Parser(r"(love jules mia)").next().simplify()
    assert x1 == x2

    x1 = (
        Parser(r"(\a.\b.some c.(and (a c) (b c)) \d.(boxer d) \d.(sleep d))")
        .next()
        .simplify()
    )
    x2 = Parser(r"some c.(and (boxer c) (sleep c))").next().simplify()
    assert x1 == x2

    x1 = Parser(r"(\a.(z a) \c.\a.(like a c))").next().simplify()
    x2 = Parser(r"(z \c.\a.(like a c))").next().simplify()
    assert x1 == x2

    x1 = Parser(r"(\a.\b.(a b) \c.\b.(like b c))").next().simplify()
    x2 = Parser(r"\b.(\c.\b.(like b c) b)").next().simplify()
    assert x1 == x2

    x1 = Parser(r"(\a.\b.(\c.(c a b) \b.\a.(loves b a)) jules mia)").next().simplify()
    x2 = Parser(r"(loves jules mia)").next().simplify()
    assert x1 == x2

    x1 = (
        Parser(r"(\a.\b.(and some b.(a b) (a b)) \c.(boxer c) vincent)")
        .next()
        .simplify()
    )
    x2 = Parser(r"(and some b.(boxer b) (boxer vincent))").next().simplify()
    assert x1 == x2


if __name__ == "__main__":
    runtests()
    main()
