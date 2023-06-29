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
    from modules.project.ExtendedClasses import ExUIDevice, ExEBUSDevice
    from extronlib.device import UIDevice, eBUSDevice

#### Python imports

#### Extron Library Imports

#### Project imports
from modules.helper.CommonUtilities import Logger
from ui.interface.ButtonPanel.Objects import ButtonPanelObjects

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class ButtonPanelInterface():
    def __init__(self, device: Union['ExUIDevice', 'UIDevice', 'ExEBUSDevice', 'eBUSDevice'], interface: str, panelType: str='NBP') -> None:
        ButtonPanelObjects.__init__(self)
        
        self.Device = device
        self.Interface = interface
        
        if panelType is not None and panelType in ['NBP', 'EBP']:
            self.Type = panelType
        else:
            raise ValueError("PanelTpye must be either NBP or EBP")
    



## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
