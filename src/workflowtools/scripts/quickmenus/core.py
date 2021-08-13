
import logging

import pymel.core as pm
import rmbmenuhook

from . import utils


__all__ = [
    "buildMenus",
    "destroyMenus",
    "getAllRegisteredMenus",
    "getRegisteredMenus",
    "MarkingMenu",
    "registerMenu",
    "registerMenuHotkeys",
    "removeMenuHotkeys",
    "RMBMarkingMenu",
    "unregisterMenu",
]


LOG = logging.getLogger("quickmenus")
LOG.level = logging.INFO


BUILD_MENU_CMD = """{importCmd}
{preBuild}

try:
    import quickmenus
    quickmenus.buildMenus('{menuName}')
except Exception as e:
    raise e
    {secondary}
"""

DESTROY_MENU_CMD = """{importCmd}

try:
    import quickmenus
    wasInvoked = quickmenus.destroyMenus('{menuName}')
except Exception as e:
    raise e
else:
    if not wasInvoked:
        {secondary}
"""

# all menus that have been registered,
# stored as a list of classes indexed by menu name
REGISTERED_MENUS = {}

# list of any active marking menus that
# can / should be destroyed when menu key is released
ACTIVE_MENUS = []


# Hotkey Management
# -----------------

def _switchToNonDefaultHotkeySet():
    if not hasattr(pm, 'hotkeySet'):
        return
    current = pm.hotkeySet(q=True, cu=True)
    if current == 'Maya_Default':
        existing = pm.hotkeySet(q=True, hotkeySetArray=True)
        if 'Maya_Default_Duplicate' in existing:
            # use the common duplicated set
            pm.hotkeySet('Maya_Default_Duplicate', e=True, cu=True)
            LOG.info("Switched to hotkey set: Maya_Default_Duplicate")
        elif len(existing) > 1:
            # there are other sets, but not with known names
            for e in existing:
                if e != 'Maya_Default':
                    pm.hotkeySet(e, e=True, cu=True)
                    LOG.info("Switched to hotkey set: " + e)
                    break
        else:
            # create a duplicate
            pm.hotkeySet('Maya_Default_Duplicate', src='Maya_Default', cu=True)
            LOG.info("Created duplicate hotkey set: Maya_Default_Duplicate")


def registerMenuHotkeys(menuName, hotkey, importCmd=None, preBuildCmd=None, secondaryCmd=None, annotation=None):
    """
    Setup hotkeys for builds and removing marking menus on hotkey press and release.

    Args:
        menuName: A string name of the menu for which to create hotkeys
        hotkey: A string representing the hotkey to use for the menu, e.g. 'Alt+Shift+Q'
        importCmd: String formatted python for any imports required by preBuild or secondary commands
        preBuildCmd: String formatted python that is called before building the menu
        secondaryCmd: String formatted python to be called on release if the menu is not invoked
        annotation: A string description of the menu to use when building the runTimeCommand
    """
    # the format for runtime command ids
    rtCmdIdFmt = "quickMenus_{0}_{1}"
    # the format for named command ids
    namedCmdIdFmt = "quickMenus_{0}_{1}_nameCmd"
    # get kwargs from hotkey string
    keyKwargs = utils.getHotkeyKwargs(hotkey)

    # shared kwargs for all runtime commands
    runTimeKwargs = {
        "annotation": annotation,
        "category": "Custom Scripts.quickmenus",
        "cl": "python",
    }

    # clean prebuild and secondary commands
    importCmd = importCmd if importCmd else ""
    preBuildCmd = preBuildCmd if preBuildCmd else ""
    secondaryCmd = secondaryCmd if secondaryCmd else "pass"

    # create run time commands
    buildCmd = BUILD_MENU_CMD.format(
        menuName=menuName, importCmd=importCmd, preBuild=preBuildCmd, secondary=secondaryCmd)
    destroyCmd = DESTROY_MENU_CMD.format(
        menuName=menuName, importCmd=importCmd, preBuild=preBuildCmd, secondary=secondaryCmd)

    buildRtCmdId = rtCmdIdFmt.format("build", menuName)
    if pm.runTimeCommand(buildRtCmdId, q=True, ex=True):
        pm.runTimeCommand(buildRtCmdId, e=True, delete=True)
    pm.runTimeCommand(buildRtCmdId, c=buildCmd, **runTimeKwargs)

    buildNameCmdId = namedCmdIdFmt.format("build", menuName)
    pm.nameCommand(buildNameCmdId, c=buildRtCmdId,
                   ann=buildRtCmdId + " Named Command")

    destroyRtCmdId = rtCmdIdFmt.format("destroy", menuName)
    if pm.runTimeCommand(destroyRtCmdId, q=True, ex=True):
        pm.runTimeCommand(destroyRtCmdId, e=True, delete=True)
    pm.runTimeCommand(destroyRtCmdId, c=destroyCmd, **runTimeKwargs)

    destroyNameCmdId = namedCmdIdFmt.format("destroy", menuName)
    pm.nameCommand(destroyNameCmdId, c=destroyRtCmdId,
                   ann=destroyRtCmdId + " Named Command")

    # make sure we're in an editable hotkey set in >2017
    _switchToNonDefaultHotkeySet()

    pm.hotkey(name=buildNameCmdId, **keyKwargs)
    pm.hotkey(releaseName=destroyNameCmdId, **keyKwargs)


def removeMenuHotkeys(menuName, hotkey):
    """
    Remove all hotkeys for the given menu

    Args:
        menuName: A string name of the registered marking menu
        hotkey: A string representing the hotkey to use for the menu, e.g. 'Alt+Shift+Q'
    """
    rtCmdIdFmt = "quickMenus_{0}_{1}"
    namedCmdIdFmt = "quickMenus_{0}_{1}_nameCmd"
    # get kwargs from hotkey string
    keyKwargs = utils.getHotkeyKwargs(hotkey)

    buildRtCmdId = rtCmdIdFmt.format("build", menuName)
    if pm.runTimeCommand(buildRtCmdId, q=True, ex=True):
        pm.runTimeCommand(buildRtCmdId, e=True, delete=True)

    destroyRtCmdId = rtCmdIdFmt.format("destroy", menuName)
    if pm.runTimeCommand(destroyRtCmdId, q=True, ex=True):
        pm.runTimeCommand(destroyRtCmdId, e=True, delete=True)

    # clear hotkeys if set
    buildNameCmdId = namedCmdIdFmt.format("build", menuName)
    destroyNameCmdId = namedCmdIdFmt.format("destroy", menuName)
    keyQueryKwargs = keyKwargs.copy()
    key = keyQueryKwargs.pop('k')
    if pm.hotkey(key, query=True, name=True, **keyQueryKwargs) == buildNameCmdId:
        pm.hotkey(name="", **keyKwargs)
    if pm.hotkey(key, query=True, releaseName=True, **keyQueryKwargs) == destroyNameCmdId:
        pm.hotkey(releaseName="", **keyKwargs)


# Building / Destroying Menus
# ---------------------------

def buildMenus(menuName):
    """
    Build any marking menus that were registered for a menu name.

    Args:
        menuName: A string name of the registered marking menu
    """
    # perform destroy before building because sometimes
    # the release-hotkey gets skipped if the current
    # key modifiers change while the menu is active
    destroyMenus(menuName)

    # find any registered menus by name
    classes = getRegisteredMenus(menuName)
    LOG.debug('Building menu classes {0}: {1}'.format(menuName, classes))
    for menuCls in classes:
        if issubclass(menuCls, rmbmenuhook.Menu):
            # for rmb menus, just register with the manager
            rmbmenuhook.registerMenu(menuName, menuCls)
        else:
            inst = menuCls()
            if inst.shouldBuild():
                LOG.debug('Building: {0}'.format(inst))
                ACTIVE_MENUS.append(inst)
                inst.build()


def destroyMenus(menuName):
    """
    Destroy any marking menus that are currently built.

    Returns:
        True if any of the menus that were destroyed were
        shown at least once.
    """
    wasAnyInvoked = False

    global ACTIVE_MENUS
    for m in ACTIVE_MENUS:
        wasAnyInvoked = wasAnyInvoked or m.wasInvoked
        LOG.debug('Destroying menu: {0}'.format(m))
        m.destroy()
    ACTIVE_MENUS = []

    # check RMBMarkingMenu flag for invocation
    wasAnyInvoked = wasAnyInvoked or RMBMarkingMenu.wasInvoked
    RMBMarkingMenu.wasInvoked = False
    rmbmenuhook.unregisterMenu(menuName)

    return wasAnyInvoked


# Menu Registration
# -----------------

def registerMenu(menuName, cls):
    """
    Register a MarkingMenu class by name

    Args:
        menuName: A string name of the registered marking menu
        cls: A MarkingMenu subclass to register for being built later
    """
    global REGISTERED_MENUS
    # get existing list of registered menus of same name
    existing = REGISTERED_MENUS.get(menuName, [])
    # prevent duplicates
    REGISTERED_MENUS[menuName] = list(set(existing + [cls]))


def unregisterMenu(menuName, cls=None, all=False):
    """
    Unregister a MarkingMenu that was previously registered by name.

    Args:
        menuName: A string name of the registered marking menu
        cls: A MarkingMenu subclass to unregister
        all: A bool, when True, all menus registered with the given
            menu name are unregistered.
    """
    if not cls and not all:
        raise ValueError(
            "`cls` argument must be given when not unregistering all menus")
    global REGISTERED_MENUS
    if menuName in REGISTERED_MENUS:
        if all:
            REGISTERED_MENUS[menuName] = []
        elif cls in REGISTERED_MENUS[menuName]:
            REGISTERED_MENUS[menuName].remove(cls)
        # remove list if empty
        if not REGISTERED_MENUS[menuName]:
            del REGISTERED_MENUS[menuName]


def getRegisteredMenus(menuName):
    """
    Return the menu class that is registered under
    the given name

    Args:
        menuName: A string name of the registered marking menu
    """
    global REGISTERED_MENUS
    if menuName in REGISTERED_MENUS:
        return REGISTERED_MENUS[menuName][:]
    return []


def getAllRegisteredMenus():
    """
    Return all registered menus
    """
    global REGISTERED_MENUS
    return REGISTERED_MENUS.items()


class MarkingMenu(object):
    """
    The base class for any quick marking menu that can
    be registered. Provides core functionality of building
    and destroying a popup menu appropriately.
    """

    def __init__(self):
        # use current modifiers to determine popup menu modifiers
        isShiftPressed, isCtrlPressed, isAltPressed = utils.getModifiers()
        self.popupKeyKwargs = {
            'mm': True,
            'aob': True,
            'parent': 'viewPanes',
            'sh': isShiftPressed,
            'ctl': isCtrlPressed,
            'alt': isAltPressed,
        }
        # variable to keep track of if this menu ever showed
        self.wasInvoked = False
        # the panel that the popup menu will be attached to
        self.panel = pm.getPanel(underPointer=True)
        # the panel type, can be used when building to determine the menu's contents
        self.panelType = pm.getPanel(typeOf=self.panel)
        LOG.debug("Panel: " + self.panel + ", Panel Type: " + self.panelType)

        # the unique id for this popup menu, must be overridden in subclasses
        self.popupMenuId = None
        # the mouse button that triggers this popup menu, 1=lmb, 2=mmb, 3=rmb
        self.mouseButton = 1
        # when True, build menu items each time the menu is displayed
        self.buildItemsOnShow = False

    def shouldBuild(self):
        """
        Override to implement custom logic for whether or not this
        menu should be built
        """
        return True

    def build(self):
        """
        Build the popup menu that all menu items will be attached to
        """
        if not self.popupMenuId:
            raise NotImplementedError(
                "popupMenuId must be set on MarkingMenu classes")
        # calling destroy as a failsafe so that duplicate
        # menus dont get created
        self.destroy()
        self.menu = pm.popupMenu(
            self.popupMenuId, b=self.mouseButton, **self.popupKeyKwargs)
        self.menu.postMenuCommand(self.onMenuWillShow)
        # if not set to build on show, build items now
        if not self.buildItemsOnShow:
            pm.setParent(self.menu, m=True)
            self.buildMenuItems()

    def destroy(self):
        """
        Remove and destroy this menu
        """
        if pm.popupMenu(self.popupMenuId, q=True, ex=True):
            pm.deleteUI(self.popupMenuId)

    def onMenuWillShow(self, menu, parent):
        self.wasInvoked = True
        if self.buildItemsOnShow:
            self.menu.deleteAllItems()
            pm.setParent(self.menu, m=True)
            self.buildMenuItems()

    def buildMenuItems(self):
        """
        Build all menu items for the current popup menu.
        Called each time the menu is about to be displayed.
        """
        pass


class RMBMarkingMenu(rmbmenuhook.Menu):
    """
    The base class for a marking menu that uses right mouse button in a model viewport.
    This is slightly different than the normal marking menu, because it is registered
    with rmbmenuhook and is instanced only when invoked.
    """

    # currently using a class variable since the instance isn't
    # available when the other menus are destroyed
    wasInvoked = False

    def __init__(self, menu, obj=None):
        rmbmenuhook.Menu.__init__(self, menu, obj)
        # the panel that the popup menu will be attached to
        self.panel = pm.getPanel(up=True)
        # the panel type, can be used when building to determine the menu's contents
        self.panelType = pm.getPanel(typeOf=self.panel)

    def build(self):
        """
        Build the popup menu that all menu items will be attached to
        """
        RMBMarkingMenu.wasInvoked = True
        pm.setParent(self.menu, m=True)
        self.buildMenuItems()

    def buildMenuItems(self):
        """
        Build all menu items for the current popup menu.
        Called each time the menu is about to be displayed.
        """
        pass
