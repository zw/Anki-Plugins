# Future:
#
#   ability to insert context somewhere else if appropriate and have the original one not show up; guess context would have to be last thing shown because it can't be disabled once already shown...or can it?  we could id it or mark it up.
#   softgroup - put grey brackets around something like (calcitonin gene)-related peptide
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
LP = "L<span style='vertical-align:sub; font-size:small; '>p</span>"

CD8 = "CD8<span style='vertical-align:super; font-size:small; '>+</span>"
CD4 = "CD4<span style='vertical-align:super; font-size:small; '>+</span>"

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
M1 = "M<span style='vertical-align:sub; font-size:small; '>1</span>"
M2 = "M<span style='vertical-align:sub; font-size:small; '>2</span>"
M3 = "M<span style='vertical-align:sub; font-size:small; '>3</span>"

ST = "<span style='vertical-align:super; font-size:small; '>st</span>"
ND = "<span style='vertical-align:super; font-size:small; '>nd</span>"
RD = "<span style='vertical-align:super; font-size:small; '>rd</span>"
TH = "<span style='vertical-align:super; font-size:small; '>th</span>"

G0 = "G<span style='vertical-align:sub; font-size:small; '>0</span>"
G1 = "G<span style='vertical-align:sub; font-size:small; '>1</span>"
G2 = "G<span style='vertical-align:sub; font-size:small; '>2</span>"
GAI = "G<span style='vertical-align:sub; font-size:small; '>&alpha;i</span>"
GAQ = "G<span style='vertical-align:sub; font-size:small; '>&alpha;q</span>"
IP3R = "IP<span style='vertical-align:sub; font-size:small; '>3</span>R"
GAS = "G<span style='vertical-align:sub; font-size:small; '>&alpha;s</span>"
INA = "I<span style='vertical-align:sub; font-size:small; '>Na</span>"
IK = "I<span style='vertical-align:sub; font-size:small; '>K</span>"
ICA = "I<span style='vertical-align:sub; font-size:small; '>Ca</span>"
IFUNNY = "I<span style='vertical-align:sub; font-size:small; '>f</span>"
NADP = "NADP<span style='vertical-align:super; font-size:small; '>+</span>"

CAI = "[" + CA + "]<span style='vertical-align:sub; font-size:small; '>i</span>"
CAMPI = "[cAMP]<span style='vertical-align:sub; font-size:small; '>i</span>"

# Tried many other Unicode arrow symbols but they're ugly in some fonts
DA = "<span style='font-weight:bold; color:blue; '>&darr;</span>"
UA = "<span style='font-weight:bold; color:blue; '>&uarr;</span>"
DDA = "<span style='font-weight:bold; color:blue; '>&#x21ca;</span>"
UUA = "<span style='font-weight:bold; color:blue; '>&#x21c8;</span>"

# A "P" in a circle, denoting phosphorylation
PPN = "&#x024c5;" 

T4 = "&there4;"
# because (upside down therefore)
BC = "&#x2235;"

POS = "<span style='color:green; font-weight:bold; '>&oplus;</span>"
NEG = "<span style='color:red; font-weight:bold; '>&#x02296;</span>"

# There's no X-bar in Unicode; combine x and the bar instead.
# FIXME: this doesn't work in some fonts -- why not?
MEAN = "x&#772;"

# Interrobang
IBANG = "&#x203D;"

# Smiley
SMILE = SMILEY = "&#x263a;"

# Replacement way of saying '<br/>', because that gets replaced with '\n' before execution of escapes.
BR = "<br />"

# Meaning, not presentation :)
raised = raises = increased = high = higher = greater = elevated = raising = maximises = maximising = UA
lowered = lowers = lower = lowering = minimises = minimising = reduces = reducing = reduced = low = decreased = decreasing = depressed = DA
inhibits = inhibited = inhibiting = NEG
activates = promotes = activating = promoting = POS


HL_FORMAT = """<span style='color:blue; font-weight:bold;'>%s</span>"""

import re


import logging
LOG_FILENAME = '/tmp/cic-zak.out'
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOG_FILENAME, delay=True))
logger.setLevel(logging.DEBUG)


import random
import sys
ETREE_PATH    = "/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/"
ETREE_PATH2   = "/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/lib-dynload/"
MARKDOWN_PATH = "/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages/"
sys.path.extend([MARKDOWN_PATH,ETREE_PATH,ETREE_PATH2])
import markdown


import CodeInCards as CIC

curRef = 1

def style(text, style):
        return "<span style='%s'>%s</span>" % (style,text)

def null(): return ''

# Could implement CICstart to clear refs and CICstop to produce a list,
# and have that list hidden unless we mouse over it.
# For now just use a char and mention it in 'source' field by that char, by hand
def ref(text, link = None):
        # small is a hack around Qt's limited CSS support; see http://tinyurl.com/yeuthno
        # would rather use 'em's to measure font relatively
        if link == None:
                return "<span style='color:blue; vertical-align:super; font-size:small; '>[%s]</span>" % (text)
        else:
                return "<span style='color:blue; vertical-align:super; font-size:small; '>[<a href='%s'>%s</a>]</span>" % (link, text)

def prob(text):
        if text == "":
                return fixme()
        return ref(text)

# Meaning, not presentation!
# This should really squirrel the text away and let me calls notes() later.
def note(short, long):
        return u'''<span title="%s">%s</span>''' % (long, ref(short))

# Presentation, not meaning!
def hidden(hoverRegionText, hiddenText):
        return u'''<span title="%s">%s</span>''' % (hiddenText, hoverRegionText)

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

def hl(text):
        return HL_FORMAT % text

# for Major System mnemonic highlighting
def hlCaps(text):
        def hlSubst(mo):
                return hl(mo.group())
        return re.sub("[A-Z]+", hlSubst, text)
        

# e.g. Which is biggest, $shuffle("a whale,an elephant,a mouse", "or")?
def shuffle(text, sep=",", join=", ", lastJoin=" and "):
        parts = text.split(sep)
        if len(parts) <= 1:
                return text
        random.shuffle(parts)
        if len(parts) == 2:
                return parts[0] + lastJoin + parts[1]
        return join.join(parts[:-1]) + lastJoin + parts[-1]

# generic improvement on <sub>blah</sub>
def sub(text):
        return u"<span style='vertical-align:sub; font-size:small; '>%s</span>" % text

def sup(text):
        return u"<span style='vertical-align:super; font-size:small; '>%s</span>" % text


def ifModelNameContains(needle, text):
        if CIC.card.cardModel.name.lower().find(needle) != -1:
                return text
        return ""

def noteStyle(text):
        return u"<div style='font-style:italic;'>" + md(text) + u"</div>"

def md(text):
        logger.debug("prebr text is " + text)
        text = re.sub("<br\s*/>", "\n", text)
        logger.debug("postbr premd text is " + text)
        text = markdown.markdown(text)
        logger.debug("postmd prehack text is " + text)
        text = re.sub("\n", "", text)
        logger.debug("posthack text is " + text)
        return text

# vim: softtabstop=8 shiftwidth=8 expandtab
