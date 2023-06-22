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

from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import SystemController
    from uofi_gui.uiObjects import ExUIDevice
    from DevelopmentProject.src.modules.project.systemHardware import SystemHardwareController

from extronlib.system import Timer, Wait
from modules.helper.UtilityFunctions import RunAsync, debug
from modules.helper.UtilityFunctions import Logger

class Source:
    def __init__(self,
                 device: 'SystemHardwareController',
                 icon: int,
                 input: int,
                 id: str=None,
                 name: str=None,
                 alert: str='',
                 srcCtl: str=None,
                 advSrcCtl: str=None) -> None:
        
        if device is not None:
            self.Device = device
            self.Id = device.Id
            self.Name = device.Name
        elif id is not None and name is not None:
            self.Device = None
            self.Id = id
            self.Name = name
        else:
            raise ValueError('Device or id and name must be provided')
        
        if type(icon) is int and icon >= 0:
            self.Icon = icon
        else:
            raise ValueError('Icon must be an integer greater than or equal to 0')
        
        if type(input) is int and input >= 0:
            self.Input = input
        else:
            raise ValueError('Input must be an integer greater than or equal to 0')
        
        self.SourceControlPage = srcCtl
        self.AdvSourceControlPage = advSrcCtl
        
        self.__AlertText = {}
        self.__AlertIndex = 0
        self.__OverrideAlert = None
        self.__OverrideState = False
        self.__DefaultAlert = alert
        
        self.__AlertTimer = Timer(1, self.__AlertTimerHandler)
        self.__AlertTimer.Stop()

    @property
    def AlertText(self):
        if not self.__OverrideState:
            if len(self.__AlertText) > 0:
                txt =  list(self.__AlertText.keys())[self.__AlertIndex]
                self.CycleAlert()
            else:
                txt = ''
        else:
            txt = self.__OverrideAlert
        return txt
    
    @property
    def AlertBlock(self):
        block = '\n'.join(self.__AlertText)
        block = block.strip()
        if self.__OverrideState:
            block = '{}\n{}'.format(self.__OverrideAlert, block)
        return block
    
    @property
    def Alerts(self):
        count = len(self.__AlertText)
        if self.__OverrideState:
            count += 1
        return count
    
    @property
    def AlertFlag(self):
        if len(self.__AlertText) > 0:
            return True
        elif self.__OverrideState:
            return True
        else:
            return False
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __AlertTimerHandler(self, timer: 'Timer', count: int):
        iterList = list(self.__AlertText.keys())
        for msg in iterList:
            if self.__AlertText[msg] > 0:
                self.__AlertText[msg] -= 1
            elif self.__AlertText[msg] == 0:
                self.__AlertText.pop(msg)
        if len(self.__AlertText) == 0:
            timer.Stop()
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def CycleAlert(self):
        self.__AlertIndex += 1
        if self.__AlertIndex >= len(self.__AlertText):
            self.__AlertIndex = 0
    
    def AppendAlert(self, msg: str=None, timeout: int=0) -> None:
        if msg is None:
            msg = self.__DefaultAlert
            
        if timeout > 0:
            self.__AlertText[msg] = timeout
        else: 
            self.__AlertText[msg] = -1
        
        if self.__AlertTimer.State in ['Paused', 'Stopped']:
            self.__AlertTimer.Restart()
        
    def OverrideAlert(self, msg: str, timeout: int=60) -> None:
        self.__OverrideAlert = msg
        self.__OverrideState = True
        if timeout > 0:
            @Wait(timeout) # pragma: no cover
            def OverrideTimeoutHandler():
                self.__OverrideState = False
    
    def ClearOverride(self):
        self.__OverrideAlert = None
        self.__OverrideState = False
    
    def ClearAlert(self, msg: str=None):
        if msg is None:
            msg = self.__DefaultAlert
            
        self.__AlertText.pop(msg)
        
        if len(self.__AlertText) == 0:
            self.__AlertTimer.Stop()
    
    def ResetAlert(self) -> None:
        self.__AlertText = {}
        self.__AlertTimer.Stop()
        