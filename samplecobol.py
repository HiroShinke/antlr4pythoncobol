

from antlr4 import *

from dist.src.main.antlr4.com.github.hiroshinke.cobolsample.Cobol85Visitor \
    import Cobol85Visitor
from dist.src.main.antlr4.com.github.hiroshinke.cobolsample.Cobol85Parser \
    import Cobol85Parser
from dist.src.main.antlr4.com.github.hiroshinke.cobolsample.Cobol85Lexer \
    import Cobol85Lexer

import argparse
from antlr4.xpath.XPath import XPath
from antlr4.tree.Tree import TerminalNode
from antlr4.tree.Trees import Trees
import io
import re

class SampleVisitor(Cobol85Visitor):
    def visitStatement(self,ctx):
        print(f"{self} {ctx}")
        return super().visitStatement(ctx)

def tree_text(tree,parser=None):

    buff = []

    def helper(t):
        if isinstance(t,TerminalNode):
            str_ = t.getText()
            if parser:
                str_ += "<" +  parser.symbolicNames[t.symbol.type] + ">"
            buff.append(str_)
        else:
            if parser:
                idx = t.getRuleIndex()                
                rn = parser.ruleNames[idx]
                buff.append(f"({rn}")
            for c in t.getChildren():
                helper(c)
            if parser:
                buff.append(f")")

    helper(tree)

    return " ".join(buff)

def tree_pretty(tree,parser):

    with io.StringIO() as fh:

        def helper(t,lev):
            if isinstance(t,TerminalNode):
                fh.write(" " * lev)
                fh.write(t.getText())
                fh.write("\n")
            else:
                idx = t.getRuleIndex()                
                rn = parser.ruleNames[idx]

                fh.write(" " * lev)
                fh.write("(" + rn)
                fh.write("\n")

                for c in t.getChildren():
                    helper(c,lev+1)

                fh.write(" " * lev)
                fh.write(")")
                fh.write("\n")                
                    
        helper(tree,0)
        return fh.getvalue()


def tree_terminals(tree):

    ret = []
    def helper(t):
        if isinstance(t,TerminalNode):
            ret.append(t)
        else:
            for c in t.getChildren():
                helper(c)

    helper(tree)
    return ret

def str_terminal(x,parser=None):
    if parser:
        return ( str(x.symbol) +
                 "<" +
                 parser.symbolicNames[x.symbol.type] +
                 ">" )
    else:
        return str(x.symbol)

def src_contents(contents):
    
    lines = contents.splitlines()
    ret = [ l[6:72] + "\n" for l in lines if not re.search(r"^.{6}\*",l) ]
    return "".join(ret)


def create_parser(contents):

    contents = src_contents(contents)
    data =  InputStream(contents)
    lexer = Cobol85Lexer(data)
    stream = CommonTokenStream(lexer)
    parser = Cobol85Parser(stream)

    return parser

def parser_from_file(f):

    with open(f) as fh:
        return create_parser(fh.read())


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--src")
    parser.add_argument("--visitor",action="store_true")
    parser.add_argument("--withrule",action="store_true")
    parser.add_argument("--prettyrule",action="store_true")
    parser.add_argument("--printdata",action="store_true")
    parser.add_argument("--printstatement",action="store_true")
    parser.add_argument("--printterminals",action="store_true")
    parser.add_argument("--printxpath")

    args = parser.parse_args()

    parser = parser_from_file(args.src)
    tree = parser.startRule()
    print(f"tree = {tree}")
    visitor = SampleVisitor()
    
    def print_proc(xpath):
        subtrees = XPath.findAll(tree,xpath,parser)
        for x in subtrees:
            if args.prettyrule:
                print(tree_pretty(x,parser))
            else:
                print(tree_text(x,parser if args.withrule else None))
                
    if args.printdata:
        print_proc("//dataDescriptionEntry")
                    
    if args.printstatement:
        print_proc("//statement")
    
    if args.printxpath:
        print_proc(args.printxpath)

    if args.printterminals:
        for x in tree_terminals(tree):
            print(str_terminal(x,parser))

    if args.visitor:
        output = visitor.visit(tree)
        print(output)

if __name__ == "__main__":
    main()
    
