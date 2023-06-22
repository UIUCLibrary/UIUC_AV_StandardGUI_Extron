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

from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import SystemController
    from uofi_gui.uiObjects import ExUIDevice
    from modules.project.Collections import DeviceCollection

## Begin ControlScript Import --------------------------------------------------

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from modules.helper.UtilityFunctions import DictValueSearchByKey, RunAsync, debug
from modules.project.ExtendedClasses import ExProcessorDevice
from modules.project.Collections import DictObj
from modules.project.ExtendedClasses import ExUIDevice, ExSPDevice
from control.PollController import PollingController

from modules.helper.UtilityFunctions import Logger


from uofi_gui.activityControls import ActivityController
from DevelopmentProject.src.modules.project.systemHardware import SystemHardwareController, VirtualDeviceInterface

## End User Import -------------------------------------------------------------
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
                 settings: object,
                 systemDevices: 'DeviceCollection',
                 processors: Union[str, List[str]], 
                 uiDevices: Union[Tuple[str, ...], List[Tuple[str, ...]]]=None,
                 expansionDevices: Union[str, List[str]]=None) -> None:
        
        
        Logger.Log('Processors: {}'.format(processors), 'UI Devices: {}'.format(uiDevices), 'Expansion Devices: {}'.format(expansionDevices), sep=' - ')
        
        ## Begin Settings Properties -------------------------------------------
        
        self.RoomName = settings.ROOM_NAME
        self.ActivityMode = settings.ACTIVITY_MODE
        self.Timers = DictObj({'startup': settings.START_UP_TIMER_DUR,
                                'switch': settings.SWITCH_TIMER_DUR,
                                'shutdown': settings.SHUTDOWN_TIMER_DUR,
                                'shutdownConf': settings.SHUTDOWN_CONF_TIMER_DUR,
                                'activityTip': settings.TIP_TIMER_DUR,
                                'initPage': settings.SPLASH_INACTIVITY_TIMER_DUR
                             })
        
        self.SystemPIN = settings.PIN_SYSTEM
        self.TechPIN = settings.PIN_TECH
        
        self.Devices = systemDevices
        
        self.DefaultSourceId = settings.DEFAULT_SOURCE
        self.DefaultCameraId = settings.DEFAULT_CAMERA
        
        self.PrimaryDestinationId = settings.PRIMARY_DEST
        self.PrimarySwitcherId = settings.PRIMARY_SW
        self.PrimaryDSPId = settings.PRIMARY_DSP
        
        self.CameraSwitcherId = settings.CAMERA_SW
        
        # System Properties
        self.SystemActivity = 'off'

        ## Processor Definition ------------------------------------------------
        if type(processors) is str:
            self.Processors = [ExProcessorDevice(processors)]
        elif type(processors) is list:
            self.Processors = []
            for p in processors:
                if type(p) is str:
                    self.Processors.append(ExProcessorDevice(p))
                else:
                    raise TypeError(type(self).GetErrorStr('E1','processors', p, type(p)))
        else: 
            raise TypeError(type(self).GetErrorStr('E1',
                                                   'processors', 
                                                   processors, 
                                                   type(processors)))

        if len(self.Processors) == 0:
            raise ValueError(type(self).GetErrorStr('E2'))
        elif hasattr(settings, 'PRIMARY_PROC') and settings.PRIMARY_PROC is not None:
            self.Proc_Main = [proc for proc in self.Processors if proc.Id == settings.PRIMARY_PROC][0]
        else:
            self.Proc_Main = self.Processors[0]
        
        ## UI Device Definition ----------------------------------------------
        
        if type(uiDevices) is tuple:
            self.UIDevices = [ExUIDevice(self, **uiDevices)]
        elif type(uiDevices) is list:
            self.UIDevices = []
            for ui in uiDevices:
                if type(ui) is tuple:
                    self.UIDevices.append(ExUIDevice(self, **uiDevices))
                else:
                    raise TypeError(type(self).GetErrorStr('E3','uiDevices', ui, type(ui)))
        else:
            raise TypeError(type(self).GetErrorStr('E3','uiDevices', uiDevices, type(uiDevices)))
        
        # TODO: Assign UI Controller to UI devices
        
        if len(self.UIDevices) == 0:
            self.UI_Main = None
        elif hasattr(settings, 'PRIMARY_UI') and settings.PRIMARY_UI is not None:
            self.UI_Main = [panel for panel in self.UIDevices if panel.Id == settings.PRIMARY_UI][0]
        else:
            self.UI_Main = self.UIDevices[0]
        
        ## Expansion Device Definition -----------------------------------------
        
        if type(expansionDevices) is str:
            self.ExpansionDevices = [ExSPDevice(self, expansionDevices)]
        elif type(expansionDevices) is list:
            self.ExpansionDevices = []
            for exp in expansionDevices:
                if type(exp) is str:
                    self.ExpansionDevices.append(ExSPDevice(self, exp))
                else:
                    raise TypeError(type(self).GetErrorStr('E1', 'epansionDevices', exp, type(exp)))
        else:
            raise TypeError(type(self).GetErrorStr('E1', 'expansionDevices', expansionDevices, type(expansionDevices)))
            
        ## Create System controllers
        self.PollCtl = PollingController()
        
        
        ## End of GUIController Init ___________________________________________

    def StartupActions(self) -> None:
        self.PollCtl.SetPollingMode('active')
        self.SrcCtl.Privacy = 'off'
        self.UI_Main.CamCtl.SendCameraHome()
        self.UI_Main.AudioCtl.AudioStartUp()
        for tp in self.UIDevices:
            tp.HdrCtl.ConfigSystemOn()
            tp.CamCtl.SelectDefaultCamera()
            
        if self.Hardware[self.PrimarySwitcherId].Manufacturer == 'AMX' and self.Hardware[self.PrimarySwitcherId].Model in ['N2300 Virtual Matrix']:
            # Take SVSI ENC endpoints out of standby mode
            self.Hardware[self.PrimarySwitcherId].interface.Set('Standby', 'Off', None)
            # Unmute SVSI DEC endpoints
            self.Hardware[self.PrimarySwitcherId].interface.Set('VideoMute', 'Off', None)
                
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
        
        if self.Hardware[self.PrimarySwitcherId].Manufacturer == 'AMX' and self.Hardware[self.PrimarySwitcherId].Model in ['N2300 Virtual Matrix']:
            # Put SVSI ENC endpoints in to standby mode
            self.Hardware[self.PrimarySwitcherId].interface.Set('Standby', 'On', None)
            # Ensure SVSI DEC endpoints are muted
            self.Hardware[self.PrimarySwitcherId].interface.Set('VideoMute', 'Video & Sync', None)
                
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
        
        for id, hw in self.Hardware.items():
            if id.startswith('WPD'):
                hw.interface.Set('BootUsers', value=None, qualifier=None)

    def ShutdownSyncedActions(self, count: int) -> None:
        pass

    def Initialize(self) -> None:
        ## Create Controllers --------------------------------------------------
        self.ActCtl = ActivityController(self)
        
        for tp in self.UIDevices:
            tp.InitializeUIControllers()
        
        self.SrcCtl = self.UI_Main.SrcCtl
        
        # Log('Source List: {}'.format(self.Sources))
        # Log('Destination List: {}'.format(self.Destinations))
        
        ## GUI Display Initialization ------------------------------------------
        self.UI_Main.ShowPage('Splash')
        self.UI_Main.Btns['Room-Label'].SetText(self.RoomName)
        for tp in self.UIDevices:
            tp.SrcCtl.UpdateDisplaySourceList()
        
        ## Associate Virtual Hardware ------------------------------------------
        # Log('Looking for Virtual Device Interfaces')
        for Hw in self.Hardware.values():
            # Log('Hardware ({}) - Interface Class: {}'.format(id, type(Hw.interface)))
            if issubclass(type(Hw.interface), VirtualDeviceInterface):
                Hw.interface.FindAssociatedHardware()
                # Log('Hardware Found for {}. New IO Size: {}'.format(Hw.Name, Hw.interface.MatrixSize))
        
        #### Start Polling
        self.PollCtl.PollEverything()
        self.PollCtl.StartPolling()
        
        Logger.Log('System Initialized')
        for tp in self.UIDevices:
            tp.BlinkLights(Rate='Fast', StateList=['Green', 'Red'], Timeout=2.5)
            tp.Click(5, 0.2)
            
    @classmethod
    def GetErrorStr(cls, Error: str, *args, **kwargs):
        return cls.errorMap[Error].format(*args, **kwargs)