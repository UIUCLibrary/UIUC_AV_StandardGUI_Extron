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
    from modules.helper.ExtendedDeviceClasses import ExUIDevice
    from modules.helper.ExtendedUIClasses.UISets import AboutPageGroup

#### Python imports

#### Extron Library Imports
from extronlib.system import Timer

#### Project imports
from modules.helper.CommonUtilities import Logger
from modules.helper.ModuleSupport import eventEx

import System

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class PanelAboutController:
    def __init__(self, UIHost: 'ExUIDevice', ControlGroup: 'AboutPageGroup') -> None:
        self.UIHost = UIHost
        self.__ControlGroup = ControlGroup
        self.__PrimaryProc = System.CONTROLLER.Processors[0]
        
        self.UpdateTimer = Timer(5, self.__PanelInfoUpdate)
        self.UpdateTimer.Stop()
        
        self.__ControlGroup.SetModel(self.__PrimaryProc.ModelName, 
                                     self.__PrimaryProc.PartNumber)
        self.__ControlGroup.SetDeviceInfo(self.__PrimaryProc.SerialNumber, 
                                          self.__PrimaryProc.MACAddress, 
                                          self.__PrimaryProc.Hostname, 
                                          self.__PrimaryProc.IPAddress, 
                                          self.__PrimaryProc.FirmwareVersion)
        self.__ControlGroup.SetProgramInfo(**self.__PrimaryProc.SystemSettings['ProgramInformation'])
        
        @eventEx(self.UIHost.PopupShown, 'Changed')
        def PageShownHandler(src, value) -> None:
            if value == 'Tech-About':
                Logger.Debug('About Page Shown')
                self.__ControlGroup.RefreshStatusInfo()
                self.UpdateTimer.Restart()
                
        @eventEx(self.UIHost.PopupHidden, 'Changed')
        def PageHiddenHandler(src, value) -> None:
            if value == 'Tech-About':
                Logger.Debug('About Page Hidden')
                self.UpdateTimer.Stop()
        
    def __PanelInfoUpdate(self, timer: 'Timer', count: int) -> None:
        self.__ControlGroup.RefreshStatusInfo()

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



