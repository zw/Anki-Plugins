# Hack around the bug fixed in this commit:
#   http://github.com/zw/ankiqt/commit/3e739e769878d1e41feef2e2428239465481d6d4
# Should have used the wrap stuff for this.  Or even just run from source.
import ankiqt.ui.facteditor
import ankiqt.ui.utils
from anki.lang import _

def _addMedia(self, file):
    try:
        return self.deck.addMedia(file)
    except (IOError, OSError), e:
        ankiqt.ui.utils.showWarning(_("Unable to add media: %s") % unicode(e),
                             parent=self.parent)

ankiqt.ui.facteditor.FactEditor._addMedia = _addMedia
