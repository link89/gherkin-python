from .parser import Parser
from .ast_builder import AstBuilder
from .token_matcher import MyTokenMatcher


def parse_gherkin(path):
    return Parser(AstBuilder()).parse(path, MyTokenMatcher())
