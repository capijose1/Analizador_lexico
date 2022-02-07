from contextlib import suppress

import pyparsing as parser
from pyparsing import pyparsing_common as ppc
from myParser import *


class PascalGrammar:
    def __init__(self):
        self.parser = self._make_parser()

    def _make_parser(self):
        num = parser.Regex('[+-]?\\d+\\.?\\d*([eE][+-]?\\d+)?')
        str_ = parser.QuotedString("'", escChar='\\', unquoteResults=False, convertWhitespaceEscapes=False)
        TRUE = parser.Literal('True')
        FALSE = parser.Literal('False')
        bool_val = FALSE | TRUE
        literal = num | str_ | bool_val
        ident = ppc.identifier.setName('ident')

        INT = parser.CaselessKeyword("integer")
        CHAR = parser.CaselessKeyword("char")
        BOOL = parser.CaselessKeyword("boolean")

        type_spec = INT | CHAR | BOOL

        LPAR, RPAR = parser.Literal('(').suppress(), parser.Literal(')').suppress()
        LBRACK, RBRACK = parser.Literal("[").suppress(), parser.Literal("]").suppress()
        LBRACE, RBRACE = parser.CaselessKeyword("begin").suppress(), parser.CaselessKeyword("end").suppress()
        SEMI, COMMA, COLON = parser.Literal(';').suppress(), parser.Literal(',').suppress(), parser.Literal(':').suppress()
        ASSIGN = parser.Literal(':=')
        VAR = parser.CaselessKeyword("var").suppress()
        DOT = parser.Literal('.').suppress()

        ADD, SUB = parser.Literal('+'), parser.Literal('-')
        MUL, DIVISION = parser.Literal('*'), parser.Literal('/')
        MOD, DIV = parser.CaselessKeyword('mod'), parser.CaselessKeyword('div')
        AND = parser.Literal('and')
        OR = parser.Literal('or')
        GE, LE, GT, LT = parser.Literal('>='), parser.Literal('<='), parser.Literal('>'), parser.Literal('<')
        NEQUALS, EQUALS = parser.Literal('!='), parser.Literal('=')
        ARRAY = parser.CaselessKeyword("array").suppress()
        OF = parser.CaselessKeyword("of").suppress()

        add = parser.Forward()
        expr = parser.Forward()
        stmt = parser.Forward()
        stmt_list = parser.Forward()
        procedure_decl = parser.Forward()
        function_decl = parser.Forward()

        array_ident = ident + LBRACK + literal + RBRACK
        call = ident + LPAR + parser.Optional(expr + parser.ZeroOrMore(COMMA + expr)) + RPAR


        group = (
                literal |
                call |
                array_ident |
                ident |
                LPAR + expr + RPAR

        )

        mult = parser.Group(group + parser.ZeroOrMore((MUL | DIVISION | MOD | DIV) + group)).setName('bin_op')
        add << parser.Group(mult + parser.ZeroOrMore((ADD | SUB) + mult)).setName('bin_op')
        compare1 = parser.Group(add + parser.Optional((GE | LE | GT | LT) + add)).setName('bin_op')
        compare2 = parser.Group(compare1 + parser.Optional((EQUALS | NEQUALS) + compare1)).setName('bin_op')
        logical_and = parser.Group(compare2 + parser.ZeroOrMore(AND + compare2)).setName('bin_op')
        logical_or = parser.Group(logical_and + parser.ZeroOrMore(OR + logical_and)).setName('bin_op')

        expr << (logical_or)


        ident_list = ident + parser.ZeroOrMore(COMMA + ident)
        var_decl = ident_list + COLON + type_spec
        array_decl = ident_list + COLON + ARRAY + LBRACK + literal + parser.Literal(
            "..").suppress() + literal + RBRACK + OF + type_spec + SEMI
        vars_decl = VAR + parser.ZeroOrMore((var_decl + SEMI) | procedure_decl | function_decl | array_decl)

        assign = parser.Optional(array_ident | ident) + ASSIGN.suppress() + expr
        simple_stmt = assign | call

        for_body = stmt | parser.Group(SEMI).setName('stmt_list')
        for_cond = assign + parser.Keyword("to").suppress() + literal

        if_ = parser.Keyword("if").suppress() + parser.ZeroOrMore(LPAR) + expr + parser.ZeroOrMore(RPAR) + parser.Keyword("then").suppress() \
              + stmt + parser.Optional(parser.Keyword("else").suppress() + stmt)
        while_ = parser.Keyword("while").suppress() + LPAR + expr + RPAR + parser.Keyword("do").suppress() + stmt
        repeat_ = parser.Keyword("repeat").suppress() + stmt_list + parser.Keyword("until").suppress() + LPAR + expr + RPAR
        for_ = parser.Keyword("for").suppress() + LPAR + for_cond + RPAR + parser.Keyword("do").suppress() + for_body

        comp_op = LBRACE + stmt_list + RBRACE + SEMI

        stmt << (
                if_ |
                for_ |
                while_ |
                repeat_ |
                comp_op |
                simple_stmt + SEMI
        )

        stmt_list << (parser.ZeroOrMore(stmt + parser.ZeroOrMore(SEMI)))

        body = LBRACE + stmt_list + RBRACE
        #params = parser.ZeroOrMore(ident + parser.ZeroOrMore(COMMA + ident) + COLON + type_spec + SEMI) + \
        #(ident + parser.ZeroOrMore(COMMA + ident) + COLON + type_spec)
        params = LPAR + parser.ZeroOrMore(var_decl) + parser.ZeroOrMore(COMMA + var_decl) + RPAR
        procedure_decl << parser.Keyword("procedure").suppress() + ident + params + SEMI + vars_decl + body + SEMI

        function_decl << parser.Keyword("function").suppress() + ident + params + COLON + type_spec + SEMI + \
        vars_decl + body + SEMI

        program = parser.Keyword("Program").suppress() + ident + SEMI + parser.Optional(vars_decl) + body + DOT

        start = program.ignore(parser.cStyleComment).ignore(parser.dblSlashComment) + parser.StringEnd()

        for var_name, value in locals().copy().items():
            if isinstance(value, parser.ParserElement):
                PascalParser.parse(var_name, value)

        return start


    def parse(self, prog: str) -> StmtListNode:
        return self.parser.parseString(str(prog))[0]
