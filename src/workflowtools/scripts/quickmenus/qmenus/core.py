
from .. import core
import menus


__all__ = [
    "disable",
    "enable",
    "registerHotkeys",
    "removeHotkeys",
]

def registerHotkeys():
    importCmd = "import maya.mel as mel"
    preBuildCmd = "mel.eval('global string $gSelect; setToolTo $gSelect;')"
    description = "Selection and display masking menus, as well as a camera quick switch menu"
    core.registerMenuHotkeys("QMenus", "Q", importCmd=importCmd, preBuildCmd=preBuildCmd, annotation=description)

    description2 = "Component selection and resetter menus"
    core.registerMenuHotkeys("AltQMenus", "Alt+Q", annotation=description2)

    print('Quick Menus: Q-Menu hotkeys registered')


def removeHotkeys():
    core.removeMenuHotkeys("QMenus", "Q")
    core.removeMenuHotkeys("AltQMenus", "Alt+Q")
    print('Quick Menus: Q-Menu hotkeys removed')


def enable():
    # TODO: would be nice to define mouse button and hotkey for each here
    core.registerMenu("QMenus", menus.SelectionMaskingMenu)
    core.registerMenu("QMenus", menus.DisplayMaskingMenu)
    core.registerMenu("QMenus", menus.CameraQuickSwitchMenu)
    core.registerMenu("AltQMenus", menus.ComponentSelectionMaskingMenu)
    core.registerMenu("AltQMenus", menus.ResetterMenu)
    print('Quick Menus: Q-Menus enabled')


def disable():
    core.unregisterMenu("QMenus", all=True)
    print('Quick Menus: Q-Menus disabled')

