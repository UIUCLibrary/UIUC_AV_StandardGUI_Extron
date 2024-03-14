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
    from modules.project.Collections import DeviceCollection, AlertCollection
    from modules.project.ExtendedSystemClasses import ExTimer

#### Python imports

#### Extron Library Imports

#### Project imports
from modules.helper.CommonUtilities import Logger, TimeIntToStr
from modules.project.ExtendedDeviceClasses import ExProcessorDevice, ExUIDevice, ExEBUSDevice
from modules.project.Collections import UIDeviceCollection, ProcessorCollection
from modules.project.PrimitiveObjects import DictObj, SettingsObject
from modules.helper.ModuleSupport import WatchVariable
from modules.project.mixins import InitializeMixin
from control.ActivityController import ActivityController
from control.SourceController import SourceController
from control.PollController import PollingController
import Variables
import Constants

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class SystemController(InitializeMixin, object):
    def __init__(self, 
                 controlDevices: list,
                 systemDevices: 'DeviceCollection',
                 # expansionDevices: Union[str, List[str]]=None,
                 alerts: 'AlertCollection'
                 ) -> None:
        
        InitializeMixin.__init__(self, self.__Initialize)
        
        # separate processor devices from UI devices for instantiating later
        processors = []
        uiDevices = []
        for dev in controlDevices:
            if dev.part_number in ExProcessorDevice.validation_part_list:
                processors.append(dev)
            elif dev.part_number in ExUIDevice.validation_part_list or dev.part_number in ExEBUSDevice.validation_part_list:
                uiDevices.append(dev)
            else:
                Logger.Log('Control Device part number not validated.', dev, separator='\n', logSeverity='warning')
        
        ## Begin Settings Properties -------------------------------------------
        
        self.RoomName = Variables.ROOM_NAME
        self.ActivityModes = Variables.SYSTEM_ACTIVITIES
        self.Timers = DictObj({'Startup': Variables.STARTUP_TIMER_DUR,
                               'StartupMin': Variables.STARTUP_TIMER_MIN,
                               'Switch': Variables.SWITCH_TIMER_DUR,
                               'Shutdown': Variables.SHUTDOWN_TIMER_DUR,
                               'ShutdownMin': Variables.SHUTDOWN_TIMER_MIN,
                               'ShutdownConf': Variables.SHUTDOWN_CONF_TIMER_DUR,
                               'ActivityTip': Variables.TIP_TIMER_DUR,
                               'SplashPage': Variables.SPLASH_INACTIVITY_TIMER_DUR
                              })
        
        self.SystemPIN = Variables.PIN_SYSTEM
        self.TechPIN = Variables.PIN_TECH
        
        self.Devices = systemDevices
        self.Devices.SystemHost = self
        self.Alerts = alerts
        self.Alerts.SystemHost = self
        
        self.DefaultSourceId = Variables.DEFAULT_SOURCE
        self.DefaultCameraId = Variables.DEFAULT_CAMERA
        
        self.PrimaryDestinationId = Variables.PRIMARY_DEST
        self.PrimarySwitcherId = Variables.PRIMARY_SW
        self.PrimaryDSPId = Variables.PRIMARY_DSP
        
        self.CameraSwitcherId = Variables.CAMERA_SW
        
        # Non-volitile Settings
        self.RoomScheduleConfig = SettingsObject(Variables.SETTINGS_ROOM_SCHEDULE)
        self.CameraPresetConfig = SettingsObject(Variables.SETTINGS_CAMERA_PRESETS)
        
        # System Properties
        self.SystemActivityWatch = WatchVariable("System Activity Mode")
        self.__SystemActivity = Constants.ActivityMode.Standby
        self.__NewSystemActivity = None
        self.__ActivityTransition = False
        
        self.SystemStateWatch = WatchVariable("System State")
        self.__SystemState = Constants.SystemState.Standby
        self.__NewSystemState = None
        self.__SystemStateTransition = False

        ## Processor Definition ------------------------------------------------
        self.Processors = ProcessorCollection()
        for p in processors:
            self.Processors.append(ExProcessorDevice(p.alias, p.part_number))

        if len(self.Processors) == 0:
            raise ValueError('No valid control processors provided.')
        elif hasattr(Variables, 'PRIMARY_PROC') and Variables.PRIMARY_PROC is not None:
            self.Proc_Main = [proc for proc in self.Processors if proc.Id == Variables.PRIMARY_PROC][0]
        else:
            self.Proc_Main = self.Processors[0]
        
        ## UI Device Definition ----------------------------------------------
        self.UIDevices = UIDeviceCollection()
        for ui in uiDevices:
            if dev.part_number in ExUIDevice.validation_part_list:
                self.UIDevices.append(ExUIDevice(ui.alias,
                                                 ui.ui.ui_config,
                                                 ui.part_number,
                                                 ui.name,
                                                 ui.extron_control_web_id))
            elif dev.part_number in ExEBUSDevice.validation_part_list:
                host = [proc for proc in self.Processors if proc.Id == ui.host_alias][0]
                self.UIDevices.append(ExEBUSDevice(host,
                                                   ui.ui.ui_config,
                                                   ui.alias,
                                                   ui.name,
                                                   ui.extron_control_web_id))
        
        if len(self.UIDevices) == 0:
            self.UI_Main = None
        elif hasattr(Variables, 'PRIMARY_UI') and Variables.PRIMARY_UI is not None:
            self.UI_Main = [panel for panel in self.UIDevices if panel.Id == Variables.PRIMARY_UI][0]
        else:
            self.UI_Main = self.UIDevices[0]
        
        Logger.CreateLoadingLabels(self.UI_Main)
        ## Expansion Device Definition -----------------------------------------
        
        # if type(expansionDevices) is str:
        #     self.ExpansionDevices = [ExSPDevice(self, expansionDevices)]
        # elif type(expansionDevices) is list:
        #     self.ExpansionDevices = []
        #     for exp in expansionDevices:
        #         if type(exp) is str:
        #             self.ExpansionDevices.append(ExSPDevice(self, exp))
        #         else:
        #             raise TypeError(type(self).GetErrorStr('E1', 'epansionDevices', exp, type(exp)))
        # else:
        #     raise TypeError(type(self).GetErrorStr('E1', 'expansionDevices', expansionDevices, type(expansionDevices)))
            
        ## Create System controllers
        self.ActCtl = ActivityController(self)
        self.SrcCtl = SourceController(self)
        self.PollCtl = PollingController(self)
        
        ## End of GUIController Init ___________________________________________

    @property
    def SystemActivity(self) -> Constants.ActivityMode:
        return self.__SystemActivity
    
    @SystemActivity.setter
    def SystemActivity(self, val: Union[Constants.ActivityMode, str, int]) -> None:
        Logger.Log("Setting SystemActivity:", val)
        if type(val) is Constants.ActivityMode:
            enumVal = val
        elif isinstance(val, int):
            enumVal = Constants.ActivityMode(val)
        elif isinstance(val, str):
            enumVal = Constants.ActivityMode[val]
        else:
            raise TypeError('val must be a str, int, or ActivityMode Enum')
        
        Logger.Log(enumVal, self.__SystemActivity, enumVal != self.__SystemActivity)
        if enumVal != self.__SystemActivity:
            self.__NewSystemActivity = enumVal
            self.__ActivityTransition = True
            if self.__NewSystemActivity in Constants.ACTIVE and self.SystemState is Constants.SystemState.Standby:
                self.__NewSystemState = Constants.SystemState.Active
                self.__SystemStateTransition = True
            elif self.__NewSystemActivity in Constants.STANDBY and self.SystemState is Constants.SystemState.Active:
                self.__NewSystemState = Constants.SystemState.Standby
                self.__SystemStateTransition = True
            
            
            self.ActCtl.SystemModeChangeHandler(self.TransitionState)
            
    @property
    def SystemState(self) -> Constants.SystemState:
        return self.__SystemState
    
    @SystemState.setter
    def SystemState(self, val) -> None:
        raise AttributeError('Setting SystemState is disallowed.')

    @property
    def TransitionState(self) -> Tuple[Tuple[bool, Constants.SystemState], Tuple[bool, Constants.ActivityMode]]:
        return ((self.__SystemStateTransition, self.__NewSystemState), (self.__ActivityTransition, self.__NewSystemActivity))
    
    @TransitionState.setter
    def TransitionState(self, val) -> None:
        raise AttributeError('Setting TransitionState is disallowed')
    
    def ActivityTransitionComplete(self) -> None:
        Logger.Log('Activity Mode Change: {} Complete'.format(self.__NewSystemActivity.name))
        self.__SystemActivity = self.__NewSystemActivity
        self.__NewSystemActivity = None
        self.__ActivityTransition = False
        self.SystemActivityWatch.Change(self.__SystemActivity)

    def __Initialize(self) -> None:
        ## GUI Display Initialization ------------------------------------------
        for uiDev in self.UIDevices:
            uiDev.Initialize()
        
        ## Device Initialization -----------------------------------------------
        self.Devices.Initialize()        
        
        ## Initialize Controllers ----------------------------------------------
        self.PollCtl.Initialize()
        self.SrcCtl.Initialize()
        self.ActCtl.Initialize()
        
        ## Intialize Other Objects ---------------------------------------------
        self.Alerts.Initialize()
        
        Logger.Log('System Initialized')
        for uiDev in self.UIDevices:
            uiDev.ShowPage('Splash')
            uiDev.BlinkLights(Rate='Fast', StateList=['Green', 'Red'], Timeout=2.5)
            uiDev.Click(5, 0.2)
            Variables.Loading = False
        
    def ShowStart(self) -> None:
        self.ActCtl.Timers.Splash.Restart()
        for uiDev in self.UIDevices:
            uiDev.ShowPage('Start')
    
    def SystemActiveInit(self) -> None:
        self.PollCtl.SetPollingMode('active')
        self.ActCtl.Timers.Splash.Stop()
        # self.SrcCtl.Privacy = 'off'
        # self.TP_Main.CamCtl.SendCameraHome()
        # self.TP_Main.AudioCtl.AudioStartUp()
        # for tp in self.TPs:
        #     tp.HdrCtl.ConfigSystemOn()
        #     tp.CamCtl.SelectDefaultCamera()
            
        # Bring switches out of standby and turn off video mute
        for switch in self.Devices.Switches:
            Logger.Log(switch)
            if 'Standby' in switch.interface.Commands:
                Logger.Log('Has Standby')
                switch.interface.Set('Standby', False)
            
            if 'VideoMute' in switch.interface.Commands:
                Logger.Log('Has VideoMute')
                switch.interface.Set('VideoMute', 'Off')
                
        # # power on displays
        for dest in self.Devices.Destinations:
            Logger.Log(dest)
            if hasattr('dest', 'PowerCommand'):
                dest.interface.Set(dest.PowerCommand['command'], 
                                   'on', 
                                   dest.PowerCommand['qualifer'] if 'qualifer' in dest.PowerCommand else None)
    
    def SystemActiveTransition(self, timer, count) -> None:
        timeRemaining = self.Timers.Startup - count
        for uiDev in self.UIDevices:
            uiDev.Interface.Transition.Count.SetText(TimeIntToStr(timeRemaining))
            uiDev.Interface.Transition.Level.SetLevel(count)
            
        destStatus = True
        # for dest in self.GUIHost.Destinations:
        #     if dest['type'] not in ['conf']:
        #         self.GUIHost.Hardware[dest['id']].interface.Update('Power')
        #         curStatus = self.GUIHost.Hardware[dest['id']].interface.ReadStatus('Power')
        #         if curStatus not in ['On', 'on', 'Power On', 'ON', 'Power on', 'POWER ON']:
        #             destStatus = False
        
        if destStatus and count > self.Timers.StartupMin:
            timer.Wrapup()
    
    def SystemActiveComplete(self, timer, count) -> None:
        self.ActCtl.SystemActivityChange(self.__NewSystemActivity)
        Logger.Log('System Mode Change: Active Complete')
        self.__SystemState = Constants.SystemState.Active
        self.__NewSystemState = None
        self.__SystemStateTransition = False
        self.SystemStateWatch.Change(self.__SystemState)
    
    def SystemStandbyInit(self) -> None:
        self.PollCtl.SetPollingMode('inactive')
        
        for uiDev in self.UIDevices:
            # reset source selection menu offset
            uiDev.Interface.Objects.ControlGroups['Source-Select'].SetOffset(0)
        
        # if self.Hardware[self.PrimarySwitcherId].Manufacturer == 'AMX' and self.Hardware[self.PrimarySwitcherId].Model in ['N2300 Virtual Matrix']:
        #     # Put SVSI ENC endpoints in to standby mode
        #     self.Hardware[self.PrimarySwitcherId].interface.Set('Standby', 'On', None)
        #     # Ensure SVSI DEC endpoints are muted
        #     self.Hardware[self.PrimarySwitcherId].interface.Set('VideoMute', 'Video & Sync', None)
                
        # # power off displays
        # for dest in self.Destinations:
        #     try:
        #         self.TP_Main.DispCtl.SetDisplayPower(dest['Id'], 'Off')
        #     except LookupError:
        #         # display does not have hardware to power on or off
        #         pass
        
        # self.SrcCtl.MatrixSwitch(0, 'All', 'untie')
        # self.TP_Main.AudioCtl.AudioShutdown()
        # for tp in self.TPs:
        #     tp.HdrCtl.ConfigSystemOff()
        
        # for id, hw in self.Hardware.items():
        #     if id.startswith('WPD'):
        #         hw.interface.Set('BootUsers', value=None, qualifier=None)
    
    def SystemStandbyTransition(self, timer, count) -> None:
        timeRemaining = self.Timers.Shutdown - count

        for uiDev in self.UIDevices:
            uiDev.Interface.Transition.Count.SetText(TimeIntToStr(timeRemaining))
            uiDev.Interface.Transition.Level.SetLevel(count)

        destStatus = True
        # for dest in self.GUIHost.Destinations:
        #     if dest['type'] not in ['conf']:
        #         self.GUIHost.Hardware[dest['id']].interface.Update('Power')
        #         curStatus = self.GUIHost.Hardware[dest['id']].interface.ReadStatus('Power')
        #         if curStatus not in ['Off', 'off', 'Power Off', 'Standby (Power Save)', 'Suspend (Power Save)', 'OFF', 'Power off', 'POWER OFF']:
        #             destStatus = False
        
        if count >= (self.Timers.Shutdown - 5) or (destStatus is True and count > self.Timers.ShutdownMin):
            # if self.Hardware[self.PrimarySwitcherId].Manufacturer == 'AMX' and self.Hardware[self.PrimarySwitcherId].Model in ['N2300 Virtual Matrix']:
            #     # Put SVSI ENC endpoints in to standby mode
            #     self.Hardware[self.PrimarySwitcherId].interface.Set('Standby', 'On', None)
            #     # Ensure SVSI DEC endpoints are muted
            #     self.Hardware[self.PrimarySwitcherId].interface.Set('VideoMute', 'Video & Sync', None)
            Logger.Debug('Testing: Put AVoIP Switching Hardware into standby')
        
        if count >= self.Timers.Shutdown or (destStatus is True and count > self.Timers.ShutdownMin):
            # self.SrcCtl.MatrixSwitch(0, 'All', 'untie')
            Logger.Debug('Untie matrix switcher')
            
        if destStatus and count > self.Timers.ShutdownMin:
            timer.Wrapup()
    
    def SystemStandbyComplete(self, timer, count) -> None:
        for uiDev in self.UIDevices:
            uiDev.HidePopup('Power-Transition')
        
        Logger.Log('System Mode Change: Standby Complete', self.__SystemActivity)
        self.__SystemActivity = self.__NewSystemActivity
        self.__NewSystemActivity = None
        self.__ActivityTransition = False
        self.__SystemState = Constants.SystemState.Standby
        self.__NewSystemState = None
        self.__SystemStateTransition = False
        self.SystemStateWatch.Change(self.__SystemState)
        self.ActCtl.Timers.Splash.Restart()
        
        
    def SplashChecker(self, timer: 'ExTimer', count: int) -> None:
        elapsedTime = timer.Interval * count
        inactivities = {}
        reset = False
        for uiDev in self.UIDevices:
            inactivities[uiDev.Id] = uiDev.InactivityTime
            if uiDev.InactivityTime < elapsedTime:
                reset = True
        if reset:
            timer.Restart()
    
    def ShowSplash(self, timer = None, count = None) -> None:
        for uiDev in self.UIDevices:
            uiDev.ShowPage('Splash')