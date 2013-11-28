from five import grok

from plone import api
from plone.directives import form
from zope import schema
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from z3c.form import button

from seantis.people.events import MembershipChangedEvent
from seantis.cover.people.interfaces import ITileEditForm
from seantis.cover.people.form import TileEditForm
from seantis.cover.people import _


class ITileRoleEditForm(ITileEditForm):

    form.mode(person='hidden')
    person = schema.TextLine(
        title=u'Person UUID',
    )

    role = schema.TextLine(
        title=_(u'Role'),
        required=False
    )


class TileRoleEditForm(TileEditForm):
    """ From to edit the role of a member in an organization. """
    
    grok.name('edit-role')
    schema = ITileRoleEditForm

    @property
    def label(self):
        if not all((self.person, self.tile)):
            return _(u'Edit role')

        return _(u'Edit role of ${organization} / ${person}', mapping={
            'person': api.content.get(UID=self.person).title,
            'organization': self.context.title
        })

    @property
    def person(self):
        return self.parameter('person')

    @property
    def role(self):
        role = self.parameter('role')
        
        if role is not None:
            return role
        else:
            return self.load_role()

    def load_role(self):
        if not all((self.tile, self.person)):
            return u''

        return (self.get_tile_data().get('roles') or {}).get(self.person, u'')

    def save_role(self):
        assert all((self.tile, self.person)), """
            Only call when tile and person are available.
        """

        # load person to ensure validity of uuid
        person = api.content.get(UID=self.person)
        
        data = self.get_tile_data()
        data['roles'] = data.get('roles') or {}
        data['roles'][self.person] = self.role

        self.set_tile_data(data)

        # notify both ends as they might rely on the role data
        notify(ObjectModifiedEvent(self.context))
        notify(MembershipChangedEvent(person))

    @button.buttonAndHandler(_(u'Save'))
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.save_role()
        self.request.response.redirect(self.redirect_url)

    @button.buttonAndHandler(_(u'Cancel'))
    def handleCancel(self, action):
        self.request.response.redirect(self.redirect_url)
