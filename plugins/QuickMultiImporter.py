'''
QuickMultiImporter - imports facts typed into text files in a certain format

Copyright 2010 Isaac Wilcox

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as
published by the Free Software Foundation.

For documentation of the file format see the file QuickMultiImporter.html
either in this directory or online at ...
'''

import sys
import re
from types import *
#import logging
#LOG_FILENAME = '/tmp/logging_example.out'
#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

QMI_FILE = u"/Users/zak/stuff/medicine/SRS scratchpad.txt"
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

class QuickMultiImporter(anki.importing.Importer):
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
                        logging.debug("here we go (again); state is " + self.curState)
                        match = re.search("_reinterpret$", self.curState)
                        if match:
                                logging.debug("it's a reinterpret, so, pre-sub: " + self.curState)
                                self.curState = re.sub("_reinterpret", "", self.curState)
                                logging.debug("post-sub: " + self.curState)
                        else:
                                line = self.fh.readline()
                                logging.debug("pristine line: " + line)
                                if line == "":
                                        if self.curState not in ('collecting_globals', 'between_facts'):
                                                raise ImportFormatError(type="systemError", info="file terminated unexpectedly in state " + self.curState)
                                        break
                                line = line.rstrip("\n\r")
                                logging.debug("stripped line: " + line)
                                if line == "__END__":
                                        if self.curState not in ('collecting_globals', 'between_facts'):
                                                raise ImportFormatError(type="systemError", info="file terminated unexpectedly in state " + self.curState)
                                        # return whatever we've gathered so far, but flag so that we don't re-enter the state machine next time we get called
                                        self.iHaveSeenTheEnd = True
                                        break
                                line = re.sub("#.*$", "", line)
                                logging.debug("line with comments removed: " + line)
                                logging.debug("state is " + self.curState)

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
                                        logging.debug("found an m: line; reinterpreting in state " + self.curState)
                                        continue
                                raise ImportFormatError(type="systemError", info="expected m: or st: but got " + line)

                        if self.curState == 'between_facts':
                                logging.debug("between facts handler")

                                match = re.search("^m: (?P<modelname>.+)$", line)
                                if match:
                                        logging.debug("found an m: line")
                                        self.haveModel = False
                                        for m in self.deck.models:
                                                logging.debug("looking for model named '" + match.group('modelname') + "' ok")
                                                if m.name == match.group('modelname'):
                                                        self.model = m
                                                        self.haveModel = True
                                                        self.numFields = len(m.fieldModels)
                                                        # Looks like parent class does this mapping crap for us with a sensible default, provided we set numFields
                                                        #self.mapping = [ fm for fm in m.fieldModels ]
                                                        #self.mapping.insert(0, None)
                                                        logging.debug("chose model " + self.model.name + " ok")
                                                        break
                                        if not self.haveModel:
                                                raise ImportFormatError(type="systemError", info="model " + match.group('modelname') + " doesn't exist; choose from " + self.deck.models.fieldModels)
                                        continue
                                if line != "":
                                        # special case: go back around and reinterpret same line in different context
                                        logging.debug("non-empty, reinterpreting...")
                                        self.curState = 'in_fact_reinterpret'
                                continue

                        if self.curState == 'in_fact':
                                logging.debug("in_fact handler")
                                # Sub-state - are we in a multiline field?
                                logging.debug("are we in multiline?")
                                if self.endOfMultilineFieldMarker != "":
                                        logging.debug("we are in multiline")
                                        match = re.search("(?P<leading>.*)" + re.escape(self.endOfMultilineFieldMarker) + "$", line)
                                        if match:
                                                logging.debug("ending multiline")
                                                if self.endOfMultilineFieldMarker == "...":
                                                        logging.debug("so far, before html-ising, we have gathered: " + "::fieldsep:::\n".join(curCard.fields))
                                                        yamlRet = yaml.load(curCard.fields[-1])
                                                        logging.debug("parsed yaml is:")
                                                        logging.debug(yamlRet)
                                                        htmlRet = self.html_list(yamlRet)
                                                        logging.debug("html is:")
                                                        curCard.fields[-1] = htmlRet
                                                        #curCard.fields.append(self.html_list(yaml.load(curCard.fields[-1])))
                                                        logging.debug("after htmlising we have: " + "::fieldsep:::\n".join(curCard.fields))
                                                else:
                                                        curCard.fields[-1] += match.group('leading')
                                                self.endOfMultilineFieldMarker = ""
                                        else:
                                                logging.debug("collecting in multiline")
                                                curCard.fields[-1] += line + self.multilineEOL
                                        continue
                                logging.debug("not in multiline; perhaps terminating fact?")
                                if line == ".":
                                        logging.debug("we are terminating fact")
                                        # Fact terminator
                                        curCard.tags += self.sharedTags
                                        curCard.fields = [ unicode(nonUTF) for nonUTF in curCard.fields ]

                                        # Pad out any remaining fields with empty strings
                                        have = len(curCard.fields)
                                        want = len(self.model.fieldModels)
                                        curCard.fields[have:want] = [ u"" for i in range(have,want) ]

                                        self.cards.append(curCard)
                                        self.curState = 'between_facts'

                                        # Fresh card
                                        curCard = ForeignCard()
                                        
                                        # Stop here and return what we have.
                                        break
                                else:
                                        logging.debug("not terminating fact; perhaps starting multiline?")
                                        # Single-line field, or start of a multiline one.
                                
                                        # `this is a
                                        # multiline string`
                                        # =>
                                        # this is a<br />multiline string
                                        match = re.search("^(?P<eof>`)(?P<trailing>.*)", line)
                                        if match:
                                                logging.debug("starting `multiline")
                                                self.endOfMultilineFieldMarker = match.group('eof')
                                                self.multilineEOL = "<br />"
                                                # Start off with new field (starting with any trailing text), added to as we collect constituent lines
                                                curCard.fields.append(match.group('trailing') + self.multilineEOL)
                                                continue
                                        # <<Eof
                                        # so
                                        # is thisEof
                                        # =>
                                        # so\nis this
                                        match = re.search("^<<(?P<eof>\S+)$", line)
                                        if match:
                                                logging.debug("starting <<multiline")
                                                self.endOfMultilineFieldMarker = match.group('eof')
                                                self.multilineEOL = "\n"
                                                # Start off with new blank field, added to as we collect constituent lines
                                                curCard.fields.append('')
                                                continue
                                        # ---
                                        # - these
                                        # - are items
                                        # - - in a list
                                        #   - sublist
                                        # - yaml love
                                        # ...
                                        match = re.search("^(?P<eof>---)$", line)
                                        if match:
                                                logging.debug("starting ---yaml")
                                                self.endOfMultilineFieldMarker = '...'
                                                self.multilineEOL = "\n"  # this'll get converted when we HTMLise the list
                                                # Start off with new blank field, added to as we collect constituent lines
                                                curCard.fields.append('')
                                                continue

                                        match = re.search("^t:(?P<facttags> .*)$", line)
                                        if match:
                                                logging.debug("adding per-fact tags")
                                                curCard.tags += match.group('facttags')
                                                continue

                                        # Single-line.
                                        logging.debug("collecting single line")
                                        curCard.fields.append(line)
                                        continue
                                continue
                        raise ImportFormatError(type="systemError", info="ended up in unhandled state")
                logging.debug("stick a fork in me: ")
                logging.debug(self.cards)
                return self.cards

        def fields(self):
                return self.numFields

class QMIImportDialog(ImportDialog):
        def getFile(self):
                self.file = QMI_FILE
                self.modelChooser.hide()
                self.dialog.tagDuplicates.hide()
                self.dialog.autoDetect.setShown(False)
                self.importer = anki.importing.Importers[0]
                self.importerFunc = QuickMultiImporter
                
def newKeyPressEvent(evt):
        if ((mw.state == "studyScreen")
            and (unicode(evt.text()) == IMPORT_KEY)):
                old = ankiqt.ui.importing.ImportDialog
                ankiqt.ui.importing.ImportDialog = QMIImportDialog 
                mw.onImport()
                ankiqt.ui.importing.ImportDialog = old 
                evt.accept()
        return oldEventHandler(evt)


# Would be much better if we could use a hook to modify this, and slightly
# better if it was at least a list rather than a tuple:
#anki.importing.Importers.append( [u"QMI text (*.txt)", QuickMultiImporter] )

anki.importing.Importers = [ e for e in anki.importing.Importers ]
anki.importing.Importers.insert( 0, [u"QMI text (*.txt)", QuickMultiImporter] )

oldEventHandler = mw.keyPressEvent
mw.keyPressEvent = newKeyPressEvent

mw.registerPlugin("QuickMultiImporter", 0)

# vim: softtabstop=8 shiftwidth=8 expandtab
