from five import grok

from zope import schema
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from z3c.form import button

from seantis.cover.people.interfaces import ITileEditForm
from seantis.cover.people.form import TileEditForm
from seantis.cover.people import _


class ITileTitleEditForm(ITileEditForm):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False
    )


class TileTitleEditForm(TileEditForm):
    """ From to edit the role of a member in an organization. """
    
    grok.name('edit-title')
    schema = ITileTitleEditForm
    label = _(u'Edit title')

    @property
    def title(self):
        title = self.parameter('title')
        if title is not None:
            return title
        else:
            return self.load_title()

    def load_title(self):
        if not self.tile:
            return u''

        return (self.get_tile_data().get('title') or _(u'Members'))

    def save_title(self):
        assert self.tile, """
            Only call when tile is available.
        """
        
        data = self.get_tile_data()
        data['title'] = self.title
        self.set_tile_data(data)

        notify(ObjectModifiedEvent(self.context))

    @button.buttonAndHandler(_(u'Save'))
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.save_title()
        self.request.response.redirect(self.redirect_url)

    @button.buttonAndHandler(_(u'Cancel'))
    def handleCancel(self, action):
        self.request.response.redirect(self.redirect_url)
