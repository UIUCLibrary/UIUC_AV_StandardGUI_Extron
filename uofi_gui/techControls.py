from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice

## Begin ControlScript Import --------------------------------------------------
from extronlib import event
from extronlib.system import MESet

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------


## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from utilityFunctions import DictValueSearchByKey, Log, RunAsync, debug

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class TechMenuController:
    def __init__(self,
                 UIHost: 'ExUIDevice') -> None:
        # Public Properties
        # utilityFunctions.Log('Set Public Properties')
        self.UIHost = UIHost
        self.GUIHost = self.UIHost.GUIHost
        self.TechMenuOpen = False
        
        # Private Properties
        # utilityFunctions.Log('Set Private Properties')
        self._PageSelects = \
            {
                'Tech-AdvancedVolume': self._AdvVolPage,
                'Tech-CameraControls': self._CamCtlsPage,
                'Tech-DisplayControls': self._DispCtlPage,
                'Tech-ManualMatrix': self._ManMtxPage,
                'Tech-RoomConfig': self._RmCfgPage
            }
        self._PageUpdates = \
            {
                'Tech-SystemStatus': self._StatusPage
            }
            
        self._menuBtns = MESet([])
        self._defaultPage = 'Tech-SystemStatus'
        self._defaultBtn = None
        for btn in DictValueSearchByKey(self.UIHost.Btns, r'Tech-\w+$', regex=True):
            if btn.Name in self._PageSelects.keys():
                btn.Page = self._PageSelects[btn.Name]()
            else:
                btn.Page = btn.Name
            self._menuBtns.Append(btn)
            if btn.Name in self._defaultPage:
                self._defaultBtn = btn
        
        self._ctlBtns = \
            {
                'prev': self.UIHost.Btns['Tech-Menu-Previous'],
                'next': self.UIHost.Btns['Tech-Menu-Next'],
                'exit': self.UIHost.Btns['Tech-Menu-Exit'],
                'menu-pages': [
                    'Menu-Tech-1',
                    'Menu-Tech-2'
                ]
            }
        self._pageIndex = 0
        # utilityFunctions.Log('Length of Menu Button MESet: {}'.format(len(self._menuBtns.Objects)))
        # utilityFunctions.Log('Create Class Events')
        
        @event(self._menuBtns.Objects, 'Pressed')
        def TechMenuBtnHandler(button, action):
            for fn in self._PageUpdates.values():
                fn(show=False)
            
            if button.Page in self._PageUpdates:
                self._PageUpdates[button.Page](show=True)
            
            self._menuBtns.SetCurrent(button)
            self.UIHost.ShowPopup(button.Page)
            
        @event(self._ctlBtns['prev'], ['Pressed', 'Released'])
        def TechMenuPrevHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
                if self._pageIndex > 0:
                    self._pageIndex -= 1
            elif action == 'Released':
                self.UIHost.ShowPopup(self._ctlBtns['menu-pages'][self._pageIndex])
                if self._pageIndex == 0:
                    button.SetState(2)
                    button.SetEnable(False)
                else:
                    button.SetState(0)
                if self._pageIndex < (len(self._ctlBtns['menu-pages'])-1):
                    self._ctlBtns['next'].SetState(0)
                    self._ctlBtns['next'].SetEnable(True)
        
        @event(self._ctlBtns['next'], ['Pressed', 'Released'])
        def TechMenuNextHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
                if self._pageIndex < (len(self._ctlBtns['menu-pages'])-1):
                    self._pageIndex += 1
            elif action == 'Released':
                self.UIHost.ShowPopup(self._ctlBtns['menu-pages'][self._pageIndex])
                if self._pageIndex == (len(self._ctlBtns['menu-pages'])-1):
                    button.SetState(2)
                    button.SetEnable(False)
                else:
                    button.SetState(0)
                if self._pageIndex > 0:
                    self._ctlBtns['prev'].SetState(0)
                    self._ctlBtns['prev'].SetEnable(True)
        
        @event(self._ctlBtns['exit'], ['Pressed', 'Released'])
        def TechMenuExitHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                button.SetState(0)
                self.CloseTechMenu()

        
                    
    # Public Methods
    def OpenTechMenu(self) -> None:
        self.TechMenuOpen = True
        # utilityFunctions.Log('Updating Tech Menu Nav')
        self._pageIndex = 0
        self.UIHost.ShowPopup(self._ctlBtns['menu-pages'][self._pageIndex])
        self._ctlBtns['prev'].SetState(2)
        self._ctlBtns['prev'].SetEnable(False)
        self._ctlBtns['next'].SetState(0)
        self._ctlBtns['next'].SetEnable(True)
        
        # utilityFunctions.Log('Checking for Page Updates')
        if self._defaultPage in self._PageUpdates:
            # utilityFunctions.Log('Starting Updates for Page: {}'.format(self._defaultPage))
            self._PageUpdates[self._defaultPage](show=True)
            
        self._menuBtns.SetCurrent(self._defaultBtn)
        self.UIHost.ShowPopup(self._defaultPage)
    
    def CloseTechMenu(self):
        self.TechMenuOpen = False
        if self.GUIHost.ActCtl.CurrentActivity == 'off':
            self.UIHost.ShowPage('Opening')
        else:
            self.UIHost.ShowPage('Main')
        for fn in self._PageUpdates.values():
            fn(show=False)
    
    # Private Methods
    def _AdvVolPage(self) -> str:
        return 'Tech-AdvancedVolume_{}'.format(len(self.GUIHost.Microphones))
    
    def _CamCtlsPage(self) -> str:
        return 'Tech-CameraControls_{}'.format(len(self.GUIHost.Cameras))
    
    def _DispCtlPage(self):
        confs = 0
        mons = 0
        projs = 0
        for dest in self.GUIHost.Destinations:
            if dest['type'] == 'proj+scn' or dest['type'] == 'proj':
                projs += 1
            elif dest['type'] == 'mon':
                mons += 1
            elif dest['type'] == 'conf' or dest['type'] == 'c-conf':
                confs += 1
        
        return 'Tech-DisplayControls_{c},{p},{m}'.format(c = confs, p = projs, m = mons)
    
    def _ManMtxPage(self):
        return 'Tech-ManualMatrix_{i}x{o}'.format(i = self.GUIHost.TechMatrixSize[0], o = self.GUIHost.TechMatrixSize[1])
    
    def _RmCfgPage(self):
        return 'Tech-RoomConfig_{}'.format(len(self.GUIHost.Lights))
    
    def _StatusPage(self, show: bool=False):
        if show:
            self.UIHost.StatusCtl.resetPages()
            self.UIHost.StatusCtl.UpdateTimer.Restart()
        else:
            self.UIHost.StatusCtl.UpdateTimer.Stop()
    

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
