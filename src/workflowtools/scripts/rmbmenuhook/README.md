# Maya RMB Marking Menu Hook

A very specific util for hooking into and extending the right mouse button marking menus in Maya.

Adding marking menus using hotkeys for most button combinations is easy, but the right mouse button (unmodified) is inextensible in vanilla Maya. This project makes it easy to conditionally add menus that can replace the RMB default marking menus.


## Basic Example

A simple example would be adding a menu that displays `Switch to IK` or `Switch to FK` if an IKFK animation control is selected.

```python
import pymel.core as pm
import rmbmenuhook

def isIKFKControl(object):
  ...

class IKFKSwitchMenu(rmbmenuhook.Menu):

  def shouldBuild(self):
    # self.object is the name of the object that is selected or under the mouse cursor
    return isIKFKControl(self.object)
  
  def build(self):
    # self.menu is the parent marking menu that menuItems should be attached to
    pm.setParent(self.menu, m=True)
    pm.menuItem(l='Switch to IK', rp='W')
    pm.menuItem(l='Switch to FK', rp='E')

# register the menu by name, so it can be unregistered by name, and give it a priority
rmbmenuhook.registerMenu('IKFKSwitchMenu', IKFKSwitchMenu, 1)
```

## Installation

Download the [latest release](https://github.com/bohdon/maya-rmbmenuhook/releases/latest) and unzip the contents into your `~/Documents/maya/modules` folder.

Add the following to `userSetup.py`:

```python
# enable RMB Marking Menu Hook
import rmbmenuhook
rmbmenuhook.enable()
```

## Version 1.0.2 (2017-10-21)
- Adds 2018 mel overrides

## Version 1.0.1 (2017-05-26)
- Updates 2015 mel overrides

## Version 1.0.0 (2017-05-21)
- Adds 2017 mel overrides
- Adds registering and unregistering menus as a replacement for finding subclasses

