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
