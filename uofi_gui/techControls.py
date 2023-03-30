from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    from extronlib.ui import Button

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
        self.UIHost = UIHost
        self.GUIHost = self.UIHost.GUIHost
        self.TechMenuOpen = False
        
        # Private Properties
        self.__PageSelects = \
            {
                'Tech-AdvancedVolume': self.__AdvVolPage,
                'Tech-CameraControls': self.__CamCtlsPage,
                'Tech-DisplayControls': self.__DispCtlPage,
                'Tech-ManualMatrix': self.__ManMtxPage,
                'Tech-RoomConfig': self.__RmCfgPage
            }
        self.__PageUpdates = \
            {
                'Tech-SystemStatus': self.__StatusPage
            }
            
        self.__MenuBtns = MESet([])
        self.__DefaultPage = 'Tech-SystemStatus'
        self.__DefaultBtn = None
        for btn in DictValueSearchByKey(self.UIHost.Btns, r'Tech-\w+$', regex=True):
            if btn.Name in self.__PageSelects.keys():
                btn.Page = self.__PageSelects[btn.Name]()
            else:
                btn.Page = btn.Name
            self.__MenuBtns.Append(btn)
            if btn.Name in self.__DefaultPage:
                self.__DefaultBtn = btn
        
        self.__CtlBtns = \
            {
                'prev': self.UIHost.Btns['Tech-Menu-Previous'],
                'next': self.UIHost.Btns['Tech-Menu-Next'],
                'exit': self.UIHost.Btns['Tech-Menu-Exit'],
                'menu-pages': [
                    'Menu-Tech-1',
                    'Menu-Tech-2'
                ]
            }
        self.__PageIndex = 0
        
        @event(self.__MenuBtns.Objects, 'Pressed') # pragma: no cover
        def TechMenuBtnHandler(button: 'Button', action: str):
            self.__TechMenuBtnHandler(button, action)
            
        @event(self.__CtlBtns['prev'], ['Pressed', 'Released']) # pragma: no cover
        def TechMenuPrevHandler(button: 'Button', action: str):
            self.__TechMenuPrevHandler(button, action)
        
        @event(self.__CtlBtns['next'], ['Pressed', 'Released']) # pragma: no cover
        def TechMenuNextHandler(button: 'Button', action: str):
            self.__TechMenuNextHandler(button, action)
        
        @event(self.__CtlBtns['exit'], ['Pressed', 'Released']) # pragma: no cover
        def TechMenuExitHandler(button: 'Button', action: str):
            self.__TechMenuExitHandler(button, action)

    # Event Handlers  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __TechMenuBtnHandler(self, button: 'Button', action: str):
        for fn in self.__PageUpdates.values():
            fn(show=False)
        
        if button.Page in self.__PageUpdates:
            self.__PageUpdates[button.Page](show=True)
        
        self.__MenuBtns.SetCurrent(button)
        self.UIHost.ShowPopup(button.Page)
    
    def __TechMenuPrevHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
            if self.__PageIndex > 0:
                self.__PageIndex -= 1
        elif action == 'Released':
            self.UIHost.ShowPopup(self.__CtlBtns['menu-pages'][self.__PageIndex])
            if self.__PageIndex == 0:
                button.SetState(2)
                button.SetEnable(False)
            else:
                button.SetState(0)
            if self.__PageIndex < (len(self.__CtlBtns['menu-pages'])-1):
                self.__CtlBtns['next'].SetState(0)
                self.__CtlBtns['next'].SetEnable(True)
    
    def __TechMenuNextHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
            if self.__PageIndex < (len(self.__CtlBtns['menu-pages'])-1):
                self.__PageIndex += 1
        elif action == 'Released':
            self.UIHost.ShowPopup(self.__CtlBtns['menu-pages'][self.__PageIndex])
            if self.__PageIndex == (len(self.__CtlBtns['menu-pages'])-1):
                button.SetState(2)
                button.SetEnable(False)
            else:
                button.SetState(0)
            if self.__PageIndex > 0:
                self.__CtlBtns['prev'].SetState(0)
                self.__CtlBtns['prev'].SetEnable(True)
    
    def __TechMenuExitHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            button.SetState(0)
            self.CloseTechMenu()
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __AdvVolPage(self) -> str:
        return 'Tech-AdvancedVolume_{}'.format(len(self.GUIHost.Microphones))
    
    def __CamCtlsPage(self) -> str:
        return 'Tech-CameraControls_{}'.format(len(self.GUIHost.Cameras))
    
    def __DispCtlPage(self):
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
    
    def __ManMtxPage(self):
        return 'Tech-ManualMatrix_{i}x{o}'.format(i = self.GUIHost.TechMatrixSize[0], o = self.GUIHost.TechMatrixSize[1])
    
    def __RmCfgPage(self):
        return 'Tech-RoomConfig_{}'.format(len(self.GUIHost.Lights))
    
    def __StatusPage(self, show: bool=False):
        if show:
            self.UIHost.StatusCtl.ResetPages()
            self.UIHost.StatusCtl.UpdateTimer.Restart()
        else:
            self.UIHost.StatusCtl.UpdateTimer.Stop()
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def OpenTechMenu(self) -> None:
        self.TechMenuOpen = True
        # utilityFunctions.Log('Updating Tech Menu Nav')
        self.__PageIndex = 0
        self.UIHost.ShowPopup(self.__CtlBtns['menu-pages'][self.__PageIndex])
        self.__CtlBtns['prev'].SetState(2)
        self.__CtlBtns['prev'].SetEnable(False)
        self.__CtlBtns['next'].SetState(0)
        self.__CtlBtns['next'].SetEnable(True)
        
        # utilityFunctions.Log('Checking for Page Updates')
        if self.__DefaultPage in self.__PageUpdates:
            # utilityFunctions.Log('Starting Updates for Page: {}'.format(self._defaultPage))
            self.__PageUpdates[self.__DefaultPage](show=True)
            
        self.__MenuBtns.SetCurrent(self.__DefaultBtn)
        self.UIHost.ShowPopup(self.__DefaultPage)
    
    def CloseTechMenu(self):
        self.TechMenuOpen = False
        if self.GUIHost.ActCtl.CurrentActivity == 'off':
            self.UIHost.ShowPage('Opening')
        else:
            self.UIHost.ShowPage('Main')
        for fn in self.__PageUpdates.values():
            fn(show=False)

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
