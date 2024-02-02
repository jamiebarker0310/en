class ParseI(object):
    """
    A processing class for deriving trees that represent possible
    structures for a sequence of tokens.  These tree structures are
    known as X{parses}.  Typically, parsers are used to derive syntax
    trees for sentences.  But parsers can also be used to derive other
    kinds of tree structure, such as morphological trees and discourse
    structures.

    """

    def parse(self, sent):
        """
        Derive a parse tree that represents the structure of the given
        sentences words, and return a Tree.  If no parse is found,
        then output C{None}.  If multiple parses are found, then
        output the best parse.

        The parsed trees derive a structure for the subtokens, but do
        not modify them.  In particular, the leaves of the subtree
        should be equal to the list of subtokens.

        @param sent: The sentence to be parsed
        @type sent: L{list} of L{string}
        """
        raise NotImplementedError()

    def get_parse(self, sent):
        """
        @return: A parse tree that represents the structure of the
        sentence.  If no parse is found, then return C{None}.

        @rtype: L{Tree}
        @param sent: The sentence to be parsed
        @type sent: L{list} of L{string}
        """

    def get_parse_list(self, sent):
        """
        @return: A list of the parse trees for the sentence.  When possible,
        this list should be sorted from most likely to least likely.

        @rtype: C{list} of L{Tree}
        @param sent: The sentence to be parsed
        @type sent: L{list} of L{string}
        """

    def get_parse_probs(self, sent):
        """
        @return: A probability distribution over the parse trees for the sentence.

        @rtype: L{ProbDistI}
        @param sent: The sentence to be parsed
        @type sent: L{list} of L{string}
        """

    def get_parse_dict(self, sent):
        """
        @return: A dictionary mapping from the parse trees for the
        sentence to numeric scores.

        @rtype: C{dict}
        @param sent: The sentence to be parsed
        @type sent: L{list} of L{string}
        """
        
class AbstractParse(ParseI):
    """
    An abstract base class for parsers.  C{AbstractParse} provides
    a default implementation for:

      - L{parse} (based on C{get_parse})
      - L{get_parse_list} (based on C{get_parse})
      - L{get_parse} (based on C{get_parse_list})

    Note that subclasses must override either C{get_parse} or
    C{get_parse_list} (or both), to avoid infinite recursion.
    """

    def __init__(self):
        """
        Construct a new parser.
        """
        # Make sure we're not directly instantiated:
        if self.__class__ == AbstractParse:
            raise AssertionError("Abstract classes can't be instantiated")

    def parse(self, token):
        return self.get_parse(token)

    def grammar(self):
        return self._grammar

    def get_parse(self, token):
        trees = self.get_parse_list(token)
        if len(trees) == 0:
            return None
        else:
            return trees[0]

    def get_parse_list(self, token):
        tree = self.get_parse(token)
        if tree is None:
            return []
        else:
            return [tree]