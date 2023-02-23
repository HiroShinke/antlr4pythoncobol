#!/bin/sh

[ -f antlr-4.12.0-complete.jar ] || \
    curl -O https://www.antlr.org/download/antlr-4.12.0-complete.jar

export CLASSPATH=".:antlr-4.12.0-complete.jar:$CLASSPATH"
alias antlr4='java -jar antlr-4.12.0-complete.jar'
alias grun='java org.antlr.v4.gui.TestRig'

antlr4 src/main/antlr4/com/github/hiroshinke/cobolsample/Cobol85.g4 -Dlanguage=Python3 -visitor -o dist
