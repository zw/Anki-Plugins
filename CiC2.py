# -*- coding: utf-8 -*-
# Execute embedded Lua code in fields.
# 
# Currently supported:
#  [*= expression *]  will evaluate expression upon fact save
#  [* chunk *]  will execute chunk upon fact save; any value left in variable 'yield' will be substituted
#  $foo  will evaluate symbol foo as an expression
#  $foo!CRP   will be treated just like "$foo CRP" but without the space
#  $foo(args)  will invoke foo as a function, passing args
#  dnl  will discard any characters that might follow it, up to and including a newline, m4-style
# 
# Context available to Lua code:
#  CiC.QorA will be "question" or "answer" as appropriate
#  CiC.fields will be a dict indexable by field name to get string value
#
# TODO:
#  $foo[bar]  will yield entry 'bar' in table foo, or access member 'bar'
#  $foo.bar   will yield entry 'bar' in table foo, or access member 'bar'
#  $$  will yield a literal dollar (although as $0.02 and bare " $ " both do what you mean, you're unlikely to need it)
#  CiC.fact will be the Anki 'Fact' object, notably with the facility to pull out fields using CiC.fact["context"]
#  [!"example"*= expression *]  will evaluate expression upon card review
#  [!"example"* chunk *]  will execute chunk upon card review; any value left in variable 'yield' will be substituted
#
# The nesting problem
# ===================
#
# It's convenient to express the card templates of a model in code.  This
# requires referring to fields within the fact.  You might try, for example:
#    $ifnem("%(question)s", ...)
# Problem is that the 'question' field might well contain quotes or brackets
# in their natural English text.  Brackets are essential for CiC to frame the
# convenient compact form $fn(args).  Quotes would mess with Lua.
#
# You could force the user to encode quotes and brackets somehow, but then
# you're making your field text hard to read (there are already enough
# abbreviations!).  So you have to allow quotes and brackets.
#
# Perhaps next you try the verbose escape format:
#    [* yield = ifnem("%(question)s", ...) *]
# but that still has the quotes problem.
#
# Perhaps next you try referring directly to the contents of the field, which
# you stuff into Lua's execution context as globals:
#    $ifnem(CiC.fields.question, ...)
# That's fine, but now you have to evaluate fields to get a value for the
# variable before evaluating the card template side that contains it --- you
# need nested execution.  Doable with recursion, although it does make sense
# to prevent fields from causing infinite recursion by referring to themselves.
# It might also make sense to prevent them from referring to each other,
# because a mutual reference would also cause cyclic recursion.

import traceback
import os
import re
import anki.hooks
import ankiqt
import lupa

LOG_FILENAME = u"/tmp/cic2.log"
NO_EXEC_TAG = u"notExec"

lua = None

def init():
    configureLogging(True)
    anki.hooks.addHook("formatQA_0", formatQA)
    global lua
    lua = lupa.LuaRuntime()
    lua.execute(u"""package.path = '""" + getLibraryDir() + u"""/?.lua'""")
    for library in getLibraries():
        basename = re.sub(ur"\.lua$", ur"", library)
        lua.require(basename)

def formatQA(html, QorA, cid, mid, fact, tags, cm):
    return processEscapes(html, QorA, fact, tags)

def processEscapes(text, QorA, fact, tags, isField=False):
    logger.debug(u"before exec, text is:\n" + text)
    if NO_EXEC_TAG in tags:
        return text

    # Give the Lua code some context regarding this escape.
    # This allows Lua code like:
    #    if CiC.QorA == "question" then <foo> else <bar> end
    # FIXME: I'm sure there's a neat Lupa way to do field access that just uses
    # __getitem__ or something.  Implement a menu that fires up a python
    # prompt on any old card allowing us to fish about in Lua to find the way.
    # I also really don't like hard-coded index into the Field table; might be
    # good enough for formatQA, but it's not good enough for me! :)

    # Code escapes can be present in fields and fields can be evaluated before
    # being nested in models via CiC.fields.fieldname, but fields don't get to
    # reference each other.
    if not isField:
        fieldname2value = dict()
        for (name, valueTuple) in fact.items():
            fieldValue = valueTuple[1]  # Ick
            fieldname2value[name] = processEscapes(fieldValue, QorA, fact, tags, isField=True)
        lua.globals().f = fieldname2value
    lua.globals().CiC = {
        u"QorA": QorA,
    }

    text = re.sub(ur"dnl.*\n", ur"", text)
    text = re.sub(ur"""(?xms)        # multiline, mostly in case an embedded %(field)s is
                       \[\*=         # opening tag: [*=
                       \s*           # eat leading whitespace
                       (?P<expr>.+?) # any old content; non-greedy
                                      # so that {%= ... %} foo {%= ... %}
                                      # will work on a single line
                       \*\]          # closing tag
                       """, evalLua, text)
    # Identical except for opening tag, and execute not eval.
    text = re.sub(ur"""(?xms)          # multiline, because code reads easier with whitespace
                         \[\*          # opening tag: [*
                         \s*           # eat leading whitespace
                         (?P<chunk>.+?) # any old content; non-greedy
                                       # so that {% ... %} foo {% ... %}
                                       # will work on a single line
                         \*\]          # closing tag
                         """, execLua, text)
    text = re.sub(ur"""(?xms)
                       (?<!\$)       # $$... isn't substituted
                       \$            # leading dollar
                       (?P<expr>     # start capture
                          [a-zA-Z_]\w*   # standard identifier rules: $idEN_tifi13r
                          (?P<tail>      # start stuff-following-identifier list, just for structure
                            (?P<args>      # start group optional args list
                              \(             # $fn(args...)
                              [^)]*          # greedily include all non-[closing parentheses]
                              \)             # end args list
                              |
                              \[             # $fn[subscript]
                              [^]]+          # greedily include all non-[closing brackets]
                              \]             # end subscript
                            )              # end group optional args list
                            |
                            (?P<dotmember>   # $somestruct.somemember
                              \.
                              [a-zA-Z_]\w*
                            )
                          )?             # end group optional args list
                       )             # finish capture
                       (!?)          # eat an optional trailing pling
                       """, evalLua, text)
    #text = re.sub(ur'\$\$', ur'$', text)
    
    logger.debug(u"after exec, text is:\n" + text)
    return text

def evalLua(matchObj):
    m = matchObj
    try:
        ret = unicode(lua.eval(m.group(u'expr')))
    except:
        #print(traceback.format_exc())
        ret = u"(!) " + unicode(m.group(u'expr'))
    return ret

def execLua(matchObj):
    m = matchObj
    try:
        lua.execute(u'yield = ""')
        lua.execute(m.group(u'chunk'))
        ret = lua.eval(u'tostring(yield)')
    except:
        print(traceback.format_exc())
        ret = u"(!) " + unicode(m.group(u'chunk'))
    return ret

def getLibraryDir():
    p = os.path.join(ankiqt.mw.pluginsFolder(), u"CiC2")
    if not os.path.exists(p):
        os.mkdir(p)
    return p

def getLibraries():
    return [p for p in os.listdir(getLibraryDir()) if p.endswith(u".lua")]

def configureLogging(debug):
    global logger
    if not debug:
        class LoggerStub:
            def debug(*a): pass
        logger = LoggerStub()
        return
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.FileHandler(LOG_FILENAME, delay=True))
    logger.setLevel(logging.DEBUG)

init()

# vim: softtabstop=4 shiftwidth=4 expandtab
