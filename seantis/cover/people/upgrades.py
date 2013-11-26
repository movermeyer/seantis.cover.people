from plone import api

def add_browserlayer(context):
    setup = api.portal.get_tool('portal_setup')
    setup.runImportStepFromProfile(
        'profile-seantis.cover.people:default', 'browserlayer'
    )
