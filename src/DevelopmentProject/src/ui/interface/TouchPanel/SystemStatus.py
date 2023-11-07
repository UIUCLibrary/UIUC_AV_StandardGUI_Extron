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
from typing import TYPE_CHECKING

if TYPE_CHECKING: # pragma: no cover
    from modules.helper.ExtendedUIClasses import ExButton
    from modules.helper.ExtendedDeviceClasses import ExUIDevice
    from modules.helper.ExtendedUIClasses.UISets import SystemStatusControlGroup
    from modules.project.SystemHardware import SystemHardwareController

#### Python Imports
import math
from datetime import datetime

#### Extron Library Imports
from extronlib.system import Timer

#### Project Imports
import System

from modules.helper.CommonUtilities import Logger, SortKeys
from modules.helper.ModuleSupport import eventEx

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class SystemStatusController:
    def __init__(self, UIHost: 'ExUIDevice', ControlGroup: 'SystemStatusControlGroup') -> None:

        self.UIHost = UIHost
        
        self.Devices = list(System.CONTROLLER.Devices.values())
        self.Devices.sort(key=SortKeys.HardwareSort)
        
        self.__ControlGroup = ControlGroup
        
        self.__CurrentPageIndex = 0
        
        self.UpdateTimer = Timer(15, self.UpdateStatusIcons)
        self.UpdateTimer.Stop()
        
        self.__ClearStatusIcons()
            
        self.__UpdatePagination()
        
        @eventEx(self.UIHost.PopupShown, 'Changed')
        def PageShownHandler(src, value) -> None:
            Logger.Log("Popup Shown Handler (System Status)", src, value, separator=' | ')
            if value == 'Tech-SystemStatus':
                Logger.Log('Status Page Shown')
                self.UpdateStatusIcons()
                self.UpdateTimer.Restart()
                self.ResetPages()
                
        @eventEx(self.UIHost.PopupHidden, 'Changed')
        def PageHiddenHandler(src, value) -> None:
            if value == 'Tech-SystemStatus':
                Logger.Log('Status Page Hidden')
                self.UpdateTimer.Stop()
    
    @property
    def __DeviceCount(self) -> int:
        return len(self.Devices)
    
    @property
    def __DisplayPages(self) -> int:
        return math.ceil(self.__DeviceCount / 15)
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def PaginationHandler(self, Offset: int):
        # do page index change
        self.__CurrentPageIndex += Offset
        
        # prevent overruns
        if self.__CurrentPageIndex >= self.__DisplayPages:
            self.__CurrentPageIndex = self.__DisplayPages
        elif self.__CurrentPageIndex < 0:
            self.__CurrentPageIndex = 0
                
        self.__UpdatePagination()
        self.__ShowStatusIcons()

    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __ClearStatusIcons(self):
        for ico in self.__ControlGroup.Objects:
            ico.SetEnable(False)
            ico.SetVisible(False)
            ico.Device = None
            ico.Label.SetText('')
    
    def __ShowStatusIcons(self):
        self.__ClearStatusIcons()
        
        indexStart = self.__CurrentPageIndex * 15
        indexEnd = ((self.__CurrentPageIndex + 1) * 15)

        displayList = []
        for i in range(indexStart, indexEnd):
            if i >= len(self.Devices):
                break
            displayList.append(self.Devices[i])
        
        if len(displayList) < len(self.__ControlGroup.Objects):
            loadRange = len(displayList)
        else:
            loadRange = 15
        
        for j in range(loadRange):
            ico = self.__ControlGroup.Objects[j]
            lbl = ico.Label
            dev = displayList[j]
            
            ico.SetState(self.__GetStatusState(dev))
            ico.SetVisible(True)
            ico.Device = dev
            lbl.SetText(dev.Name)
    
    def __GetStatusState(self, device: 'SystemHardwareController') -> int: # pragma: no cover
        if device.ConnectionStatus == 'Connected':
            return 2
        else:
            if not isinstance(device.LastStatusChange, datetime):
                return 3
            else:
                delta = datetime.now() - device.LastStatusChange
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
            self.__ControlGroup.UIControls['Previous'].SetEnable(False)
            self.__ControlGroup.UIControls['Previous'].SetVisible(False)
            self.__ControlGroup.UIControls['Next'].SetEnable(False)
            self.__ControlGroup.UIControls['Next'].SetVisible(False)
            
            self.__ControlGroup.HidePagination()
            
        elif self.__DisplayPages > 1 and self.__CurrentPageIndex == 0:
            # Show page flips, disable prev button
            self.__ControlGroup.UIControls['Previous'].SetEnable(False)
            self.__ControlGroup.UIControls['Previous'].SetVisible(True)
            self.__ControlGroup.UIControls['Next'].SetEnable(True)
            self.__ControlGroup.UIControls['Next'].SetVisible(True)
            
            self.__ControlGroup.UIControls['Previous'].SetState(2)
            self.__ControlGroup.UIControls['Next'].SetState(0)

            self.__ControlGroup.ShowPagination()
            self.__ControlGroup.SetCurrentPage(self.__CurrentPageIndex + 1)
            self.__ControlGroup.SetTotalPages(self.__DisplayPages)            
            
        elif self.__DisplayPages > 1 and (self.__CurrentPageIndex + 1) == self.__DisplayPages:
            # Show page flips, disable next button
            self.__ControlGroup.UIControls['Previous'].SetEnable(True)
            self.__ControlGroup.UIControls['Previous'].SetVisible(True)
            self.__ControlGroup.UIControls['Next'].SetEnable(False)
            self.__ControlGroup.UIControls['Next'].SetVisible(True)
            
            self.__ControlGroup.UIControls['Previous'].SetState(0)
            self.__ControlGroup.UIControls['Next'].SetState(2)
        
            self.__ControlGroup.ShowPagination()
            self.__ControlGroup.SetCurrentPage(self.__CurrentPageIndex + 1)
            self.__ControlGroup.SetTotalPages(self.__DisplayPages)

        
        elif self.__DisplayPages > 1:
            # Show page flips, both arrows enabled
            self.__ControlGroup.UIControls['Previous'].SetEnable(True)
            self.__ControlGroup.UIControls['Previous'].SetVisible(True)
            self.__ControlGroup.UIControls['Next'].SetEnable(True)
            self.__ControlGroup.UIControls['Next'].SetVisible(True)
            
            self.__ControlGroup.UIControls['Previous'].SetState(0)
            self.__ControlGroup.UIControls['Next'].SetState(0)
            
            self.__ControlGroup.ShowPagination()
            self.__ControlGroup.SetCurrentPage(self.__CurrentPageIndex + 1)
            self.__ControlGroup.SetTotalPages(self.__DisplayPages)

    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def ResetPages(self):
        self.__CurrentPageIndex = 0
        self.__UpdatePagination()
        self.__ShowStatusIcons()
        
    def UpdateStatusIcons(self):
        for ico in self.__ControlGroup.Objects:
            if ico.Device is not None:
                ico.SetState(self.__GetStatusState(ico.Device))

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def SystemStatusPagination(source: 'ExButton', value: str) -> None:
    uiDev = source.UIHost
    uiDev.SystemStatusCtl.PaginationHandler(source.Offset)

## End Function Definitions ----------------------------------------------------



