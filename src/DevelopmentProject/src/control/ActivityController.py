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
from typing import TYPE_CHECKING, Tuple, Union
if TYPE_CHECKING: # pragma: no cover
    from modules.project.SystemHost import SystemController
    from extronlib.ui import Button
    from modules.helper.ExtendedUIClasses import ExButton

#### Python imports

#### Extron Library Imports

#### Project imports
from modules.helper.CommonUtilities import Logger, TimeIntToStr
from modules.helper.ExtendedSystemClasses import ExTimer
from modules.helper.PrimitiveObjects import DictObj
from Constants import STANDBY, ActivityMode, SystemState, TieType, MATRIX_ACTION
import System
from ui.interface.TouchPanel import StartShutdownConfirmation


## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class ActivityController:
    def __init__(self, SystemHost: 'SystemController') -> None:
        self.SystemHost = SystemHost
        
        self.Timers = DictObj({
            'Startup':  ExTimer(1, 
                                self.SystemHost.SystemActiveTransition, 
                                self.SystemHost.Timers.Startup, 
                                self.SystemHost.SystemActiveComplete),
            'Switch':   ExTimer(1, 
                                self.ActivitySwitchTransition, 
                                SystemHost.Timers.Switch, 
                                self.ActivitySwitchComplete),
            'Shutdown': ExTimer(1, 
                                self.SystemHost.SystemStandbyTransition, 
                                self.SystemHost.Timers.Shutdown, 
                                self.SystemHost.SystemStandbyComplete),
            'Splash':   ExTimer(30,
                                self.SystemHost.SplashChecker,
                                self.SystemHost.Timers.SplashPage,
                                self.SystemHost.ShowSplash)
        })
        self.Timers.Startup.Stop()
        self.Timers.Switch.Stop()
        self.Timers.Shutdown.Stop()
        self.Timers.Splash.Stop()
        
        self.Initialized = False
            
    @property
    def CurrentActivity(self) -> ActivityMode:
        return self.SystemHost.SystemActivity
    
    @CurrentActivity.setter
    def CurrentActivity(self, val) -> None:
        raise AttributeError('Setting CurrentActivity is disallowed. Use System.CONTROLLER.SystemActivity instead.')

    def SystemStateChange(self, state: SystemState) -> None:
        for uiDev in self.SystemHost.UIDevices:
            uiDev.Interface.TransitionSystemState(state)
        
        if state is SystemState.Active:
            # Start System feedback
            for uiDev in self.SystemHost.UIDevices:
                uiDev.Interface.Transition.Label.SetText('System is switching on. Please Wait...')
                uiDev.Interface.Transition.Level.SetRange(0, self.SystemHost.Timers.Startup, 1)
                uiDev.Interface.Transition.Level.SetLevel(0)
                uiDev.Interface.Transition.Count.SetText(TimeIntToStr(self.SystemHost.Timers.Startup))
            
            self.Timers.Startup.Restart()
            
            self.SystemHost.SystemActiveInit()
                
        elif state is SystemState.Standby:
            # Shutdown System
            for uiDev in self.SystemHost.UIDevices:
                uiDev.Interface.Transition.Label.SetText('System is switching off. Please Wait...')
                uiDev.Interface.Transition.Level.SetRange(0, self.SystemHost.Timers.Shutdown, 1)
                uiDev.Interface.Transition.Level.SetLevel(0)
                uiDev.Interface.Transition.Count.SetText(TimeIntToStr(self.SystemHost.Timers.Shutdown))
            
            self.Timers.Shutdown.Restart()
            
            self.SystemHost.SystemStandbyInit()

    def SystemActivityChange(self, activity: ActivityMode) -> None:
        if activity is ActivityMode.Share:
            TransitionText = 'System is switching to Share mode. Please Wait...'
        elif activity is ActivityMode.AdvShare:
            TransitionText = 'System is switching to Advanced Share mode. Please Wait...'
        elif activity is ActivityMode.GroupWork:
            TransitionText = 'System is switching to Group Work mode. Please Wait...'
        
        for uiDev in self.SystemHost.UIDevices:
            uiDev.Interface.TransitionActivity(activity)
            uiDev.Interface.Transition.Label.SetText(TransitionText)
            uiDev.Interface.Transition.Level.SetRange(0, self.SystemHost.Timers.Switch, 1)
            uiDev.Interface.Transition.Level.SetLevel(0)
            uiDev.Interface.Transition.Count.SetText(TimeIntToStr(self.SystemHost.Timers.Switch))

        self.Timers.Switch.Restart()
        
        self.ActivitySwitchInit()

    def Initialize(self) -> None:        
        self.Initialized = True
        
    def SystemModeChangeHandler(self, Transition: Tuple[Tuple[bool, SystemState], Tuple[bool, ActivityMode]]) -> None:
        Logger.Log('System Transition:', Transition)
        
        if Transition[0][0] is True:
            Logger.Log('Changing State ({})'.format(Transition[0][1].name))
            self.SystemStateChange(Transition[0][1])
        else:
            if Transition[1][0] is True:
                Logger.Log('Changing Activity ({})'.format(Transition[1][1].name))
                self.SystemActivityChange(Transition[1][1])
                    
    def ActivitySwitchInit(self) -> None:
        Logger.Log('ActivitySwitchInit Func', self.SystemHost.TransitionState)
        if self.SystemHost.TransitionState[0][1] == SystemState.Active:
            # Start Up Source Switches
            if self.SystemHost.TransitionState[1][1] == ActivityMode.Share:
                # Share Mode
                swMatrixAction = MATRIX_ACTION(output= 'all', 
                                               input= self.SystemHost.Devices.GetSource(id=self.SystemHost.DefaultSourceId).Input, 
                                               type= TieType.AudioVideo)
            elif self.SystemHost.TransitionState[1][1] == ActivityMode.AdvShare:
                # Adv Share Mode
                swMatrixAction = MATRIX_ACTION(output= 'all', 
                                               input= self.SystemHost.Devices.GetSource(id=self.SystemHost.DefaultSourceId).Input, 
                                               type= TieType.AudioVideo)
            elif self.SystemHost.TransitionState[1][1] == ActivityMode.GroupWork:
                # Group Work
                swMatrixAction = []
                for dest in self.SystemHost.Devices.Destinations:
                    Logger.Log("Destination Info", type(dest.Destination), dest.Destination.GroupWorkSource), type(dest.Destination.GroupWorkSource)
                    swMatrixAction.append(MATRIX_ACTION(output= dest.Destination.Output,
                                                        input= dest.Destination.GroupWorkSource.Input,
                                                        type= TieType.AudioVideo))
        else:
            currentPriSource = self.SystemHost.SrcCtl.GetCurrentSourceForDestination(self.SystemHost.PrimaryDestinationId)
            
            # Activity Switch Source Switches
            if self.SystemHost.TransitionState[1][1] == ActivityMode.Share:
                # Share Mode
                swMatrixAction = MATRIX_ACTION(output= 'all',
                                               input= currentPriSource.video,
                                               type= TieType.AudioVideo)
                
            elif self.SystemHost.TransitionState[1][1] == ActivityMode.AdvShare:
                # Adv Share Mode
                # can probably just leave these as they are for this transition
                swMatrixAction = None
            elif self.SystemHost.TransitionState[1][1] == ActivityMode.GroupWork:
                # Group Work
                swMatrixAction = []
                for dest in self.SystemHost.Devices.Destinations:
                    Logger.Log("Destination Info", type(dest.Destination), dest.Destination.GroupWorkSource), type(dest.Destination.GroupWorkSource)
                    if dest.Id == self.SystemHost.PrimaryDestinationId:
                        swMatrixAction.append(MATRIX_ACTION(output= dest.Destination.Output,
                                                            input= currentPriSource.video,
                                                            type= TieType.AudioVideo))
                    else:
                        swMatrixAction.append(MATRIX_ACTION(output= dest.Destination.Output,
                                                            input= dest.Destination.GroupWorkSource.Input,
                                                            type= TieType.AudioVideo))
        
        Logger.Log('Matrix Action(s)', swMatrixAction)
        if swMatrixAction is not None:
            result = self.SystemHost.SrcCtl.MatrixAction(swMatrixAction)
            Logger.Log('Matrix Result', result)
            
        # START_HERE
        # Not seeing the blank button added to the list or at least that the list isn't being updated correctly
        if self.SystemHost.TransitionState[1][1] == ActivityMode.AdvShare:
            self.SystemHost.SrcCtl.AddBlankBtns()
        else:
            self.SystemHost.SrcCtl.RemoveBlankBtns()
    
    def ActivitySwitchTransition(self, timer, count) -> None:
        timeRemaining = self.SystemHost.Timers.Switch - count
        for uiDev in self.SystemHost.UIDevices:
            uiDev.Interface.Transition.Count.SetText(TimeIntToStr(timeRemaining))
            uiDev.Interface.Transition.Level.SetLevel(count)
    
    def ActivitySwitchComplete(self, timer, count) -> None:
        for uiDev in self.SystemHost.UIDevices:
            uiDev.HidePopup('Power-Transition')
        self.SystemHost.ActivityTransitionComplete()

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def ActivitySelect(button: Union['Button', 'ExButton'], action: str) -> None:
    if button.activity not in STANDBY:
        System.CONTROLLER.SystemActivity = ActivityMode[button.activity]
    else:
        StartShutdownConfirmation(System.CONTROLLER.SystemActivity, click=True)

## End Function Definitions ----------------------------------------------------



