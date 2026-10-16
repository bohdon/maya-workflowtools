import maya.cmds as mc
import maya.mel as mel

def model_panel_menus():
    modelPanels = mc.getPanel(typ='modelPanel')
    viewPortMenus = []
    for modPanel in modelPanels:
        try:
            viewPortMenus =  mc.menuBarLayout(modPanel, q=1, ma=1)
            for menu_ in viewPortMenus:
                print(menu_)
                mel.eval(f'updateShadingMenu {viewPortMenus[1]} {modPanel}')
                mel.eval(f'updateLightingMenu {viewPortMenus[2]} {modPanel}')
                mel.eval(f'updateShowMenu {viewPortMenus[3]} {modPanel} {modPanel} "Playblast Display"')
        except:
            pass
                
                
# PyMEL
'''
import pymel.core as pm
def model_panel_menus():
    modelPanels = pm.getPanel(typ='modelPanel')
    viewPortMenus = []
    for modPanel in modelPanels:
        viewPortMenus =  pm.menuBarLayout(modPanel, q=1, ma=1)    
        for menu in viewPortMenus:
            mel.eval(f'updateShadingMenu {viewPortMenus[1]} {modPanel.name()}')
            mel.eval(f'updateLightingMenu {viewPortMenus[2]} {modPanel.name()}')
            mel.eval(f'updateShowMenu {viewPortMenus[3]} {modPanel.name()} {modPanel.name()} "Playblast Display"')
'''