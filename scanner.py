from asyncio.windows_events import NULL
import re
import string
from cv2 import line
from prettytable import PrettyTable
from utils import Error

from pyparsing import lineEnd
kwords = ["ARRAY","DOWNTO","FUNCTION","OF","REPEAT","UNTIL","BEGIN","ELSE","GOTO","PACKED"
          ,"SET","VAR","CASE","END","IF","PROCEDURE","THEN","WHILE","CONST","FILE","LABEL"
          ,"PROGRAM","TO","WITH","DO","FOR","NIL","RECORD","TYPE","WRITE","READ","WRITELN"]


#tokens of language
tokens = {
    ':=':'ASSIGN',
    '==':'EQUAL', 
    '=':'ASSIGN_VAR',
    '<=':'LTE', 
    '>=':'GTE',
    '<>':'DIFERENT',
    '>':'GT', 
    '<':'LT', 
    '/':'DIV',
     '-':'MINUS',
    '+':'PLUS', 
    '*':'MULT',
    '^':'puntero',
    'AND':'AND', 
    'OR':'OR',
    'NOT':'NOT',
    'DIV':'DIV',
    'MOD':'MOD',
    'IN':'IN'
        }
delimitadores = {
     '..':'DOTDOT', 
     '.':'DOT',
    ':':'COLON', 
    ';':'SEMICOLON', 
    ',':'COMMA',
    '[':'LCOL', 
    ']':'RCOL',
    '(':'LBRACKET', 
    ')':'RBRACKET',
        }
tipos= {'boolean': 'BOOLEAN',
    'integer': 'INTEGER',
    'INTEGER': 'INTEGER',
    'real': 'REAL',
    'REAL': 'REAL',
    'STRING': 'STRING',
    'string': 'STRING',}
def eliminarComentario(linea):
    linea = re.sub('\(\*.*\*\)', '', linea)
    return linea
def eliminarComentarioParentesis(linea):
    if(linea.find('{')!=-1 and linea.find('}')!=-1):
        tmp=linea[linea.find('{'):linea.find('}')+1]
        linea=linea.replace(tmp,'')
    return linea
class Token:
    type=NULL
    value=NULL
    row=NULL
    def __init__(self, type, value, row):
        self.type = type
        self.value = value
        self.row = row

    def __str__(self):
        return f'Type: {self.type}, Value: {self.value}, Row: {self.row}'
    def __repr__(self):
	    return self.__str__()
class Scanner:
    def __init__(self, file_path):
        self.file = open(file_path, 'r')
        self.data = None
        self.errors = []
        self.tokens = []
        self.value = []
        self.state = 0
        
        self.tabla_simbolos = {}
        self.values = []
        self.values2 = []

        self.simbolos = 1
    def get_value(self):
        return "".join(self.value)

    def clean_value(self):
        self.value = []

    def printter(self):
        tokens = PrettyTable()
        tokens.field_names = ["Type", "value", "Row"]
        tokens.add_rows([
            [token.type, token.value, token.row] for token in self.tokens
        ])
        return tokens

    def printter(self):
        tokens = PrettyTable()
        tokens.field_names = ["Type", "value", "Row"]
        tokens.add_rows([
            [token.type, token.value, token.row] for token in self.tokens
        ])
        return tokens
    def imprimir_errores(self):
        with open('result.txt', 'w') as file:
            file.write("LEXEMAS: \n")
            for lex in self.values2:
                file.write('--->'+lex)
    def scan(self):
        row = 0
        for linea in self.file:
            row += 1
            linea = eliminarComentario(linea)
            linea = eliminarComentarioParentesis(linea)
            if re.search("'.*'", linea):
                linea = re.sub("'.*'", re.search("'.*'", linea).group().replace(' ', '$'), linea)
            linea = linea.replace(';', ' ; ')
            linea = linea.replace(',', ' , ')
            linea = linea.replace('{', ' { ')
            linea = linea.replace('}', ' } ')
            linea = linea.replace('[', ' [ ')
            linea = linea.replace(']', ' ] ')
            linea = linea.replace(':', ' : ')


            linea = linea.replace('+', ' + ')
            linea = linea.replace('-', ' - ')
            linea = linea.replace('*', ' * ')
            linea = linea.replace('/', ' / ')
            
            
        
            linea = linea.replace('<', ' < ')
            linea = linea.replace('>', ' > ')
            linea = linea.replace('< >', ' <> ')
            linea = linea.replace('<>', ' <> ')
            linea = linea.replace(' <  > ', ' <> ')
            linea = linea.replace(':=', ' := ')
            linea = linea.replace('=', ' = ')
            linea = linea.replace('=  =', ' == ')
            linea = linea.replace(' :  =', ' := ')
            linea = linea.replace(' > =', ' >= ')
            linea = linea.replace('>=', ' >= ')
            linea = linea.replace(' < =', ' <= ')
            linea = linea.replace('<=', ' <= ')
            linea = linea.replace('^', ' ^ ')
            linea = linea.replace(' \n}', ' } ')
            if(not re.search('\d+.\d+', linea)):
                linea = linea.replace(".", " . ")
            linea = linea.replace(' . .', ' .. ')
            linea = linea.replace(' < >', ' <> ')
            linea = linea.replace('(', ' ( ')
            linea = linea.replace('e + ', 'e+')
            linea = linea.replace('e - ', 'e-')
            linea=linea.replace("'''","''")
            linea = linea.replace(')', ' ) ').split()
            self.values.append(linea)

        for index, value in enumerate(self.values):
            for lex in value:
                if lex.find("'") != -1:
                    if(lex.count("'")%2 != 0):
                        self.values2.append('Error de string en la linea {}.\n'.format(index+1))
                        lex = ''
                    else:
                        self.values2.append('linea: {}, Lexema: {} , token( String, {} )\n'.format(index+1, lex.replace('$', ' '), lex.replace('$', ' ')))
                        self.tokens.append(Token('STRING_LITERAL', lex.replace('$', ' '), index+1))
                elif re.search(r"^[-+]?[\d]+\.?[\d]*[Ee](?:[-+]?[\d]+)?$", lex):
                    self.values2.append('linea: {}, Lexema: {} , token( {} , {} )\n'.format(index+1, lex, 'SCIENTIFIC_NUMBER', lex))
                    self.tokens.append(Token('SCIENTIFIC_NUMBER', lex, index+1))
                elif lex.upper() in kwords:
                    self.values2.append('linea: {}, Lexema: {} , token( Keyword , {} )\n'.format(index+1, lex, ''))
                    self.tokens.append(Token(lex.upper(), lex, index+1))
                elif lex.lower() in tipos:
                    self.values2.append('linea: {}, Lexema: {} , Tipo( Keyword , {} )\n'.format(index+1, lex, ''))
                    self.tokens.append(Token(tipos[lex], lex, index+1))
                elif lex in tokens.keys():
                    self.values2.append('linea: {}, Lexema: {} , token( {} , {} )\n'.format(index+1, lex, lex, tokens[lex]))
                    self.tokens.append(Token(tokens[lex], lex, index+1))
                elif lex in delimitadores.keys():
                    self.values2.append('linea: {}, Lexema: {} , delimitador( {} , {} )\n'.format(index+1, lex, lex, delimitadores[lex]))
                    self.tokens.append(Token(delimitadores[lex], lex, index+1))
                elif re.search('^[_a-zA-Z]\w*$', lex): #usamos el lenguaje regular para hacer una busqueda
                    if lex not in self.tabla_simbolos.keys():
                        self.tabla_simbolos[lex] = ['linea: {}, Lexema: {} , token: {} , address: {} )\n'.format(index+1, lex, 'ID', self.simbolos), self.simbolos]
                        self.values2.append('linea: {}, Lexema: {} , token( {} , {} )\n'.format(index+1, lex, 'ID', self.simbolos))
                        self.simbolos += 1
                    else:
                        self.values2.append('linea: {}, Lexema: {} , token( {} , {} )\n'.format(index+1, lex, 'ID', self.tabla_simbolos[lex][1]))
                    self.tokens.append(Token('ID', lex, index+1))
                elif re.search('^\d+.\d$', lex):
                    self.values2.append('linea: {}, Lexema: {} , token( {} , {} )\n'.format(index+1, lex, 'FLOAT_CONST', lex))
                    self.tokens.append(Token('FLOAT_CONST', lex, index+1))
                elif re.search('^\d+$', lex):
                    self.values2.append('linea: {}, Lexema: {} , token( {} , {} )\n'.format(index+1, lex, 'INTEGER_CONST', lex))
                    self.tokens.append(Token('INTEGER_CONST', lex, index+1))
            
                else:
                    print("|"+lex+"|")
                    self.errors.append(Token('Lexical_Error',lex,index+1))
                    Error(lex, index+1, 'Lexical error')
    def imprimir(self):
        with open('result.txt', 'w') as file:
            file.write("LEXEMAS: \n")
            for lex in self.values2:
                file.write('--->'+lex)
    