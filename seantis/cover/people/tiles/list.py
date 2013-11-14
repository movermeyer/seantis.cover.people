from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.list import ListTile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implements

from seantis.plonetools import tools
from seantis.people.interfaces import IPerson


class IMemberListTile(IPersistentCoverTile):

    uuids = schema.List(
        title=_(u'Members'),
        value_type=schema.TextLine(),
        required=False
    )

class MemberListTile(ListTile):

    implements(IPersistentCoverTile)
    index = ViewPageTemplateFile('templates/list.pt')

    is_editable = False
    is_configurable = False

    short_name = _(u'Memberlist')
    limit = 1000

    def accepted_ct(self):
        """Return 'Document' and 'News Item' as the only content types
        accepted in the tile.
        """
        return [
            fti.id for fti in 
            tools.get_type_info_by_behavior(IPerson.__identifier__)
        ]
