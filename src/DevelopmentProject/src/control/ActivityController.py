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
from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable, cast
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import SystemController
    from uofi_gui.uiObjects import ExUIDevice
    from extronlib.ui import Button
    from modules.helper.ExtendedUIClasses import ExButton

#### Python imports

#### Extron Library Imports
from extronlib import event
from extronlib.system import Timer

#### Project imports
from modules.helper.CommonUtilities import Logger, TimeIntToStr
from modules.helper.ModuleSupport import eventEx
from Constants import STANDBY, SHARE, ADVSHARE, GROUPWORK, ActivityMode
import System
from ui.interface.TouchPanel import StartShutdownConfirmation


## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class ActivityController:
    def __init__(self, SystemHost: SystemController) -> None:
        self.SystemHost = SystemHost
        
        
        @eventEx(SystemHost.SystemActivityWatch, 'Changed')
        def SystemModeChangeHandler(src, val: ActivityMode) -> None:
            Logger.Log('New System Mode:', val.name)
            if val is ActivityMode.Share:
                pass
            elif val is ActivityMode.AdvShare:
                pass
            elif val is ActivityMode.GroupWork:
                pass
            elif val is ActivityMode.Standby:
                pass
            
    @property
    def CurrentActivity(self) -> ActivityMode:
        return self.SystemHost.SystemActivity
    
    @CurrentActivity.setter
    def CurrentActivity(self, val) -> None:
        raise AttributeError('Setting CurrentActivity is disallowed. Use System.CONTROLLER.SystemActivity instead.')

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def ActivitySelect(button: Union['Button', 'ExButton'], action: str) -> None:
    if button.activity not in STANDBY:
        System.CONTROLLER.SystemActivity = ActivityMode[button.activity]
    else:
        StartShutdownConfirmation(click=True)

## End Function Definitions ----------------------------------------------------



