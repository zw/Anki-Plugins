'''
CodeInCards - an Anki plugin to embed Python code in cards/card templates

Copyright 2010 Isaac Wilcox.  This program is free software: you can
redistribute it and/or modify it under the terms of the GNU General Public
License version 3 as published by the Free Software Foundation.
 
Loads substition "libraries" from %pluginsFolder%/CodeInCards/*.py
then provides syntax to let you substitute library calls into cards.

Documentation can be found in CodeInCards.html or at:
  http://bit.ly/codeincardsdoc

An example library can be found in CodeInCards/default.py or at:
  http://bit.ly/codeincards

'''

securityWarning = """\
A trusted deck is inherently a potential security hole.  If someone/something \
deliberately or accidentally causes you to run CodeInCard escapes you didn't \
write, or even if you just write buggy escapes, it could lead to you losing \
data and/or control of your computer (e.g. getting infected with viruses and \
trojans).

You are strongly advised to trust only decks which you've built yourself, from \
scratch, and which are not shared or synchronised online. You have been warned!\
"""

import re
import sys
import os
import traceback
import textwrap
import htmlentitydefs

import anki
import ankiqt
import ankiqt.ui.utils

import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4.Qt

IGNORED_ESCAPES_WARNING = """\
<span style='color:red; font-style:italic; '>
CodeInCards escapes were found but ignored because this deck is not trusted.
Use menu option 'Tools-&gt;Advanced-&gt;CodeInCards Deck Trust...'
to change this.</span><br />"""

CONFIG_KEY = 'CodeInCards.trustedDecks'

modulesMap = {}
libsSymtab = {}
showHTML = False
QorA = None
isSummary = False
card = None
substExec = None
substEval = None
showTrustMessage = None

def evalQuestion(html, card):
        return evalSide(html, card, "q", False)

def evalAnswer(html, card):
        return evalSide(html, card, "a", False)

def evalSide(html, _card, _QorA, _isSummary):
        global showHTML, QorA, card, isSummary, showTrustMessage
        showHTML = False
        QorA = _QorA
        card = _card
        isSummary = _isSummary
        showTrustMessage = False

        # The {%= ... %} takes precedence by being subbed first.
        # Don't want to make it a parameter.
        html = re.sub("""(?xms)        # multiline mostly in case field substs are!
                         \{\%=         # opening tag
                         \s*           # eat leading whitespace
                         (?P<expr>.+?) # any old content, non-greedy
                                       # so {%= ... %} foo {%= ... %}
                                       # will work on a single line
                         \%\}          # closing tag
                         """, substEval, html)
        html = re.sub("""(?xms)        # multiline because code block might be
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
                            (?P<args>      # start group optional args list
                                           # named only for later reference
                               \(            # start args list
                               [^)]*         # greedily include all non-brackets
                               \)            # end args list
                            )?            # end group optional args list
                         )             # finish capture
                         (?(args)|!?)  # eat an optional pling if no args
                         """, substEval, html)
        html = re.sub('\$\$', '$', html)

        if not isSummary:
                if showHTML:
                        html = re.sub("<", "&lt;", html)
                        html = re.sub(">", "&gt;", html)
                        html = "<span style='white-space:pre; font-family:monospace;'>" + html + "</span>"
                if showTrustMessage:
                        html += IGNORED_ESCAPES_WARNING

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
        tempSymtab.update({'QorA': QorA, 'card': card, 'isSummary': isSummary})
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
        
        ret = """\
               <div style='color:red; font-family:monospace; white-space:pre'>
               Error evaluating code substitution:<br />%s
               libs symtab is:<br />%s<br />
               '''code''' is:<br />'''%s'''
               </div>"""  % (prettyTrace, shortPrettySymtab, code)
        return textwrap.dedent(ret)
        
def getLibraryDir():
        # For testing:
        # p = "/Users/zak/Library/Application Support/Anki/plugins/CodeInCards"
        p = os.path.join(ankiqt.mw.pluginsFolder(), "CodeInCards")
        if not os.path.exists(p):
                os.mkdir(p)
        return p

def getLibraries():
        return [p for p in os.listdir(getLibraryDir()) if p.endswith(".py")]

def buildSymtab(modules):
        "Build a pooled symtab with symbols from all substitution libraries, plus 'CIC' alias for this module"
        global libsSymtab
        libsSymtab = {}
        for m in modules:
                libsSymtab.update(dict([(symbol, getattr(m, symbol)) for symbol in dir(m)]))
        libsSymtab.update({'CIC': sys.modules[__name__]})

def loadLibraries():
        "Import or reload all modules found in %pluginsDir%/CodeInCards/*.py and build a pooled symtab"
        global modulesMap
        libraries = getLibraries()

        # Out with modules that have disappeared, if any.
        for nopy in modulesMap.keys():
                if (nopy + ".py") not in libraries:
                        del modulesMap[nopy]
        # Load or reload each lib with a .py
        for lib in libraries:
                nopy = lib.replace(".py", "")
                try:
                        if nopy not in modulesMap:
                                modulesMap[nopy] = __import__(nopy)
                        else:
                                reload(modulesMap[nopy])
                except:
                        print >>sys.stderr, "Error in %s" % lib
                        traceback.print_exc()
        buildSymtab(modulesMap.values())

def onReloadLibraries():
        try:
                loadLibraries()
                ankiqt.ui.utils.showInfo("Libraries reloaded.")
        except Exception as e:
                raise e

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

def entitySubst(match):
        ''' Replace &entityname; with corresponding entity '''
        if match.group('entname') in htmlentitydefs.name2codepoint:
                return unichr(htmlentitydefs.name2codepoint[match.group('entname')])
        # Pass through bad names unchanged
        return match.group()

def cardListData(self, index, role, _old=None):
        '''
        A wrapper around anki.ui.cardlist.DeckModel.data() - i.e. the card list
        table cell renderer.
        This is a hack and should be patched in Anki to be hookable instead.
        Hooks will want to know:
          - whether they're rendering Q or A (examining index is fragile)
          - the card object (?not available here?)

        'ret' is a QVariant
        '''
        ret = _old(self, index, role)
        if not ret.isValid() \
           or not (role == PyQt4.QtCore.Qt.DisplayRole
                   or role == PyQt4.QtCore.Qt.EditRole) \
           or index.column() >= 2:
                return ret
        s = ret.toString().__str__()

        # This is the only code we should need once there's a hook.
        # Note we're setting a local QorA here, not the global.
        if index.column() == 0:
                QorA = 'q'
        elif index.column() == 1:
                QorA = 'a'
        s = evalSide(s, None, QorA, True)

        # Copied straight from original, except more aggressive entity
        # reference resolution.
        s = s.replace("<br>", u" ")
        s = s.replace("<br />", u" ")
        s = s.replace("\n", u"  ")
        s = anki.utils.stripHTML(s)
        s = re.sub("\[sound:[^]]+\]", "", s)
        s = re.sub("&(?P<entname>[a-zA-Z0-9]+);", entitySubst, s)
        s = s.strip()
        # End copy

        return PyQt4.QtCore.QVariant(s)

def init():
        action = PyQt4.QtGui.QAction(ankiqt.mw)
        action.setText("CodeInCards Deck Trust...")
        ankiqt.mw.connect(action, PyQt4.QtCore.SIGNAL("triggered()"), onConfigureTrust)
        ankiqt.mw.mainWin.menuAdvanced.addAction(action)

        action = PyQt4.QtGui.QAction(ankiqt.mw)
        action.setText("Reload CodeInCards libraries")
        ankiqt.mw.connect(action, PyQt4.QtCore.SIGNAL("triggered()"), onReloadLibraries)
        ankiqt.mw.mainWin.menuAdvanced.addAction(action)

        anki.hooks.addHook("drawAnswer", evalAnswer)
        anki.hooks.addHook("drawQuestion", evalQuestion)
        anki.hooks.addHook("enableDeckMenuItems", enableDeckMenuItems)
        
        ankiqt.ui.cardlist.DeckModel.data = anki.hooks.wrap(ankiqt.ui.cardlist.DeckModel.data, cardListData, "wrap")

        sys.path.append(getLibraryDir())
        loadLibraries()


init()

# vim: softtabstop=8 shiftwidth=8 expandtab
