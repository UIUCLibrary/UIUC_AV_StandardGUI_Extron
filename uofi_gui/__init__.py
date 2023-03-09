## Begin ControlScript Import --------------------------------------------------
from extronlib.device import ProcessorDevice
## End ControlScript Import ----------------------------------------------------

from typing import Dict, Tuple, List, Callable, Union

from utilityFunctions import Log, RunAsync, debug

from uofi_gui.uiObjects import ExUIDevice
from uofi_gui.activityControls import ActivityController
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
            'E1': '{} must be a string device alias or a list of string device alaises. {} ({}) provided',
            'E2': 'No valid control processors provided.'
        }
    
    def __init__(self, 
                 Settings: object,
                 CtlProcs: Union[str, List], 
                 TouchPanels: Union[str, List]=None,
                 ButtonPanels: Union[str, List]=None) -> None:
        ## Begin Settings Properties -------------------------------------------
        
        Log('CtlProcs: {}'.format(CtlProcs))
        Log('TouchPanels: {}'.format(TouchPanels))
        
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

        if len(self.CtlProcs) == 0:
            raise ValueError(type(self).GetErrorStr('E2'))
        elif hasattr(Settings, 'primaryProcessor'):
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
            tp = ExUIDevice(self, TouchPanels)
            tp.BuildAll(jsonPath=self.CtlJSON)
            tp.BlinkLights('Slow', ['red', 'off'])
            self.TPs = [tp]
        elif type(TouchPanels) is list:
            self.TPs = []
            for tp in TouchPanels:
                if type(tp) is not str:
                    raise TypeError(type(self).GetErrorStr('E1','TPs', tp, type(tp)))
                panel = ExUIDevice(self, tp)
                panel.BuildAll(jsonPath=self.CtlJSON)
                panel.BlinkLights('Slow', ['red', 'off'])
                self.TPs.append(panel)
                # Log(['Button: {} ({}, {})'.format(btn.Name, btn.ID, btn) for btn in panel.Btn_Grps['Activity-Select'].Objects])
        else:
            raise TypeError(type(self).GetErrorStr('E1','TPs', TouchPanels, type(TouchPanels)))
        
        # Log(['Button: {} ({}, {})'.format(btn.Name, btn.ID, btn) for btn in self.TPs[0].Btn_Grps['Activity-Select'].Objects])
        
        if len(self.TPs) == 0:
            Log('No touch panels designated')
            self.TP_Main = None
        elif hasattr(Settings, 'primaryTouchPanel'):
            Log('Set TP_Main by settings.primaryTouchPanel')
            self.TP_Main = [panel for panel in self.TPs if panel.Id == Settings.primaryTouchPanel][0]
        else:
            Log('Set TP_Main by index')
            self.TP_Main = self.TPs[0]
        # Log(['Button: {} ({}, {})'.format(btn.Name, btn.ID, btn) for btn in self.TP_Main.Btn_Grps['Activity-Select'].Objects])
        
        ## Button Panel Definition ---------------------------------------------
        # TODO: button panel init

        ## End of GUIController Init ___________________________________________

    def StartupActions(self) -> None:
        self.PollCtl.SetPollingMode('active')
        self.SrcCtl.SetPrivacyOff()
        self.TP_Main.CamCtl.SendCameraHome()
        self.TP_Main.AudioCtl.AudioStartUp()
        for tp in self.TPs:
            tp.HdrCtl.ConfigSystemOn()
            tp.CamCtl.SelectDefaultCamera()

    def StartupSyncedActions(self, count: int) -> None:
        pass

    def SwitchActions(self) -> None:
        for tp in self.TPs:
            tp.SrcCtl.ShowSelectedSource()
            # tp.SrcCtl.UpdateSourceMenu()

    def SwitchSyncedActions(self, count: int) -> None:
        pass

    def ShutdownActions(self) -> None:
        self.PollCtl.SetPollingMode('inactive')
        self.SrcCtl.MatrixSwitch(0, 'All', 'untie')
        self.TP_Main.AudioCtl.AudioShutdown()
        for tp in self.TPs:
            tp.HdrCtl.ConfigSystemOff()
        
        # for id, hw in self.Hardware:
        #     if id.startswith('WPD'):
        #         hw.interface.Set('BootUsers', value=None, qualifier=None)

    def ShutdownSyncedActions(self, count: int) -> None:
        pass

    def Initialize(self) -> None:
        ## Create Controllers --------------------------------------------------
        # Log(['Button: {} ({}, {})'.format(btn.Name, btn.ID, btn) for btn in self.TPs[0].Btn_Grps['Activity-Select'].Objects])
        self.ActCtl = ActivityController(self)
        
        for tp in self.TPs:
            tp.InitializeUIControllers()
        
        self.SrcCtl = self.TP_Main.SrcCtl
        
        # Log('Source List: {}'.format(self.Sources))
        # Log('Destination List: {}'.format(self.Destinations))
        
        ## GUI Display Initialization ------------------------------------------
        self.TP_Main.ShowPage('Splash')
        self.TP_Main.Btns['Room-Label'].SetText(self.RoomName)
        for tp in self.TPs:
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
        
        print('System Initialized')
        Log('System Initialized')
        for tp in self.TPs:
            tp.BlinkLights(Rate='Fast', StateList=['green', 'red'], Timeout=2.5)
            tp.Click(5, 0.2)
            
    @classmethod
    def GetErrorStr(cls, Error: str, *args, **kwargs):
        return cls.errorMap[Error].format(*args, **kwargs)