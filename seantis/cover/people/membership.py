from five import grok
from plone import api

from zope.interface import implements, Interface
from zope.annotation.interfaces import IAnnotations

from seantis.people.interfaces import IMembership, IMembershipSource


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

    def get_tile_ids(self, brain):
        for key, values in IAnnotations(brain.getObject()).items():
            if 'is_memberlist_tile' in values:
                yield key.replace('plone.tiles.data.', '')

    def get_tiles(self, brain):
        for uid in self.get_tile_ids(brain):
            path = str('/'.join((brain.getPath(), self.tile_id, uid)))
            yield self.context.restrictedTraverse(path)

    def memberships(self, person=None):
        query = {'portal_type': 'collective.cover.content'}
        brains = api.portal.get_tool(name='portal_catalog')(**query)

        # XXX horrible, slow, barely workable way to do it

        memberships = {}

        for ix, brain in enumerate(brains):
            
            organization = brain.UID

            for tile in self.get_tiles(brain):

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