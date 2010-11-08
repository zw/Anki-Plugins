# -*- coding: utf-8 -*-
# Treat card HTML as Markdown when formatting.

import re
import anki.hooks
import markdown

LOG_FILENAME = u"/tmp/markdown.log"
NO_MARKDOWN_TAG = u"notMarkdown"

def formatQA(html, type, cid, mid, fact, tags, cm):
    logger.debug(u"before markdown, html is:\n" + html)
    if NO_MARKDOWN_TAG not in tags:
        html = markdown.markdown(html)
        # QTextEdit doesn't seem to condense whitespace, but we can force
        # sensible layout while maintaining document structure by just removing
        # some newlines.
        html = re.sub(ur"</li>\n", ur"</li>", html)
        html = re.sub(ur"</ul>\n", ur"</ul>", html)
        html = re.sub(ur"<ul>\n", ur"<ul>", html)
        html = re.sub(ur"</p>\n", ur"</p>", html)

    logger.debug(u"after markdown, html is:\n" + html)
    return html

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

configureLogging(False)
anki.hooks.addHook("formatQA", formatQA)

# vim: softtabstop=4 shiftwidth=4 expandtab
