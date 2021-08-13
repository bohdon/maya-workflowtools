
import pymel.core as pm


__all__ = [
    "getHotkeyKwargs",
    "getModifiers",
    "getRadialMenuPositions",
]


def getModifiers():
    """
    Return the state of all modifier keys

    Returns:
        A tuple of bools representing (isShiftPressed, isCtrlPressed, isAltPressed)
    """
    mods = pm.cmds.getModifiers()
    isShiftPressed = (mods & 1) > 0
    isCtrlPressed = (mods & 4) > 0
    isAltPressed = (mods & 8) > 0
    return (isShiftPressed, isCtrlPressed, isAltPressed)


def getHotkeyKwargs(keyString):
    """
    Return kwargs to be given to the maya `hotkey` command given a hotkey string

    Args:
        keyString: A string representing a hotkey, including modifiers, e.g. 'Alt+Shift+Q'
    """
    split = keyString.lower().split('+')
    kwargs = {}
    for s in split:
        if s == 'alt':
            kwargs['alt'] = True
        elif s == 'shift':
            kwargs['sht'] = True
        elif s == 'ctrl':
            kwargs['ctl'] = True
        elif s == 'command':
            kwargs['cmd'] = True
        else:
            if 'k' not in kwargs:
                kwargs['k'] = s
            else:
                raise ValueError('Invalid keyString: ' + keyString)
    return kwargs


def getRadialMenuPositions(count):
    """
    Return a list of radial positions for the given number of items.
    Positions are distributed when count is lower than 8

    Args:
        count: An int representing number of items in the menu
    """
    if count < 0:
        raise ValueError("count cannot be negative")
    defaults = [
        [], ['N'], ['N', 'S'], ['N', 'E', 'W'], ['N', 'E', 'S', 'W'],
    ]
    ordered = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    if count < len(defaults):
        return defaults[count]
    else:
        results = []
        for i in range(count):
            if i < len(ordered):
                results.append(ordered[i])
            else:
                results.append(None)
        return results
