from scanner import Scanner
from analyzer import Parser,SymbolTableBuilder,Interpreter
from utils import printter
file_path='test.txt'
scanner = Scanner('test.txt')
scanner.scan()
print(scanner.printter())
analiz=Parser(scanner.tokens,scanner.errors)
tree=analiz.parse()
symtab_builder = SymbolTableBuilder()
symtab_builder.visit(tree)
print('')
print('Symbol Table contents:')
print(symtab_builder.symtab)

interpreter = Interpreter(tree)
result = interpreter.interpret()
print('')
print('Memoria Global contiene:')
for k, v in sorted(interpreter.GLOBAL_MEMORY.items()):
    print('%s = %s' % (k, v))
#print(len(scanner.errors))
