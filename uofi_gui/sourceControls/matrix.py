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
## Begin Python Imports --------------------------------------------------------
from datetime import datetime
import json
from typing import Dict, Tuple, List, Union, Callable
from collections import namedtuple
import re

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
import utilityFunctions as utFn
import settings
# from uofi_gui.sourceControls import SourceController, MatrixTuple

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class MatrixController:
    def __init__(self,
                 srcCtl, #: SourceController,
                 matrixBtns: List[Button],
                 matrixCtls: MESet,
                 matrixDelAll: Button,
                 inputLabels: List[Label],
                 outputLabels: List[Label]) -> None:
        self.SourceController = srcCtl
        self.Mode = 'AV'
        
        matrixRows = {}
        for btn in matrixBtns:
            row = btn.Name[-1]
            if row not in matrixRows:
                matrixRows[row] = [btn]
            else:
                matrixRows[row].append(btn)
            
        self._ctls = matrixCtls
        self._del = matrixDelAll
        self._inputLbls = inputLabels
        self._outputLbls = outputLabels
        self._stateDict = {
            'AV': 3,
            'Aud': 2,
            'Vid': 1,
            'untie': 0
        }
        
        self._rows = {}
        for r in matrixRows:
            self._rows[int(r)] = MatrixRow(self, matrixRows[r], int(r))
        
        for dest in self.SourceController.Destinations:
            dest._MatrixRow = self._rows[dest.Output]
        
        @event(self._ctls.Objects, 'Pressed')
        def matrixModeHandler(button: Button, action: str):
            if button.Name.endswith('AV'):
                self.Mode = 'AV'
            elif button.Name.endswith('Audio'):
                self.Mode = 'Aud'
            elif button.Name.endswith('Vid'):
                self.Mode = 'Vid'
            elif button.Name.endswith('Untie'):
                self.Mode = 'untie'
        
        @event(self._del, 'Pressed')
        def matrixDelAllTiesHandler(button: Button, action: str):
            for row in self._rows.values():
                for btn in row.Objects:
                    btn.SetState(0)

            self.SourceController.MatrixSwitch(self.SourceController._none_source)
            
        for inLbl in self._inputLbls:
            inLbl.SetText('Not Connected')
        for src in self.SourceController.Sources:
            self._inputLbls[src.Input - 1].SetText(src.Name)
            
        for outLbl in self._outputLbls:
            outLbl.SetText('Not Connected')
        for dest in self.SourceController.Destinations:
            self._outputLbls[dest.Output - 1].SetText(dest.Name)
        
class MatrixRow:
    def __init__(self,
                 Matrix: MatrixController,
                 rowBtns: List[Button],
                 output: int) -> None:
        
        self.Matrix = Matrix
        self.MatrixOutput = output
        self.VidSelect = 0
        self.AudSelect = 0
        self.Objects = rowBtns
        
        # Overload matrix row buttons with Input property
        for btn in self.Objects:
            regex = r"Tech-Matrix-(\d+),(\d+)"
            re_match = re.match(regex, btn.Name)
            # 0 is full match, 1 is input, 2 is output
            btn.Input = int(re_match.group(1))
        
        @event(self.Objects, 'Pressed')
        def matrixSelectHandler(button: Button, action: str):
            # send switch commands
            if self.Matrix.Mode == "untie":
                self.Matrix.SourceController.MatrixSwitch(0, self.MatrixOutput, self.Matrix.Mode)
            else:
                self.Matrix.SourceController.MatrixSwitch(btn.Input, self.MatrixOutput, self.Matrix.Mode)
            
            # set pressed button's feedback
            button.SetState(self.Matrix._stateDict[self.Matrix.Mode])
            button.SetText(self.Matrix.Mode)
            
            self._UpdateRowBtns(button, self.Matrix.Mode)
        
    def _UpdateRowBtns(self, modBtn: Button, tieType: str="AV") -> None:
        for btn in self.Objects:
            if btn != modBtn:
                if tieType == 'AV':
                    btn.SetState(0) # untie everything else in output row
                    btn.SetText('')
                elif tieType == 'Aud':
                    if btn.State == 2: # Button has Audio tie, untie button
                        btn.SetState(0)
                        btn.SetText('')
                    elif btn.State == 3: # Button has AV tie, untie audio only
                        btn.SetState(1)
                        btn.SetText('Vid')
                elif tieType == 'Vid':
                    if btn.State == 1: # Button has Video tie, untie button
                        btn.SetState(0)
                        btn.SetText('')
                    elif btn.State == 3: # Button has AV tie, untie video only
                        btn.SetState(2)
                        btn.SetText('Aud')
    
    def MakeTie(self, input: int, tieType: str="AV") -> None:
        if not (tieType == 'AV' or tieType == 'Aud' or tieType == 'Vid'):
            raise ValueError("TieType must be one of 'AV', 'Aud', or 'Vid'")
        
        modBtn = self.Objects[input]
        modBtn.SetState(self.Matrix._stateDict[tieType])
        modBtn.SetText(tieType)
        
        self._UpdateRowBtns(modBtn, tieType)
    
## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------    

## End Function Definitions ----------------------------------------------------


