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
    from modules.helper.Collections import DeviceCollection

#### Python imports
from os.path import splitext

#### Extron Library Imports

#### Project imports
from modules.helper.CommonUtilities import Logger, DictValueSearchByKey, RunAsync, debug
from modules.helper.ExtendedDeviceClasses import ExProcessorDevice, ExUIDevice, ExSPDevice, ExEBUSDevice
from modules.helper.Collections import DictObj
from control.PollController import PollingController
import Variables

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class SystemController:
    errorMap = \
        {
            'E1': '{} must be a string device alias or a list of string device alaises. {} ({}) provided',
            'E2': 'No valid control processors provided.',
            'E3': '{} must be a tuple of device alias and uiLayout name or a list of these tuples. {} ({}) provided'
        }
    
    def __init__(self, 
                #  settings: object,
                 controlDevices: list,
                 systemDevices: 'DeviceCollection',
                #  expansionDevices: Union[str, List[str]]=None
                 ) -> None:
        
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
        
        Logger.Log('Processors: {}'.format(processors), 
                   'UI Devices: {}'.format(uiDevices), 
                   # 'Expansion Devices: {}'.format(expansionDevices), 
                   separator=' - ')
        Logger.Log(systemDevices)
        
        ## Begin Settings Properties -------------------------------------------
        
        self.RoomName = Variables.ROOM_NAME
        self.ActivityModes = Variables.SYSTEM_ACTIVITIES
        self.Timers = DictObj({'startup': Variables.STARTUP_TIMER_DUR,
                               'switch': Variables.SWITCH_TIMER_DUR,
                               'shutdown': Variables.SHUTDOWN_TIMER_DUR,
                               'shutdownConf': Variables.SHUTDOWN_CONF_TIMER_DUR,
                               'activityTip': Variables.TIP_TIMER_DUR,
                               'initPage': Variables.SPLASH_INACTIVITY_TIMER_DUR
                              })
        
        self.SystemPIN = Variables.PIN_SYSTEM
        self.TechPIN = Variables.PIN_TECH
        
        self.Devices = systemDevices
        
        self.DefaultSourceId = Variables.DEFAULT_SOURCE
        self.DefaultCameraId = Variables.DEFAULT_CAMERA
        
        self.PrimaryDestinationId = Variables.PRIMARY_DEST
        self.PrimarySwitcherId = Variables.PRIMARY_SW
        self.PrimaryDSPId = Variables.PRIMARY_DSP
        
        self.CameraSwitcherId = Variables.CAMERA_SW
        
        # System Properties
        self.SystemActivity = 'off'

        ## Processor Definition ------------------------------------------------
        self.Processors = []
        for p in processors:
            self.Processors.append(ExProcessorDevice(p.alias, p.part_number))

        if len(self.Processors) == 0:
            raise ValueError(type(self).GetErrorStr('E2'))
        elif hasattr(Variables, 'PRIMARY_PROC') and Variables.PRIMARY_PROC is not None:
            self.Proc_Main = [proc for proc in self.Processors if proc.Id == Variables.PRIMARY_PROC][0]
        else:
            self.Proc_Main = self.Processors[0]
        
        ## UI Device Definition ----------------------------------------------
        self.UIDevices = []
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
        self.PollCtl = PollingController(self.Devices)
        
        
        ## End of GUIController Init ___________________________________________

    def StartupActions(self) -> None:
        self.PollCtl.SetPollingMode('active')
        self.SrcCtl.Privacy = 'off'
        self.UI_Main.CamCtl.SendCameraHome()
        self.UI_Main.AudioCtl.AudioStartUp()
        for tp in self.UIDevices:
            tp.HdrCtl.ConfigSystemOn()
            tp.CamCtl.SelectDefaultCamera()
            
        if self.Devices[self.PrimarySwitcherId].Manufacturer == 'AMX' and self.Devices[self.PrimarySwitcherId].Model in ['N2300 Virtual Matrix']:
            # Take SVSI ENC endpoints out of standby mode
            self.Devices[self.PrimarySwitcherId].interface.Set('Standby', 'Off', None)
            # Unmute SVSI DEC endpoints
            self.Devices[self.PrimarySwitcherId].interface.Set('VideoMute', 'Off', None)
                
        # power on displays
        for dest in self.Destinations:
            try:
                self.UI_Main.DispCtl.SetDisplayPower(dest['Id'], 'On')
            except LookupError:
                # display does not have hardware to power on or off
                pass

    def StartupSyncedActions(self, count: int) -> None:
        pass

    def SwitchActions(self) -> None:
        # set display sources
        for dest in self.Destinations:
            try:
                self.UI_Main.DispCtl.SetDisplaySource(dest['Id'])
            except LookupError:
                # display does not have hardware to power on or off
                pass
            
        for tp in self.UIDevices:
            tp.SrcCtl.ShowSelectedSource()

    def SwitchSyncedActions(self, count: int) -> None:
        pass

    def ShutdownActions(self) -> None:
        self.PollCtl.SetPollingMode('inactive')
        
        if self.Devices[self.PrimarySwitcherId].Manufacturer == 'AMX' and self.Devices[self.PrimarySwitcherId].Model in ['N2300 Virtual Matrix']:
            # Put SVSI ENC endpoints in to standby mode
            self.Devices[self.PrimarySwitcherId].interface.Set('Standby', 'On', None)
            # Ensure SVSI DEC endpoints are muted
            self.Devices[self.PrimarySwitcherId].interface.Set('VideoMute', 'Video & Sync', None)
                
        # power off displays
        for dest in self.Destinations:
            try:
                self.UI_Main.DispCtl.SetDisplayPower(dest['Id'], 'Off')
            except LookupError:
                # display does not have hardware to power on or off
                pass
        
        self.SrcCtl.MatrixSwitch(0, 'All', 'untie')
        self.UI_Main.AudioCtl.AudioShutdown()
        for tp in self.UIDevices:
            tp.HdrCtl.ConfigSystemOff()
        
        for id, hw in self.Devices.items():
            if id.startswith('WPD'):
                hw.interface.Set('BootUsers', value=None, qualifier=None)

    def ShutdownSyncedActions(self, count: int) -> None:
        pass

    def Initialize(self) -> None:
        ## Create Controllers --------------------------------------------------
        #self.ActCtl = ActivityController(self)
        
        for tp in self.UIDevices:
            tp.Interface.InitializeControlObjects()
        
        # self.SrcCtl = self.UI_Main.SrcCtl
        
        # Log('Source List: {}'.format(self.Sources))
        # Log('Destination List: {}'.format(self.Destinations))
        
        ## GUI Display Initialization ------------------------------------------
        self.UI_Main.ShowPage('Splash')
        # self.UI_Main.Btns['Room-Label'].SetText(self.RoomName)
        for tp in self.UIDevices:
            # tp.SrcCtl.UpdateDisplaySourceList()
            pass
        
        ## Associate Virtual Hardware ------------------------------------------
        # Log('Looking for Virtual Device Interfaces')
        for Hw in self.Devices.values():
            # Log('Hardware ({}) - Interface Class: {}'.format(id, type(Hw.interface)))
            # if issubclass(type(Hw.interface), VirtualDeviceInterface):
            #     Hw.interface.FindAssociatedHardware()
            #     # Log('Hardware Found for {}. New IO Size: {}'.format(Hw.Name, Hw.interface.MatrixSize))
            pass
        #### Start Polling
        self.PollCtl.PollEverything()
        self.PollCtl.SetPollingMode('inactive')
        
        Logger.Log('System Initialized')
        for tp in self.UIDevices:
            tp.BlinkLights(Rate='Fast', StateList=['Green', 'Red'], Timeout=2.5)
            tp.Click(5, 0.2)
            
    @classmethod
    def GetErrorStr(cls, Error: str, *args, **kwargs):
        return cls.errorMap[Error].format(*args, **kwargs)