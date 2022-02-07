from ast import Return
from inspect import currentframe, getframeinfo
from itertools import count
from lib2to3.pgen2.token import DOT
from pickle import FALSE, TRUE
from tokenize import Triple
from typing_extensions import Self
from unicodedata import name
from black import err
from cv2 import sepFilter2D
from prettytable import PrettyTable
from utils import Error
from anytree import Node, RenderTree
from scanner import Scanner,tipos
from collections import OrderedDict
import operator
"""
class Token:
    type=NULL
    lexeme=NULL
    row=NULL
    def __init__(self, type, lexeme, row):
        self.type = type
        self.lexeme = lexeme
        self.row = row

    def __str__(self):
        return f'Type: {self.type}, Lexeme: {self.lexeme}, Row: {self.lexeme}'
"""
def comp_list(list_a,list_b,op):
    operadores_com = {
        '<': operator.lt,
        '>': operator.gt,
        '<=': operator.le,
        '>=': operator.ge,
        '==': operator.eq,
        '!=': operator.ne
        }
    fop = operadores_com.get(op)
    bool_list=[]
    for i in range (len(list_a)):
        bool_list.append(fop(list_a[i],list_b[i]))
    return bool_list
    

        
########################### PARSER ##########################

class AST(object):
	pass

class BinOp(AST):
	def __init__(self, left, op, right):
		self.left = left
		self.token = self.op = op
		self.right = right

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value=0
        if(token.type=="INTEGER_CONST"):
            self.value=int(token.value)
        if(token.type=="FLOAT_CONST" or token.type=="SCIENTIFIC_NUMBER"):
            self.value=float(token.value)
        if(token.type=="STRING_LITERAL"):
            self.value=token.value
class UnaryOp(AST):
	def __init__(self, op, expr):
		self.token = self.op = op
		self.expr = expr

class Compound(AST):
	"""Represents a 'BEGIN ... END' block"""
	def __init__(self):
		self.children = []

class Assign(AST):
	def __init__(self, left, op, right):
		self.left = left
		self.token = self.op = op
		self.right = right

class Var(AST):
	def __init__(self, token):
		self.token = token
		self.value = token.value
class Const(AST):
    def __init__(self, token,valor):
        self.token = token
        self.value = token.value
        self.valor = valor

class NoOp(AST):
	pass

class Program(AST):
	def __init__(self, name, block):
		self.name = name
		self.block = block

class Block(AST):
	def __init__(self, declarations, compound_statement):
		self.declarations = declarations
		self.compound_statement = compound_statement

class VarDecl(AST):
	def __init__(self, var_node, type_node):
		self.var_node = var_node
		self.type_node = type_node
class ConstDecl(AST):
	def __init__(self, var_node, type_node):
		self.var_node = var_node
		self.type_node = type_node


class Type(AST):
	def __init__(self, token):
		self.token = token
		self.value = token.type


class Parser(object):
    def __init__(self,tokens,errores):
        self.puntero=0
        self.tokens=tokens
        self.errores=errores
        self.current_token = self.getNextToken()
    def getNextToken(self):
        self.aumentarPuntero()
        return self.tokens[self.puntero-1]
    def aumentarPuntero(self):
        self.puntero+=1
        if self.puntero> len(self.tokens):
            self.puntero-=1

    def error(self):
        raise Exception('Invalid Syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.getNextToken()
        else:
            print("Error de syntaxis con el token",self.current_token.value,"-",self.current_token.type)
    def program(self):
        """program : PROGRAM variable SEMI block DOT"""
        self.eat("PROGRAM")
        nodo_var=self.variable()
        prog_name=nodo_var.value
        self.eat("SEMICOLON")
        block_node=self.block()
        prog_nodo=Program(prog_name,block_node)
        self.eat("DOT")
        return prog_nodo
    def block(self):
        """block : declarations compound_statement"""
        declaration_nodes=self.declarations()
        compound_statement_node = self.compound_statement()
        node = Block(declaration_nodes[0], compound_statement_node)
        return node
    def declarations(self):
        """declarations : VAR (variable_declaration SEMI)+| empty"""
        declaration=[]
        const_declaration=[]
        if self.current_token.type=="CONST":
            self.eat("CONST")
            while self.current_token.type=="ID":
                const_decl=self.const_declaration()
                const_declaration.extend(const_decl)
                self.eat("SEMICOLON")
                
        if self.current_token.type=="VAR":
            self.eat("VAR")
            while self.current_token.type=="ID":
                var_decl=self.variable_declaration()
                declaration.extend(var_decl)
                self.eat("SEMICOLON")
        return [declaration,const_declaration]
    def variable_declaration(self):
        """variable_declaration : ID (COMMA ID)* COLON type_spec"""
        var_nodes = [Var(self.current_token)]
        self.eat("ID")
        while self.current_token.type == "COMMA":
            self.eat("COMMA")
            var_nodes.append(Var(self.current_token))
            self.eat("ID")
        self.eat("COLON")
        type_node = self.type_spec()
        var_declarations = [
            VarDecl(var_node, type_node)
            for var_node in var_nodes
        ]
        return var_declarations
    def const_declaration(self):

        const_node = self.current_token
        self.eat("ID")
        self.eat("ASSIGN_VAR")
        val=self.current_token
        self.eat(val.type)
        const_nodes=[Const(const_node,val)]
        return const_nodes
    def type_spec(self):
        """type_spec : INTEGER | REAL """
        token = self.current_token
        if self.current_token.type == "INTEGER":
            self.eat("INTEGER")
        elif self.current_token.type == "STRING":
            self.eat("STRING")
        else:
            self.eat("REAL")
        node = Type(token)	
        return node
    def compound_statement(self):
        """ compound_statement: BEGIN statement_list END """
        self.eat("BEGIN")
        nodes = self.statement_list()
        self.eat("END")
        root = Compound()
        for node in nodes:
            root.children.append(node)
        return root
    def statement_list(self):
        """ statement_list :Statement StatementList | Statement """
        node = self.statement()
        results = [node]
        while self.current_token.type == "SEMICOLON":
            self.eat("SEMICOLON")
            results.append(self.statement())

        if self.current_token.type == "ID":
            self.error()
        return results
    def statement(self):
        """ statement : compound_statement | assignment_statement | empty """
        if self.current_token.type == "BEGIN":
            node = self.compound_statement()
        elif self.current_token.type == "ID":
            node = self.assignment_statement()
        if self.current_token.type=="WRITE":
            self.write_statement()
            node = self.empty()
        elif self.current_token.type=="WRITELN":
            self.writeln_statement()
            node = self.empty()
        else:
            node = self.empty()
        return node
    def write_statement(self):

        self.eat("WRITE")
        self.eat("LBRACKET")
        self.string_stament()
        self.eat("RBRACKET")
        return 
    def writeln_statement(self):
        print("Entro aqui")
        self.eat("LBRACKET")
        self.string_stament()
        self.eat("RBRACKET")
        return
    def string_stament(self):
        node_string=self.current_token
        self.eat(node_string.type)
        return
    def assignment_statement(self):
        """ assignment_statement : variable ASSIGN expr """
        left = self.variable()
        token = self.current_token
        self.eat("ASSIGN")
        right = self.expr()
        node = Assign(left, token, right)
        return node
    def variable(self):
        """ variable : ID """
        node = Var(self.current_token)
        self.eat("ID")
        return node

    def empty(self):
        """An empty production"""
        return NoOp()
    def expr(self):
        """ expr : term ((OPERATORS) term)* """
        node = self.term()

        while self.current_token.type in ("PLUS", "MINUS"   ):
            token = self.current_token
            if token.type == "PLUS":
                self.eat("PLUS")
            elif token.type == "MINUS":
                self.eat("MINUS")
            node = BinOp(left = node, op = token, right = self.term())
        return node

    def term(self):
        """term : factor ((MUL | DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in ("MULT", "DIV"):
            token = self.current_token
            if token.type == "MULT":
                self.eat("MULT")
            elif token.type == "DIV":
                self.eat("DIV")
            node = BinOp(left = node, op = token, right = self.factor())

        return node
    def factor(self):
        """factor : PLUS factor
                    | MINUS factor
                    | INTEGER_CONST
                    | REAL_CONST
                    | LPAREN expr RPAREN
                    | variable
        """
        token = self.current_token
        if token.type == "PLUS":
            self.eat("PLUS")
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == "MINUS":
            self.eat("MINUS")
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == "INTEGER_CONST":
            self.eat("INTEGER_CONST")
            return Num(token)
        elif token.type == "FLOAT_CONST":
            self.eat("FLOAT_CONST")
            return Num(token)
        elif token.type == "LBRACKET":
            self.eat("LBRACKET")
            node = self.expr()
            self.eat("RBRACKET")
            return node
        else:
            node = self.variable()
            return node
    def parse(self):
        node = self.program()
        return node


class NodeVisitor(object):
	def visit(self, node):
		method_name = 'visit_'+type(node).__name__
		visitor = getattr(self, method_name, self.visita_general)
		return visitor(node)

	def visita_general(self, node):
		raise Exception('No hay visitas_{} metodo'.format(type(node).__name__))

########################## Simbolos ###########################

class Symbol(object):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type

class VarSymbol(Symbol):
    def __init__(self, name, type):
        super(VarSymbol, self).__init__(name, type)

    def __str__(self):
        return '<{name}:{type}>'.format(name=self.name, type=self.type)

    __repr__ = __str__
    
class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super(BuiltinTypeSymbol, self).__init__(name)

    def __str__(self):
        return self.name

    __repr__ = __str__

class SymbolTable(object):
    def __init__(self):
        self._symbols = OrderedDict()
        self._init_builtins()

    def _init_builtins(self):
        self.define(BuiltinTypeSymbol('INTEGER'))
        self.define(BuiltinTypeSymbol('REAL'))
        self.define(BuiltinTypeSymbol('STRING'))

    def __str__(self):
        s = 'Symbols: {symbols}'.format(
            symbols=[value for value in self._symbols.values()]
        )
        return s

    __repr__ = __str__

    def define(self, symbol):
        print('Definimos: %s' % symbol)
        self._symbols[symbol.name] = symbol

    def lookup(self, name):
        print('Tenemos: %s' % name)
        symbol = self._symbols.get(name)
        return symbol

class SymbolTableBuilder(NodeVisitor):
    def __init__(self):
        self.symtab = SymbolTable()

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_ProcedureDecl(self, node):
    	pass

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Num(self, node):
        pass

    def visit_UnaryOp(self, node):
        self.visit(node.expr)

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_VarDecl(self, node):
        type_name = node.type_node.value
        type_symbol = self.symtab.lookup(type_name)
        var_name = node.var_node.value
        var_symbol = VarSymbol(var_name, type_symbol)
        self.symtab.define(var_symbol)

    def visit_Assign(self, node):
        var_name = node.left.value
        var_symbol = self.symtab.lookup(var_name)
        if var_symbol is None:
            raise NameError(repr(var_name))

        self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value
        var_symbol = self.symtab.lookup(var_name)

        if var_symbol is None:
            raise NameError(repr(var_name))

########################### Interprete ##########################

class Interpreter(NodeVisitor):
    def __init__(self, tree):
        self.tree = tree
        self.GLOBAL_MEMORY = OrderedDict()
        
    def visit_ProcedureDecl(self, node):
    	pass

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node):
        # Do nothing
        pass

    def visit_Type(self, node):
        # Do nothing
        pass

    def visit_BinOp(self, node):
        if node.op.type == "PLUS":
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == "MINUS":
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == "MULT":
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == "DIV":
            return float(self.visit(node.left)) / float(self.visit(node.right))

    def visit_Num(self, node):
        return node.value

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == "PLUS":
            return +self.visit(node.expr)
        elif op == "MINUS":
            return -self.visit(node.expr)

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        var_name = node.left.value
        var_value = self.visit(node.right)
        self.GLOBAL_MEMORY[var_name] = var_value

    def visit_Var(self, node):
        var_name = node.value
        var_value = self.GLOBAL_SCOPE.get(var_name)
        return var_value

    def visit_NoOp(self, node):
        pass

    def interpret(self):
        tree = self.tree
        if tree is None:
            return ''
        return self.visit(tree)	