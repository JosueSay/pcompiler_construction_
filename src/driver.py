import sys
from antlr4 import *
from antlr_gen.CompiscriptLexer import CompiscriptLexer
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.visitor import VisitorCPS

def main(argv):
    input_stream = FileStream(argv[1], encoding='utf-8')
    lexer = CompiscriptLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CompiscriptParser(stream)
    tree = parser.program()  # We are using 'prog' since this is the starting rule based on our Compiscript grammar, yay!
    
    visitor = VisitorCPS()
    visitor.visit(tree)
    
    if visitor.errors:
        print("Errores encontrados:")
        for e in visitor.errors:
            print(f" - {e}")
    else:
        print("Visitor executed successfully.")

if __name__ == '__main__':
    main(sys.argv)