
import pymel.core as pm
import logging

from . import core

__all__ = [
    "GUI",
    "printDefaults",
    "printObjectsWithDefaults",
]

LOG = logging.getLogger('resetter')
LOG.setLevel(logging.INFO)


# Utils
# -----

def printObjectsWithDefaults():
    nodes = core.getObjectsWithDefaults()
    LOG.info('Objects with defaults ({0})'.format(len(nodes)))
    for n in nodes:
        LOG.info('   {0}'.format(n))


def printDefaults():
    nodes = core.getObjectsWithDefaults()
    LOG.info('Object defaults ({0})'.format(len(nodes)))
    for n in nodes:
        defaults = core.getDefaults(n)
        LOG.info('   {0}: {1}'.format(n, defaults))


def selectObjectsWithDefaults():
    pm.select(core.getObjectsWithDefaults())


# View
# ----

class GUI(object):
    def __init__(self):
        self.winName = 'boResetterWin'
        # define colors
        self.colSet = [0.3, 0.36, 0.49]
        self.colRemove = [0.49, 0.3, 0.3]
        self.colReset = [0.2, 0.2, 0.2]
        self.colReset2 = [0.25, 0.25, 0.25]
        self.build()

    def build(self):
        # check for pre-existing window
        if pm.window(self.winName, ex=True):
            pm.deleteUI(self.winName, wnd=True)

        if not pm.windowPref(self.winName, ex=True):
            pm.windowPref(self.winName, tlc=(200, 200))
        pm.windowPref(self.winName, e=True, w=280, h=100)

        with pm.window(self.winName, rtf=1, mb=1, tlb=True, t='Resetter') as self.win:
            imenu = pm.menu(l='Info')
            pm.setParent(imenu, m=True)
            pm.menuItem(l='Select Objects with Defaults',
                        c=pm.Callback(selectObjectsWithDefaults))
            pm.menuItem(l='Print Objects with Defaults',
                        c=pm.Callback(printObjectsWithDefaults))
            pm.menuItem(l='Print Default Values', c=pm.Callback(printDefaults))

            with pm.formLayout(nd=100) as form:

                with pm.frameLayout(l='Set/Remove Defaults', bs='out', mw=2, mh=2, cll=True, cl=True) as setFrame:
                    with pm.columnLayout(rs=2, adj=True):
                        pm.button(l='Set Defaults', c=pm.Callback(core.setDefaults), bgc=self.colSet,
                                  ann='Set defaults on the selected objects using all keyable attributes')
                        pm.button(l='Set Defaults Include Non-Keyable', c=pm.Callback(core.setDefaultsNonkeyable), bgc=self.colSet,
                                  ann='Set defaults on the selected objects using keyable and non-keyable attributes in the channel box')
                        pm.button(l='Set Defaults with CB Selection', c=pm.Callback(core.setDefaultsCBSelection),
                                  bgc=self.colSet, ann='Set defaults on the selected objects using the selected channel box attributes')
                        pm.button(l='Remove Defaults', c=pm.Callback(
                            core.removeDefaults), bgc=self.colRemove, ann='Remove all defaults from the selected objects')
                        pm.button(l='Remove from All Objects', c=pm.Callback(
                            core.removeAllDefaults), bgc=self.colRemove, ann='Remove defaults from all objects in the scene')

                with pm.frameLayout(l='Reset', bs='out', mw=2, mh=2) as resetFrame:
                    with pm.formLayout(nd=100) as resetForm:
                        b6 = pm.button(l='Reset', c=pm.Callback(core.reset), bgc=self.colReset,
                                       ann='Reset the selected objects. Uses basic transform defaults if no defaults are defined for translate, rotate, and scale')
                        b7 = pm.button(l='Defined Only', c=pm.Callback(
                            self.resetDefinedOnly), bgc=self.colReset, ann='Reset the selected objects using only defined defaults')
                        b9 = pm.button(l='All Defined', c=pm.Callback(
                            core.resetAll), bgc=self.colReset2, ann='Reset all objects in the scene with defaults')
                        pm.formLayout(resetForm, e=True,
                                      ap=[(b6, 'left', 0, 0), (b6, 'right', 2, 33),
                                          (b7, 'left', 2, 33), (b7, 'right', 2, 66),
                                          (b9, 'left', 2, 66), (b9, 'right', 2, 100), ])

                mw = 4
                pm.formLayout(form, e=True,
                              af=[(setFrame, 'left', mw), (setFrame, 'right', mw),
                                  (resetFrame, 'left', mw), (resetFrame, 'right', mw)],
                              ac=[(resetFrame, 'top', 2, setFrame)],)

    def resetDefinedOnly(self):
        core.reset(useBasicDefaults=False)

    def resetBasicTransformsOnly(self):
        core.resetBasicTransforms()
