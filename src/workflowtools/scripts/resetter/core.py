
import pymel.core as pm
import logging

__all__ = [
    "getChannelBoxSelection",
    "getDefaults",
    "getDefaultsAttr",
    "getObjectsWithDefaults",
    "removeAllDefaults",
    "removeDefaults",
    "reset",
    "resetAll",
    "setDefaults",
    "setDefaultsCBSelection",
    "setDefaultsForAttrs",
    "setDefaultsNonkeyable",
]


DEFAULTS_ATTR = 'brstDefaults'

LOG = logging.getLogger('resetter')
LOG.setLevel(logging.INFO)



# Set/Get Defaults
# ----------------

def setDefaultsNonkeyable(nodes=None):
    setDefaults(nodes, nonkey=True)

def setDefaultsCBSelection(nodes=None):
    setDefaults(nodes, key=False, cbsel=True)

def setDefaults(nodes=None, attrList=[], key=True, nonkey=False, cbsel=False, attrQuery={}):
    """
    Set the default settings for the given nodes. Uses attributes based
    on the given settings. Default is to use all unlocked keyable attributes.
    Uses the selection if no nodes are given.
    
    `attrList` -- list of attributes to use. works in addition to other options
    `key` -- include keyable attributes
    `nonkey` -- include all channel box attributes, including nonkeyable
    `cbsel` -- use only the selected channel box attributes
    `attrQuery` -- a kwargs dict to be used with listAttr to find the
        attributes for which to store defaults. works in addition to other options
    """
    if nodes is None:
        nodes = pm.selected()
    if not isinstance(nodes, (list, tuple)):
        nodes = [nodes]
    nodes = [n for n in nodes if isinstance(n, (str, pm.nt.DependNode))]
    if len(nodes) == 0:
        return
    
    selAttrs = getChannelBoxSelection()
    # keyable and nonkeyable queries cannot be combined, so we build multiple queries.
    # any given customListAttr options are used as a third possible query
    queries = []
    if key:
        queries.append({'unlocked':True, 'k':True})
    if nonkey:
        queries.append({'unlocked':True, 'cb':True})
    if len(attrQuery) > 0:
        queries.append(attrQuery)
    def getAttrs(node):
        if cbsel:
            return selAttrs[node] if node in selAttrs else []
        else:
            listed = [a for a in [attrs for query in queries for attrs in node.listAttr(**query)]]
            custom = [node.attr(a) for a in attrList if node.hasAttr(a)]
            return listed + custom
    
    for n in nodes:
        attrs = getAttrs(n)
        if len(attrs) > 0:
            setDefaultsForAttrs(attrs)
        else:
            pm.warning('No matching attributes for {0} to set defaults. removing defaults'.format(n))
            removeDefaults(n)
    LOG.debug('set defaults for {0} object(s)'.format(len(nodes)))

def setDefaultsForAttrs(attrs):
    """
    Store the current values of each attr as defaults.
    Assumes the given attributes are all for the same object.
    """
    if attrs is None:
        return
    node = attrs[0].node()
    defaults = {}
    for attr in attrs:
        if attr.attrName() == DEFAULTS_ATTR:
            pm.warning('skipping {0} as it stores defaults and therefore cannot have a default'.format(attr))
            continue
        if attr.node() == node:
            try:
                defaults[attr.attrName()] = attr.get()
            except:
                # complex attributes just dont work
                pm.warning('could not store defaults for attribute: {0}'.format(attr))
    dattr = getDefaultsAttr(node, True)
    if dattr.isLocked():
        pm.warning('cannot store defaults, {0} is locked'.format(dattr))
    else:
        dattr.set(str(defaults))
        LOG.debug('stored {0} default(s) for {1}: {2}'.format(len(defaults.keys()), node, defaults.keys()))



def getObjectsWithDefaults(nodes=None):
    """
    Return all objects with defaults.
    Searches the given nodes, or all nodes if none are given.
    """
    if nodes is None:
        nodes = pm.ls()
    return [obj for obj in nodes if obj.hasAttr(DEFAULTS_ATTR)]

def getDefaultsAttr(node, create=False):
    """ Return the defaults attribute for the given nodeect """
    if not isinstance(node, (str, pm.nt.DependNode)):
        raise TypeError('expected node or node name, got {0}'.format(type(node).__name__))
    node = pm.PyNode(node)
    if create and not node.hasAttr(DEFAULTS_ATTR):
        if node.isReadOnly() or node.isLocked():
            pm.warning('Cannot add defaults to {0}. Node is locked or read-only'.format(node))
            return
        node.addAttr(DEFAULTS_ATTR, dt='string')
        dattr = node.attr(DEFAULTS_ATTR)
        dattr.set('{}')
    if node.hasAttr(DEFAULTS_ATTR):
        return node.attr(DEFAULTS_ATTR)

def getDefaults(node):
    """ Returns the defaults of a node, if they exist, as a dictionary. """
    dattr = getDefaultsAttr(node)
    if dattr is not None:
        defaultsRaw = None
        val = dattr.get()
        try:
            defaultsRaw = eval(val)
        except:
            pass
        # validate defaults
        if not isinstance(defaultsRaw, dict):
            pm.warning('invalid defaults found on: {0}'.format(node))
            return {}
        # process defaults
        defaults = {}
        for k, v in defaultsRaw.items():
            # skip the defaults attribute itself, if it somehow got in there
            if k == DEFAULTS_ATTR:
                pm.warning('skipping attribute {0}. it stores defaults and is therefore unable to have a default'.format(k))
                continue
            if not node.hasAttr(k):
                pm.warning('skipping default, {0} has no attribute .{1}'.format(node, k))
                continue
            # backwards compatibility checking
            if type(node.attr(k).get()) != type(v):
                pm.warning('default values for {0} are deprecated. please re-set the defaults'.format(node.attr(k)))
                # parse the value assuming its a tuple (old resetter)
                if isinstance(v, tuple) and len(v) == 1:
                    v = v[0]
            defaults[node.attr(k)] = v
        return defaults
    return {}
    



def removeDefaults(nodes=None):
    """
    Remove defaults from the given nodes.
    Returns the nodes for which defaults were removed.
    """
    if nodes is None:
        nodes = pm.selected()
    if not isinstance(nodes, (list, tuple)):
        nodes = [nodes]

    removed = []
    for n in nodes:
        if n.isReadOnly() or n.isLocked():
            pm.warning('Could not remove defaults from {0}. Node is locked or read-only.'.format(n))
            continue
        dattr = getDefaultsAttr(n)
        if dattr is not None:
            removed.append(pm.PyNode(n))
            dattr.delete()
    return removed

def removeAllDefaults():
    """ Remove all defaults from all objects in the scene. """
    return removeDefaults(getObjectsWithDefaults())



# Resetting
# ---------

def resetAll():
    """
    Find and reset all nodes in the scene that have
    defaults defined.
    """
    reset(getObjectsWithDefaults(), useBasicDefaults=False)


def reset(nodes=None, useBasicDefaults=True, useCBSelection=True):
    """
    Reset the given nodes' attributes to their default values.
    Uses the selection if no nodes are given.

    Args:
        useBasicDefaults: When True, if no defaults have been defined for a node, and the
            node is a transform, reset its translate, rotate, scale to 0, 0, and 1
        useCBSelection: When True, if there is a channel box selection, use it
            to limit which attributes will be reset
    """
    if nodes is None:
        nodes = pm.selected()
    else:
        if not isinstance(nodes, (list, tuple)):
            if not isinstance(nodes, (str, pm.nt.DependNode)):
                raise TypeError('expected node, node name, or list of nodes; got {0}'.format(type(nodes).__name__))
            nodes = [nodes]
        nodes = [pm.PyNode(n) for n in nodes]
    
    selAttrs = getChannelBoxSelection()
    for n in nodes:
        newAttrVals = {}
        # add pre-defined defaults
        defaults = getDefaults(n)
        newAttrVals.update(defaults)
        # add basic transform reset values
        if useBasicDefaults and len(newAttrVals) == 0:
            for a in [i+j for i in 'trs' for j in 'xyz']:
                # only add if they are settable
                if n.hasAttr(a) and n.attr(a).isSettable():
                    newAttrVals[n.attr(a)] = 1 if 's' in a else 0
        # trim using cb selection
        if useCBSelection and len(selAttrs) > 0:
            nodeSelAttrs = {} if not selAttrs.has_key(n) else selAttrs[n]
            delAttrs = [a for a in newAttrVals.keys() if a not in nodeSelAttrs]
            for a in delAttrs:
                del newAttrVals[a]
                
        for attr, value in newAttrVals.items():
            if attr.isSettable():
                try:
                    attr.set(value)
                except Exception as e:    
                    LOG.info ('skipping {0}. could not set attribute:'.format(attr))
                    LOG.info (e)
            else:
                LOG.info ('skipping {0}. attribute not settable'.format(attr))



# Utils
# -----


def getChannelBoxSelection(main=True, shape=True, out=True, hist=True):
    """
    Returns a dictionary representing the current selection in the channel box.
    
    eg. {myNode: ['attr1', 'attr2'], myOtherNode: ['attr1', 'attr2', 'attr3']}
    
    Includes attributes from these sections:
    `main` -- the main attributes section
    `shape` -- the shape nodes section
    `out` -- the outputs section of the node
    `hist` -- the inputs (history) section of the node
    """
    
    def cbinfo(flag):
        return pm.channelBox('mainChannelBox', q=True, **{flag:True})
    
    # for all flags {0} = m, s, o, or h (main, selected, out, history)
    # see channelBox documentation for flag specifications
    opts = {'m':main, 's':shape, 'o':out, 'h':hist}
    modes = [i[0] for i in opts.items() if i[1]]
    objFlag = '{0}ol' # o=object l=list
    attrFlag = 's{0}a' # s=selected, a=attrs
    
    result = {}
    for mode in modes:
        objs = cbinfo(objFlag.format(mode))
        attrs = cbinfo(attrFlag.format(mode))
        if objs is not None and attrs is not None:
            for obj in objs:
                pyobj = pm.PyNode(obj)
                if not result.has_key(pyobj):
                    result[pyobj] = []
                thisObjsAttrs = [pyobj.attr(a) for a in attrs if pyobj.hasAttr(a)]
                result[pyobj].extend(thisObjsAttrs)
    
    return result

