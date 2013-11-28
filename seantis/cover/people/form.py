from five import grok
from plone.directives import form
from zope.annotation.interfaces import IAnnotations
from zope.schema import getFieldNames

from collective.cover.content import ICover

from seantis.cover.people.interfaces import ITileEditForm


class TileEditForm(form.SchemaForm):
    """ From to edit the role of a member in an organization. """

    grok.baseclass()
    grok.require('cmf.ModifyPortalContent')
    grok.context(ICover)

    schema = ITileEditForm
    ignoreContext = True

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
    def tile(self):
        return self.parameter('tile')

    @property
    def tile_data_key(self):
        return 'plone.tiles.data.{}'.format(self.tile)

    def get_tile_data(self):
        return IAnnotations(self.context).get(self.tile_data_key) or {}

    def set_tile_data(self, data):
        IAnnotations(self.context)[self.tile_data_key] = data

    def update(self, **kwargs):
        super(TileEditForm, self).update()

        # update the widgets with the values from the request
        for param in getFieldNames(self.schema):
            self.widgets[param].value = getattr(self, param)

    def updateActions(self):
        super(TileEditForm, self).updateActions()

        if 'save' in self.actions:
            self.actions['save'].addClass('context')

        if 'cancel' in self.actions:
            self.actions['cancel'].addClass('standalone')

