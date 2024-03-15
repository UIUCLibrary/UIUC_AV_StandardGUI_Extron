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
from typing import TYPE_CHECKING, Dict, Union, cast
if TYPE_CHECKING: # pragma: no cover
    from modules.project.Devices import SystemHardwareController
    from extronlib.ui import Button, Label
    from modules.project.PrimitiveObjects import Layout

#### Python imports

#### Extron Library Imports
from extronlib import event

#### Project imports
from modules.project.MixIns import DeviceMixIn
from modules.device.mersive_solstice_pod import PodFeedbackHelper
from modules.project.PrimitiveObjects import MatrixTie

import System

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class Source(DeviceMixIn, object):
    def __init__(self,
                 device: 'SystemHardwareController',
                 icon: int,
                 input: int,
                 id: str=None,
                 name: str=None,
                #  alert: str='',
                 srcCtl: str=None,
                 advSrcCtl: str=None) -> None:
        
        DeviceMixIn.__init__(self, device, id, name)
        
        if isinstance(icon, int) and icon >= 0:
            self.Icon = icon
        else:
            raise ValueError('Icon must be an integer greater than or equal to 0')
        
        if isinstance(input, int) and input >= 0:
            self.Input = input
        else:
            raise ValueError('Input must be an integer greater than or equal to 0')
        
        self.SourceControlPage = srcCtl
        self.AdvSourceControlPage = advSrcCtl
        
        # self.__AlertText = {}
        # self.__AlertIndex = 0
        # self.__OverrideAlert = None
        # self.__OverrideState = False
        # self.__DefaultAlert = alert
        
        # self.__AlertTimer = Timer(1, self.__AlertTimerHandler)
        # self.__AlertTimer.Stop()

    # @property
    # def AlertText(self):
    #     if not self.__OverrideState:
    #         if len(self.__AlertText) > 0:
    #             txt =  list(self.__AlertText.keys())[self.__AlertIndex]
    #             self.CycleAlert()
    #         else:
    #             txt = ''
    #     else:
    #         txt = self.__OverrideAlert
    #     return txt
    
    # @property
    # def AlertBlock(self):
    #     block = '\n'.join(self.__AlertText)
    #     block = block.strip()
    #     if self.__OverrideState:
    #         block = '{}\n{}'.format(self.__OverrideAlert, block)
    #     return block
    
    # @property
    # def Alerts(self):
    #     count = len(self.__AlertText)
    #     if self.__OverrideState:
    #         count += 1
    #     return count
    
    # @property
    # def AlertFlag(self):
    #     if len(self.__AlertText) > 0:
    #         return True
    #     elif self.__OverrideState:
    #         return True
    #     else:
    #         return False
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # def __AlertTimerHandler(self, timer: 'Timer', count: int):
    #     iterList = list(self.__AlertText.keys())
    #     for msg in iterList:
    #         if self.__AlertText[msg] > 0:
    #             self.__AlertText[msg] -= 1
    #         elif self.__AlertText[msg] == 0:
    #             self.__AlertText.pop(msg)
    #     if len(self.__AlertText) == 0:
    #         timer.Stop()
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # def CycleAlert(self):
    #     self.__AlertIndex += 1
    #     if self.__AlertIndex >= len(self.__AlertText):
    #         self.__AlertIndex = 0
    
    # def AppendAlert(self, msg: str=None, timeout: int=0) -> None:
    #     if msg is None:
    #         msg = self.__DefaultAlert
            
    #     if timeout > 0:
    #         self.__AlertText[msg] = timeout
    #     else: 
    #         self.__AlertText[msg] = -1
        
    #     if self.__AlertTimer.State in ['Paused', 'Stopped']:
    #         self.__AlertTimer.Restart()
        
    # def OverrideAlert(self, msg: str, timeout: int=60) -> None:
    #     self.__OverrideAlert = msg
    #     self.__OverrideState = True
    #     if timeout > 0:
    #         @Wait(timeout) # pragma: no cover
    #         def OverrideTimeoutHandler():
    #             self.__OverrideState = False
    
    # def ClearOverride(self):
    #     self.__OverrideAlert = None
    #     self.__OverrideState = False
    
    # def ClearAlert(self, msg: str=None):
    #     if msg is None:
    #         msg = self.__DefaultAlert
            
    #     self.__AlertText.pop(msg)
        
    #     if len(self.__AlertText) == 0:
    #         self.__AlertTimer.Stop()
    
    # def ResetAlert(self) -> None:
    #     self.__AlertText = {}
    #     self.__AlertTimer.Stop()
        
BLANK_SOURCE = Source(None, 0, 0, 'blank', 'None')

class Destination(DeviceMixIn, object):
    def __init__(self,
                 device: 'SystemHardwareController',
                 output: int,
                 destType: str,
                 groupWrkSrc: str,
                 advLayout: 'Layout',
                 screen: str = None,
                 confFollow: str=None,
                 id: str=None,
                 name: str=None) -> None:
        
        DeviceMixIn.__init__(self, device, id, name)
        
        if isinstance(output, int) and output >= 0:
            self.Output = output
        else:
            raise ValueError('Output must be an integer greater than or equal to 0')
        
        self.AdvLayoutPosition = advLayout
        self.GroupWorkSource = System.CONTROLLER.Devices.GetSource(id = groupWrkSrc)
        self.Type = destType
        self.ConfFollow = confFollow
        self.ScreenId = screen
        
        self.__Mute = False
        self.__AssignedVidSource = BLANK_SOURCE
        self.__AssignedAudSource = BLANK_SOURCE
        self.__AdvSelectBtn = None
        self.__AdvCtlBtn = None
        self.__AdvAudBtn = None
        self.__AdvAlertBtn = None
        self.__AdvScnBtn = None
        self.__AdvLabel = None
        self.__MatrixRow = None
    
    @property
    def AssignedSource(self) -> MatrixTie:
        return MatrixTie(video=self.__AssignedVidSource, audio=self.__AssignedAudSource)
    
    @property
    def AssignedInput(self) -> MatrixTie:
        return MatrixTie(video=self.__AssignedVidInput, audio=self.__AssignedAudInput)
    
    @property
    def __AssignedVidInput(self) -> int:
        return self.__AssignedVidSource.Input
    
    @property
    def __AssignedAudInput(self) -> int:
        return self.__AssignedAudSource.Input
    
    @property
    def Mute(self) -> bool:
        return self.__Mute
    
    @Mute.setter
    def Mute(self, state: Union[bool, int, str]):
        setState = (state in ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE'])
        self.__Mute = setState
        
    @property
    def SystemAudioState(self) -> int:
        if self.__AdvAudBtn is None:
            return None # this has not yet been assigned
        else:
            return self.__AdvAudBtn.State
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __SelectHandler(self, button: 'Button', action: str):
        self.SourceController.SwitchSources(self.SourceController.SelectedSource, [self])
    
    def __SourceControlHandler(self, button: 'Button', action: str):
        # configure source control page
        modal = 'Modal-SrcCtl-{}'.format(self.AssignedSource.Vid.AdvSourceControlPage)
        
        if modal == 'Modal-SrcCtl-WPD':
            PodFeedbackHelper(self.SourceController.UIHost, self.AssignedSource.Vid.Id, blank_on_fail=True)
        
        # show source control page
        self.SourceController.UIHost.ShowPopup(modal)
        self.SourceController.OpenControlPopup = {
            'page': modal,
            'source': self.AssignedSource.Vid
        }
    
    def __AudioHandler(self, button: 'Button', action: str):
        if action == "Tapped":
            if button.State == 0: # system audio currently selected
                # deselect this destination as the system audio follow
                button.SetState(1)
                self.SourceController.SystemAudioFollowDestination = None
            elif button.State == 1: # system audio currently unselected
                # select this destination as the system audio follow, deselect any other destination as the system audio follow
                button.SetState(0)
                self.SourceController.SystemAudioFollowDestination = self
            elif button.State == 2: # local audio unmuted
                # mute local audio
                button.SetState(3)
                self.SourceController.UIHost.DispCtl.DisplayMute = (self, 'On')
            elif button.State == 3: # local audio muted
                # unmute local audio
                button.SetState(2)
                self.SourceController.UIHost.DispCtl.DisplayMute = (self, 'Off')
        elif action == "Released":
            if (button.State in [0, 1]) and self.Type == 'mon':
                if self is self.SourceController.SystemAudioFollowDestination:
                    self.SourceController.SystemAudioFollowDestination = None
                    
                muteState = self.SourceController.UIHost.DispCtl.DisplayMute[self.Id]
                    
                if muteState:
                    button.SetState(3)
                else:
                    button.SetState(2)
            elif (button.State == 2 or button.State == 3):
                button.SetState(1)
                self.SourceController.UIHost.DispCtl.DisplayMute = (self, 'On')
        elif action == 'Held':
            if self.Type == 'mon':
                self.SourceController.UIHost.Click(1)
    
    def __AlertHandler(self, button: 'Button', action: str):
        self.SourceController.UIHost.Lbls['SourceAlertLabel'].SetText(self.AssignedSource.Vid.AlertBlock)
        self.SourceController.UIHost.ShowPopup('Modal-SrcErr')
    
    def __ScreenHandler(self, button: 'Button', action: str):
        # Configure Screen Control Modal
        self.SourceController.SetAdvRelayDestination(self)
        # Show Screen Control Modal
        self.SourceController.UIHost.ShowPopup('Modal-ScnCtl')
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def DestAudioFeedbackHandler(self, Configuration: Union[int, str]):
        # TODO: Change AudDict to an Enum object
        AudDict = \
            {
                0: 'System Source',
                1: 'System Mute',
                2: 'Local Source',
                3: 'Local Mute'
            }
        if isinstance(Configuration, int) and Configuration in list(AudDict.keys()):
            pass
        elif isinstance(Configuration, str) and Configuration in list(AudDict.values()):
            Configuration = list(AudDict.values()).index(Configuration)
        else:
            if not isinstance(Configuration, (int, str)):
                raise TypeError("Configuration must be a str or int")
            else:
                raise ValueError("Configuration must be a valid state int or str")
        
        curConfig = self.__AdvAudBtn.State
        
        if Configuration == 0:
            if curConfig == 2:
                self.SourceController.UIHost.DispCtl.DisplayMute = (self, 'On')
            if self is not self.SourceController.SystemAudioFollowDestination:
                self.SourceController.SystemAudioFollowDestination = self
            self.__AdvAudBtn.SetState(Configuration)
        if Configuration == 1:
            if curConfig == 2:
                self.SourceController.UIHost.DispCtl.DisplayMute = (self, 'On')
            self.__AdvAudBtn.SetState(Configuration)
        if Configuration == 2:
            if curConfig == 3:
                self.SourceController.UIHost.DispCtl.DisplayMute = (self, 'Off')
            elif curConfig == 0 and self is self.SourceController.SystemAudioFollowDestination:
                self.SourceController.SystemAudioFollowDestination = None
            self.__AdvAudBtn.SetState(Configuration)
        if Configuration == 3:
            if curConfig == 2:
                self.SourceController.UIHost.DispCtl.DisplayMute = (self, 'On')
            elif curConfig == 0 and self is self.SourceController.SystemAudioFollowDestination:
                self.SourceController.SystemAudioFollowDestination = None
            self.__AdvAudBtn.SetState(Configuration)
    
    def ToggleMute(self) -> None:
        self.__Mute = not self.__Mute
    
    def AssignMatrixRow(self, row) -> None:
        self.__MatrixRow = row
    
    def AssignInput(self, input: 'int') -> None:
        self.AssignMatrixByInput(input, 'AV')
        
    def AssignSource(self, source: 'Source') -> None:
        self.AssignMatrixBySource(source, 'AV')
    
    def AssignMatrixByInput(self, input: int, tieType: str='AV') -> None:
        if not isinstance(input, int):
            raise ValueError('Input must be an integer')
        
        inputSrc = self.SourceController.GetSourceByInput(input)
            
        self.AssignMatrixBySource(inputSrc, tieType)
    
    def AssignMatrixBySource(self, source: 'Source', tieType: str='AV') -> None:
        if not (tieType == 'Aud' or tieType == 'Vid' or tieType == 'AV' or tieType == 'untie'):
            raise ValueError("TieType must either be 'AV', 'Aud', 'Vid', or 'untie'. Provided TieType: {}".format(tieType))
        
        if not isinstance(source, Source):
            raise ValueError('Source must be a Source object')
        
        if tieType == 'Vid' or tieType == 'AV':
            self.__AssignedVidSource = source
        if tieType == 'Aud' or tieType == 'AV':
            self.__AssignedAudSource = source
            
        self.UpdateAdvUI()
        
        self.__MatrixRow.MakeTie(source.Input, tieType)

    def AssignAdvUI(self, ui: Dict[str, Union['Button', 'Label']]) -> None:
        self.__AdvSelectBtn = ui['select']
        self.__AdvCtlBtn = ui['ctl']
        self.__AdvAudBtn = ui['aud']
        self.__AdvAlertBtn = ui['alert']
        self.__AdvScnBtn = ui['scn']
        self.__AdvLabel = ui['label']
        
        # set distination label text
        self.__AdvLabel.SetText(self.Name)
        
        # clear selected source text
        self.__AdvSelectBtn.SetText("") 
        
        @event(self.__AdvSelectBtn, 'Pressed') # pragma: no cover
        def advSelectHandler(button: 'Button', action: str):
            self.__SelectHandler(button, action)
            
        # Source Control Buttons
        self.__AdvCtlBtn.SetVisible(False)
        self.__AdvCtlBtn.SetEnable(False)
        
        @event(self.__AdvCtlBtn, 'Pressed') # pragma: no cover
        def advSrcCtlHandler(button: 'Button', action: str):
            self.__SourceControlHandler(button, action)
        
        # Destination Audio Buttons
        if self.Type == 'conf':
            self.__AdvAudBtn.SetEnable(False)
            self.__AdvAudBtn.SetVisible(False)
        else:
            if self is self.SourceController.PrimaryDestination:
                self.__AdvAudBtn.SetState(0)
            else:
                self.__AdvAudBtn.SetState(1)
        
        @event(self.__AdvAudBtn, ['Tapped', 'Released', 'Held']) # pragma: no cover
        def advAudHandler(button: 'Button', action: str):
            self.__AudioHandler(button, action)
        
        # Destination Alert Buttons
        self.__AdvAlertBtn.SetVisible(False)
        self.__AdvAlertBtn.SetEnable(False)
        
        @event(self.__AdvAlertBtn, 'Pressed') # pragma: no cover
        def advAlertHandler(button: 'Button', action: str):
            self.__AlertHandler(button, action)
        
        # Screen Control Buttons
        if self.Type == "proj+scn":
            self.__AdvScnBtn.SetVisible(True)
            self.__AdvScnBtn.SetEnable(True)
        else:
            self.__AdvScnBtn.SetVisible(False)
            self.__AdvScnBtn.SetEnable(False)
            
        @event(self.__AdvScnBtn, 'Pressed') # pragma: no cover
        def advScnHandler(button: 'Button', action: str):
            self.__ScreenHandler(button, action)
    
    def UpdateAdvUI(self) -> None:
        vidSrc = self.AssignedSource.Vid
        vidSrc = cast('Source', vidSrc)
        self.__AdvSelectBtn.SetText(vidSrc.Name)
        
        if vidSrc.AdvSourceControlPage is None:
            self.__AdvCtlBtn.SetVisible(False)
            self.__AdvCtlBtn.SetEnable(False)
        else:
            self.__AdvCtlBtn.SetVisible(True)
            self.__AdvCtlBtn.SetEnable(True)
            
    def AdvSourceAlertHandler(self) -> None:
        if self.AssignedSource is not None and self.AssignedSource.Vid.AlertFlag:
            self.__AdvAlertBtn.SetVisible(True)
            self.__AdvAlertBtn.SetEnable(True)
            self.__AdvAlertBtn.SetBlinking('Medium', [0,1])
        else:
            self.__AdvAlertBtn.SetVisible(False)
            self.__AdvAlertBtn.SetEnable(False)
            self.__AdvAlertBtn.SetState(1)
            
class Camera(DeviceMixIn, object):
    def __init__(self,
                 device: 'SystemHardwareController',
                 id: str=None,
                 name: str=None) -> None:
        
        DeviceMixIn.__init__(self, device, id, name)
        

class Switch(DeviceMixIn, object):
    def __init__(self,
                 device: 'SystemHardwareController',
                 id: str=None,
                 name: str=None) -> None:
        
        DeviceMixIn.__init__(self, device, id, name)
        
class Microphone(DeviceMixIn, object):
    def __init__(self,
                 device: 'SystemHardwareController',
                 id: str=None,
                 name: str=None) -> None:
        
        DeviceMixIn.__init__(self, device, id, name)

class Screen(DeviceMixIn, object):
    def __init__(self,
                 device: 'SystemHardwareController',
                 id: str=None,
                 name: str=None) -> None:
        
        DeviceMixIn.__init__(self, device, id, name)

class Light(DeviceMixIn, object):
    def __init__(self,
                 device: 'SystemHardwareController',
                 id: str=None,
                 name: str=None) -> None:
        
        DeviceMixIn.__init__(self, device, id, name)

class Shade(DeviceMixIn, object):
    def __init__(self,
                 device: 'SystemHardwareController',
                 id: str=None,
                 name: str=None) -> None:
        
        DeviceMixIn.__init__(self, device, id, name)

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



