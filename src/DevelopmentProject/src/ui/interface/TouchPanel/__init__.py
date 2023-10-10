################################################################################
# Copyright © 2023 The Board of Trustees of the University of Illinois
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

## Begin Imports ---------------------------------------------------------------

#### Type Checking
from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from modules.helper.ExtendedDeviceClasses import ExUIDevice
    from modules.helper.ExtendedUIClasses import ExButton
    from extronlib.device import UIDevice
    from extronlib.ui import Button
    

#### Python imports
import json

#### Extron Library Imports
from extronlib.system import File

#### Project imports
from modules.helper.CommonUtilities import Logger, TimeIntToStr
from modules.helper.ExtendedSystemClasses import ExTimer
from ui.interface.TouchPanel.Objects import TouchPanelObjects
from Constants import ActivityMode
import System
import Variables

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class TouchPanelInterface():
    def __init__(self, device: Union['ExUIDevice', 'UIDevice'], interfaceType: str) -> None:
        self.__LayoutPath = '/var/nortxe/gcp/layout'
        self.__LayoutGLD = '{}.gdl'.format(Variables.UI_LAYOUT)
        self.__LayoutJSON = '{}_objects.json'.format(Variables.UI_LAYOUT)
        self.__ControlJSON = '{}_controls.json'.format(Variables.UI_LAYOUT)

        self.__LayoutDict = json.load(open('{}/{}'.format(self.__LayoutPath, self.__LayoutJSON)))
        self.__ControlDict = json.load(open('{}/{}'.format(self.__LayoutPath, self.__ControlJSON)))

        self.Device = device
        self.InterfaceType = interfaceType
        
        self.Objects = TouchPanelObjects()
        self.Initialized = False
    
    def Initialize(self) -> None:
        ## Load UI Objects
        self.Objects.LoadButtons(UIHost=self.Device, jsonObj=self.__LayoutDict)
        self.Objects.LoadKnobs(UIHost=self.Device, jsonObj=self.__LayoutDict)
        self.Objects.LoadLabels(UIHost=self.Device, jsonObj=self.__LayoutDict)
        self.Objects.LoadLevels(UIHost=self.Device, jsonObj=self.__LayoutDict)
        self.Objects.LoadSliders(UIHost=self.Device, jsonObj=self.__LayoutDict)
        
        ## Load Page Lists
        self.Objects.LoadModalPages(jsonObj=self.__LayoutDict)
        self.Objects.LoadPopoverPages(jsonObj=self.__LayoutDict)
        self.Objects.LoadPopupGroups(jsonObj=self.__LayoutDict)
        
        ## Load Controls
        self.Objects.LoadControlGroups(UIHost=self.Device, jsonObj=self.__LayoutDict)
        self.Objects.LoadControls(jsonObj=self.__ControlDict)

        self.Initialized = True

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def SplashStartHandler(button: Union['Button', 'ExButton'], action: str) -> None:
    tp = button.UIHost
    if System.CONTROLLER.SystemPIN is not None:
        tp.SecureAccess.System.Open(PIN=System.CONTROLLER.SystemPIN, Callback=SplashPinSuccess)
    else:
        System.CONTROLLER.ShowStart()
        
def SplashPinSuccess() -> None:
    System.CONTROLLER.ShowStart()
        
def StartShutdownConfirmation(click: bool=False) -> None:
    def CountdownHandler(timer: 'ExTimer', count: int):
        timeTillShutdown = int(System.CONTROLLER.Timers.shutdownConf - (count * timer.Interval))
        
        for UI in System.CONTROLLER.UIDevices:
            Label = UI.Interface.Objects.Labels['ShutdownConf-Count']
            Level = UI.Interface.Objects.Levels['ShutdownConfIndicator']
            
            Label.SetText(TimeIntToStr(timeTillShutdown))
            Level.SetLevel(int(count * timer.Interval))
            
    def ShutdownHandler(timer: 'ExTimer', count: int):
        System.CONTROLLER.SystemActivity = ActivityMode.Standby
    
    for UI in System.CONTROLLER.UIDevices:
        Level = UI.Interface.Objects.Levels['ShutdownConfIndicator']
        Level.SetRange(0, System.CONTROLLER.Timers.shutdownConf, 1)
        Level.SetLevel(0)
        
    ShutdownTimer = ExTimer(1, CountdownHandler, System.CONTROLLER.Timers.shutdownConf, ShutdownHandler)

## End Function Definitions ----------------------------------------------------
