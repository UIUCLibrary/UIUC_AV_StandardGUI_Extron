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
    from modules.project.ExtendedClasses import ExUIDevice
    from extronlib.device import UIDevice

#### Python imports

#### Extron Library Imports

#### Project imports
from modules.helper.CommonUtilities import Logger
from ui.interface.TouchPanel.Objects import TouchPanelObjects

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class TouchPanelInterface():
    def __init__(self, device: Union['ExUIDevice', 'UIDevice'], interface: str) -> None:
        TouchPanelObjects.__init__(self)
        
        self.Device = device
        self.Interface = interface
        
    



## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
