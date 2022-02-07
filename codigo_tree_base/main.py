import os
from grammar import *
def read_from_file(filename) -> str:
        f = open(filename, "r")
        return f.read()



def main():
    #Codigo base de TREE con nodos y gramatica
    prog = read_from_file('test.txt')
    g = PascalGrammar()
    prog = g.parse(prog)
    print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()
