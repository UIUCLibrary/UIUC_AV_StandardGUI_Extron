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
from modules.project.extended.System import TimerEx
from modules.helper.CommonUtilities import isinstanceEx
from ui.Feedback.Source import ShowSourceControlFeedback
import Constants
import Variables

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def NewActivityFeedback(devices: List[Constants.UI_HOSTS], activity: Constants.ActivityMode) -> None:
    TipTimer.devices = devices
    TipTimer.activity = activity
    
    OpenTips()
    
    for uiDev in devices:
        uiDev.HidePopup('Power-Transition')

def TipRunnerCallback(timer: 'TimerEx', count: int) -> None:
    closeTipBtns = [uiDev.Interface.Objects.Buttons['Activity-Splash-Close'] for uiDev in timer.devices]
    
    for closeBtn in closeTipBtns:
        closeBtn.SetText('Close Tip ({})'.format(timer.Remaining))

def OpenTips(button: Constants.UI_BUTTONS=None, action: str=None) -> None:
    if button is not None:
        uiDev = button.UIHost
    
    closeTipBtns = [uiDev.Interface.Objects.Buttons['Activity-Splash-Close'] for uiDev in TipTimer.devices]
    for closeBtn in closeTipBtns:
        closeBtn.SetText('Close Tip ({})'.format(TipTimer.Remaining))
    
    if TipTimer.activity in Constants.SHARE or TipTimer.activity in Constants.GROUPWORK:
        TipTimer.Restart()
        for uiDev in TipTimer.devices:
            uiDev.ShowPopup('Source-Control-Splash-{}'.format(TipTimer.activity.name))

def CloseTips(*args) -> None:
    if isinstanceEx(args[0], 'ExTimer'):
        timer = args[0]
    else:
        timer = TipTimer
        
    timer.Stop()
    for uiDev in timer.devices:
        uiDev.HidePopup('Source-Control-Splash-{}'.format(timer.activity.name))
    
    ShowSourceControlFeedback(timer.devices)

## End Function Definitions ----------------------------------------------------

TipTimer = TimerEx(1, TipRunnerCallback, Variables.TIP_TIMER_DUR, CloseTips)
TipTimer.Stop()
TipTimer.devices = []
TipTimer.activity = None