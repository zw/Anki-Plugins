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

NA = "Na<sup>+</sup>"
K = "K<sup>+</sup>"
CA = "Ca<sup>2+</sup>"
H = "H<sup>+</sup>"
H3O = "H<sub>3</sub>O<sup>+</sup>"
H2O = "H<sub>2</sub>O"
CO2 = "CO<sub>2</sub>"

import re
import logging
LOG_FILENAME = '/tmp/cic-zak.out'
logging.basicConfig(filename=LOG_FILENAME,level=logging.CRITICAL)
#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

import sys
ETREE_PATH    = "/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/"
ETREE_PATH2   = "/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/lib-dynload/"
MARKDOWN_PATH = "/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages/"
sys.path.extend([MARKDOWN_PATH,ETREE_PATH,ETREE_PATH2])
import markdown

def md(text):
        logging.debug("prebr text is " + text)
        text = re.sub("<br\s*/>", "\n", text)
        logging.debug("postbr premd text is " + text)
        text = markdown.markdown(text)
        logging.debug("postmd prehack text is " + text)
        text = re.sub("\n", "", text)
        logging.debug("posthack text is " + text)
        return text

# vim: softtabstop=8 shiftwidth=8 expandtab
