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
from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING: # pragma: no cover
    from modules.project.extended.Device import ExUIDevice
    from modules.project.Collections.UISets import ScheduleConfigGroup, ScheduleEditGroup
    from modules.project.extended.UI import ButtonEx
    from datetime import datetime

#### Python imports

#### Extron Library Imports
from extronlib.system import Timer, Clock

#### Project imports
from modules.helper.ModuleSupport import eventEx
from modules.helper.CommonUtilities import Logger
from modules.project.PrimitiveObjects import ActivityMode, SystemState
from ui.interface.TouchPanel import StartShutdownConfirmation
import System

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class ScheduleController():
    def __init__(self, 
                 UIHost: 'ExUIDevice', 
                 ControlGroup: 'ScheduleConfigGroup',
                 EditGroup: 'ScheduleEditGroup') -> None:

        self.UIHost = UIHost
        
        self.__ControlGroup = ControlGroup
        self.__EditGroup = EditGroup
        
        self.__EditPage = "Modal-Scheduler"
        self.__EditMode = None
        
        self.ConfigSettings = System.CONTROLLER.RoomScheduleConfig
        
        self.__LastConfig = None
        
        self.UpdateTimer = Timer(5, self.UpdateTechPage)
        self.UpdateTimer.Stop()
        
        self.StartClock = Clock([self.__TimeConverter(self.ConfigSettings.Settings['auto_start']['pattern']['time'])],
                                self.ConfigSettings.Settings.serialize()['auto_start']['pattern']['days'],
                                self.__StartHandler)
        if self.ConfigSettings.Settings['auto_start']['enabled']:
            self.StartClock.Enable()
        else:
            self.StartClock.Disable()
            
        self.ShutdClock = Clock([self.__TimeConverter(self.ConfigSettings.Settings['auto_shutdown']['pattern']['time'])],
                                self.ConfigSettings.Settings.serialize()['auto_shutdown']['pattern']['days'],
                                self.__ShutdownHandler)
        if self.ConfigSettings.Settings['auto_shutdown']['enabled']:
            self.ShutdClock.Enable()
        else:
            self.ShutdClock.Disable()
        
        @eventEx(self.UIHost.PopupShown, 'Changed')
        def PageShownHandler(src, value) -> None:
            if value == 'Tech-RoomSchedule':
                Logger.Debug('Room Schedule Page Shown')
                self.UpdateTechPage(force=True)
                self.UpdateTimer.Restart()
                
        @eventEx(self.UIHost.PopupHidden, 'Changed')
        def PageHiddenHandler(src, value) -> None:
            if value == 'Tech-RoomSchedule':
                Logger.Debug('Room Schedule Page Hidden')
                self.UpdateTimer.Stop()
    
    def __StartHandler(self, clock: 'Clock'=None, dt: 'datetime'=None) -> None:
        mapDict = {
            'share': ActivityMode.Share,
            'adv_share': ActivityMode.AdvShare,
            'group_work': ActivityMode.GroupWork
        }
        
        mode = mapDict[self.ConfigSettings.Settings['auto_start']['mode']]
        ctlGrp = self.UIHost.Interface.Objects.ControlGroups['Activity-Select']
        
        ctlGrp.SetCurrent('ActivitySelect-{}'.format(mode.name))
        System.CONTROLLER.SystemActivity = mode
    
    def __ShutdownHandler(self, clock: 'Clock'=None, dt: 'datetime'=None) -> None:
        if System.CONTROLLER.SystemState is not SystemState.Standby:
            ctlGrp = self.UIHost.Interface.Objects.ControlGroups['Activity-Select']
            ctlGrp.SetCurrent('ActivitySelect-Off')
            StartShutdownConfirmation(System.CONTROLLER.SystemActivity, click=True)
        else:
            Logger.Debug('Automatic shutdown not running. System already in standby.')
    
    def __TimeConverter(self, timeDict: Dict[str, str]) -> str:
        if timeDict['ampm'] == 'PM':
            if timeDict['hr'] == '12':
                hr = '12'
            else:
                hr = str(int(timeDict['hr']) + 12).zfill(2)
        elif timeDict['ampm'] == 'AM':
            if timeDict['hr'] == '12':
                hr = '00'
            else:
                hr = timeDict['hr'].zfill(2)
        
        return "{hour}:{minute}:00".format(
                    hour = hr,
                    minute = timeDict['min']
                )
    
    def UpdateTechPage(self, timer: 'Timer' = None, count: int = None, force: bool = False) -> None:
        if self.ConfigSettings.Settings != self.__LastConfig or force:
            self.__LastConfig = self.ConfigSettings.Settings
            
            for key, settings in self.ConfigSettings.Settings.items():
                self.__ControlGroup.LoadCurrentSettings(key, settings)
                
    def UpdateEditor(self) -> None:
        self.__EditGroup.UpdatePattern()
        
    def UpdateEditorTime(self, mode: str, offset: int) -> None:
        self.__EditGroup.AdjustTime(mode, offset)
        
    def UpdateClockState(self, mode: str, state: bool) -> None:
        if mode == 'auto_start':
            if state:
                self.StartClock.Enable()
            else:
                self.StartClock.Disable()
        elif mode == 'auto_shutdown':
            if state:
                self.ShutdClock.Enable()
            else:
                self.ShutdClock.Disable()
        else:
            raise ValueError('Mode must be one of "auto_start" or "auto_shutdown"')
        
        self.ConfigSettings.Settings[mode]['enabled'] = state
                
    def ShowEditor(self, Mode: str) -> None:
        if Mode not in ['auto_start', 'auto_shutdown']:
            raise ValueError('Mode must be one of "auto_start" or "auto_shutdown"')
        
        self.__EditMode = Mode
        self.__EditGroup.LoadPattern(self.ConfigSettings.Settings[Mode]['pattern'])
        self.UIHost.ShowPopup(self.__EditPage)
        
    def SaveEditor(self) -> None:
        currentPattern = {
            "days": [],
            "time": {}
        }
        currentPattern['days'] = [btn.day for btn in self.__EditGroup.GetActive()]
        currentPattern['time'] = self.__EditGroup.GetTime()
        
        self.ConfigSettings.Settings[self.__EditMode]['pattern'] = currentPattern
        if self.__EditMode == 'auto_start':
            self.StartClock.SetDays(currentPattern['days'])
            self.StartClock.SetTimes([self.__TimeConverter(currentPattern['time'])])
        elif self.__EditMode == 'auto_shutdown':
            self.ShutdClock.SetDays(currentPattern['days'])
            self.ShutdClock.SetTimes([self.__TimeConverter(currentPattern['time'])])
        
        self.UpdateTechPage(force=True)
            
        self.__EditMode = None
        self.UIHost.HidePopup(self.__EditPage)
    
    def CancelEditor(self) -> None:
        self.__EditMode = None
        self.UpdateTechPage(force=True)
        self.UIHost.HidePopup(self.__EditPage)

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

def ScheduleToggleHandler(source: 'ButtonEx', event: str) -> None:
    uiDev = source.UIHost
    
    uiDev.ScheduleCtl.UpdateClockState(source.mode, bool(source.State))
    uiDev.ScheduleCtl.UpdateTechPage(force=True)

def ScheduleEditHandler(source: 'ButtonEx', event: str) -> None:
    uiDev = source.UIHost
    
    uiDev.ScheduleCtl.ShowEditor(source.mode)

def ScheduleModeHandler(source: 'ButtonEx', event: str) -> None:
    uiDev = source.UIHost
    
    uiDev.ScheduleCtl.ConfigSettings.Settings['auto_start']['mode'] = source.value
    uiDev.ScheduleCtl.UpdateTechPage(force=True)

def ScheduleDayHandler(source: 'ButtonEx', event: str) -> None:
    uiDev = source.UIHost
    
    uiDev.ScheduleCtl.UpdateEditor()

def ScheduleAllDaysHandler(source: 'ButtonEx', event: str) -> None:
    uiDev = source.UIHost
    daysGroup = source.Group
    
    daysGroup.SetActive('All')
    uiDev.ScheduleCtl.UpdateEditor()

def ScheduleWeekDaysHandler(source: 'ButtonEx', event: str) -> None:
    uiDev = source.UIHost
    daysGroup = source.Group
    
    daysGroup.SetActive(None)
    daysGroup.SetActive(['Schedule-Mon',
                         'Schedule-Tue',
                         'Schedule-Wed',
                         'Schedule-Thu',
                         'Schedule-Fri'])
    uiDev.ScheduleCtl.UpdateEditor()

def ScheduleTimeHandler(source: 'ButtonEx', event: str) -> None:
    uiDev = source.UIHost
    
    uiDev.ScheduleCtl.UpdateEditorTime(source.mode, source.Offset)
    uiDev.ScheduleCtl.UpdateEditor()

def ScheduleAmPmHandler(source: 'ButtonEx', event: str) -> None:
    uiDev = source.UIHost
    
    uiDev.ScheduleCtl.UpdateEditor()

def ScheduleSaveHandler(source: 'ButtonEx', event: str) -> None:
    uiDev = source.UIHost
    uiDev.ScheduleCtl.SaveEditor()

def ScheduleCancelHandler(source: 'ButtonEx', event: str) -> None:
    uiDev = source.UIHost
    uiDev.ScheduleCtl.CancelEditor()

## End Function Definitions ----------------------------------------------------



