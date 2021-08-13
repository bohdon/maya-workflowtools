"""
Functions for installing and uninstalling the rmb hooks by sourcing
the appropriate mel scripts.

Installing and uninstalling has no effect on which menus are
currently registered.
"""


import pymel.core as pm
import os

__all__ = [
    'enable',
    'disable',
]


# original scripts that can be sourced to remove the rmb hooks
ORIGINAL_SCRIPTS = [
    'buildObjectMenuItemsNow',
    'dagMenuProc'
]


def enable():
    """
    Source the appropriate mel scripts
    """

    # ensure the overidden scripts have been sourced
    # at least once to prevent them sourcing later
    for script in ORIGINAL_SCRIPTS:
        pm.mel.source(script)

    # build list of mel scripts to source
    vers = pm.about(version=True).split(' ')[0]
    scripts = [
        'rmbmenuhook.mel',
        'rmbmenuhookOverrides{0}.mel'.format(vers),
    ]

    # source using full path for each script
    dir = os.path.dirname(__file__)
    for script in scripts:
        fullPath = os.path.join(dir, script).replace('\\', '/')
        print('Sourcing {0}'.format(fullPath))
        pm.mel.source(fullPath)
    print('RMB Marking Menu Hooks enabled')


def disable():
    """
    Source the default mel scripts
    to remove any custom overrides
    """
    for script in ORIGINAL_SCRIPTS:
        pm.mel.source(script)
    print('RMB Marking Menu Hooks disabled')



