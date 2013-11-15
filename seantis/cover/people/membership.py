from five import grok
from plone import api
from plone.uuid.interfaces import IUUID

from zope.interface import implements, Interface

from seantis.cover.people.tiles.list import get_list_tiles
from seantis.people.interfaces import IMembership, IMembershipSource


def get_people_uuids_from_cover(cover):
    uuids = []

    for tile in get_list_tiles(cover):
        uuids.extend(tile.data['uuids'])

    return uuids


class CoverMembership(object):

    implements(IMembership)

    def __init__(self, uuid, title=None, start=None, end=None):
        self.uuid = uuid
        self.title = title
        self.start = start
        self.end = end

    @property
    def person(self):
        return api.content.get(UID=self.uuid)


class CoverMembershipSource(grok.Adapter):

    grok.name('cover-membership-source')
    grok.provides(IMembershipSource)
    grok.context(Interface)

    def memberships(self, person=None):
        query = {'portal_type': 'collective.cover.content'}
        brains = api.portal.get_tool(name='portal_catalog')(**query)

        # XXX horrible, slow, barely workable way to do it

        memberships = {}
        target_uuid = IUUID(person)

        for ix, brain in enumerate(brains):
            cover = brain.getObject()
            organization = brain.UID

            uuids = [
                uuid for uuid in get_people_uuids_from_cover(cover)
                if person is None or uuid == target_uuid
            ]

            for uuid in uuids:
                memberships.setdefault(organization, []).append(
                    CoverMembership(uuid)
                )

        return memberships
