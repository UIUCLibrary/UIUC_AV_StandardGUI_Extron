# from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING:
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    from uofi_gui.sourceControls import SourceController

from extronlib.system import Timer, Wait
from utilityFunctions import Log, RunAsync, debug

class Source:
    def __init__(self,
                 SrcCtl: SourceController,
                 id: str,
                 name: str,
                 icon: int,
                 input: int,
                 alert: int,
                 srcCtl: str=None,
                 advSrcCtl: str=None) -> None:
        
        self.SourceController = SrcCtl
        self.Id = id
        self.Name = name
        self.Icon = icon
        self.Input = input
        self.SourceControlPage = srcCtl
        self.AdvSourceControlPage = advSrcCtl
        
        self.__AlertText = {}
        self.__AlertIndex = 0
        self.__OverrideAlert = None
        self.__OverrideState = False
        self.__DefaultAlert = alert
        
        self.__AlertTimer = Timer(1, self.__AlertTimerHandler)
        self.__AlertTimer.Stop()

    @property
    def AlertText(self):
        if not self.__OverrideState:
            txt =  list(self.__AlertText.keys())[self.__AlertIndex]
            Log('AlertText: {}'.format(txt))
            self.CycleAlert()
        else:
            txt = self.__OverrideAlert
        return txt
    
    @property
    def AlertBlock(self):
        block = '\n'.join(self.__AlertText)
        block = block.strip()
        if self.__OverrideState:
            block = '{}\n{}'.format(self.__OverrideAlert, block)
        return block
    
    @property
    def Alerts(self):
        count = len(self.__AlertText)
        if self.__OverrideState:
            count += 1
        return count
    
    @property
    def AlertFlag(self):
        if len(self.__AlertText) > 0:
            return True
        elif self.__OverrideState:
            return True
        else:
            return False
    
    def CycleAlert(self):
        self.__AlertIndex += 1
        if self.__AlertIndex >= len(self.__AlertText):
            self.__AlertIndex = 0
    
    def AppendAlert(self, msg: str=None, timeout: int=0) -> None:
        if msg is None:
            msg = self.__DefaultAlert
            
        if timeout > 0:
            self.__AlertText[msg] = timeout
        else: 
            self.__AlertText[msg] = -1
        
        if self.__AlertTimer.State in ['Paused', 'Stopped']:
            self.__AlertTimer.Restart()
        
    def OverrideAlert(self, msg: str, timeout: int=60) -> None:
        self.__OverrideAlert = msg
        self.__OverrideState = True
        if timeout > 0:
            @Wait(timeout)
            def OverrideTimeoutHandler():
                self.__OverrideState = False
    
    def ClearOverride(self):
        self.__OverrideState = False
    
    def ClearAlert(self, msg: str=None):
        if msg is None:
            msg = self.__DefaultAlert
            
        self.__AlertText.pop(msg)
        
        if len(self.__AlertText) == 0:
            self.__AlertTimer.Stop()
    
    def ResetAlert(self) -> None:
        self.__AlertText = {}
        self.__AlertTimer.Stop()
        
    def __AlertTimerHandler(self, timer: Timer, count: int):
        for msg in self.__AlertText.keys():
            if self.__AlertText[msg] > 0:
                self.__AlertText[msg] -= 1
                if self.__AlertText[msg] == 0:
                    self.__AlertText.pop(msg)
        if len(self.__AlertText) == 0:
            timer.Stop()
                