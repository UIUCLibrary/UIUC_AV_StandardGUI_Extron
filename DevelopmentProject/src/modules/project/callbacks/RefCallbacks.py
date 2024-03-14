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

#### Python imports

#### Extron Library Imports

#### Project imports
import System
import Constants
import modules.project.callbacks.PopupCallbacks
from modules.helper.CommonUtilities import Logger, SortKeys

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def SourceSelectRefCallback(UIHost: 'ExUIDevice') -> None:
    RefBtnList = []
    for src in System.CONTROLLER.Devices.Sources:
        srcDict = {
            "Name": "Source-Select-Ref-{}".format(src.Id),
            "Text": src.Name,
            "icon": src.Source['icon'],
            "input": src.Source['input'],
            "srcId": src.Id
        }
        RefBtnList.append(srcDict)
        
    RefBtnList.append({
        "Name": "Source-Select-Ref-{}".format(Constants.BLANK_SOURCE.Id),
        "Text": Constants.BLANK_SOURCE.Name,
        "icon": Constants.BLANK_SOURCE.Icon,
        "input": Constants.BLANK_SOURCE.Input,
        "srcId": Constants.BLANK_SOURCE.Id
    })
    
    RefBtnList.sort(key = SortKeys.SourceSort)
    Logger.Log(RefBtnList)
    return RefBtnList

def TechMenuRefCallback(UIHost: 'ExUIDevice') -> None:
    RefBtnList = []
    
    for item in UIHost.Interface.TechPgDict:
        menuItemDict = {
            'Name': "Tech-Menu-Select-{}".format(item['Name']),
            'Text': item['DisplayName'],
        }
        if item['Suffix'] is not None:
            mod = modules.project.callbacks.PopupCallbacks
            suffixCB = getattr(mod, item['Suffix'])
            menuItemDict['page'] = "{}_{}".format(item['Page'], suffixCB())
        else:
            menuItemDict['page'] = item['Page']
        RefBtnList.append(menuItemDict)
    return RefBtnList



## End Function Definitions ----------------------------------------------------



