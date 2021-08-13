"""
Contains functions for registering menus that can be built
using the rmb hook.

Example Menu:

class MyMenu(Menu):
    def build(self):
        pm.setParent(self.menu, m=True)
        pm.menuItem(l='My Action')

Example Menu that only appears when right clicking on an object:

class MyObjectMenu(Menu):
    def shouldBuild(self):
        return self.hit

    def build(self):
        pm.setParent(self.menu, m=True)
        pm.menuItem(l='My Object Action')

"""

import pymel.core as pm

__all__ = [
    'registerMenu',
    'unregisterMenu',
    'getRegisteredMenu',
    'getAllRegisteredMenus',
    'getPrioritizedMenuClasses',
    'buildMenu',
    'Menu',
]


REGISTERED_MENUS = {}

def registerMenu(name, cls, priority=0):
    """
    Register a Menu class under the given name
    with the given priority.
    """
    global REGISTERED_MENUS
    REGISTERED_MENUS[name] = (cls, priority)

def unregisterMenu(name):
    """
    Unregister a Menu that was previously registered
    under the given name.
    """
    global REGISTERED_MENUS
    if name in REGISTERED_MENUS:
        del REGISTERED_MENUS[name]

def getRegisteredMenu(name):
    """
    Return the menu class that is registered under
    the given name
    """
    global REGISTERED_MENUS
    if name in REGISTERED_MENUS:
        return REGISTERED_MENUS[name]

def getAllRegisteredMenus():
    """
    Return all registered menus
    """
    global REGISTERED_MENUS
    return REGISTERED_MENUS.items()

def getPrioritizedMenuClasses():
    """
    Return a list Menu classes sorted by priority
    with higher priority numbers ordered first.
    """
    # registered values are tuples of (cls, priority)
    global REGISTERED_MENUS
    classes = REGISTERED_MENUS.values()
    # sort by priority
    classes.sort(key=lambda x: x[1])
    classes.reverse()
    # return only the classes
    return [c for (c, p) in classes]



def buildMenu(menu, obj=None):
    """
    Build a rmb marking menu (if one is available) using
    the given menu and object which were passed by the rmb hooks
    from mel where they originated.


    `obj` will be set if an object is under the mouse
        or a transform/shape is selected.
    """
    classes = getPrioritizedMenuClasses()
    for menuCls in classes:
        inst = menuCls(menu, obj)
        if inst.shouldBuild():
            inst.build()
            return True
    return False




class Menu(object):
    """
    The base class for any rmb marking menu.
    Menu classes must be registered before they will be
    considered for building.

    Menus have the following members available for use:
        `self.menu` - the name of the parent popup menu
        `self.object` - the name of the selected or hit object, if any
        `self.hit` - whether the mouse is currently over the object
    """

    def __init__(self, menu, obj=None):
        self.menu = pm.ui.Menu(menu)
        self.object = obj
        self.hit = bool(pm.mel.dagObjectHit())

    def shouldBuild(self):
        """
        Override to implement custom logic for whether or not this
        menu should be built
        """
        return True

    def build(self):
        """
        Build a custom menu using `self.menu` as the parent.
        `self.object` is the current selected or hit object.
        `self.hit` is True if the object is under the mouse cursor.
        """
        pass