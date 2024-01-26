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
from typing import TYPE_CHECKING, List
if TYPE_CHECKING: # pragma: no cover
    pass

#### Python imports

#### Extron Library Imports

#### Project imports
import Constants
import System

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def ShowSourceSelectionFeedback(devices: List[Constants.UI_HOSTS], selection: Constants.UI_BUTTONS) -> None:
    selectionUIDev = selection.UIHost
    
    for uiDev in devices:
        if uiDev is not selectionUIDev:
            uiDev.Interface.Objects.ControlGroups['Source-Select'].SetCurrentRef(selection.Name)

def ShowSourceControlFeedback(devices: List[Constants.UI_HOSTS]) -> None:
    refBtn = devices[0].Interface.Objects.ControlGroups['Source-Select'].GetCurrentRef()
    srcCtl = System.CONTROLLER.Devices.GetSourceByInput(refBtn.input).SourceControlPage
    camCount = len(System.CONTROLLER.Devices.Cameras)
    
    ## get popup page string
    if srcCtl in ['PC']:
        srcCtlPage = 'Source-Control-{}_{}'.format(srcCtl, camCount)
    else:
        srcCtlPage = 'Source-Control-{}'.format(srcCtl)
        
    # TODO: configure initial feedback information for Source Control Pages
    ## All pages - Alert area
    ## WPD - Pod Name, Pod IP, Pod Key
    ## PC with 2+ cameras - Currently selected camera
        
    ## show popup page on all touch panels
    for uiDev in devices:
        uiDev.ShowPopup(srcCtlPage)

## End Function Definitions ----------------------------------------------------



