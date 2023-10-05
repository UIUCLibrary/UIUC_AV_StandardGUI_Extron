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
    from extronlib.device import UIDevice

#### Python imports
import json

#### Extron Library Imports
from extronlib.system import File

#### Project imports
import Variables
from modules.helper.CommonUtilities import Logger
from ui.interface.TouchPanel.Objects import TouchPanelObjects

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class TouchPanelInterface():
    def __init__(self, device: Union['ExUIDevice', 'UIDevice'], interfaceType: str) -> None:
        self.__LayoutPath = '/var/nortxe/gcp/layout'
        self.__LayoutGLD = '{}.gdl'.format(Variables.UI_LAYOUT)
        self.__LayoutJSON = '{}.json'.format(Variables.UI_LAYOUT)

        self.__LayoutDict = json.load(open('{}/{}'.format(self.__LayoutPath, self.__LayoutJSON)))
        
        self.Device = device
        self.InterfaceType = interfaceType
        
        self.Objects = TouchPanelObjects()
        self.Initialized = False
        
        self.Device.HideAllPopups()
    
    def InitializeControlObjects(self) -> None:
        self.Objects.LoadButtons(UIHost=self.Device, jsonObj=self.__LayoutDict)
        self.Objects.LoadKnobs(UIHost=self.Device, jsonObj=self.__LayoutDict)
        self.Objects.LoadLabels(UIHost=self.Device, jsonObj=self.__LayoutDict)
        self.Objects.LoadLevels(UIHost=self.Device, jsonObj=self.__LayoutDict)
        self.Objects.LoadSliders(UIHost=self.Device, jsonObj=self.__LayoutDict)
        
        self.Objects.LoadModalPages(jsonObj=self.__LayoutDict)
        self.Objects.LoadPopoverPages(jsonObj=self.__LayoutDict)
        self.Objects.LoadPopupGroups(jsonObj=self.__LayoutDict)
        
        self.Objects.LoadButtonGroups(UIHost=self.Device, jsonObj=self.__LayoutDict)

        self.Initialized = True

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
