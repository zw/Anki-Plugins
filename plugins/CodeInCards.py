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

$Id$
'''

securityWarning = """\
Executing code is a potential security risk.  If an attacker creates \
or is able to modify the deck or if anyone (including you) puts buggy \
code in the deck, it could lead to your computer being damaged and/or \
taken over by viruses and trojans.  You are strongly advised to enable \
CodeInCards only on decks you built yourself from scratch and which are \
not shared or synchronised online.  You have been warned!\
"""

import re
import sys
import os
import traceback

import anki
import ankiqt

import PyQt4.QtCore
import PyQt4.QtGui

# For debugging.
#import logging
#LOG_FILENAME = '/tmp/codeincards.out'
#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

CONFIG_KEY = 'CodeInCards.trustedDecks'

modules = []
libsSymtab = {}
showHTML = False
QorA = None
card = None
substExec = None
substEval = None
showTrustMessage = None

def evalQuestion(html, card):
        return evalSide(html, card, "q")

def evalAnswer(html, card):
        return evalSide(html, card, "a")

def evalSide(html, _card, _QorA):
        global showHTML, QorA, card, showTrustMessage
        showHTML = False
        QorA = _QorA
        card = _card
        showTrustMessage = False

        # The {%= ... %} takes precedence by being subbed first.
        # Don't want to make it a parameter.
        html = re.sub("""(?x)
                         \{\%=         # opening tag
                         \s*           # eat leading whitespace
                         (?P<expr>.+?) # any old content, non-greedy
                                       # so {%= ... %} foo {%= ... %}
                                       # will work on a single line
                         \%\}          # closing tag
                         """, substEval, html)
        html = re.sub("""(?xms)
                         \{\%          # opening tag
                         \s*           # eat leading whitespace
                         (?P<code>.+?) # any old content; non-greedy
                                       # so {% ... %} foo {% ... %}
                                       # will work on a single line
                         \%\}          # closing tag
                         """, substExec, html)
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
                         """, substEval, html)
        if showHTML:
                html = re.sub("<", "&lt;", html)
                html = re.sub(">", "&gt;", html)
                html = "<span style='white-space:pre; font-family:monospace;'>" + html + "</span>"
        if showTrustMessage:
                html = ("""<span style='color:red; font-style:italic; '>
                           CodeInCards escapes were found but ignored because
                           this deck ('%s') is not trusted.  Use menu option
                           'Tools-&gt;Advanced-&gt;CodeInCards Deck Trust...'
                           to change this.</span><br />"""
                               % (ankiqt.mw.deck.name()) ) + html
        return html

class StringWriter:
        # Impersonates sys.stdout, accumulating the write()n strings
        s = ""
        def write(self, str):
                self.s += str

def realSubstExec(match):
        code = match.group('code')
        code = re.sub("<br\s*/?>", "\n", code)
        
        swriter = StringWriter()
        oldstdout = sys.stdout
        sys.stdout = swriter

        ret = ""
        try:
                exec code in copySymtab()
                ret = swriter.s
        except:
                ret = prettyError(code, traceback.format_exc())
        finally:
                sys.stdout = oldstdout
        return ret

def realSubstEval(match):
        expr = match.group('expr')
        expr = re.sub("<br\s*/?>", "\n", expr)

        try:
                return str(eval(expr, copySymtab()))
        except:
                return prettyError(expr, traceback.format_exc())

def copySymtab():
        "Clone the pooled symtab and insert some convenience symbols"
        tempSymtab = libsSymtab.copy()
        tempSymtab.update({'QorA': QorA, 'card': card})
        return tempSymtab

def prettyError(code, trace):
        shortSymtab = libsSymtab.copy()
        shortSymtab['__builtins__'] = None
        shortPrettySymtab = str(shortSymtab)
        shortPrettySymtab = re.sub("<", "&lt;", shortPrettySymtab)
        shortPrettySymtab = re.sub(">", "&gt;", shortPrettySymtab)
        prettyTrace = trace[:]
        prettyTrace = re.sub("<", "&lt;", prettyTrace)
        prettyTrace = re.sub(">", "&gt;", prettyTrace)
        prettyTrace = re.sub("\n", "<br />", prettyTrace)
        
        return """\
               <div style='color:red; font-family:monospace; white-space:pre'>
               Error evaluating code substitution:<br />%s
               libs symtab is:<br />%s<br />
               '''code''' is:<br />'''%s'''
               </div>"""  % (prettyTrace, shortPrettySymtab, code)
        
def getLibraryDir():
        # For testing:
        # p = "/Users/zak/Library/Application Support/Anki/plugins/CodeInCards"
        p = ankiqt.mw.pluginsFolder() + "/CodeInCards"
        if not os.path.exists(p):
                os.mkdir(p)
        return p

def getLibraries():
        return [p for p in os.listdir(getLibraryDir()) if p.endswith(".py")]

def buildSymtab():
        "Build a pooled symtab with symbols from all substitution libraries, plus 'CIC' alias for this module"
        for m in modules:
                libsSymtab.update(dict([(symbol, getattr(m, symbol)) for symbol in dir(m)]))
        libsSymtab.update({'CIC': sys.modules[__name__]})
        return libsSymtab

def loadLibraries():
        "Import all modules found in %pluginsDir%/CodeInCards/*.py and build a pooled symtab"
        sys.path.insert(0, getLibraryDir())
        for lib in getLibraries():
                try:
                        nopy = lib.replace(".py", "")
                        modules.append(__import__(nopy))
                except:
                        print >>sys.stderr, "Error in %s" % lib
                        traceback.print_exc()
        buildSymtab()

def safeSubst(match):
        "Leave code escape untouched, and flag the need to show 'deck not trusted' message"
        global showTrustMessage
        showTrustMessage = True
        return match.group()

def onConfigureTrust():
        "Handle selection of Tools->Advanced->CodeInCards Deck Trust"
        trustedDecksDialog = PyQt4.QtGui.QDialog(ankiqt.mw)
        trustedDecksDialog.setWindowTitle("Configure CodeInCards Deck Trust")
        l = PyQt4.QtGui.QVBoxLayout()

        # Ugly hack to set a sensible minimum width without using absolute
        # sizes in pixels.  Does QT have a way to set width in 'em'?
        widthLabel = PyQt4.QtGui.QLabel()
        widthLabel.setText("------------------------------------------------------")
        widthLabel.setMaximumHeight(1)
        widthLabel.setWordWrap(False)
        l.addWidget(widthLabel)
        
        warningLabel = PyQt4.QtGui.QLabel()
        warningLabel.setText(securityWarning)
        warningLabel.setWordWrap(True)
        warningLabel.setStyleSheet("QLabel { color:red; }")
        l.addWidget(warningLabel)

        checkBox = PyQt4.QtGui.QCheckBox()
        checkBox.setText("Execute CodeInCards escapes in this deck")
        if deckIsTrusted(ankiqt.mw.deck, ankiqt.mw.config):
                checkBox.setChecked(True)
        l.addWidget(checkBox)

        trustedDecksDialog.connect(checkBox, PyQt4.QtCore.SIGNAL("stateChanged(int)"), onCheckBox)
        trustedDecksDialog.setLayout(l)
        trustedDecksDialog.show()

def onCheckBox(newState):
        "Update config and execution behaviour to match trust dialog checkbox"
        setDeckTrust(newState == PyQt4.QtCore.Qt.Checked, ankiqt.mw.deck, ankiqt.mw.config)
        applyDeckTrust(ankiqt.mw.deck, ankiqt.mw.config)

def deckIsTrusted(deck, config):
        return (CONFIG_KEY in config
                and deckHash(deck) in config[CONFIG_KEY])

def setDeckTrust(trust, deck, config):
        if CONFIG_KEY not in config:
                config[CONFIG_KEY] = {} 

        if trust:
                config[CONFIG_KEY][deckHash(deck)] = ""
        else:
                del config[CONFIG_KEY][deckHash(deck)]

def deckHash(deck):
        return str(deck.name()) + str(deck.created)

# Anki hook
def enableDeckMenuItems(enabled):
        "Update execution behaviour each time we load a new deck"
        if enabled:
                applyDeckTrust(ankiqt.mw.deck, ankiqt.mw.config)

def applyDeckTrust(deck, config):
        global substExec, substEval
        if deckIsTrusted(deck, config):
                substExec = realSubstExec
                substEval = realSubstEval
        else:
                substExec = safeSubst
                substEval = safeSubst

def init():
        action = PyQt4.QtGui.QAction(ankiqt.mw)
        action.setText("CodeInCards Deck Trust...")
        ankiqt.mw.connect(action, PyQt4.QtCore.SIGNAL("triggered()"), onConfigureTrust)
        ankiqt.mw.mainWin.menuAdvanced.addAction(action)

        loadLibraries()

        anki.hooks.addHook("drawAnswer", evalAnswer)
        anki.hooks.addHook("drawQuestion", evalQuestion)
        anki.hooks.addHook("enableDeckMenuItems", enableDeckMenuItems)

init()

# vim: softtabstop=8 shiftwidth=8 expandtab
