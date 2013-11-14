from plone import api
from seantis.people.interfaces import IPerson
from seantis.cover.people import tests


class TestMemberships(tests.IntegrationTestCase):

    def test_memberships_by_cover(self):

        layout = """'
        [{"type": "row", "children": [{"data": {"layout-type": "column", 
        "column-size": 16}, "type": "group", "children": [{"tile-type": 
        "seantis.cover.people.memberlist", "type": "tile", "id": 
        "ad6614ac74324647a73bf4ae5a576094"}], "roles": ["Manager"]}]}]'
        """.replace('\n', '')

        with self.user('admin'):
            person_type = self.new_temporary_type(
                behaviors=[IPerson.__identifier__]
            )

            cover = api.content.create(
                id='cover',
                type='collective.cover.content',
                container=self.new_temporary_folder(),
                cover_layout=layout
            )

            person = api.content.create(
                title='person',
                type=person_type.id,
                container=self.new_temporary_folder()
            )

        tile = cover.restrictedTraverse('seantis.cover.people.memberlist')
        tile.populate_with_object(person)

        self.assertEqual(tile.results(), [person])
        self.assertEqual(len(IPerson(person).memberships()), 1)
