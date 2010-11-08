u'''
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

securityWarning = u"""\
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
import anki.deck
import ankiqt
import ankiqt.ui.utils

import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4.Qt

IGNORED_ESCAPES_WARNING = u"""\
<span style='color:red; font-style:italic; '>
CodeInCards escapes were found but ignored because this deck is not trusted.
Use menu option 'Tools-&gt;Advanced-&gt;CodeInCards Deck Trust...'
to change this.</span><br />\
"""

CONFIG_KEY = u'CodeInCards.trustedDecks'

debug = True
LOG_FILENAME = u'/tmp/CodeInCards.out'
logger = None

modulesMap = {}
libsSymtab = {}
showHTML = False
QorA = None
isSummary = False
card = None
substExec = None
substEval = None
showTrustMessage = None
f = None
depth = 0

def evalQuestion(html, card):
        logger.debug(u"html's type is " + str(type(html)))
        return evalSide(html, card, u"q", False)

def evalAnswer(html, card):
        return evalSide(html, card, u"a", False)

def evalSide(html, _card, _QorA, _isSummary):
        global showHTML, QorA, card, isSummary, showTrustMessage, depth
        if depth:
                saved_showHTML = showHTML
                saved_QorA = QorA
                saved_card = card
                saved_isSummary = isSummary
                depth += 1
        showHTML = False
        QorA = _QorA
        card = _card
        isSummary = _isSummary
        showTrustMessage = False

        # The {%= ... %} takes precedence by being subbed first.
        # Don't want to make it a parameter.
        logger.debug("to execute:\n" + html)
        html = re.sub(ur"dnl.*<br\s*/?>", ur"", html)
        html = re.sub(ur"dnl.*\n", ur"", html)
        html = re.sub(ur"""(?xms)        # multiline mostly in case field substs are!
                         \{\%=         # opening tag
                         \s*           # eat leading whitespace
                         (?P<expr>.+?) # any old content, non-greedy
                                       # so {%= ... %} foo {%= ... %}
                                       # will work on a single line
                         \%\}          # closing tag
                         """, substEval, html)
        html = re.sub(ur"""(?xms)        # multiline because code block might be
                         \{\%          # opening tag
                         \s*           # eat leading whitespace
                         (?P<code>.+?) # any old content; non-greedy
                                       # so {% ... %} foo {% ... %}
                                       # will work on a single line
                         \%\}          # closing tag
                         """, substExec, html)
        html = re.sub(ur"""(?xms)
                         (?<!\$)       # $$... isn't substituted
                         \$            # leading dollar
                         (?P<expr>     # start capture
                            [a-zA-Z_]\w*   # standard identifier rules
                            (?P<args>      # start group optional args list
                                           # named only for later reference
                               \(            # start args list
                               [^)]*         # greedily include all non-brackets
                               \)            # end args list
                               |
                               \[            # start subscription
                               [^]]*         # greedily include all non-brackets
                               \]            # end subscription
                            )?            # end group optional args list
                         )             # finish capture
                         (?(args)|!?)  # eat an optional pling if no args
                         """, substEval, html)
        html = re.sub(ur'\$\$', ur'$', html)

        if not isSummary:
                if showHTML:
                        html = re.sub(ur"<", ur"&lt;", html)
                        html = re.sub(ur">", ur"&gt;", html)
                        html = u"<span style='white-space:pre; font-family:monospace;'>" + html + u"</span>"
                if showTrustMessage:
                        html += IGNORED_ESCAPES_WARNING

        logger.debug("result:\n" + html)
        if depth:
                showHTML = saved_showHTML
                QorA = saved_QorA
                card = saved_card
                isSummary = saved_isSummary
                depth -= 1
        return html

class StringWriter:
        # Impersonates sys.stdout, accumulating the write()n strings
        s = u""
        def write(self, str):
                self.s += str

def realSubstExec(match):
        code = match.group(u'code')
        #if isSummary:
        #        return code
        code = re.sub(ur"<br\s*/?>", ur"\n", code)
        
        swriter = StringWriter()
        oldstdout = sys.stdout
        sys.stdout = swriter

        ret = u""
        try:
                logger.debug(u"code's type is " + str(type(code)))
                exec code in copySymtab()
                ret = swriter.s
        except:
                ret = prettyError(code, traceback.format_exc())
        finally:
                sys.stdout = oldstdout
        return ret

def realSubstEval(match):
        expr = match.group(u'expr')
        #if isSummary:
        #        return expr
        expr = re.sub(ur"<br\s*/?>", ur"\n", expr)

        ret = u""
        try:
                logger.debug(u"expr's type is " + str(type(expr)))
                ret = eval(expr, copySymtab())
        except:
                ret = prettyError(expr, traceback.format_exc())
        if not (type(ret) == str or type(ret) == unicode):
                return u"Error: CodeInCards expression escape returned something other than a string"
        return ret

class FieldGetter:
        u"""
        Just a hack for getting a field to be accessible via f[name] instead of
        f(name), to work around the nested brackets that don't work in
        $doSomethingWithF(f('foo')).
        I'd prefer to declare __getitem__ class or static and say:
          f=FieldGetter
          f['field']
        but that yields:
          TypeError: 'classobj' object is unsubscriptable
        so we instantiate this in init() instead.
        """
        def __getitem__(self, name):
                u"""Convenience method to pull out field by name, evaluate any escapes
                    and return the result."""
                # Just for clarity, we're using the card set up by evalSide
                global card
                ret = u""
                try:
                        ret = card.fact[name]
                except KeyError:
                        return "No such field '%s'" % name
                return evalSide(ret, card, QorA, isSummary)

def copySymtab():
        u"Clone the pooled symtab and insert some convenience symbols"
        tempSymtab = libsSymtab.copy()
        tempSymtab.update({u'QorA': QorA, u'card': card, u'isSummary': isSummary, u'f': f})
        return tempSymtab

def prettyError(code, trace):
        shortSymtab = libsSymtab.copy()
        shortSymtab[u'__builtins__'] = None
        shortPrettySymtab = str(shortSymtab)
        shortPrettySymtab = re.sub(ur"<", ur"&lt;", shortPrettySymtab)
        shortPrettySymtab = re.sub(ur">", ur"&gt;", shortPrettySymtab)

        # Python includes 'code' in the traceback str, resulting in a string
        # object (whose encoding is always implicitly 'ascii') even when 'code'
        # contains non-ASCII.  This is probably a Python bug. 
        try:
                prettyTrace = trace.decode(u'utf-8')
        except UnicodeDecodeError:
                prettyTrace = u""
                prettyTraceChars = list(trace)
                for c in prettyTraceChars:
                        if ord(c) > 127:
                                prettyTrace += u'0x%x' % ord(c)
                        else:
                                prettyTrace += c
        prettyTrace = re.sub(ur"<", ur"&lt;", prettyTrace)
        prettyTrace = re.sub(ur">", ur"&gt;", prettyTrace)
        prettyTrace = re.sub(ur"\n", ur"<br />", prettyTrace)
        
        ret = u"""\
               <div style='color:red; font-family:monospace; white-space:pre; text-align:left; '>
               Error evaluating code substitution:<br />%s
               '''code''' is:<br />'''%s'''
               </div>"""  % (prettyTrace, code)
        return textwrap.dedent(ret)
        
def getLibraryDir():
        # For testing:
        # p = "/Users/zak/Library/Application Support/Anki/plugins/CodeInCards"
        p = os.path.join(ankiqt.mw.pluginsFolder(), u"CodeInCards")
        if not os.path.exists(p):
                os.mkdir(p)
        return p

def getLibraries():
        return [p for p in os.listdir(getLibraryDir()) if p.endswith(u".py")]

def buildSymtab(modules):
        u"Build a pooled symtab with symbols from all substitution libraries, plus 'CIC' alias for this module"
        global libsSymtab
        libsSymtab = {}
        for m in modules:
                libsSymtab.update(dict([(symbol, getattr(m, symbol)) for symbol in dir(m)]))
        libsSymtab.update({u'CIC': sys.modules[__name__]})

def loadLibraries():
        u"Import or reload all modules found in %pluginsDir%/CodeInCards/*.py and build a pooled symtab"
        global modulesMap
        libraries = getLibraries()

        # Out with modules that have disappeared, if any.
        for nopy in modulesMap.keys():
                if (nopy + u".py") not in libraries:
                        del modulesMap[nopy]
        # Load or reload each lib with a .py
        for lib in libraries:
                nopy = lib.replace(u".py", u"")
                try:
                        if nopy not in modulesMap:
                                modulesMap[nopy] = __import__(nopy)
                        else:
                                reload(modulesMap[nopy])
                except:
                        print >>sys.stderr, u"Error in %s" % lib
                        traceback.print_exc()
        buildSymtab(modulesMap.values())

def onReloadLibraries():
        try:
                loadLibraries()
                ankiqt.ui.utils.showInfo(u"Libraries reloaded.")
        except Exception as e:
                raise e

def safeSubst(match):
        u"Leave code escape untouched, and flag the need to show 'deck not trusted' message"
        global showTrustMessage
        showTrustMessage = True
        return match.group()

def onConfigureTrust():
        u"Handle selection of Tools->Advanced->CodeInCards Deck Trust"
        trustedDecksDialog = PyQt4.QtGui.QDialog(ankiqt.mw)
        trustedDecksDialog.setWindowTitle(u"Configure CodeInCards Deck Trust")
        l = PyQt4.QtGui.QVBoxLayout()

        # Ugly hack to set a sensible minimum width without using absolute
        # sizes in pixels.  Does QT have a way to set width in 'em'?
        widthLabel = PyQt4.QtGui.QLabel()
        widthLabel.setText(u"------------------------------------------------------")
        widthLabel.setMaximumHeight(1)
        widthLabel.setWordWrap(False)
        l.addWidget(widthLabel)
        
        warningLabel = PyQt4.QtGui.QLabel()
        warningLabel.setText(securityWarning)
        warningLabel.setWordWrap(True)
        warningLabel.setStyleSheet(u"QLabel { color:red; }")
        l.addWidget(warningLabel)

        checkBox = PyQt4.QtGui.QCheckBox()
        checkBox.setText(u"Execute CodeInCards escapes in this deck")
        if deckIsTrusted(ankiqt.mw.deck, ankiqt.mw.config):
                checkBox.setChecked(True)
        l.addWidget(checkBox)

        trustedDecksDialog.connect(checkBox, PyQt4.QtCore.SIGNAL(u"stateChanged(int)"), onCheckBox)
        trustedDecksDialog.setLayout(l)
        trustedDecksDialog.show()

def onCheckBox(newState):
        u"Update config and execution behaviour to match trust dialog checkbox"
        setDeckTrust(newState == PyQt4.QtCore.Qt.Checked, ankiqt.mw.deck, ankiqt.mw.config)
        applyDeckTrust(ankiqt.mw.deck, ankiqt.mw.config)

def deckIsTrusted(deck, config):
        return (CONFIG_KEY in config
                and deckHash(deck) in config[CONFIG_KEY])

def setDeckTrust(trust, deck, config):
        if CONFIG_KEY not in config:
                config[CONFIG_KEY] = {} 

        if trust:
                config[CONFIG_KEY][deckHash(deck)] = u""
        else:
                del config[CONFIG_KEY][deckHash(deck)]

def deckHash(deck):
        return str(deck.name()) + str(deck.created)

# Anki hook
def enableDeckMenuItems(enabled):
        u"Update execution behaviour each time we load a new deck"
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
        u''' Replace &entityname; with corresponding entity '''
        if match.group(u'entname') in htmlentitydefs.name2codepoint:
                return unichr(htmlentitydefs.name2codepoint[match.group(u'entname')])
        # Pass through bad names unchanged
        return match.group()

def cardListData(self, index, role, _old=None):
        u'''
        A clone of anki.ui.cardlist.DeckModel.data() - i.e. the card list
        table cell renderer.
        This is a hack and should be patched in Anki to be hookable instead.
        Hooks will want to know:
          - whether they're rendering Q or A (examining index is fragile)
          - the card object (?not available here?)
        '''
        if not index.isValid():
                return PyQt4.QtCore.QVariant()
        if role == PyQt4.QtCore.Qt.FontRole:
                f = PyQt4.QtGui.QFont()
                f.setPixelSize(self.parent.config[u'editFontSize'])
                return PyQt4.QtCore.QVariant(f)
        if role == PyQt4.QtCore.Qt.TextAlignmentRole and index.column() == 2:
                return PyQt4.QtCore.QVariant(PyQt4.QtCore.Qt.AlignHCenter)
        elif role == PyQt4.QtCore.Qt.DisplayRole or role == PyQt4.QtCore.Qt.EditRole:
                if len(self.cards[index.row()]) == 1:
                        # not cached yet
                        self.updateCard(index)
                s = self.columns[index.column()][1](index)

                if index.column() == 0:
                        QorA = u'q'
                elif index.column() == 1:
                        QorA = u'a'

                if index.column() < 2:
                        card = self.getCard(index)
                        s = evalSide(s, card, QorA, True)
                        s = anki.hooks.runFilter(u"drawSummary", s, card)

                s = re.sub(ur"<li>", ur" &bull; ", s)
                # More aggressive entity reference resolution.
                s = re.sub(ur"&(?P<entname>[a-zA-Z0-9]+);", entitySubst, s)

                s = s.replace(u"<br>", u" ")
                s = s.replace(u"<br />", u" ")
                s = s.replace(u"\n", u"  ")
                s = anki.utils.stripHTML(s)
                s = re.sub(ur"\[sound:[^]]+\]", ur"", s)
                s = s.replace(u"&amp;", u"&")
                s = s.strip()
                return PyQt4.QtCore.QVariant(s)
        else:
                return PyQt4.QtCore.QVariant()


def configureLogging(debug):
        global logger
        if not debug:
                class LoggerStub:
                        def debug(self, s): pass
                logger = LoggerStub()
                return
        import logging
        logger = logging.getLogger(__name__)
        logger.addHandler(logging.FileHandler(LOG_FILENAME, delay=True))
        logger.setLevel(logging.DEBUG)

def init():
        global f
        f = FieldGetter()
        configureLogging(debug)
        action = PyQt4.QtGui.QAction(ankiqt.mw)
        action.setText(u"CodeInCards Deck Trust...")
        ankiqt.mw.connect(action, PyQt4.QtCore.SIGNAL(u"triggered()"), onConfigureTrust)
        ankiqt.mw.mainWin.menuAdvanced.addAction(action)

        action = PyQt4.QtGui.QAction(ankiqt.mw)
        action.setText(u"Reload CodeInCards libraries")
        ankiqt.mw.connect(action, PyQt4.QtCore.SIGNAL(u"triggered()"), onReloadLibraries)
        ankiqt.mw.mainWin.menuAdvanced.addAction(action)

        # FIXME: loading after SynSugar plugin causes problems.  Ideally we'd
        # do something like this:
        #   anki.hooks.addHook(u"allPluginsLoaded", prependOurHooks)
        #   def prependOurHooks():
        #           anki.hooks.prependHook(u"drawAnswer", evalAnswer)
        #           anki.hooks.prependHook(u"drawQuestion", evalQuestion)
        # It's a bit arrogant to assume you have the right to be the first
        # hook, but code is rather sensitive to modifications.
        # In the meantime, hack it by modifying anki.hooks internals.
        if 'SynSugar' in sys.modules:
                anki.hooks._hooks['drawAnswer'].insert(0, evalAnswer)
                anki.hooks._hooks['drawQuestion'].insert(0, evalQuestion)
        else:
                anki.hooks.addHook(u"drawAnswer", evalAnswer)
                anki.hooks.addHook(u"drawQuestion", evalQuestion)
        anki.hooks.addHook(u"enableDeckMenuItems", enableDeckMenuItems)
        
        ankiqt.ui.cardlist.DeckModel.data = anki.hooks.wrap(ankiqt.ui.cardlist.DeckModel.data, cardListData, u"wrap")

        # Anki cleverly checks whether there's any point rendering a card,
        # deciding that if no %(foo)s substitutions get made then the card
        # is empty.  Because we use $f['blah'] we'll hack it for now.
        def availableCardModels(self, fact, checkActive=True):
                models = []
                for cardModel in fact.model.cardModels:
                        if cardModel.active or not checkActive:
                                models.append(cardModel)
                return models
        anki.deck.Deck.availableCardModels = availableCardModels


        sys.path.append(getLibraryDir())
        loadLibraries()

init()

# vim: softtabstop=8 shiftwidth=8 expandtab
