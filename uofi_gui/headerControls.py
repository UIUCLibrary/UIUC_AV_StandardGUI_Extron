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

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------
class HeaderController: 
    def __init__(self,
                 UIHost: UIDevice,
                 HeaderDict: Dict[str, Union[Button, Dict]]) -> None:
        
        # Public Properties
        utilityFunctions.Log('Set Public Properties')
        self.UIHost = UIHost
        
        # Private Properties
        utilityFunctions.Log('Set Private Properties')
        self._closeBtn = HeaderDict['popover-close']
        HeaderDict.pop('popover-close')
        
        self._hideWhenOff = ['camera']
        self._hideAlways = ['alert']
        
        self._headerBtns = []
        self._allPopovers = []
        for key in HeaderDict:
            HeaderDict[key]['btn'].PopoverName = HeaderDict[key]['popover']
            HeaderDict[key]['btn'].Hide = None
            if key in self._hideWhenOff:
                HeaderDict[key]['btn'].Hide = 'off'
            if key in self._hideAlways:
                HeaderDict[key]['btn'].Hide = 'always'
            self._headerBtns.append(HeaderDict[key]['btn'])
            self._allPopovers.append(HeaderDict[key]['popover'])
            
        utilityFunctions.Log('Create Class Events')
        
        @event(self._headerBtns, ['Pressed', 'Tapped','Released'])
        def HeaderBtnHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif (action == 'Released' and not hasattr(button, 'holdTime')) or action == 'Tapped':
                button.SetState(0)
                self.UIHost.ShowPopup(button.PopoverName)
        
        @event(self._closeBtn, 'Pressed')
        def PopoverCloseHandler(button, action):
            for po in self._allPopovers:
                self.UIHost.HidePopup(po)
        
        for btn in self._headerBtns:
            if btn.Hide is not None:
                btn.SetEnable(False)
                btn.SetVisible(False)
                
            # we don't have anything to do with the room name at this point,
            # so we are going to disable it for now
            # this can be removed if used in the future
            if btn.Name == 'Room-Label':
                btn.SetEnable(False)
                
    # Private Methods
    
    # Public Methods
    def ConfigSystemOn(self) -> None:
        for btn in self._headerBtns:
            if btn.Hide == 'off':
                btn.SetEnable(True)
                btn.SetVisible(True)
    
    def ConfigSystemOff(self) -> None:
        for btn in self._headerBtns:
            if btn.Hide == 'off':
                btn.SetEnable(False)
                btn.SetVisible(False)
        
## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
