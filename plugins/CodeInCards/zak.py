# Future:
#
#   $class(<text>, <class>)
#     applies CSS class to text, as defined in either the card template or an external stylesheet called ss.css in the plugins directory
#   $rcsl(orange, apple, pear tree, honey bee)
#     randomises the order of the given comma-separated list
#   $rorl(go big, go home)
#     randomises the order of the given comma-separated list, but uses "or" between the final two items
#   $randl(swings, roundabouts)
#     randomises the order of the given comma-separated list, but uses "and" between the final two items
#   $pick(woven, trabecular, cancellous, spongy)
#     randomly pick any of a list of strings; also sets a variable for use by...
#   $pick2(woven, trabecular, cancellous, spongy)
#     pick the same indexed thing as was picked by $pick(...);
#     this allows a random choice to be made once then used in both question and answer
#   $list(<yaml>)
#     HTML-ify a yaml structure to make a list, seeing as QT can't leave 'em the fuck alone
#   $rlist(<yaml>)
#     same as $list but randomises the 1st-level order

NA = "Na<span style='vertical-align:super; font-size:small; '>+</span>"
CA = "Ca<span style='vertical-align:super; font-size:small; '>2+</span>"
NCX = "%s/%s" % (NA, CA)
K = "K<span style='vertical-align:super; font-size:small; '>+</span>"
KD = "K<span style='vertical-align:sub; font-size:small; '>D</span>"
EC50 = "EC<span style='vertical-align:sub; font-size:small; '>50</span>"
LD50 = "LD<span style='vertical-align:sub; font-size:small; '>50</span>"
H = "H<span style='vertical-align:super; font-size:small; '>+</span>"
H3O = "H<span style='vertical-align:sub; font-size:small; '>3</span>O<span style='vertical-align:super; font-size:small; '>+</span>"
H2O = "H<span style='vertical-align:sub; font-size:small; '>2</span>O"
CO2 = "CO<span style='vertical-align:sub; font-size:small; '>2</span>"
O2 = "O<span style='vertical-align:sub; font-size:small; '>2</span>"

PGG2 = "PGG<span style='vertical-align:sub; font-size:small; '>2</span>"
PGH2 = "PGH<span style='vertical-align:sub; font-size:small; '>2</span>"
PGI2 = "PGI<span style='vertical-align:sub; font-size:small; '>2</span>"
PGI3 = "PGI<span style='vertical-align:sub; font-size:small; '>3</span>"
TXA2 = "TXA<span style='vertical-align:sub; font-size:small; '>2</span>"
TXA3 = "TXA<span style='vertical-align:sub; font-size:small; '>3</span>"

A1 = "&alpha;<span style='vertical-align:sub; font-size:small; '>1</span>"
A2 = "&alpha;<span style='vertical-align:sub; font-size:small; '>2</span>"
B1 = "&beta;<span style='vertical-align:sub; font-size:small; '>1</span>"
B2 = "&beta;<span style='vertical-align:sub; font-size:small; '>2</span>"

ST = "<span style='vertical-align:super; font-size:small; '>st</span>"
ND = "<span style='vertical-align:super; font-size:small; '>nd</span>"
RD = "<span style='vertical-align:super; font-size:small; '>rd</span>"
TH = "<span style='vertical-align:super; font-size:small; '>th</span>"

G0 = "G<span style='vertical-align:sub; font-size:small; '>0</span>"
G1 = "G<span style='vertical-align:sub; font-size:small; '>1</span>"
G2 = "G<span style='vertical-align:sub; font-size:small; '>2</span>"

# Tried many other Unicode arrow symbols but they're ugly in some fonts
DA = "<span style='font-weight:bold; color:blue; '>&darr;</span>"
UA = "<span style='font-weight:bold; color:blue; '>&uarr;</span>"
DDA = "<span style='font-weight:bold; color:blue; '>&#x21ca;</span>"
UUA = "<span style='font-weight:bold; color:blue; '>&#x21c8;</span>"

# A "P" in a circle, denoting phosphorylation
PHN = "&#x024c5;" 

T4 = "&there4;"
# because (upside down therefore)
BC = "&#x2235;"

POS = "<span style='color:green; font-weight:bold; '>&oplus;</span>"
NEG = "<span style='color:red; font-weight:bold; '>&#x02296;</span>"

import re
#import logging
#LOG_FILENAME = '/tmp/cic-zak.out'
#logging.basicConfig(filename=LOG_FILENAME,level=logging.CRITICAL)
#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

import random
import sys
ETREE_PATH    = "/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/"
ETREE_PATH2   = "/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/lib-dynload/"
MARKDOWN_PATH = "/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages/"
sys.path.extend([MARKDOWN_PATH,ETREE_PATH,ETREE_PATH2])
import markdown

curRef = 1

def style(text, style):
        return "<span style='%s'>%s</span>" % (style,text)

def null(): return ''

# Could implement CICstart to clear refs and CICstop to produce a list,
# and have that list hidden unless we mouse over it.
# For now just use a char and mention it in 'source' field by that char, by hand
def ref(text, link = None):
        # small is a hack around Qt's limited CSS support; see http://tinyurl.com/yeuthno
        # would rather use em
        if link == None:
                return "<span style='color:blue; vertical-align:super; font-size:small; '>[%s]</span>" % (text)
        else:
                return "<span style='color:blue; vertical-align:super; font-size:small; '>[<a href='%s'>%s</a>]</span>" % (link, text)

def fixme(link = None):
        # small is a hack around Qt's limited CSS support; see http://tinyurl.com/yeuthno
        # would rather use em
        if link == None:
                return "<span style='color:blue; vertical-align:super; font-size:small; '>[?]</span>"
        else:
                return "<span style='color:blue; vertical-align:super; font-size:small; '><a href='%s'>[?]</a></span>" % (link)

def link(url, text = None):
        if text == None:
                return "<a href='%s'>%s</a>" % (url, url)
        else:
                return "<a href='%s'>%s</a>" % (url, text)

# for Major System mnemonic highlighting
def hlCaps(text):
        def hl(mo):
                return "<span style='color:blue; '>%s</span>" % mo.group()
        return re.sub("[A-Z]+", hl, text)
        

# e.g. Which is biggest, $shuffleCSL("or", "my cock,your cock")?
def shuffleCSL(lastWord, text):
        parts = text.split(",")
        random.shuffle(parts)
        return ", ".join(parts[:-1]) + " " + lastWord + " " + parts[-1]

# generic improvement on <sub>blah</sub>
def sub(text):
        return "<span style='vertical-align:sub; font-size:small; '>%s</span>" % text

def md(text):
        #logging.debug("prebr text is " + text)
        text = re.sub("<br\s*/>", "\n", text)
        #logging.debug("postbr premd text is " + text)
        text = markdown.markdown(text)
        #logging.debug("postmd prehack text is " + text)
        text = re.sub("\n", "", text)
        #logging.debug("posthack text is " + text)
        return text

# vim: softtabstop=8 shiftwidth=8 expandtab
