## Begin ControlScript Import --------------------------------------------------
from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
    DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
    EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
    RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
    VolumeInterface)
from extronlib.ui import Button, Knob, Label, Level, Slider
from extronlib.system import (Email, Clock, MESet, Timer, Wait, File, RFile,
    ProgramLog, SaveProgramLog, Ping, WakeOnLan, SetAutomaticTime, SetTimeZone)

print(Version()) ## Sanity check ControlScript Import
## End ControlScript Import ----------------------------------------------------
##

from typing import Dict, Tuple, List, Callable, Union

from utilityFunctions import Log, RunAsync, debug

from uofi_gui.uiObjects import ExUIDevice
from uofi_gui.systemHardware import (SystemHardwareController,
                                     SystemPollingController, 
                                     VirtualDeviceInterface)

class ExProcessorDevice(ProcessorDevice):
    def __init__(self, DeviceAlias: str, PartNumber: str = None) -> object:
        super().__init__(DeviceAlias, PartNumber)
        self.Id = DeviceAlias

class GUIController:
    errorMap = \
        {
            'E1': '{} must be a string device alias or a list of string device alaises. {} ({}) provided'
        }
    
    @classmethod
    def GetErrorStr(cls, Error: str, *args, **kwargs):
        return cls.errorMap[Error].format(*args, **kwargs)
    
    def __init__(self, 
                 Settings: object,
                 CtlProcs: Union[str, List], 
                 TouchPanels: Union[str, List]=None,
                 ButtonPanels: Union[str, List]=None) -> None:
        ## Begin Settings Properties -------------------------------------------
        
        self.CtlJSON = Settings.ctlJSON
        self.RoomName = Settings.roomName
        self.ActivityMode = Settings.activityMode
        self.Timers = \
            {
                'startup': Settings.startupTimer,
                'switch': Settings.switchTimer,
                'shutdown': Settings.shutdownTimer,
                'shutdownConf': Settings.shutdownConfTimer,
                'activitySplash': Settings.activitySplashTimer,
            }
            
        self.TechMatrixSize = Settings.techMatrixSize
        self.TechPIN = Settings.techPIN
        
        self.CameraSwitcherId = Settings.camSwitcher
            
        self.Sources = Settings.sources
        self.Destinations = Settings.destinations
        self.Cameras = Settings.cameras
        self.Microphones = Settings.microphones
        self.Lights = Settings.lights
        
        self.DefaultSourceId = Settings.defaultSource
        self.DefaultCameraId = Settings.defaultCamera
        
        self.PrimaryDestinationId = Settings.primaryDestination
        self.PrimarySwitcherId = Settings.primarySwitcher
        self.PrimaryDSPId = Settings.primaryDSP
        
        # TODO: Other settings go here

        ## Processor Definition ------------------------------------------------
        if type(CtlProcs) is str:
            self.CtlProcs = [ExProcessorDevice(CtlProcs)]
        elif type(CtlProcs) is list:
            self.CtlProcs = []
            for p in CtlProcs:
                if type(p) is not str:
                    raise TypeError(type(self).GetErrorStr('E1','CtlProcs', p, type(p)))
                self.CtlProcs.append(ExProcessorDevice(p))
        else: 
            raise TypeError(type(self).GetErrorStr('E1',
                                                   'CtlProcs', 
                                                   CtlProcs, 
                                                   type(CtlProcs)))

        if hasattr(Settings, 'primaryProcessor'):
            self.CtlProc_Main = [proc for proc in self.CtlProcs if proc.Id == Settings.primaryProcessor][0]
        else:
            self.CtlProc_Main = self.CtlProcs[0]
        
        ## Poll Control Module - needs to exist before creating hardware controllers
        self.PollCtl = SystemPollingController()

        ## Create Hardware interfaces ------------------------------------------
        self.Hardware = {}
        for hw in Settings.hardware:
            self.Hardware[hw['Id']] = SystemHardwareController(self, **hw)
        
        ## Touch Panel Definition ----------------------------------------------
        
        if type(TouchPanels) is str:
            tp = ExUIDevice(TouchPanels)
            tp.BuildAll(jsonPath=self.CtlJSON)
            self.TPs = [tp]
        elif type(TouchPanels) is list:
            self.TPs = []
            for tp in TouchPanels:
                if type(tp) is not str:
                    raise TypeError(type(self).GetErrorStr('E1','TPs', tp, type(tp)))
                panel = ExUIDevice(self, tp)
                panel.BuildAll(jsonPath=self.CtlJSON)
                self.TPs.append(panel)
        else:
            raise TypeError(type(self).GetErrorStr('E1','TPs', TouchPanels, type(TouchPanels)))
        
        if hasattr(Settings, 'primaryTouchPanel'):
            self.TP_Main = [panel for panel in self.TPs if panel.Id == Settings.primaryTouchPanel][0]
        else:
            self.TP_Main = self.TPs[0]
        
        ## Button Panel Definition ---------------------------------------------
        # TODO: button panel init
        
        ## Create Controllers --------------------------------------------------
        
        self.ActCtl = self.TP_Main.ActCtl
        
        self.SrcCtl = self.TP_Main.SrcCtl
        
        Log('Source List: {}'.format(self.Sources))
        Log('Destination List: {}'.format(self.Destinations))
        
        # self.HdrCtl = self.TP_Main.HdrCtl
        
        # self.TechCtl = self.TP_Main.TechCtl
        
        # self.StatusCtl = self.TP_Main.StatusCtl
        
        # self.CamCtl = self.TP_Main.CamCtl
        
        ## End of GUIController Init ___________________________________________

    def StartupActions(self) -> None:
        self.PollCtl.SetPollingMode('active')
        self.HdrCtl.ConfigSystemOn()
        self.SrcCtl.SetPrivacyOff()
        self.CamCtl.SelectDefaultCamera()
        self.CamCtl.SendCameraHome()
        self.AudioCtl.AudioStartUp()

    def StartupSyncedActions(self, count: int) -> None:
        pass

    def SwitchActions(self) -> None:
        self.SrcCtl.UpdateSourceMenu()
        self.SrcCtl.ShowSelectedSource()

    def SwitchSyncedActions(self, count: int) -> None:
        pass

    def ShutdownActions(self) -> None:
        self.PollCtl.SetPollingMode('inactive')
        self.HdrCtl.ConfigSystemOff()
        self.SrcCtl.MatrixSwitch(0, 'All', 'untie')
        self.AudioCtl.AudioShutdown()
        
        # for id, hw in self.Hardware:
        #     if id.startswith('WPD'):
        #         hw.interface.Set('BootUsers', value=None, qualifier=None)

    def ShutdownSyncedActions(self, count: int) -> None:
        pass

    def Initialize(self) -> None:
        #### Set initial page & room name
        self.TP_Main.HideAllPopups()
        self.TP_Main.ShowPage('Splash')
        self.TP_Main.Btns['Room-Label'].SetText(self.RoomName)
        
        ## DO ADDITIONAL INITIALIZATION ITEMS HERE
        
        # Associate Virtual Hardware
        # utFn.Log('Looking for Virtual Device Interfaces')
        for Hw in self.Hardware.values():
            # utFn.Log('Hardware ({}) - Interface Class: {}'.format(id, type(Hw.interface)))
            if issubclass(type(Hw.interface), VirtualDeviceInterface):
                Hw.interface.FindAssociatedHardware()
                # utFn.Log('Hardware Found for {}. New IO Size: {}'.format(Hw.Name, Hw.interface.MatrixSize))
        
        #### Start Polling
        self.PollCtl.PollEverything()
        self.PollCtl.StartPolling()
        
        Log('System Initialized')
        self.TP_Main.BlinkLights(Rate='Fast', StateList=['green', 'red'])
        self.TP_Main.Click(5, 0.2)
        @Wait(3)
        def StopTPLight():
            self.TP_Main.LightsOff()