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

import re
import htmlentitydefs

import logging
LOG_FILENAME = '/tmp/synsugar.out'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

logging.debug("alive")

import anki.hooks

import sys
ETREE_PATH    = "/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/"
ETREE_PATH2   = "/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/lib-dynload/"
MARKDOWN_PATH = "/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages/"
sys.path.extend([MARKDOWN_PATH,ETREE_PATH,ETREE_PATH2])
import markdown


NO_MARKDOWN_TAG = u"notMarkdown"

def ent_subst(match):
        if match.group('entname') in htmlentitydefs.name2codepoint:
                return unichr(htmlentitydefs.name2codepoint[match.group('entname')])
        # Pass through bad names unchanged
        return match.group()

def reallySplit(tags):
        splitTags = []
        for t in tags:
                splitTags.extend(t.split())
        return splitTags

def formatQA(html, type, cid, mid, fact, tags, cm):
        # html is what Anki has already generated
        html = re.sub("&amp;(?P<entname>[a-zA-Z0-9]+);", "&\g<entname>;", html)
        # =&gt; may well come directly before or after tags - <li>=&gt; being a classic
        html = re.sub("(?<=[ >])=&gt;(?=[ <])", "&rArr;", html)
        # Smartypants ideas ( http://daringfireball.net/projects/smartypants/ )
        html = re.sub("\.\.\.", "&hellip;", html)
        # Quotes around "stuff that's, well, texty", except after an '=' where they're
        # probably HTML attributes.
        html = re.sub('(?<!=)"([a-zA-Z\', ]+)"', "&ldquo;\g<1>&rdquo;", html)
        # Dashes only if not preceded or followed by dashes.
        html = re.sub('(?<!-)--(?!-)', "&ndash;", html)
        html = re.sub('(?<= )---(?= )', "&mdash;", html)

        logging.debug("tags are " + str(tags))
        logging.debug("fixed tags are " + str(reallySplit(tags)))
        if NO_MARKDOWN_TAG not in reallySplit(tags):
                # Can't do this - span doesn't wrap quite the whole side when there are templates
                #logging.debug("pre strip:\n" + html)
                #html = re.sub('^<span[^>]*>', "", html)
                #html = re.sub('</span>$', "", html)
                html = re.sub('^(<span[^>]*>)', "\g<1>\n\n", html)
                logging.debug("pre fudge:\n" + html)
                html = re.sub("<br[^>]*>", "\n", html)
                html = re.sub("<p>", "", html)
                html = re.sub("</p>", "\n", html)
                html = re.sub("&(?P<entname>[a-zA-Z0-9]+);", ent_subst, html)
                logging.debug("post fudge but pre markdown:\n" + html)
                html = markdown.markdown(html)
                logging.debug("post markdown:\n" + html)
                # QT's widget copies newlines in a few cases,
                # so get rid of those now we're formatted
                html = re.sub("</li>\n", "</li>", html)
                html = re.sub("</ul>\n", "</ul>", html)
                html = re.sub("<ul>\n", "<ul>", html)
                html = re.sub("</p>\n", "</p>", html)
                # Oh, and we inserted two more we no longer need.
                html = re.sub('^(<span[^>]*>)\n\n', "\g<1>", html)
                logging.debug("final post whitespace fudge:\n" + html)

        return html

anki.hooks.addHook("formatQA", formatQA)

# vim: softtabstop=8 shiftwidth=8 expandtab
