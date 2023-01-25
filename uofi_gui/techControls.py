## Begin ControlScript Import --------------------------------------------------
from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
    DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
    EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
    RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
    VolumeInterface)
from extronlib.ui import Button, Knob, Label, Level, Slider
from extronlib.system import (Email, Clock, MESet, Timer, Wait, File, RFile,
    ProgramLog, SaveProgramLog, Ping, WakeOnLan, SetAutomaticTime, SetTimeZone)

print(Version()) ## Sanity check ControlScript Import
## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
from datetime import datetime
import json
from typing import Dict, Tuple, List, Union

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
import utilityFunctions
import settings
import vars

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class TechMenuController:
    def __init__(self,
                 UIHost: UIDevice,
                 ControlDict: Dict,
                 BtnList: List) -> None:
        # Public Properties
        utilityFunctions.Log('Set Public Properties')
        self.UIHost = UIHost
        
        # Private Properties
        utilityFunctions.Log('Set Private Properties')
        self._PageSelects = \
            {
                'Tech-AdvancedVolume': self._AdvVolPage,
                'Tech-CameraControls': self._CamCtlsPage,
                'Tech-DisplayControls': self._DispCtlPage,
                'Tech-ManualMatrix': self._ManMtxPage,
                'Tech-RoomConfig': self._RmCfgPage
            }
            
        self._menuBtns = MESet([])
        self._defaultPage = 'Tech-SystemStatus'
        self._defaultBtn = None
        for btn in BtnList:
            if btn.Name in self._PageSelects.keys():
                btn.Page = self._PageSelects[btn.Name]()
            else:
                btn.Page = btn.Name
            self._menuBtns.Append(btn)
            if btn.Name in self._defaultPage:
                self._defaultBtn = btn
        
        self._ctlBtns = ControlDict
        self._pageIndex = 0
        utilityFunctions.Log('Length of Menu Button MESet: {}'.format(len(self._menuBtns.Objects)))
        utilityFunctions.Log('Create Class Events')
        
        @event(self._menuBtns.Objects, 'Pressed')
        def TechMenuBtnHandler(button, action):
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
                if vars.ActCtl.CurrentActivity == 'off':
                    self.UIHost.ShowPage('Opening')
                else:
                    self.UIHost.ShowPage('Main')
    # Public Methods
    def OpenTechMenu(self) -> None:
        self._pageIndex = 0
        self.UIHost.ShowPopup(self._ctlBtns['menu-pages'][self._pageIndex])
        self._ctlBtns['prev'].SetState(2)
        self._ctlBtns['prev'].SetEnable(False)
        
        self._menuBtns.SetCurrent(self._defaultBtn)
        self.UIHost.ShowPopup(self._defaultPage)
        
    # Private Methods
    def _AdvVolPage(self) -> str:
        return 'Tech-AdvancedVolume_{}'.format(settings.micCtl)
    
    def _CamCtlsPage(self) -> str:
        return 'Tech-CameraControls_{}'.format(len(settings.cameras))
    
    def _DispCtlPage(self):
        mons = 0
        projs = 0
        for dest in settings.destinations:
            if dest['type'] == 'proj+scn' or dest['type'] == 'proj':
                projs += 1
            elif dest['type'] == 'mon':
                mons +=1
        
        return 'Tech-DisplayControls_{p},{m}'.format(p = projs, m = mons)
    
    def _ManMtxPage(self):
        return 'Tech-ManualMatrix_{i}x{o}'.format(i = settings.techMatrixSize[0], o = settings.techMatrixSize[1])
    
    def _RmCfgPage(self):
        return 'Tech-RoomConfig_{}'.format(len(settings.lights))
    

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
