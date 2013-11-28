from plone.directives import form
from zope import schema
from zope.interface import Interface


class ISeantisCoverPeopleSpecific(Interface):
    pass


class ITileEditForm(form.Schema):

    form.mode(tile='hidden')
    tile = schema.TextLine(
        title=u'Tile UUID',
    )
