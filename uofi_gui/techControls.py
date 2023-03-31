import sys
TESTING = ('unittest' in sys.modules.keys())

from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    from extronlib.device import UIDevice
    from extronlib.ui import Button, Slider

## Begin ControlScript Import --------------------------------------------------
from extronlib import event
from extronlib.system import MESet, Timer

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
import os
from subprocess import Popen, PIPE
from math import floor as roundDown

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from utilityFunctions import DictValueSearchByKey, Log, RunAsync, debug

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class TechMenuController:
    def __init__(self,
                 UIHost: 'ExUIDevice') -> None:
        # Public Properties
        self.UIHost = UIHost
        self.GUIHost = self.UIHost.GUIHost
        self.TechMenuOpen = False
        
        # Private Properties
        self.__AboutUpdateTimer = Timer(5, self.__AboutUpdateHandler)
        self.__AboutUpdateTimer.Stop()
        
        self.__AboutLabels = DictValueSearchByKey(self.UIHost.Lbls, r'Proc(?:Info|Status)Label-(\w+)', regex=True, capture_dict=True)
        self.__PanelLabels = DictValueSearchByKey(self.UIHost.Lbls, r'PanelInfoLabel-(\w+)', regex=True, capture_dict=True)
        self.__PanelControls = \
            {
                'sleep': 
                    {
                        'slider': self.UIHost.Slds['Slider-PanelSleepTime'],
                        'label': self.UIHost.Lbls['PanelSleepLabel-Timer'],
                        'auto-sleep': self.UIHost.Btns['PanelSetting-AutoSleep'],
                        'wake-on-motion': self.UIHost.Btns['PanelSetting-WakeOnMotion']
                    },
                'brightness':
                    {
                        'slider': self.UIHost.Slds['Slider-PanelBrightness'],
                        'auto-brightness': self.UIHost.Btns['PanelSetting-AutoBrightness']
                    },
                'volume':
                    {
                        'slider': self.UIHost.Slds['Slider-PanelAudio']
                    }
            }
        self.__PanelControls['sleep']['slider'].SetRange(0, 200, 1)
        self.__PanelControls['sleep']['slider'].SetFill(self.UIHost.SleepTimer)
        self.__PanelControls['sleep']['label'].SetText(str(self.UIHost.SleepTimer))
        self.__PanelControls['sleep']['auto-sleep'].SetState(int(self.UIHost.SleepTimerEnabled))
        self.__PanelControls['sleep']['wake-on-motion'].SetState(int(self.UIHost.WakeOnMotion))
        self.__PanelControls['brightness']['slider'].SetRange(0, 100, 1)
        self.__PanelControls['brightness']['slider'].SetFill(self.UIHost.Brightness)
        if self.UIHost.AutoBrightness:
            self.__PanelControls['brightness']['slider'].SetEnable(False)
        self.__PanelControls['brightness']['auto-brightness'].SetState(int(self.UIHost.AutoBrightness))
        self.__PanelControls['volume']['slider'].SetRange(0, 100, 1)
        self.__PanelControls['volume']['slider'].SetFill(self.UIHost.GetVolume('Master'))
        
        self.__PageSelects = \
            {
                'Tech-AdvancedVolume': self.__AdvVolPage,
                'Tech-CameraControls': self.__CamCtlsPage,
                'Tech-DisplayControls': self.__DispCtlPage,
                'Tech-ManualMatrix': self.__ManMtxPage,
                'Tech-RoomConfig': self.__RmCfgPage
            }
        self.__PageUpdates = \
            {
                'Tech-SystemStatus': self.__StatusUpdate,
                'Tech-About': self.__AboutUpdate,
                'Tech-PanelSetup': self.__PnlSetupUpdate,
            }
            
        self.__MenuBtns = MESet([])
        self.__DefaultPage = 'Tech-SystemStatus'
        self.__DefaultBtn = None
        for btn in DictValueSearchByKey(self.UIHost.Btns, r'Tech-\w+$', regex=True):
            if btn.Name in self.__PageSelects.keys():
                btn.Page = self.__PageSelects[btn.Name]()
            else:
                btn.Page = btn.Name
            self.__MenuBtns.Append(btn)
            if btn.Name in self.__DefaultPage:
                self.__DefaultBtn = btn
        
        self.__CtlBtns = \
            {
                'prev': self.UIHost.Btns['Tech-Menu-Previous'],
                'next': self.UIHost.Btns['Tech-Menu-Next'],
                'exit': self.UIHost.Btns['Tech-Menu-Exit'],
                'menu-pages': [
                    'Menu-Tech-1',
                    'Menu-Tech-2'
                ]
            }
        self.__PageIndex = 0
        
        @event(self.__MenuBtns.Objects, 'Pressed') # pragma: no cover
        def TechMenuBtnHandler(button: 'Button', action: str):
            self.__TechMenuBtnHandler(button, action)
            
        @event(self.__CtlBtns['prev'], ['Pressed', 'Released']) # pragma: no cover
        def TechMenuPrevHandler(button: 'Button', action: str):
            self.__TechMenuPrevHandler(button, action)
        
        @event(self.__CtlBtns['next'], ['Pressed', 'Released']) # pragma: no cover
        def TechMenuNextHandler(button: 'Button', action: str):
            self.__TechMenuNextHandler(button, action)
        
        @event(self.__CtlBtns['exit'], ['Pressed', 'Released']) # pragma: no cover
        def TechMenuExitHandler(button: 'Button', action: str):
            self.__TechMenuExitHandler(button, action)
            
        @event(self.__PanelControls['sleep']['slider'], ['Changed']) # pragma: no cover
        def PanelSleepHandler(slider: 'Slider', action: str, value: Union[int, float]):
            self.__PanelSleepHandler(slider, action, value)
            
        @event(self.__PanelControls['sleep']['auto-sleep'], ['Released']) # pragma: no cover
        def PanelAutoSleepHandler(button: 'Button', action: str):
            self.__PanelAutoSleepHandler(button, action)

        @event(self.__PanelControls['sleep']['wake-on-motion'], ['Released']) # pragma: no cover
        def PanelWakeOnMotionHandler(button: 'Button', action: str):
            self.__PanelWakeOnMotionHandler(button, action)
            
        @event(self.__PanelControls['brightness']['slider'], ['Changed']) # pragma: no cover
        def PanelBrightnessHandler(slider: 'Slider', action: str, value: Union[int, float]):
            self.__PanelBrightnessHandler(slider, action, value)
            
        @event(self.__PanelControls['brightness']['auto-brightness'], ['Released']) # pragma: no cover
        def PanelAutoBrightnessHandler(button: 'Button', action: str):
            self.__PanelAutoBrightnessHandler(button, action)
            
        @event(self.UIHost, 'BrightnessChanged') # pragma: no cover
        def PanelBrightnessChangeHandler(tp: Union['ExUIDevice', 'UIDevice'], value: int):
            self.__PanelBrightnessChangeHandler(tp, value)
            
        @event(self.__PanelControls['volume']['slider'], ['Changed']) # pragma: no cover
        def PanelVolumeHandler(slider: 'Slider', action: str, value: Union[int, float]):
            self.__PanelVolumeHandler(slider, action)

    # Event Handlers  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __TechMenuBtnHandler(self, button: 'Button', action: str):
        for fn in self.__PageUpdates.values():
            fn(show=False)
        
        if button.Page in self.__PageUpdates:
            self.__PageUpdates[button.Page](show=True)
        
        self.__MenuBtns.SetCurrent(button)
        self.UIHost.ShowPopup(button.Page)
    
    def __TechMenuPrevHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
            if self.__PageIndex > 0:
                self.__PageIndex -= 1
        elif action == 'Released':
            self.UIHost.ShowPopup(self.__CtlBtns['menu-pages'][self.__PageIndex])
            if self.__PageIndex == 0:
                button.SetState(2)
                button.SetEnable(False)
            else:
                button.SetState(0)
            if self.__PageIndex < (len(self.__CtlBtns['menu-pages'])-1):
                self.__CtlBtns['next'].SetState(0)
                self.__CtlBtns['next'].SetEnable(True)
    
    def __TechMenuNextHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
            if self.__PageIndex < (len(self.__CtlBtns['menu-pages'])-1):
                self.__PageIndex += 1
        elif action == 'Released':
            self.UIHost.ShowPopup(self.__CtlBtns['menu-pages'][self.__PageIndex])
            if self.__PageIndex == (len(self.__CtlBtns['menu-pages'])-1):
                button.SetState(2)
                button.SetEnable(False)
            else:
                button.SetState(0)
            if self.__PageIndex > 0:
                self.__CtlBtns['prev'].SetState(0)
                self.__CtlBtns['prev'].SetEnable(True)
    
    def __TechMenuExitHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            button.SetState(0)
            self.CloseTechMenu()
    
    def __PanelSleepHandler(self, slider: 'Slider', action: str, value: Union[int, float]):
        slider.SetFill(value)
        self.__PanelControls['sleep']['label'].SetText(str(round(value)))
        if self.UIHost.SleepTimerEnabled:
            self.UIHost.SetSleepTimer('On', int(value))
    
    def __PanelAutoSleepHandler(self, button: 'Button', action: str):
        if self.UIHost.SleepTimerEnabled:
            self.UIHost.SetSleepTimer('Off')
            button.SetState(0)
        else:
            self.UIHost.SetSleepTimer('On', int(self.__PanelControls['sleep']['slider'].Fill))
            button.SetState(1)
    
    def __PanelWakeOnMotionHandler(self, button: 'Button', action: str):
        state = not self.UIHost.WakeOnMotion
        self.UIHost.SetWakeOnMotion(state)
        button.SetState(int(state))
    
    def __PanelBrightnessHandler(self, slider: 'Slider', action: str, value: Union[int, float]):
        slider.SetFill(value)
        self.UIHost.SetBrightness(int(value))
    
    def __PanelAutoBrightnessHandler(self, button: 'Button', action: str):
        state = not self.UIHost.AutoBrightness
        button.SetState(int(state))
        self.__PanelControls['brightness']['slider'].SetEnable(state)
        self.UIHost.SetAutoBrightness(state)
    
    def __PanelBrightnessChangeHandler(self, tp: Union['ExUIDevice', 'UIDevice'], value: int):
        self.__PanelControls['brightness']['slider'].SetFill(value)
    
    def __PanelVolumeHandler(self, slider: 'Slider', action: str, value: Union[int, float]):
        slider.SetFill(value)
        self.UIHost.SetVolume('Master', int(value))
    
    def __AboutUpdateHandler(self, timer: Timer, count: int):
        used = roundDown(self.GUIHost.CtlProc_Main.UserUsage[0]/1024)
        total = roundDown(self.GUIHost.CtlProc_Main.UserUsage[1]/1024)
        self.__AboutLabels['Storage'].SetText('{}/{} MB'.format(used, total))
        self.__AboutLabels['CPU'].SetText('{}%'.format(self.__GetCPUUsage()))
        self.__AboutLabels['Memory'].SetText('{} used; {} free; {} total'.format(*self.__GetRAMUsage()))
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __GetCPUUsage(self) -> float: # pragma: no cover
        if TESTING:
            return 42.17
        
        sub = Popen(('grep', 'cpu', '/proc/stat'), stdout=PIPE, stderr=PIPE)
        cpuData = str(sub.communicate()[0], 'UTF-8')
        top_vals = [int(val) for val in cpuData.split('\n')[0].split()[1:5]]
        return round((top_vals[0] + top_vals[2]) * 100. /(top_vals[0] + top_vals[2] + top_vals[3]), 2)

    def __GetRAMUsage(self) -> Tuple[float, ...]: # pragma: no cover
        if TESTING:
            return (20, 25, 45)
        
        filepath = "/proc/meminfo"
        meminfo = dict(
            (i.split()[0].rstrip(":"), int(i.split()[1]))
            for i in open(filepath).readlines()
        )
        memTotalMB = round(meminfo["MemTotal"] / (2 ** 10), 2)
        memFreeMB = round(meminfo["MemFree"] / (2 ** 10), 2)
        memUsedMB = round(((meminfo["MemTotal"] - meminfo["MemFree"]) / (2 ** 10)), 2)
        return (memUsedMB, memFreeMB, memTotalMB)
    
    def __AdvVolPage(self) -> str:
        return 'Tech-AdvancedVolume_{}'.format(len(self.GUIHost.Microphones))
    
    def __CamCtlsPage(self) -> str:
        return 'Tech-CameraControls_{}'.format(len(self.GUIHost.Cameras))
    
    def __DispCtlPage(self):
        confs = 0
        mons = 0
        projs = 0
        for dest in self.GUIHost.Destinations:
            if dest['type'] == 'proj+scn' or dest['type'] == 'proj':
                projs += 1
            elif dest['type'] == 'mon':
                mons += 1
            elif dest['type'] == 'conf' or dest['type'] == 'c-conf':
                confs += 1
        
        return 'Tech-DisplayControls_{c},{p},{m}'.format(c = confs, p = projs, m = mons)
    
    def __ManMtxPage(self):
        return 'Tech-ManualMatrix_{i}x{o}'.format(i = self.GUIHost.TechMatrixSize[0], o = self.GUIHost.TechMatrixSize[1])
    
    def __RmCfgPage(self):
        return 'Tech-RoomConfig_{}'.format(len(self.GUIHost.Lights))
    
    def __StatusUpdate(self, show: bool=False):
        if show:
            self.UIHost.StatusCtl.ResetPages()
            self.UIHost.StatusCtl.UpdateTimer.Restart()
        else:
            self.UIHost.StatusCtl.UpdateTimer.Stop()
    
    def __PnlSetupUpdate(self, show: bool=False):
        self.__PanelLabels['Model'].SetText(self.UIHost.ModelName)
        self.__PanelLabels['Serial'].SetText(self.UIHost.SerialNumber)
        self.__PanelLabels['MAC'].SetText(self.UIHost.MACAddress)
        self.__PanelLabels['Host'].SetText(self.UIHost.Hostname)
        self.__PanelLabels['IP'].SetText(self.UIHost.IPAddress)
        self.__PanelLabels['FW'].SetText(self.UIHost.FirmwareVersion)
    
    def __AboutUpdate(self, show: bool=False):
        if show:
            self.__AboutLabels['Model'].SetText(self.GUIHost.CtlProc_Main.ModelName)
            self.__AboutLabels['Serial'].SetText(self.GUIHost.CtlProc_Main.SerialNumber)
            self.__AboutLabels['MAC'].SetText(self.GUIHost.CtlProc_Main.MACAddress)
            self.__AboutLabels['Host'].SetText(self.GUIHost.CtlProc_Main.Hostname)
            self.__AboutLabels['IP'].SetText(self.GUIHost.CtlProc_Main.IPAddress)
            self.__AboutLabels['FW'].SetText(self.GUIHost.CtlProc_Main.FirmwareVersion)
            self.__AboutLabels['File'].SetText(self.GUIHost.CtlProc_Main.SystemSettings['ProgramInformation']['FileLoaded'])
            self.__AboutLabels['Version'].SetText(self.GUIHost.CtlProc_Main.SystemSettings['ProgramInformation']['SoftwareVersion'])
            self.__AboutLabels['Author'].SetText(self.GUIHost.CtlProc_Main.SystemSettings['ProgramInformation']['Author'])
                        
            self.__AboutUpdateHandler(None, None)
            self.__AboutUpdateTimer.Restart()
        else:
            self.__AboutUpdateTimer.Stop()
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def OpenTechMenu(self) -> None:
        self.TechMenuOpen = True
        # utilityFunctions.Log('Updating Tech Menu Nav')
        self.__PageIndex = 0
        self.UIHost.ShowPopup(self.__CtlBtns['menu-pages'][self.__PageIndex])
        self.__CtlBtns['prev'].SetState(2)
        self.__CtlBtns['prev'].SetEnable(False)
        self.__CtlBtns['next'].SetState(0)
        self.__CtlBtns['next'].SetEnable(True)
        
        # utilityFunctions.Log('Checking for Page Updates')
        if self.__DefaultPage in self.__PageUpdates:
            # utilityFunctions.Log('Starting Updates for Page: {}'.format(self._defaultPage))
            self.__PageUpdates[self.__DefaultPage](show=True)
            
        self.__MenuBtns.SetCurrent(self.__DefaultBtn)
        self.UIHost.ShowPopup(self.__DefaultPage)
    
    def CloseTechMenu(self):
        self.TechMenuOpen = False
        if self.GUIHost.ActCtl.CurrentActivity == 'off':
            self.UIHost.ShowPage('Opening')
        else:
            self.UIHost.ShowPage('Main')
        for fn in self.__PageUpdates.values():
            fn(show=False)

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------
