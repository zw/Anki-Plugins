# -*- coding: utf-8 -*-
# Translate punctuation according to SmartyPants rules.

import re
import anki.hooks
import smartypants

LOG_FILENAME = u"/tmp/smartypants.log"
NO_SMARTYPANTS_TAG = u"notSmartyPants"

def formatQA(html, type, cid, mid, fact, tags, cm):
    logger.debug(u"before smartypants, html is:\n" + html)
    if NO_SMARTYPANTS_TAG not in tags:
        html = smartypants.smartyPants(html, attr="2")

    logger.debug(u"after smartypants, html is:\n" + html)
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
