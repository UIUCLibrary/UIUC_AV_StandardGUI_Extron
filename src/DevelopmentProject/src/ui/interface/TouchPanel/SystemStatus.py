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
    from modules.helper.Collections import DeviceCollection
    from uofi_gui.uiObjects import ExUIDevice
    from extronlib.ui import Button, Knob, Label, Level, Slider

#### Python Imports
from datetime import datetime
import importlib
import math
import re
import functools

#### Exron Library Imports
from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
    DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
    EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
    RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
    VolumeInterface)
from extronlib.system import (Email, Clock, MESet, Timer, Wait, File, RFile,
    ProgramLog, SaveProgramLog, Ping, WakeOnLan, SetAutomaticTime, SetTimeZone)

#### Project Imports
from modules.helper.ConnectionHandler import GetConnectionHandler
from modules.helper.CommonUtilities import Logger, RunAsync, debug, DictValueSearchByKey, SortKeys

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class SystemStatusController:
    def __init__(self, UIHost: 'ExUIDevice') -> None:

        self.UIHost = UIHost
        self.GUIHost = self.UIHost.GUIHost
        self.Hardware = list(self.GUIHost.Hardware.values())
        self.Hardware.sort(key=SortKeys.HardwareSort)
        
        self.__StatusIcons = DictValueSearchByKey(self.UIHost.Btns, r'DeviceStatusIcon-\d+', regex=True)
        self.__StatusIcons.sort(key=SortKeys.StatusSort)
        self.__StatusLabels = DictValueSearchByKey(self.UIHost.Lbls, r'DeviceStatusLabel-\d+', regex=True)
        self.__StatusLabels.sort(key=SortKeys.StatusSort)
        self.__Arrows = \
            {
                'prev': self.UIHost.Btns['DeviceStatus-PageDown'],
                'next': self.UIHost.Btns['DeviceStatus-PageUp']
            }
        self.__PageLabels = \
            {
                'current': self.UIHost.Lbls['DeviceStatusPage-Current'],
                'total': self.UIHost.Lbls['DeviceStatusPage-Total'],
                'div': self.UIHost.Lbls['PaginationSlash']
            }
        
        self.__CurrentPageIndex = 0
        
        self.UpdateTimer = Timer(15, self.__UpdateHandler)
        self.UpdateTimer.Stop()
        
        self.__ClearStatusIcons()
            
        self.__UpdatePagination()
        
        @event(list(self.__Arrows.values()), ['Pressed','Released']) # pragma: no cover
        def paginationHandler(button: 'Button', action: str):
            self.__PaginationHandler(button, action)
    
    @property
    def __HardwareCount(self) -> int:
        return len(self.Hardware)
    
    @property
    def __DisplayPages(self) -> int:
        return math.ceil(self.__HardwareCount / 15)
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __PaginationHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            button.SetState(0)
            if button.Name.endswith('Up'):
                # do page up
                self.__CurrentPageIndex += 1
                if self.__CurrentPageIndex >= self.__DisplayPages:
                    self.__CurrentPageIndex = self.__DisplayPages
            elif button.Name.endswith('Down'):
                # do page down
                self.__CurrentPageIndex -= 1
                if self.__CurrentPageIndex < 0:
                    self.__CurrentPageIndex = 0
                
            self.__UpdatePagination()
            self.__ShowStatusIcons()
            
    def __UpdateHandler(self, timer: 'Timer', count: int):
        self.UpdateStatusIcons()

    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __ClearStatusIcons(self):
        for ico in self.__StatusIcons:
            ico.SetEnable(False)
            ico.SetVisible(False)
            ico.HW = None
            
        for lbl in self.__StatusLabels:
            lbl.SetText('')
    
    def __ShowStatusIcons(self):
        self.__ClearStatusIcons()
        
        indexStart = self.__CurrentPageIndex * 15
        indexEnd = ((self.__CurrentPageIndex + 1) * 15)

        displayList = []
        for i in range(indexStart, indexEnd):
            if i >= len(self.Hardware):
                break
            displayList.append(self.Hardware[i])
        
        if len(displayList) < len(self.__StatusIcons):
            loadRange = len(displayList)
        else:
            loadRange = 15
        
        for j in range(loadRange):
            ico = self.__StatusIcons[j]
            lbl = self.__StatusLabels[j]
            hw = displayList[j]
            
            ico.SetState(self.__GetStatusState(hw))
            ico.SetVisible(True)
            ico.HW = hw
            lbl.SetText(hw.Name)
    
    def __GetStatusState(self, hw) -> int: # pragma: no cover
        if hw.ConnectionStatus == 'Connected':
            return 2
        else:
            if type(hw.LastStatusChange) != datetime:
                return 3
            else:
                delta = datetime.now() - hw.LastStatusChange
                secs = delta.total_seconds()
                if secs < 180:
                    return 2
                elif secs >= 180 and secs < 300:
                    return 1
                elif secs >= 300:
                    return 0
                    
    def __UpdatePagination(self):
        if self.__DisplayPages == 1:
            # No page flips. Show no pagination
            self.__Arrows['prev'].SetEnable(False)
            self.__Arrows['prev'].SetVisible(False)
            self.__Arrows['next'].SetEnable(False)
            self.__Arrows['next'].SetVisible(False)
            
            self.__PageLabels['current'].SetVisible(False)
            self.__PageLabels['total'].SetVisible(False)
            self.__PageLabels['div'].SetVisible(False)
            
        elif self.__DisplayPages > 1 and self.__CurrentPageIndex == 0:
            # Show page flips, disable prev button
            self.__Arrows['prev'].SetEnable(False)
            self.__Arrows['prev'].SetVisible(True)
            self.__Arrows['next'].SetEnable(True)
            self.__Arrows['next'].SetVisible(True)
            
            self.__Arrows['prev'].SetState(2)
            self.__Arrows['next'].SetState(0)

            self.__PageLabels['current'].SetVisible(True)
            self.__PageLabels['current'].SetText(str(self.__CurrentPageIndex + 1))
            self.__PageLabels['total'].SetVisible(True)
            self.__PageLabels['total'].SetText(str(self.__DisplayPages))
            self.__PageLabels['div'].SetVisible(True)
            
        elif self.__DisplayPages > 1 and (self.__CurrentPageIndex + 1) == self.__DisplayPages:
            # Show page flips, disable next button
            self.__Arrows['prev'].SetEnable(True)
            self.__Arrows['prev'].SetVisible(True)
            self.__Arrows['next'].SetEnable(False)
            self.__Arrows['next'].SetVisible(True)
            
            self.__Arrows['prev'].SetState(0)
            self.__Arrows['next'].SetState(2)
        
            self.__PageLabels['current'].SetVisible(True)
            self.__PageLabels['current'].SetText(str(self.__CurrentPageIndex + 1))
            self.__PageLabels['total'].SetVisible(True)
            self.__PageLabels['total'].SetText(str(self.__DisplayPages))
            self.__PageLabels['div'].SetVisible(True)
        
        elif self.__DisplayPages > 1:
            # Show page flips, both arrows enabled
            self.__Arrows['prev'].SetEnable(True)
            self.__Arrows['prev'].SetVisible(True)
            self.__Arrows['next'].SetEnable(True)
            self.__Arrows['next'].SetVisible(True)
            
            self.__Arrows['prev'].SetState(0)
            self.__Arrows['next'].SetState(0)
            
            self.__PageLabels['current'].SetVisible(True)
            self.__PageLabels['current'].SetText(str(self.__CurrentPageIndex + 1))
            self.__PageLabels['total'].SetVisible(True)
            self.__PageLabels['total'].SetText(str(self.__DisplayPages))
            self.__PageLabels['div'].SetVisible(True)
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def ResetPages(self):
        self.__CurrentPageIndex = 0
        self.__UpdatePagination()
        self.__ShowStatusIcons()
        
    def UpdateStatusIcons(self):
        for ico in self.__StatusIcons:
            if ico.HW is not None:
                ico.SetState(self.__GetStatusState(ico.HW))

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



