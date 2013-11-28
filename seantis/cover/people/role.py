from five import grok

from plone import api
from plone.directives import form
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from z3c.form import button

from collective.cover.content import ICover
from seantis.people.events import MembershipChangedEvent
from seantis.cover.people import _


class IRole(form.Schema):

    form.mode(tile='hidden')
    tile = schema.TextLine(
        title=u'Tile UUID',
    )

    form.mode(person='hidden')
    person = schema.TextLine(
        title=u'Person UUID',
    )

    role = schema.TextLine(
        title=_(u'Role'),
        required=False
    )


class RoleEditForm(form.SchemaForm):
    """ From to edit the role of a member in an organization. """
    
    grok.name('edit-role')
    grok.require('cmf.ModifyPortalContent')
    grok.context(ICover)

    schema = IRole
    ignoreContext = True

    @property
    def label(self):
        if not all((self.person, self.tile)):
            return _(u'Edit role')

        return _(u'Edit role of ${organization} / ${person}', mapping={
            'person': api.content.get(UID=self.person).title,
            'organization': self.context.title
        })

    @property
    def redirect_url(self):
        return '/'.join((self.context.absolute_url(), 'compose'))

    def parameter(self, name):
        if self.request.get(name) is not None:
            return self.request.get(name)

        if self.request.get('form.widgets.{}'.format(name)) is not None:
            return self.request.get('form.widgets.{}'.format(name))

        return None

    @property
    def person(self):
        return self.parameter('person')

    @property
    def tile(self):
        return self.parameter('tile')

    @property
    def role(self):
        role = self.parameter('role')
        
        if role is not None:
            return role
        else:
            return self.load_role()

    def update(self, **kwargs):
        super(RoleEditForm, self).update()

        # update the widgets with the values from the request
        for param in ('person', 'tile', 'role'):
            self.widgets[param].value = getattr(self, param)

    @property
    def tile_data_key(self):
        return 'plone.tiles.data.{}'.format(self.tile)

    def get_tile_data(self):
        return IAnnotations(self.context).get(self.tile_data_key) or {}
        
    def set_tile_data(self, data):
        IAnnotations(self.context)[self.tile_data_key] = data

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
