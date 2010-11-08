'''
TypedTextImporter - imports facts typed into text files in a certain format

Copyright 2010 Isaac Wilcox

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as
published by the Free Software Foundation.

For documentation see:
   http://bit.ly/TypedTextImporterDoc

$Id$
'''

import sys
import re
from types import *

import logging
debug = False
LOG_FILENAME = '/tmp/TypedTextImporter.out'
logger = None

TTI_FILE = u"/Users/zak/stuff/medicine/SRS scratchpad.txt"
IMPORT_KEY=u"Z"
YAML_PATH = "/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages/"

sys.path.append(YAML_PATH)
import yaml

from anki.errors import ImportFormatError
import anki.importing
from anki.importing import ForeignCard
from anki.deck import NEW_CARDS_RANDOM

from ankiqt import mw
from ankiqt.ui import utils
from ankiqt.ui.importing import ImportDialog
import ankiqt

class TypedTextImporter(anki.importing.Importer):
        needMapper = False
        def __init__(self, deck, file):
                anki.importing.Importer.__init__(self, deck, file)
                self.numFields = 0
                self.iHaveSeenTheEnd = False

        def doImport(self):
                random = self.deck.newCardOrder == NEW_CARDS_RANDOM
                # This gets wiped by needMapper processing if set much earlier than here.
                self.tagDuplicates = True
                try:
                        self.fh = open(self.file, "r")
                except (IOError, OSError), e:
                        raise ImportFormatError(type="systemError", info=str(e))
                self.curState = 'collecting_globals'
                self.sharedTags = ''
                self.endOfMultilineFieldMarker = ""
                self.multilineEOL = ""
                while True:
                        c = self.foreignCards()
                        if not c:
                                break
                        if self.importCards(c):
                                self.deck.updateCardTags(self.cardIds)
                                self.deck.updatePriorities(self.cardIds)
                                if random:
                                        self.deck.randomizeNewCards(self.cardIds)
                        self.deck.setModified()
                self.fh.close()

        def html_list(self, list, level=0):
                html = "<ul>"
                for e in list:
                        if type(e) is ListType:
                                html += self.html_list(e, level+1)
                        elif type(e) is StringType:
                                html += "<li>%s</li>" % (e)
                        elif type(e) is DictType and level == 0:
                                if 't' in e:
                                        # Explicitly, "- t: include this line outside any list" => break list, insert text, restart list
                                        html += "</ul><p>%s</p><ul>" % (e['t'])
                                else:
                                        # Implicitly, "- signs of gout:" => treat key name as just another list item
                                        # Allows you to forget about the Yaml-ness, accidentally use a trailing colon and still DWIM
                                        html += "<li>%s</li>" % (e.popitem()[0])
                html += "</ul>"
                return html

        def foreignCards(self):
                "Return a list of foreign cards for importing."
                if self.iHaveSeenTheEnd:
                        return None
                self.cards = []
                curCard = ForeignCard()

                while True:
                        logger.debug("here we go (again); state is " + self.curState)
                        match = re.search("_reinterpret$", self.curState)
                        if match:
                                logger.debug("it's a reinterpret, so, pre-sub: " + self.curState)
                                self.curState = re.sub("_reinterpret", "", self.curState)
                                logger.debug("post-sub: " + self.curState)
                        else:
                                line = self.fh.readline()
                                logger.debug("pristine line: '''" + line + "'''")
                                if line == "":
                                        if self.curState not in ('collecting_globals', 'between_facts'):
                                                raise ImportFormatError(type="systemError", info="file terminated unexpectedly in state " + self.curState)
                                        break
                                line = re.sub("#.*$", "", line)
                                logger.debug("line with comments removed: '''" + line + "'''")
                                line = line.rstrip()
                                logger.debug("stripped line: '''" + line + "'''")
                                if line == "__END__":
                                        if self.curState not in ('collecting_globals', 'between_facts'):
                                                raise ImportFormatError(type="systemError", info="file terminated unexpectedly in state " + self.curState)
                                        # return whatever we've gathered so far, but flag so that we don't re-enter the state machine next time we get called
                                        self.iHaveSeenTheEnd = True
                                        break
                                logger.debug("state is " + self.curState)

                        if self.curState == 'collecting_globals':
                                if re.search("^\s*$",line):
                                        continue
                                match = re.search("^st: (?P<tags>.*)$", line)
                                if match:
                                        self.sharedTags += " " + match.group('tags')
                                        continue
                                match = re.search("^m: (?P<modelname>.+)$", line)
                                if match:
                                        self.curState = 'between_facts_reinterpret'
                                        logger.debug("found an m: line; reinterpreting in state " + self.curState)
                                        continue
                                raise ImportFormatError(type="systemError", info="expected m: or st: but got " + line)

                        if self.curState == 'between_facts':
                                logger.debug("between facts handler")

                                match = re.search("^st: (?P<tags>.*)$", line)
                                if match:
                                        self.sharedTags += " " + match.group('tags')
                                        continue
                                match = re.search("^m: (?P<modelname>.+)$", line)
                                if match:
                                        logger.debug("found an m: line")
                                        self.curModel = None
                                        for m in self.deck.models:
                                                logger.debug("looking for model named '" + match.group('modelname') + "' ok")
                                                if m.name == match.group('modelname'):
                                                        self.curModel = m
                                                        logger.debug("chose model " + self.curModel.name + " with " + str(self.numFields) + " fields, ok")
                                                        break
                                        if not self.curModel:
                                                raise ImportFormatError(type="systemError", info="model " + match.group('modelname') + " doesn't exist; choose from " + self.deck.models.fieldModels)
                                        continue
                                if line != "":
                                        # special case: go back around and reinterpret same line in different context
                                        logger.debug("non-empty, reinterpreting...")
                                        self.curState = 'in_fact_reinterpret'
                                continue

                        if self.curState == 'in_fact':
                                logger.debug("in_fact handler")
                                # Sub-state - are we in a multiline field?
                                logger.debug("are we in multiline?")
                                if self.endOfMultilineFieldMarker != "":
                                        logger.debug("we are in multiline")
                                        match = re.search(re.escape(self.endOfMultilineFieldMarker) + "$", line)
                                        if match:
                                                logger.debug("ending multiline")
                                                self.endOfMultilineFieldMarker = ""
                                        else:
                                                logger.debug("still collecting in multiline")
                                                curCard.fields[-1] += line + self.multilineEOL
                                        continue
                                logger.debug("not in multiline; perhaps terminating fact?")
                                if line == ".":
                                        # Fact terminator
                                        logger.debug("we are terminating fact")
                                
                                        # Not sure why but ForeignCard takes *both* the contents of .tags
                                        # *and* contents of a special member of .fields and concatenates
                                        # those to get overall tags.  If you don't give the special field
                                        # it gets angry.  So, provide an empty one.  Default mapping will
                                        # expect to find this in the last field.
                                        curCard.tags += self.sharedTags
                                        curCard.fields = [ unicode(nonUTF) for nonUTF in curCard.fields ]

                                        # Pad out any remaining fields with empty strings.
                                        # Perhaps at a later point we'll support syntax for specifying a field by "^<s>: "
                                        # where s is some unambiguous prefix of the field name, at which point we'll need
                                        # to specify our own mappings.
                                        logger.debug("purely simply collected fields: " + str(curCard.fields))
                                        have = len(curCard.fields)
                                        want = len(self.curModel.fieldModels)
                                        logger.debug("numFields: %d, have: %d, want: %d" % (self.numFields, have, want))
                                        curCard.fields[have:want] = [ u"" for i in range(have,want) ]

                                        # special tags field
                                        curCard.fields.append(u"")
                                        logger.debug("full set of fields with trailing null strings and empty tags: " + str(curCard.fields))
                                        self.numFields = len(curCard.fields)
                                        # Setting model computes mapping.
                                        self.model = self.curModel

                                        self.cards.append(curCard)
                                        self.curState = 'between_facts'

                                        # Fresh card
                                        curCard = ForeignCard()
                                        
                                        # Stop here and return what we have.
                                        break
                                else:
                                        logger.debug("not terminating fact; perhaps starting multiline?")
                                        # Single-line field, or start of a multiline one.
                                
                                        # `
                                        # this is a
                                        # multiline string
                                        # `
                                        # =>
                                        # this is a\nmultiline string
                                        match = re.search("^(?P<eof>`)(?P<flags>[b]?)$", line)
                                        if match:
                                                logger.debug("starting `multiline")
                                                self.endOfMultilineFieldMarker = match.group('eof')
                                                # FIXME: Anki seems to fuck with this if not set to <br/>
                                                #if match.group('flags') == "b":
                                                self.multilineEOL = "<br/>"
                                                #else:
                                                #self.multilineEOL = "\n"
                                                # Start off with new empty field, added to as we collect constituent lines
                                                curCard.fields.append("")
                                                continue
                                        # <<Eof
                                        # so
                                        # is this
                                        # Eof
                                        # =>
                                        # so\nis this
                                        match = re.search("^<<(?P<eof>\S+)$", line)
                                        if match:
                                                logger.debug("starting <<multiline")
                                                self.endOfMultilineFieldMarker = match.group('eof')
                                                self.multilineEOL = "\n"
                                                # Start off with new blank field, added to as we collect constituent lines
                                                curCard.fields.append('')
                                                continue

                                        match = re.search("^t:(?P<facttags> .*)$", line)
                                        if match:
                                                logger.debug("adding per-fact tags")
                                                curCard.tags += match.group('facttags')
                                                continue

                                        # Single-line.
                                        logger.debug("collecting single line")
                                        curCard.fields.append(line)
                                        continue
                                continue
                        raise ImportFormatError(type="systemError", info="ended up in unhandled state")
                logger.debug("stick a fork in me: ")
                logger.debug(self.cards)
                return self.cards

        def fields(self):
                return self.numFields

class TTIImportDialog(ImportDialog):
        def getFile(self):
                self.file = TTI_FILE
                self.modelChooser.hide()
                self.dialog.tagDuplicates.hide()
                self.dialog.autoDetect.setShown(False)
                self.importer = anki.importing.Importers[0]
                self.importerFunc = TypedTextImporter
                
def newKeyPressEvent(evt):
        if ((mw.state == "studyScreen")
            and (unicode(evt.text()) == IMPORT_KEY)):
                old = ankiqt.ui.importing.ImportDialog
                ankiqt.ui.importing.ImportDialog = TTIImportDialog 
                mw.onImport()
                ankiqt.ui.importing.ImportDialog = old 
                evt.accept()
        return oldEventHandler(evt)

def configureLogging(debug):
        global logger
        if not debug:
                class LoggerStub:
                        def debug(self, s): pass
                logger = LoggerStub()
                return
        import logging
        logger = logging.getLogger(__name__)
        logger.addHandler(logging.FileHandler(LOG_FILENAME, delay=True))
        logger.setLevel(logging.DEBUG)

configureLogging(debug)

# Would be much better if we could use a hook to modify this, and slightly
# better if it was at least a list rather than a tuple:
#anki.importing.Importers.append( [u"TypedTextImporter (*.txt)", TypedTextImporter] )

anki.importing.Importers = [ e for e in anki.importing.Importers ]
anki.importing.Importers.insert( 0, [u"TypedTextImporter (*.txt)", TypedTextImporter] )

oldEventHandler = mw.keyPressEvent
mw.keyPressEvent = newKeyPressEvent

mw.registerPlugin("TypedTextImporter", 0)

# vim: softtabstop=8 shiftwidth=8 expandtab
