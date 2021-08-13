
import logging

import pymel.core as pm

try:
    import resetter
except:
    resetter = None

from .. import core
from .. import utils


__all__ = [
    'CameraQuickSwitchMenu',
    'ComponentSelectionMaskingMenu',
    'DisplayMaskingMenu',
    'ResetterMenu',
    'SelectionMaskingMenu',
]


LOG = logging.getLogger('quickmenus')


class SelectionMaskingMenu(core.MarkingMenu):
    """
    A radial menu for quickly changing selection masking settings.
    Only displays on model viewport panels.
    """

    allkeys = [
        'handle', 'ikHandle', 'joint', 'nurbsCurve',
        'cos', 'stroke', 'nurbsSurface', 'polymesh',
        'subdiv', 'plane', 'lattice', 'cluster',
        'sculpt', 'nonlinear', 'particleShape', 'emitter',
        'field', 'spring', 'rigidBody', 'fluid',
        'hairSystem', 'follicle', 'rigidConstraint', 'collisionModel',
        'light', 'camera', 'texture', 'ikEndEffector',
        'locator', 'dimension', 'nCloth', 'nRigid', 'dynamicConstraint',
    ]

    def __init__(self):
        super().__init__()
        self.popupMenuId = 'QuickMenus_SelectionMaskingMenu'
        self.mouseButton = 1
        self.buildItemsOnShow = True

    def shouldBuild(self):
        return self.panelType == 'modelPanel'

    def buildMenuItems(self):
        pm.menuItem(rp='NW', l='Reset', ecr=False, ann='Reset all selection masks',
                    c=pm.Callback(self.resetSelectionMasking))
        pm.menuItem(rp='NE', l='All Off', ecr=False, c=pm.Callback(
            self.setObjectSelectType, enabled=False, keys=self.allkeys))
        pm.menuItem(rp='SE', l='Clear Selection', ecr=True,
                    c=pm.Callback(pm.select, cl=True))
        pm.menuItem(rp='S', l='Use Selected',
                    c=pm.Callback(self.setMaskingToSelection))

        def selType(x): return pm.selectType(q=True, **{x: True})

        # common masking
        pm.menuItem(rp='N', l='Polys', ecr=False, cb=selType(
            'p'), c=pm.CallbackWithArgs(self.setObjectSelectType, keys=['polymesh']))
        pm.menuItem(rp='E', l='Curves', ecr=False, cb=selType('nurbsCurve'), c=pm.CallbackWithArgs(
            self.setObjectSelectType, keys=['nurbsCurve', 'cos', 'stroke']))
        pm.menuItem(rp='SW', l='Joints', ecr=False, cb=selType(
            'joint'), c=pm.CallbackWithArgs(self.setObjectSelectType, keys=['joint']))
        pm.menuItem(rp='W', l='Surfaces', ecr=False, cb=selType('nurbsSurface'), c=pm.CallbackWithArgs(
            self.setObjectSelectType, keys=['nurbsSurface', 'subdiv', 'plane']))

        # extended menu
        pm.menuItem(l='Selection Masking', en=False)
        pm.menuItem(d=True)
        pm.menuItem(l='Render', ecr=False, cb=selType('light'), c=pm.CallbackWithArgs(
            self.setObjectSelectType, keys=['light', 'camera', 'texture']))
        pm.menuItem(l='Deformers', ecr=False, cb=selType('lattice'), c=pm.CallbackWithArgs(
            self.setObjectSelectType, keys=['lattice', 'cluster', 'sculpt', 'nonlinear']))
        pm.menuItem(l='Dynamics', ecr=False, cb=selType('particleShape'), c=pm.CallbackWithArgs(self.setObjectSelectType, keys=[
                    'particleShape', 'emitter', 'field', 'spring', 'rigidBody', 'fluid', 'hairSystem', 'follicle', 'rigidConstraint']))
        pm.menuItem(l='Misc', ecr=False, cb=selType('ikEndEffector'), c=pm.CallbackWithArgs(
            self.setObjectSelectType, keys=['ikEndEffector', 'locator', 'dimension']))

    def setObjectSelectType(self, enabled, keys):
        pm.selectMode(object=True)
        kwargs = {}
        for k in keys:
            kwargs[k] = enabled
        pm.selectType(**kwargs)

    def resetSelectionMasking(self):
        pm.selectMode(component=True)
        pm.selectMode(object=True)
        pm.mel.selectionMaskResetAll()

    def setMaskingToSelection(self):
        self.setObjectSelectType(enabled=False, keys=self.allkeys)
        sel = pm.selected()
        keys = set()
        for obj in sel:
            if obj.nodeType() == 'transform':
                shapes = obj.getShapes()
                if len(shapes):
                    selType = shapes[0].nodeType()
                    if selType in ['nurbsSurface', 'subdiv', 'joint', 'camera', 'locator']:
                        keys.add(str(selType))
                    elif selType == 'mesh':
                        keys.add('polymesh')
                    elif 'light' in selType.lower():
                        keys.add('light')
                    elif selType == 'nurbsCurve':
                        keys.add('curve')
        if not len(keys):
            return
        LOG.info('Set selection masking to {0}'.format(', '.join(keys)))
        self.setObjectSelectType(enabled=True, keys=keys)


class DisplayMaskingMenu(core.MarkingMenu):
    """
    A radial menu for quickly changing display masking settings.
    Only displays on model viewport panels.
    """

    def __init__(self):
        super().__init__()
        self.popupMenuId = 'QuickMenus_DisplayMaskingMenu'
        self.mouseButton = 2
        self.buildItemsOnShow = True

    def shouldBuild(self):
        return self.panelType == 'modelPanel'

    def buildMenuItems(self):
        pm.menuItem(rp='NW', l='Show All', ecr=False, c=pm.Callback(
            self.setDisplay, enabled=True, keys=['allObjects']))
        pm.menuItem(rp='NE', l='Hide All', ecr=False, c=pm.Callback(
            self.setDisplay, enabled=False, keys=['allObjects']))
        pm.menuItem(rp='S', l='Hide Selected', ecr=True,
                    c=pm.Callback(self.hideSelected))

        def query(x): return pm.modelEditor(self.panel, q=True, **{x: True})

        # common masking
        pm.menuItem(rp='N', l='Polys', ecr=False, cb=query(
            'polymeshes'), c=pm.CallbackWithArgs(self.setDisplay, keys=['polymeshes']))
        pm.menuItem(rp='E', l='Curves', ecr=False, cb=query(
            'nurbsCurves'), c=pm.CallbackWithArgs(self.setDisplay, keys=['nurbsCurves']))
        pm.menuItem(rp='W', l='Surfaces', ecr=False, cb=query('nurbsSurfaces'), c=pm.CallbackWithArgs(
            self.setDisplay, keys=['nurbsSurfaces', 'subdivSurfaces']))
        pm.menuItem(rp='SW', l='Joints', ecr=False, cb=query(
            'joints'), c=pm.CallbackWithArgs(self.setDisplay, keys=['joints']))
        pm.menuItem(rp='SE', l='Lights', ecr=False, cb=query(
            'lights'), c=pm.CallbackWithArgs(self.setDisplay, keys=['lights']))

        # extended menu
        pm.menuItem(l='Display Masking', en=False)
        pm.menuItem(d=True)
        pm.menuItem(l='Cameras', ecr=False, cb=query('cameras'),
                    c=pm.CallbackWithArgs(self.setDisplay, keys=['cameras']))
        pm.menuItem(l='Locators', ecr=False, cb=query('locators'),
                    c=pm.CallbackWithArgs(self.setDisplay, keys=['locators']))
        pm.menuItem(l='Deformers', ecr=False, cb=query('deformers'),
                    c=pm.CallbackWithArgs(self.setDisplay, keys=['deformers']))
        pm.menuItem(l='Dynamics', ecr=False, cb=query('dynamics'),
                    c=pm.CallbackWithArgs(self.setDisplay, keys=['dynamics']))
        pm.menuItem(l='Misc', ecr=False, cb=query('planes'), c=pm.CallbackWithArgs(self.setDisplay, keys=[
                    'planes', 'ikHandles', 'fluids', 'hairSystems', 'follicles', 'dynamicConstraints', 'pivots', 'handles', 'textures', 'strokes']))
        # pm.menuItem(l='GUI', ecr=False, cb=query('planes'), c=pm.CallbackWithArgs(self.setObjectSelectType, keys=['ikEndEffector', 'locator', 'dimension']))

    def setDisplay(self, enabled, keys):
        kwargs = {}
        for k in keys:
            kwargs[k] = enabled
        pm.modelEditor(self.panel, e=True, **kwargs)

    def hideSelected(self):
        sel = pm.selected()
        keys = set()
        for obj in sel:
            objkeys = self.getDisplayKeys(obj)
            for k in objkeys:
                keys.add(k)
        if not len(keys):
            return
        LOG.info('Hiding {0}'.format(', '.join(keys)))
        self.setDisplay(False, keys)

    def getDisplayKeys(self, obj):
        # conversion of node type -> display flag
        nodeTypeDict = {
            'nurbsCurve': 'nurbsCurves',
            'nurbsSurface': 'nurbsSurfaces',
            'mesh': 'polymeshes',
            'subdiv': 'subdivSurfaces',
            'plane': 'planes',
            'light': 'lights',
            'camera': 'cameras',
            'controlVertices': 'controlVertices',
            'grid': 'grid',
            'hulls': 'hulls',
            'joint': 'joints',
            'ikHandle': 'ikHandles',
            'lattice': 'deformers',
            'clusterHandle': 'deformers',
            'softModHandle': 'deformers',
            'deformFunc': 'deformers',
            'implicitSphere': 'deformers',
            'particle': 'dynamics',
            'pointEmitter': 'dynamics',
            'rigidBody': 'dynamics',
            'field': 'dynamics',
            'rigidConstraint': 'dynamics',
            'fluidShape': 'fluids',
            'hairSystem': 'hairSystems',
            'follicle': 'follicles',
            'nCloth': 'nCloths',
            'nParticle': 'nParticles',
            'nRigid': 'nRigids',
            'dynamicConstraint': 'dynamicConstraints',
            'locator': 'locators',
            'manipulators': 'manipulators',
            'dimensionShape': 'dimensions',
            'handle': 'handles',
            'pivot': 'pivots',
            'place3dTexture': 'textures',
            'place2dTexture': 'textures',
            'pfxGeometry': 'strokes',
        }
        types = self.getShapeTypes(obj, nodeTypeDict.keys())
        keys = [nodeTypeDict[t] for t in types if t in nodeTypeDict]
        return keys

    def getShapeTypes(self, obj, options):
        """
        Return all shape types represented by the given object
        that are in the given list of options
        Climbs the inheritance tree to find values if needed
        """
        objtype = obj.nodeType()
        if objtype in options:
            return [objtype]
        # get shapes
        if objtype == 'transform':
            shapes = obj.getShapes()
        else:
            shapes = [objtype]
        # analyze shape types
        types = []
        for s in shapes:
            inheritypes = s.nodeType(i=True)
            for t in reversed(inheritypes):
                if t in options:
                    types.append(t)
                    break
        return types


class CameraQuickSwitchMenu(core.RMBMarkingMenu):
    """
    A radial menu that displays all cameras in the scene for easy switching.
    """

    def buildMenuItems(self):
        # find camera
        try:
            camUnderPointer = pm.PyNode(
                pm.modelPanel(self.panel, q=True, cam=True))
            if isinstance(camUnderPointer, pm.nt.Camera):
                camera = camUnderPointer
            else:
                camera = camUnderPointer.getShape()
        except:
            LOG.warning(
                'could not find camera for panel: {0}'.format(self.panel))
            return

        menuItemCol = pm.radioMenuItemCollection()
        isOrtho = camera.isOrtho()
        # list same type camera in radial positions
        similar = sorted([c for c in pm.ls(typ='camera')
                         if c.isOrtho() == isOrtho])
        rps = utils.getRadialMenuPositions(len(similar))
        for cam, rp in zip(similar, rps):
            kw = {}
            if rp is not None:
                kw['rp'] = rp
            if cam == camera:
                kw['rb'] = True
                kw['cl'] = menuItemCol
            pm.menuItem(l=cam.getParent(), c=pm.Callback(
                pm.mel.lookThroughModelPanel, str(cam), str(self.panel)), **kw)
        if len(rps) > 8:
            pm.menuItem(d=True)
        # list other cameras
        dissimilar = sorted(
            [c for c in pm.ls(typ='camera') if c.isOrtho() != isOrtho])
        for cam in dissimilar:
            pm.menuItem(l=cam.getParent(), c=pm.Callback(
                pm.mel.lookThroughModelPanel, str(cam), str(self.panel)))


class ComponentSelectionMaskingMenu(core.MarkingMenu):
    allkeys = [
        'cv', 'vertex', 'subdivMeshPoint', 'latticePoint',
        'particle', 'editPoint', 'curveParameterPoint',
        'surfaceParameterPoint', 'puv', 'polymeshEdge',
        'subdivMeshEdge', 'isoparm', 'surfaceEdge', 'surfaceFace',
        'springComponent', 'facet', 'subdivMeshFace', 'hull',
        'rotatePivot', 'scalePivot', 'jointPivot', 'selectHandle',
        'localRotationAxis', 'imagePlane', 'surfaceUV'
    ]

    def __init__(self):
        super().__init__()
        self.popupMenuId = 'QuickMenus_ComponentSelectionMaskingMenu'
        self.mouseButton = 1
        self.buildItemsOnShow = True

    def shouldBuild(self):
        return self.panelType == 'modelPanel'

    def buildMenuItems(self):
        pm.menuItem(rp='N', l='Points', ecr=False, c=pm.Callback(self.setComponentSelectType, keys=[
                    'cv', 'vertex', 'subdivMeshPoint', 'latticePoint', 'particle']))
        pm.menuItem(rp='NE', l='Handles', ecr=False, c=pm.Callback(
            self.setComponentSelectType, keys=['selectHandle']))
        pm.menuItem(rp='E', l='Lines', ecr=False, c=pm.Callback(self.setComponentSelectType, keys=[
                    'polymeshEdge', 'subdivMeshEdge', 'isoparm', 'surfaceEdge', 'springComponent']))
        pm.menuItem(rp='SE', l='Hulls', ecr=False, c=pm.Callback(
            self.setComponentSelectType, keys=['hull']))
        pm.menuItem(rp='S', l='Faces', ecr=False, c=pm.Callback(
            self.setComponentSelectType, keys=['surfaceFace', 'facet', 'subdivMeshFace']))
        pm.menuItem(rp='SW', l='Pivots', ecr=False, c=pm.Callback(
            self.setComponentSelectType, keys=['rotatePivot', 'scalePivot', 'jointPivot']))
        pm.menuItem(rp='W', l='Param', ecr=False, c=pm.Callback(self.setComponentSelectType, keys=[
                    'editPoint', 'curveParameterPoint', 'surfaceParameterPoint', 'surfaceUV', 'puv']))
        pm.menuItem(rp='NW', l='Misc', ecr=False, c=pm.Callback(
            self.setComponentSelectType, keys=['localRotationAxis', 'imagePlane']))

    def setComponentSelectType(self, enabled=True, keys={}):
        pm.selectMode(component=True)
        kwargs = {}
        for k in keys:
            kwargs[k] = enabled
        for k in self.allkeys:
            if k not in kwargs:
                kwargs[k] = not enabled
        pm.selectType(**kwargs)


class ResetterMenu(core.MarkingMenu):

    def __init__(self):
        super().__init__()
        self.popupMenuId = 'QuickMenus_ResetterMenu'
        self.mouseButton = 2

    def shouldBuild(self):
        return self.panelType == 'modelPanel'

    def buildMenuItems(self):
        self.buildSimpleItems()
        self.buildResetterItems()

    def buildSimpleItems(self):
        pm.menuItem(rp='W', l='Rotate', ecr=True, c=pm.Callback(
            self.simpleReset, rot=True), ann='Reset the rotation of the selected objects')
        pm.menuItem(rp='S', l='Translate', ecr=True, c=pm.Callback(
            self.simpleReset, trans=True), ann='Reset the position of the selected objects')
        pm.menuItem(rp='E', l='Scale', ecr=True, c=pm.Callback(
            self.simpleReset, scale=True), ann='Reset the scale of the selected objects')
        if not resetter:
            # add fallback menu item if resetter is not available
            pm.menuItem(rp='N', l='TRS', ecr=True, c=pm.Callback(self.simpleReset, trans=True, rot=True, scale=True),
                        ann='Reset the selected objects\' transformations to identity, even if defaults are set')

    def buildResetterItems(self):
        if not resetter:
            return
        pm.menuItem(rp='N', l='Smart', ecr=True, c=pm.Callback(resetter.reset),
                    ann='Reset the selected objects\' attributes to the defaults, or identity if defaults are not set')
        pm.menuItem(rp='NE', l='Defaults', ecr=True, c=pm.CallbackWithArgs(resetter.reset, useBasicDefaults=False),
                    ann='Reset the selected objects\' attributes to their defaults, does nothing if no defaults are set')
        pm.menuItem(rp='SE', l='All Defaults', ecr=True, c=pm.Callback(resetter.resetAll),
                    ann='Reset all objects\' attributes with defaults set to their default values')

        pm.menuItem(l='Resetter', ecr=False, c=pm.Callback(
            resetter.GUI), ann='Open the Resetter GUI')
        pm.menuItem(d=True)
        pm.menuItem(l='Select Objects', ecr=True, c=pm.Callback(self.selectObjectsWithDefaults),
                    ann='Select all objects in the scene that have attribute defaults')

    def selectObjectsWithDefaults(self):
        if resetter:
            pm.select(resetter.getObjectsWithDefaults())

    def simpleReset(self, trans=False, rot=False, scale=False):
        for obj in pm.selected(typ='transform'):
            if trans:
                obj.t.set([0, 0, 0])
            if rot:
                obj.r.set([0, 0, 0])
            if scale:
                obj.s.set([1, 1, 1])
