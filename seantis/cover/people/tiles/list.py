from contextlib import contextmanager

from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.list import ListTile

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.tiles.interfaces import ITileDataManager
from plone import api

from zope import schema
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from seantis.plonetools import tools
from seantis.cover.people import _
from seantis.people.interfaces import IPerson


def get_list_tile_ids( cover):
        for key, values in IAnnotations(cover).items():
            if 'is_memberlist_tile' in values:
                yield key.replace('plone.tiles.data.', '')


def get_list_tiles(cover):
    for uid in get_list_tile_ids(cover):
        path = str('/'.join(('seantis.cover.people.memberlist', uid)))
        yield cover.restrictedTraverse(path)


class IMemberListTile(IPersistentCoverTile):

    uuids = schema.List(
        title=_(u'Members'),
        value_type=schema.TextLine(),
        required=False
    )

    is_memberlist_tile = schema.Bool(
        required=False
    )

    roles = schema.Dict(
        title=_(u'Roles'),
        key_type=schema.TextLine(),
        value_type=schema.TextLine()
    )

    title = schema.TextLine(
        title=_(u'Title'),
        required=False
    )


class MemberListTile(ListTile):

    implements(IPersistentCoverTile)
    index = ViewPageTemplateFile('templates/list.pt')

    is_editable = False
    is_configurable = True

    short_name = _(u'Memberlist')
    limit = 1000

    def translate(self, text):
        return tools.translator(self.request, 'seantis.cover.people')(text)

    @contextmanager
    def change_data(self):
        data_mgr = ITileDataManager(self)
        data = data_mgr.get()
        yield data
        data_mgr.set(data)

    def get_title(self):
        title = self.data.get('title')
        title = title if title is not None else _(u'Members')
        return self.translate(title)

    def set_title(self, title):
        with self.change_data() as data:
            data['title'] = title

    def get_role(self, uuid):
        roles = self.data.get('roles') or {}
        return roles.get(uuid, u'')

    def set_role(self, uuid, role):
        with self.change_data() as data:
            data['roles'] = data.get('roles') or {}
            data['roles'][uuid] = role

    def populate_with_object(self, obj):
        super(MemberListTile, self).populate_with_object(obj)
        notify(ObjectModifiedEvent(obj))

    def remove_item(self, uuid):
        super(MemberListTile, self).remove_item(uuid)

        with self.change_data() as data:
            if uuid in data['roles']:
                del data['roles'][uuid]

        notify(ObjectModifiedEvent(api.content.get(UID=uuid)))

    def accepted_ct(self):
        return [
            fti.id for fti in
            tools.get_type_info_by_behavior(IPerson.__identifier__)
        ]
