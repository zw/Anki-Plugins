# -*- coding: utf-8 -*-
# Translate punctuation according to SmartyZaks rules, which are:
#    =>   gets translated to    &rarr;
#    :)   gets translated to    &#x263a; (a smiley character)


import re
import anki.hooks

LOG_FILENAME = u"/tmp/smartyzaks.log"
NO_SMARTYZAKS_TAG = u"notSmartyZaks"

def formatQA(html, type, cid, mid, fact, tags, cm):
    logger.debug(u"before smartyzaks, html is:\n" + html)
    if NO_SMARTYZAKS_TAG not in tags:
        html = re.sub(ur"(?<=[ >(])=(&gt;|>)(?=[ <])", ur"&rArr;", html)
        html = re.sub(ur':\)', ur"&#x263a;", html)

    logger.debug(u"after smartyzaks, html is:\n" + html)
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
