# -*- coding: utf-8 -*-
# Treat card HTML as Markdown plus some personal extensions.
# Some of these substitutions could be done permanently to the source fields
# without losing any editability; others could not.
#
# => becomes &rArr;
# &amp;rArr; becomes the actual unicode character
#
# Smartypants:
#  ... => …
#  "curly quotes" => “curly quotes”
#  -- => en-dash
#  --- => em-dash
#  :) => &#x263a; (unicode smiley face) 
#  "=>" or "=&gt;" becomes &rArr; ("equals, greater than" turns into "&rarr;") 

import re
import htmlentitydefs

debug = True
LOG_FILENAME = u'/tmp/SynSugar.out'
logger = None

import anki.hooks

import sys
ETREE_PATH    = u"/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/"
ETREE_PATH2   = u"/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/lib-dynload/"
MARKDOWN_PATH = u"/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages/"
sys.path.extend([MARKDOWN_PATH,ETREE_PATH,ETREE_PATH2])
import markdown


NO_MARKDOWN_TAG = u"notMarkdown"

def ent_subst(match):
        if match.group(u'entname') in htmlentitydefs.name2codepoint:
                return unichr(htmlentitydefs.name2codepoint[match.group(u'entname')])
        # Pass through bad names unchanged
        return match.group()

def reallySplit(tags):
        splitTags = []
        for t in tags.split():
                logger.debug(u"tag is " + unicode(type(t)) + unicode(t))
                splitTags.append(t)
        return splitTags

def processSide(html, card):
        if re.search(ur"SynSugarOff", html):
                return html
        # html is what Anki has already generated
        if not re.search(ur"SynSugarEntsOff", html):
                html = re.sub(ur"&amp;(?P<entname>[a-zA-Z0-9]+);", ur"&\g<entname>;", html)
        # =&gt; may well come directly before or after tags - <li>=&gt; being a classic
        html = re.sub(ur"(?<=[ >(])=(&gt;|>)(?=[ <])", ur"&rArr;", html)
        # Smartypants ideas ( http://daringfireball.net/projects/smartypants/ )
        html = re.sub(ur"\.\.\.", ur"&hellip;", html)
        # Quotes around "stuff that's, well, texty?", except after an '=' where they're
        # probably HTML attributes.
        html = re.sub(ur'(?<!=)"([a-zA-Z\', ?]+)"', ur"&ldquo;\g<1>&rdquo;", html)
        # Dashes only if not preceded or followed by dashes.
        html = re.sub(ur'(?<!-)--(?!-)', ur"&ndash;", html)
        html = re.sub(ur'(?<= )---(?= )', ur"&mdash;", html)
        # Smiley
        html = re.sub(ur':\)', ur"&#x263a;", html)

        logger.debug(u"tags are " + unicode(card.fact.tags) + unicode(type(card.fact.tags)))
        logger.debug(u"fixed tags are " + unicode(reallySplit(card.fact.tags)))
        if NO_MARKDOWN_TAG not in reallySplit(card.fact.tags):
                # Can't do this - span doesn't wrap quite the whole side when there are templates
                #logger.debug("pre strip:\n" + html)
                #html = re.sub('^<span[^>]*>', "", html)
                #html = re.sub('</span>$', "", html)
                logger.debug("pre strip:\n" + html)
                html = re.sub(ur'(?s)^<center>(?P<content>.*?)</center>$', ur"\g<content>", html)
                html = re.sub(ur'(?s)^<table width=95%>(?P<content>.*?)</table>$', ur"\g<content>", html)
                html = re.sub(ur'(?s)^<tr>(?P<content>.*?)</tr>$', ur"\g<content>", html)
                html = re.sub(ur'(?s)^<td align=[a-z]+>(?P<content>.*?)</td>$', ur"\g<content>", html)
                html = re.sub(ur'(?s)^<div class="card." id="cm[aq][a-fA-F0-9]+">(?P<content>.*?)</div>$', ur"\g<content>", html)
                # Can't do this either - no way to ensure the <span> and </span> are matching 'cause we can't use ^$ for it.
                #html = re.sub(ur'(?s)<span class="fm[a-fA-F0-9]+".*?>(?P<content>.*?)</span>', ur"\g<content>", html)
                logger.debug("post strip, pre whitespace=>newline fudge:\n" + html)
                # I think this fudge was here to deal with <p> that QT/Anki
                # inserted but which weren't wanted.
                html = re.sub(ur"<br[^>]*>", ur"\n", html)
                #html = re.sub(ur"<p>", ur"", html)
                #html = re.sub(ur"</p>", ur"\n", html)

                # FIXME: What was the point of this again?
                #if not re.search(ur"SynSugarEntsOff", html):
                #        html = re.sub(ur"&(?P<entname>[a-zA-Z0-9]+);", ent_subst, html)
                logger.debug(u"post whitespace=>newline fudge, pre markdown:\n" + html)
                html = markdown.markdown(html)
                logger.debug(u"post markdown:\n" + html)
                # QT's widget copies newlines in a few cases,
                # so get rid of those now we're formatted
                html = re.sub(ur"</li>\n", ur"</li>", html)
                html = re.sub(ur"</ul>\n", ur"</ul>", html)
                html = re.sub(ur"<ul>\n", ur"<ul>", html)
                html = re.sub(ur"</p>\n", ur"</p>", html)
                logger.debug(u"final post whitespace fudge:\n" + html)
                html = u'<div class="giveOver">' + html + u"</div>"

        return html

def addStyles(css, card):
        css += u"""\
                .giveOver {font-size:14pt; margin-left:10px; text-align:left; }
                hr {margin-left:0px; }
        """
        return css

def configureLogging(debug):
        global logger
        if not debug:
                class LoggerStub:
                        def debug(s): pass
                logger = LoggerStub()
                return
        import logging
        logger = logging.getLogger(__name__)
        logger.addHandler(logging.FileHandler(LOG_FILENAME, delay=True))
        logger.setLevel(logging.DEBUG)

configureLogging(debug)
anki.hooks.addHook("drawQuestion", processSide)
anki.hooks.addHook("drawAnswer", processSide)
anki.hooks.addHook("addStyles", addStyles)
# A custom hook provided by CodeInCards; render a card list cell
anki.hooks.addHook("drawSummary", processSide)

# vim: softtabstop=8 shiftwidth=8 expandtab
