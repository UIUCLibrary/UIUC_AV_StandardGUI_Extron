from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING:
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    from extronlib.ui import Button, Knob, Label, Level, Slider

## Begin ControlScript Import --------------------------------------------------
from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
    DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
    EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
    RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
    VolumeInterface)
from extronlib.system import (Email, Clock, MESet, Timer, Wait, File, RFile,
    ProgramLog, SaveProgramLog, Ping, WakeOnLan, SetAutomaticTime, SetTimeZone)

print(Version()) ## Sanity check ControlScript Import
## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
from datetime import datetime
import json
import re
from typing import Dict, Tuple, List, Union

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from utilityFunctions import DictValueSearchByKey, Log, RunAsync, debug


#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------
class HeaderController: 
    def __init__(self,
                 UIHost: 'ExUIDevice') -> None:
        
        # Public Properties
        # utilityFunctions.Log('Set Public Properties')
        self.UIHost = UIHost
        self.GUIHost = self.UIHost.GUIHost

        # Private Properties
        # utilityFunctions.Log('Set Private Properties')
        self._closeBtn = self.UIHost.Btns['Popover-Close']
        
        self._hideWhenOff = ['Camera']
        self._hideAlways = ['Alert']
        
        self.UIHost.Btns['Header-Alert'].PopoverName = 'Popover-Ctl-Alert'
        self.UIHost.Btns['Header-Camera'].PopoverName = 'Popover-Ctl-Camera_{}'.format(len(self.GUIHost.Cameras))
        self.UIHost.Btns['Header-Lights'].PopoverName = 'Popover-Ctl-Lights_{}'.format(len(self.GUIHost.Lights))
        self.UIHost.Btns['Header-Settings'].PopoverName = 'Popover-Ctl-Audio_{}'.format(len(self.GUIHost.Microphones))
        self.UIHost.Btns['Header-Help'].PopoverName = 'Popover-Ctl-Help'
        self.UIHost.Btns['Room-Label'].PopoverName = 'Popover-Room'
        
        self._headerBtns = [
            self.UIHost.Btns['Header-Alert'],
            self.UIHost.Btns['Header-Camera'],
            self.UIHost.Btns['Header-Lights'],
            self.UIHost.Btns['Header-Settings'],
            self.UIHost.Btns['Header-Help'],
            self.UIHost.Btns['Room-Label'],
        ]
        
        self._allPopovers = []
        for btn in self._headerBtns:
            btn.Hide = None
            re_match = re.match(r'Popover-Ctl-([A-Za-z]*)(?:_\d+)?', btn.PopoverName)
            if re_match is not None and re_match.group(1) is not None:
                if re_match.group(1) in self._hideWhenOff:
                    btn.Hide = 'off'
                if re_match.group(1) in self._hideAlways:
                    btn.Hide = 'always'
            self._allPopovers.append(btn.PopoverName)
            
        # utilityFunctions.Log('Create Class Events')
        
        @event(self._headerBtns, ['Pressed', 'Tapped','Released'])
        def HeaderBtnHandler(button: 'Button', action: str):
            if action == 'Pressed':
                button.SetState(1)
            elif (action == 'Released' and not hasattr(button, 'holdTime')) or action == 'Tapped':
                button.SetState(0)
                self.UIHost.ShowPopup(button.PopoverName)
        
        @event(self._closeBtn, 'Pressed')
        def PopoverCloseHandler(button: 'Button', action: str):
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
