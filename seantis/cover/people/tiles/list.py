from five import grok
from plone import api

from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.list import ListTile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implements, Interface
from zope.annotation.interfaces import IAnnotations

from seantis.plonetools import tools
from seantis.people.interfaces import IPerson, IMembership, IMembershipSource


class CoverMembership(object):

    implements(IMembership)

    def __init__(self, person, title=None, start=None, end=None):
        self.person = person
        self.title = title
        self.start = start
        self.end = end


class CoverMembershipSource(grok.Adapter):

    grok.name('cover-membership-source')
    grok.provides(IMembershipSource)
    grok.context(Interface)

    tile_id = 'seantis.cover.people.memberlist'

    def memberships(self, person=None):
        query = {'portal_type': 'collective.cover.content'}
        brains = api.portal.get_tool(name='portal_catalog')(**query)

        # XXX horrible, slow, barely workable way to do it

        memberships = {}
        for ix, brain in enumerate(brains):
            tiles = IAnnotations(brain.getObject()).get('current_tiles', {})
            
            organization = brain.UID

            for uid in tiles.keys():
                path = '/'.join((brain.getPath(), self.tile_id, uid))
                tile = self.context.restrictedTraverse(path)

                people = [
                    p for p in tile.results() if person is None or person == p
                ]

                if people:
                    if organization not in memberships:
                        memberships[organization] = []

                    memberships[organization].extend(
                        CoverMembership(p) for p in people
                    )

        return memberships


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
