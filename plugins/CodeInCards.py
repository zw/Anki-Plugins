'''
CodeInCards - an Anki plugin to embed Python code in cards/card templates

Copyright 2010 Isaac Wilcox.  This program is free software: you can
redistribute it and/or modify it under the terms of the GNU General Public
License version 3 as published by the Free Software Foundation.
 
Loads substition "libraries" from %pluginsFolder%/CodeInCards/*.py
then provides syntax to let you substitute library calls into cards.

Documentation can be found at:
  http://bit.ly/codeincardsdoc

An example library can be found at:
  http://bit.ly/codeincards
'''

import re
import sys
import os
import traceback

import anki

# For debugging.
#import logging
#LOG_FILENAME = '/tmp/codeincards.out'
#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

modules = []
libsSymtab = {}

def evalQuestion(html, card):
        return evalSide(html, card, "q")

def evalAnswer(html, card):
        return evalSide(html, card, "a")

def evalSide(html, card, QorA):
        def substExecClosure(m):
                return substExec(m, html, card, QorA)
        def substEvalClosure(m):
                return substEval(m, html, card, QorA)

        # The {%= ... %} takes precedence by being subbed first.
        # Don't want to make it a parameter.
        html = re.sub("""(?x)
                         \{\%=         # opening tag
                         \s*           # eat leading whitespace
                         (?P<expr>.+?) # any old content, non-greedy
                                       # so {%= ... %} foo {%= ... %}
                                       # will work on a single line
                         \%\}          # closing tag
                         """, substEvalClosure, html)
        html = re.sub("""(?xms)
                         \{\%          # opening tag
                         \s*           # eat leading whitespace
                         (?P<code>.+?) # any old content; non-greedy
                                       # so {% ... %} foo {% ... %}
                                       # will work on a single line
                         \%\}          # closing tag
                         """, substExecClosure, html)
        html = re.sub("""(?xms)
                         (?<!\$)       # $$... isn't substituted
                         \$            # leading dollar
                         (?P<expr>     # start capture
                            [a-zA-Z_]\w*   # standard identifier rules
                            (?:           # start group optional args list
                               \(            # start args list
                               [^)]*         # greedily include all non-brackets
                               \)            # end args list
                            )?            # end group optional args list
                         )             # finish capture
                         """, substEvalClosure, html)
        return html

class StringWriter:
        # Impersonates sys.stdout, accumulating the write()n strings
        s = ""
        def write(self, str):
                self.s += str

def substExec(m, html, card, QorA):
        code = m.group('code')
        code = re.sub("<br\s*/?>", "\n", code)
        
        swriter = StringWriter()
        oldstdout = sys.stdout
        sys.stdout = swriter

        # Stuff QorA into each global symtab of each module, 'cause we don't know
        # which we're going to evaluate code from.
        for mod in modules:
                m.QorA = QorA
                m.card = card
        ret = ""
        try:
                exec code in libsSymtab
                ret = swriter.s
        except:
                ret = prettyError(code, traceback.format_exc())
        finally:
                sys.stdout = oldstdout
        return ret

def substEval(m, html, card, QorA):
        expr = m.group('expr')
        expr = re.sub("<br\s*/?>", "\n", expr)

        # Stuff QorA into each global symtab of each module, 'cause we don't know
        # which we're going to evaluate code from.
        for mod in modules:
                mod.QorA = QorA
                mod.card = card
        try:
                return str(eval(expr, libsSymtab))
        except:
                return prettyError(expr, traceback.format_exc())

def prettyError(code, trace):
                shortSymtab = libsSymtab.copy()
                shortSymtab['__builtins__'] = None
                shortPrettySymtab = str(shortSymtab)
                shortPrettySymtab = re.sub("<", "&lt;", shortPrettySymtab)
                shortPrettySymtab = re.sub(">", "&gt;", shortPrettySymtab)
                prettyTrace = trace[:]
                prettyTrace = re.sub("<", "&lt;", prettyTrace)
                prettyTrace = re.sub(">", "&gt;", prettyTrace)
                prettyTrace = re.sub("\n", "<br />\n", prettyTrace)
                #logging.debug("Error evaluating code substitution:\n" + traceback.format_exc() + "libs symtab is:\n" + str(shortSymtab) + "'''code''' is:\n'''" + expr + "'''")
        
                # Maybe you shouldn't wrap <pre>, but it works.
                return "<span style='color:red'><pre>Error evaluating code substitution:<br />" + prettyTrace + "libs symtab is:<br />" + shortPrettySymtab + "<br/>'''code''' is:<br />'''" + code + "'''</pre></span>"
        
def getLibraryDir():
        # For testing:
        # p = "/Users/zak/Library/Application Support/Anki/plugins/CodeInCards"
        from ankiqt import mw
        p = mw.pluginsFolder() + "/CodeInCards"
        if not os.path.exists(p):
                os.mkdir(p)
        return p

def getLibraries():
        return [p for p in os.listdir(getLibraryDir()) if p.endswith(".py")]

def buildSymtab():
        for m in modules:
                libsSymtab.update(dict([(symbol, getattr(m, symbol)) for symbol in dir(m)]))
        return libsSymtab

def loadLibraries():
        sys.path.insert(0, getLibraryDir())
        for lib in getLibraries():
                try:
                        nopy = lib.replace(".py", "")
                        modules.append(__import__(nopy))
                except:
                        print >>sys.stderr, "Error in %s" % lib
                        traceback.print_exc()
        buildSymtab()

loadLibraries()

anki.hooks.addHook("drawQuestion", evalQuestion)
anki.hooks.addHook("drawAnswer", evalAnswer)

# vim: softtabstop=8 shiftwidth=8 expandtab
