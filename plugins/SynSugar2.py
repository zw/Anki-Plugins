# Some quick and dirty hacks for formatQA that do one-off substitutions.
#
# => becomes &rArr;
# &amp;rArr; becomes the actual unicode character

import re
#import htmlentitydefs

from anki.hooks import addHook

#def ent_subst(match):
#        return unichr(htmlentitydefs.name2codepoint[match.group('entname')])

def formatQA(html, type, cid, mid, fact, tags, cm):
        # html is what Anki has already generated
        html = re.sub("&amp;(?P<entname>.*?);", "&\g<entname>;", html)
        html = re.sub("(?<=[ >])=&gt;(?=[ <])", "&rArr;", html)
        return html

addHook("formatQA", formatQA)

# vim: softtabstop=8 shiftwidth=8 expandtab
