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
from typing import TYPE_CHECKING, Union
if TYPE_CHECKING: # pragma: no cover
    from modules.project.ExtendedDeviceClasses import ExUIDevice
    from modules.project.ExtendedUIClasses import ExButton, ExSlider
    from extronlib.device import UIDevice
    from extronlib.ui import Button
    

#### Python imports
import json
import functools

#### Extron Library Imports
from extronlib import event

#### Project imports
from modules.project.PrimitiveObjects import DictObj, TieType, MatrixAction, ActivityMode, SystemState
from modules.helper.CommonUtilities import TimeIntToStr, Logger
from modules.project.ExtendedSystemClasses import ExTimer
from ui.interface.TouchPanel.Objects import TouchPanelObjects
from ui.Feedback.Source import ShowSourceSelectionFeedback, ShowSourceControlFeedback

import System
import Variables

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class TouchPanelInterface():
    def __init__(self, device: Union['ExUIDevice', 'UIDevice'], interfaceType: str) -> None:
        self.__LayoutPath = '/var/nortxe/gcp/layout'
        self.__LayoutGLD = '{}.gdl'.format(Variables.UI_LAYOUT)
        self.__LayoutJSON = '{}_objects.json'.format(Variables.UI_LAYOUT)
        self.__ControlJSON = '{}_controls.json'.format(Variables.UI_LAYOUT)
        self.__TechPgsJSON = '{}_techPages.json'.format(Variables.UI_LAYOUT)

        self.LayoutDict = json.load(open('{}/{}'.format(self.__LayoutPath, self.__LayoutJSON)))
        self.ControlDict = json.load(open('{}/{}'.format(self.__LayoutPath, self.__ControlJSON)))
        self.TechPgDict = json.load(open('{}/{}'.format(self.__LayoutPath, self.__TechPgsJSON)))

        self.Device = device
        self.InterfaceType = interfaceType
        self.Objects = TouchPanelObjects()
        self.Transition = DictObj({
            "Label": None,
            "Level": None,
            "Count": None
        })
        
        self.Initialized = False
    
    def Initialize(self) -> None:
        ## Load UI Objects
        self.Objects.LoadButtons(UIHost=self.Device, jsonObj=self.LayoutDict)
        self.Objects.LoadKnobs(UIHost=self.Device, jsonObj=self.LayoutDict)
        self.Objects.LoadLabels(UIHost=self.Device, jsonObj=self.LayoutDict)
        self.Objects.LoadLevels(UIHost=self.Device, jsonObj=self.LayoutDict)
        self.Objects.LoadSliders(UIHost=self.Device, jsonObj=self.LayoutDict)
        
        ## Load Page Lists
        self.Objects.LoadModalPages(jsonObj=self.LayoutDict)
        self.Objects.LoadPopoverPages(jsonObj=self.LayoutDict)
        self.Objects.LoadPopupGroups(jsonObj=self.LayoutDict)
        
        ## Load Controls
        self.Objects.LoadControlGroups(UIHost=self.Device, jsonObj=self.LayoutDict)
        self.Objects.LoadControls(jsonObj=self.ControlDict)

        self.Transition.Label = self.Objects.Labels['PowerTransLabel-State']
        self.Transition.Level = self.Objects.Levels['PowerTransIndicator']
        self.Transition.Count = self.Objects.Labels['PowerTransLabel-Count']

        ## Initialize Objects
        for btn in self.Objects.Buttons.values():
            btn.Initialize()
        for knb in self.Objects.Knobs.values():
            knb.Initialize()
        for lbl in self.Objects.Labels.values():
            lbl.Initialize()
        for lvl in self.Objects.Levels.values():
            lvl.Initialize()
        for sld in self.Objects.Sliders.values():
            sld.Initialize()

        self.Initialized = True
    
    def TransitionSystemState(self, state: SystemState) -> None:
        if state is SystemState.Active:
            self.Device.ShowPopup('Power-Transition')
            self.Device.ShowPage('Main')
        elif state is SystemState.Standby:
            self.Device.ShowPopup('Power-Transition')
            self.Device.HidePopup('Shutdown-Confirmation')
            self.Device.ShowPage('Start')
    
    def TransitionActivity(self, activity: ActivityMode) -> None:
        self.Device.ShowPopup('Power-Transition')
        self.Device.ShowPage('Main')
    
    def __ActivityTipProgress(self, timer, count) -> None:
        pass
    
    def __ActivityTipComplete(self, timer, count) -> None:
        pass
    
    def CloseTechMenu(self) -> None:
        Logger.Log("Closing Tech Menu", System.CONTROLLER.SystemState, System.CONTROLLER.TransitionState)
        if System.CONTROLLER.SystemState is SystemState.Standby:
            self.Device.ShowPage('Start')
        else:
            self.Device.ShowPage('Main')

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def SplashStartHandler(button: Union['Button', 'ExButton'], action: str) -> None:
    uiDev = button.UIHost
    
    if System.CONTROLLER.SystemPIN is not None:
        uiDev.PINAccess.Open(PIN=System.CONTROLLER.SystemPIN, Callback=SplashPinSuccess)
    else:
        SplashPinSuccess()
        
def SplashPinSuccess() -> None:
    System.CONTROLLER.ShowStart()
        
def StartShutdownConfirmation(prevActivity: ActivityMode, click: bool=False) -> None:
    cancelBtns = [uiDev.Interface.Objects.Buttons['Shutdown-Cancel'] for uiDev in System.CONTROLLER.UIDevices]
    endNowBtns = [uiDev.Interface.Objects.Buttons['Shutdown-EndNow'] for uiDev in System.CONTROLLER.UIDevices]
    
    # due to how these are called, don't use eventEx
    @event(cancelBtns, ['Pressed', 'Released'])
    def CancelBtnHandler(button: 'ExButton', event: str):
        if event == 'Pressed':
            button.SetState(1)
        elif event == 'Released':
            for uiDev in System.CONTROLLER.UIDevices:
                # the below line technically doesn't for the ActivitySelect-Off button, but that should never be the case
                uiDev.Interface.Objects.ControlGroups['Activity-Select'].SetCurrent('ActivitySelect-{}'.format(prevActivity.name))
                uiDev.HidePopup('Shutdown-Confirmation')
                uiDev.LightsOff()
            ShutdownTimer.Stop()
            button.SetState(0)
    
    # due to how these are called, don't use eventEx
    @event(endNowBtns, ['Pressed', 'Released'])
    def EndNowBtnHandler(button: 'ExButton', event: str):
        if event == 'Pressed':
            button.SetState(1)
        elif event == 'Released':
            ShutdownTimer.Wrapup()
            button.SetState(0)
    
    def CountdownHandler(timer: 'ExTimer', count: int):
        timeTillShutdown = int(System.CONTROLLER.Timers.ShutdownConf - (count * timer.Interval))
        
        for uiDev in System.CONTROLLER.UIDevices:
            Label = uiDev.Interface.Objects.Labels['ShutdownConf-Count']
            Level = uiDev.Interface.Objects.Levels['ShutdownConfIndicator']
            
            Label.SetText(TimeIntToStr(timeTillShutdown))
            Level.SetLevel(int(count * timer.Interval))
            
            if timeTillShutdown <= 5:
                uiDev.Click()
            
    def ShutdownHandler(timer: 'ExTimer', count: int):
        for uiDev in System.CONTROLLER.UIDevices:
            uiDev.LightsOff()
        System.CONTROLLER.SystemActivity = ActivityMode.Standby
        Logger.Log('ShutdownHandler',  ActivityMode.Standby, System.CONTROLLER.SystemActivity)
    
    for uiDev in System.CONTROLLER.UIDevices:
        Label = uiDev.Interface.Objects.Labels['ShutdownConf-Count']
        Level = uiDev.Interface.Objects.Levels['ShutdownConfIndicator']
        
        Level.SetRange(0, System.CONTROLLER.Timers.ShutdownConf, 1)
        Level.SetLevel(0)
        Label.SetText(TimeIntToStr(System.CONTROLLER.Timers.ShutdownConf))
        uiDev.ShowPopup('Shutdown-Confirmation')
        uiDev.Click(5, 0.2)
        uiDev.BlinkLights(Rate='Fast', StateList=['Red', 'Off'])
        
    ShutdownTimer = ExTimer(1, CountdownHandler, System.CONTROLLER.Timers.ShutdownConf, ShutdownHandler)

def HeaderSelect(button: 'ExButton', action: str) -> None:
    uiDev = button.UIHost
    if button.HeaderAction == 'Room':
        uiDev.ShowPopup('Popover-Room')
    elif button.HeaderAction in ['Help', 'Alert']:
        uiDev.ShowPopup('Popover-Ctl-{}'.format(button.HeaderAction))
    elif button.HeaderAction in ['Audio', 'Lights', 'Camera']:
        uiDev.ShowPopup('Popover-Ctl-{}_{}'.format(button.HeaderAction, button.PopoverSuffix()))
    elif button.HeaderAction == 'Close':
        for popover in uiDev.Interface.Objects.PopoverPages:
            uiDev.HidePopup(popover)
            
def OpenTechPages(button: 'ExButton', action: str) -> None:
    uiDev = button.UIHost
    
    if System.CONTROLLER.TechPIN is not None:
        callbackFn = functools.partial(TechPinSuccess, uiDev=uiDev)
        uiDev.PINAccess.Open(PIN=System.CONTROLLER.TechPIN, Callback=callbackFn)
    else:
        TechPinSuccess(uiDev)
        
def TechPinSuccess(uiDev: 'ExUIDevice') -> None:
    uiSet = uiDev.Interface.Objects.ControlGroups['Tech-Menu-Select']
    uiSet.SetCurrentRef(0)
    uiSet.SetOffset(0)
    uiDev.ShowPopup(uiSet.GetCurrentRef().page)
    uiDev.ShowPage('Tech')
    
def CloseTechPages(button: 'ExButton', action: str) -> None:
    uiDev = button.UIHost
    
    uiDev.Interface.CloseTechMenu()
        
def TechPageMenuNav(button: 'ExButton', action: str) -> None:
    # uiDev = button.UIHost
    uiSet = button.Group
    
    newOff = uiSet.Offset + button.Offset
    uiSet.SetOffset(newOff)
    
def TechPageSelect(button: 'ExButton', action: str) -> None:
    uiDev = button.UIHost
    uiSet = button.Group.Group
    
    refBtn = uiSet.GetRefByObject(button)
    uiSet.SetCurrentRef(refBtn)
    
    uiDev.ShowPopup(refBtn.page)
    
def PanelBrightnessHandler(source: 'ExSlider', event: str, value: Union[int, float]) -> None:
    uiDev = source.UIHost
    
    uiDev.SetBrightness(int(value))

def PanelAutoBrightnessHandler(source: 'ExButton', event: str) -> None:
    uiDev = source.UIHost
    
    uiDev.SetAutoBrightness(bool(source.State))

def PanelVolumeHandler(source: 'ExSlider', event: str, value: Union[int, float]) -> None:
    uiDev = source.UIHost
    
    uiDev.SetVolume('Master', int(value))

def PanelSleepHandler(source: 'ExSlider', event: str, value: Union[int, float]) -> None:
    uiDev = source.UIHost
    
    uiDev.SetSleepTimer(True, int(value * 60))

def PanelAutoSleepHandler(source: 'ExButton', event: str) -> None:
    uiDev = source.UIHost
    
    state = bool(source.State)
    
    if state:
        sleepTime = uiDev.SleepTimer
    else:
        sleepTime = None
        
    uiDev.SetSleepTimer(state, sleepTime)
        

def PanelWakeOnMotionHandler(source: 'ExButton', event: str) -> None:
    uiDev = source.UIHost
    
    uiDev.SetWakeOnMotion(bool(source.State))

def SourceMenuNav(button: 'ExButton', action: str) -> None:
    # uiDev = button.UIHost
    uiSet = button.Group
    
    newOff = uiSet.Offset + button.Offset
    uiSet.SetOffset(newOff)

def SourceSelect(button: 'ExButton', action: str) -> None:
    uiSet = button.Group.Group
    
    refBtn = uiSet.GetRefByObject(button)
    uiSet.SetCurrentRef(refBtn)
    
    Logger.Debug("Button", button, "RefButton", refBtn)
    
    if System.CONTROLLER.SystemActivity == ActivityMode.Share:
        # Source Switch
        swMatrixAction = MatrixAction(output='all',
                                       input=refBtn.input,
                                       type=TieType.AudioVideo)
        Logger.Debug('Source Switch Matrix Action (Share)', swMatrixAction)
        System.CONTROLLER.SrcCtl.MatrixAction(swMatrixAction)
        
        # Update other panels' source selection
        ShowSourceSelectionFeedback(System.CONTROLLER.UIDevices, refBtn)
        
        # Update source control area
        ShowSourceControlFeedback(System.CONTROLLER.UIDevices, refBtn)
        
    elif System.CONTROLLER.SystemActivity == ActivityMode.GroupWork:
        # Source Switch
        swMatrixAction = MatrixAction(output=System.CONTROLLER.Devices.GetDestination(System.CONTROLLER.PrimaryDestinationId).Output,
                                       input=refBtn.input,
                                       type=TieType.AudioVideo)
        Logger.Debug('Source Switch Matrix Action (GroupWork)', swMatrixAction)
        System.CONTROLLER.SrcCtl.MatrixAction(swMatrixAction)
        
        # Update other panels' source selection
        ShowSourceSelectionFeedback(System.CONTROLLER.UIDevices, refBtn)
        
        # Update source control area
        ShowSourceControlFeedback(System.CONTROLLER.UIDevices, refBtn)
        
    elif System.CONTROLLER.SystemActivity == ActivityMode.AdvShare:
        # Source Select Only
        Logger.Debug('Source Selected (AdvShare)', refBtn.Name, refBtn.input)
        

## End Function Definitions ----------------------------------------------------
