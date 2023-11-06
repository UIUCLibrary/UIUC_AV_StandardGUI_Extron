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
    from extronlib.ui import Button
    from modules.helper.ExtendedUIClasses import ExButton, RefButton

#### Python imports

#### Extron Library Imports

#### Project imports
from modules.helper.CommonUtilities import Logger
import System

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def ActivitySelectPopupCallback(UISet) -> str:
    actMax = max(System.CONTROLLER.ActivityModes)
    
    return "Menu-Activity-{}".format(actMax)

def SourceSelectPopupCallback(UISet) -> str:
    length = len(UISet.RefObjects)
    
    if length < 2:
        raise ValueError("Objects must contain at least two RefButtons")
    elif length >=2 and length <=5:
        return "Menu-Source-{}".format(length)
    elif length > 5:
        return "Menu-Source-5+"
    
def TechMenuPagePopupCallback(UISet) -> str:
    length = len(UISet.RefObjects)
    
    fullpages = length // 5
    remainder = length % 5
    
    if (UISet.Offset + 1) > (fullpages * 5):
        return "Menu-Tech-{}".format(remainder)
    else:
        return "Menu-Tech-5"
    
def TechDisplayControlsCallback() -> str:
    return "1,1,4"

def TechCameraControlsCallback() -> str:
    return str(len(System.CONTROLLER.Devices.Cameras))

def TechRoomConfigurationCallback() -> str:
    return "0"

def TechAdvVolCallback() -> str:
    return str(len(System.CONTROLLER.Devices.Microphones))

## End Function Definitions ----------------------------------------------------



