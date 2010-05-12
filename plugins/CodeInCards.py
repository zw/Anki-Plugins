'''
CodeInCards - a plugin to embed Python code in cards/card templates
 
Loads substition "libraries" from %pluginsFolder%/CodeInCards/*.py
then provides syntax to let you substitute library calls into cards.

Escapes may be included either encoded as HTML or among the markup
(i.e. you can enter them directly in the browser-editor field, or the
"HTML editor".  Four escape formats are supported; the first pair
values brevity over flexibility:

  $varName
    Interpolate variable "varName".  Subscripting and dot-whatever
    isn't supported (yet!) but you can use another format.

  $functionName(arg, arg, ...)
    Call "fuctionName" with supplied args, and interpolate the returned
    string, e.g.:
      $myFunc(myVar, "another arg")
    Closing brackets aren't allowed anywhere in the args, so you can't say:
      $functionName("a (broken) example")
    You must also be careful with quotes around arguments.  Single
    quotes tend to work better than doubles.

The second pair is more flexible but more verbose:

  {%= <expression> %}
    Evaluates <expression> (a single expression) and substitutes
    result, e.g.:
      {%= 6 * 9 %}
    will yield "42" in the card or template (well, OK, "54").  Function
    calls also work, e.g.:
      {%= functionName("a (working) example", someOtherFunc()) %}

  {% <code> %}
    Executes <code>; anything printed to stdout gets substituted, e.g.:
      {%
      if random.randint(0, 1000000) == 42:
        print "The Ultimate Answer!"
      %}

Apart from globals in your libraries you can also use the following
symbols:
   QorA - 'q' or 'a', depending what card side is being rendered
   card - the card being rendered; see the Anki source

Compile errors get interpolated as HTML-ized strings.

The string '<br />' is removed from within code if present before
executione.  This allows you to add code in the card editor as well as
card templates but means you can't include a BR in an escape.  If
that matters to you, define a variable in your library called "BR" and
use than in place of "<br/>".  No other HTML is removed, so be careful
not to style any part of an escape entered in an card editor field.

Get a small example library here: http://bit.ly/bit.ly/codeincards
save it in %pluginsFolder%/CodeInCards/ and read it to see some
trivial examples.
 
Caveats:
  - This module is a gaping security hole if you ever import cards from
    untrusted sources.
  - At the moment there's no way to prevent the escapes appearing in the
    browser, so cards start to look quite ugly.
  - It's too easy to get carried away and implement your own SRS
    mini-language packed with syntactic sugar.

TODO: add individual fact fields alongside QorA and card in a dict
  (need to marry up card.fact.values with card.model.names)
TODO: implement m4's 'dnl' feature - perhaps by terminating a
  multiline with "%}." instead of "%}"
TODO: reload libraries without restarting Anki
TODO: support $foo['index'] and maybe $foo.bar and $foo.bar()
TODO: remove escapes from browser; there's no hook, but a sick hack
  might be to wrap stripHTML()
'''

import re
import sys
import os
import traceback

import anki

# For debugging.
#import logging
#LOG_FILENAME = '/tmp/logging_example.out'
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
