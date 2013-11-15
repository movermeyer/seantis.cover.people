import json

from zope.annotation.interfaces import IAnnotations

from uuid import uuid4 as new_uuid
from plone import api

from seantis.people.interfaces import IPerson
from seantis.cover.people import tests


class TestMemberships(tests.IntegrationTestCase):

    def add_layout_row(self, cover):
        layout = cover.cover_layout and json.loads(cover.cover_layout) or []
        id = new_uuid().hex

        layout.append(
            {"type": "row", "children": [{
                "data": {"layout-type": "column", "column-size": 16}, 
                "type": "group", "children": [{
                    "tile-type": "seantis.cover.people.memberlist", 
                    "type": "tile", "id": id
                }], 
                "roles": ["Manager"]
            }]}
        )

        cover.cover_layout = json.dumps(layout)

        annotations = IAnnotations(cover)
        annotations['current_tiles'] = annotations.get('current_tiles', {})
        annotations['current_tiles'][id] = {
            'type': 'seantis.cover.people.memberlist',
            'title': ''
        }

        cover.reindexObject()

        return 'seantis.cover.people.memberlist/{}'.format(id)

    def test_memberships_by_cover(self):

        with self.user('admin'):
            person_type = self.new_temporary_type(
                behaviors=[IPerson.__identifier__]
            )

            cover = api.content.create(
                id='cover',
                type='collective.cover.content',
                container=self.new_temporary_folder()
            )

            person = api.content.create(
                title='person',
                type=person_type.id,
                container=self.new_temporary_folder()
            )

            path1 = self.add_layout_row(cover)
            path2 = self.add_layout_row(cover)

        tile1 = cover.restrictedTraverse(path1)
        tile2 = cover.restrictedTraverse(path2)
        
        tile1.populate_with_object(person)
        memberships = IPerson(person).memberships()

        self.assertEqual(tile1.results(), [person])

        self.assertEqual(len(memberships.keys()), 1)
        self.assertEqual(len(memberships.values()[0]), 1)

        tile2.populate_with_object(person)
        memberships = IPerson(person).memberships()

        self.assertEqual(tile1.results(), [person])
        self.assertEqual(tile2.results(), [person])
        self.assertEqual(len(memberships.keys()), 1)
        self.assertEqual(len(memberships.values()[0]), 2)
