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
from typing import TYPE_CHECKING, Dict, Tuple, Union
if TYPE_CHECKING: # pragma: no cover
    pass

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

def __LogFeedback (Name: str, Command: str, Value: Union[int, str], Qualifier: Dict = None, Tag: Tuple[str, Union[str, int]] = None):
    logList =   [
                    '{} {} Callback'.format(Name, Command),
                    'Value: {}'.format(Value)
                ]
    if Qualifier is not None:
        logList.append('Qualifier: {}'.format(Qualifier))
    if Tag is not None:
        logList.append('Tag: {}'.format(Tag))
    
    Logger.Log(logList, separator="; ", logSeverity='info')

def DSP_MuteHandler(command, value, qualifier, hardware=None, tag=None):
    __LogFeedback(hardware.Name, command, value, Qualifier=qualifier, Tag=tag)
    for UIDev in System.CONTROLLER.UIDevices:
        # TP.AudioCtl.AudioMuteFeedback(tag, value)
        pass
    
def DSP_LevelHandler(command, value, qualifier, hardware=None, tag=None):
    __LogFeedback(hardware.Name, command, value, Qualifier=qualifier, Tag=tag)
    for UIDev in System.CONTROLLER.UIDevices:
        # TP.AudioCtl.AudioLevelFeedback(tag, value)
        pass

def DSP_GainHandler(command, value, qualifier, hardware=None, tag=None):
    __LogFeedback(hardware.Name, command, value, Qualifier=qualifier, Tag=tag)
    for UIDev in System.CONTROLLER.UIDevices:
        # TP.AudioCtl.AudioGainFeedback(qualifier, value)
        pass
        
def DSP_PhantomHandler(command, value, qualifier, hardware=None, tag=None):
    __LogFeedback(hardware.Name, command, value, Qualifier=qualifier, Tag=tag)
    for UIDev in System.CONTROLLER.UIDevices:
        # TP.AudioCtl.AudioPhantomFeedback(qualifier, value)
        pass
    
def Display_AudioMuteStatusHandler(command, value, qualifier, hardware=None):
    __LogFeedback(hardware.Name, command, value, Qualifier=qualifier)
    for UIDev in System.CONTROLLER.UIDevices:
        # TP.DispCtl.DisplayMuteFeedback(hardware.Id, value)
        pass
    
def Display_PowerStatusHandler(command, value, qualifier, hardware=None):
    __LogFeedback(hardware.Name, command, value, Qualifier=qualifier)
    for UIDev in System.CONTROLLER.UIDevices:
        # TP.DispCtl.DisplayPowerFeedback(hardware.Id, value)
        pass
    
def Display_VolumeStatusHandler(command, value, qualifier, hardware=None):
    __LogFeedback(hardware.Name, command, value, Qualifier=qualifier)
    for UIDev in System.CONTROLLER.UIDevices:
        # TP.DispCtl.DisplayVolumeFeedback(hardware.Id, value)
        pass
    
def Mic_MuteHandler(command, value, qualifier, hardware=None, tag=None):
    __LogFeedback(hardware.Name, command, value, Qualifier=qualifier, Tag=tag)
    for UIDev in System.CONTROLLER.UIDevices:
        # TP.AudioCtl.AudioMuteFeedback(tag, value)
        pass
        
def WPD_StatusHandler(command, value, qualifier, hardware=None):
    __LogFeedback(hardware.Name, command, value, Qualifier=qualifier)
    for UIDev in System.CONTROLLER.UIDevices:
        # if self.GUIHost.ActCtl.CurrentActivity != 'adv_share':
        #     if TP.SrcCtl.SelectedSource.Id == hardware.Id:
        #         PodFeedbackHelper(TP, hardware, blank_on_fail=False)
        # else:
        #     if (TP.SrcCtl.OpenControlPopup is not None and
        #         TP.SrcCtl.OpenControlPopup['page'] == 'Modal-SrcCtl-WPD' and 
        #         TP.SrcCtl.OpenControlPopup['source'].Id == hardware.Id):
        #             PodFeedbackHelper(TP, hardware, blank_on_fail=False)
        pass
    
def VMX_InputHandler(command, value, qualifier, hardware=None):
    __LogFeedback(hardware.Name, command, value, Qualifier=qualifier)
    for UIDev in System.CONTROLLER.UIDevices:
        # srcObj = TP.SrcCtl.GetSourceByInput(qualifier['Input'])
        # if value == 'Active':
        #     srcObj.ClearAlert()
        # elif value == 'Not Active':
        #     srcObj.AppendAlert()
        pass
    
def VMX_OutputHandler(command, value, qualifier, hardware=None):
    __LogFeedback(hardware.Name, command, value, Qualifier=qualifier)
    Logger.Log('Tie: {}\n    {} -> {}'.format(qualifier['Tie Type'], qualifier['Output'], value))


## End Function Definitions ----------------------------------------------------



