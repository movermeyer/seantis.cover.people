from five import grok
from plone import api
from plone.uuid.interfaces import IUUID
from plone.indexer.decorator import indexer

from zope.interface import implements, Interface

from collective.cover.content import ICover

from seantis.cover.people.tiles.list import get_list_tiles
from seantis.people.interfaces import IMembership, IMembershipSource


def get_people_uuids_from_cover(cover):
    uuids = []

    for tile in get_list_tiles(cover):
        if tile.data['uuids']:
            uuids.extend(tile.data['uuids'])

    return uuids


def get_people_roles_from_cover(cover):
    roles = {}

    for tile in get_list_tiles(cover):
        if tile.data['roles']:
            roles.update(tile.data['roles'])

    return roles


@indexer(ICover)
def people_uuids(cover):
    return get_people_uuids_from_cover(cover)


class CoverMembership(object):

    implements(IMembership)

    def __init__(self, uuid, role=None, start=None, end=None):
        self.uuid = uuid
        self.role = role
        self.start = start
        self.end = end

    @property
    def person(self):
        return api.content.get(UID=self.uuid)


class CoverMembershipSource(grok.Adapter):

    grok.name('cover-membership-source')
    grok.provides(IMembershipSource)
    grok.context(Interface)

    @property
    def is_available(self):
        try:
            catalog = api.portal.get_tool(name='portal_catalog')
            catalog._catalog.getIndex('people_uuids')
        except KeyError:
            return False

        return True

    def memberships(self, person=None):

        # I probably need to make these adapters require the request so the
        # grok.layer directive can be used. Right now this adapter is active
        # even if the addon is not installed, which is less than ideal.
        if not self.is_available:
            return {}

        # get all brains, optionally the ones which include a certain uuid
        query = {'portal_type': 'collective.cover.content'}

        if person:
            target_uuid = IUUID(person)
            query['people_uuids'] = {'query': target_uuid}

        catalog = api.portal.get_tool(name='portal_catalog')
        brains = catalog(**query)

        index = catalog._catalog.getIndex('people_uuids')
        get_values = lambda brain: index.getEntryForObject(brain.getRID(), '')

        memberships = {}

        # the cover is the organization
        for brain in brains:
            organization = brain.UID

            # get all uuids, optionally filter the for the person
            uuids = get_values(brain)

            # we'll see how this plays out performance wise
            roles = get_people_roles_from_cover(brain.getObject())

            for uuid in uuids:
                if person is not None and uuid != target_uuid:
                    continue

                memberships.setdefault(organization, []).append(
                    CoverMembership(uuid, roles.get(uuid, u''))
                )

        return memberships
