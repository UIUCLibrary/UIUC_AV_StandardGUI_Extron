from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable, cast
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    from uofi_gui.sourceControls import SourceController, Source, Destination, LayoutTuple, RelayTuple, MatrixTuple
    from extronlib.ui import Knob, Label, Level, Slider
    from extronlib.system import MESet

from extronlib import event
from extronlib.system import Wait
from extronlib.ui import Button

import re

from utilityFunctions import Log

class MatrixController:
    def __init__(self,
                 srcCtl: 'SourceController',
                 matrixBtns: List['Button'],
                 matrixCtls: 'MESet',
                 matrixDelAll: 'Button',
                 inputLabels: List['Label'],
                 outputLabels: List['Label']) -> None:
        
        # Log('Set Public Properties')
        self.SourceController = srcCtl
        self.Mode = 'AV'
        
        self.Hardware = self.SourceController.GUIHost.Hardware[self.SourceController.GUIHost.PrimarySwitcherId]
        
        # Log('Create Matrix Rows')
        matrixRows = {}
        for btn in matrixBtns:
            row = int(btn.Name[-1])
            if row not in matrixRows:
                matrixRows[row] = [btn]
            else:
                matrixRows[row].append(btn)

        self.__Rows = {}
        for r in matrixRows:
            self.__Rows[r] = MatrixRow(self, matrixRows[r], r)
        
        for dest in self.SourceController.Destinations:
            dest = cast('Destination', dest)
            dest.AssignMatrixRow(self.__Rows[dest.Output])
            
        self.__CtlsSet = matrixCtls
        self.__DelBtn = matrixDelAll
        self.__InputLbls = inputLabels
        self.__OutputLbls = outputLabels
        self.StateDict = {
            'AV': 3,
            'Aud': 2,
            'Vid': 1,
            'untie': 0
        }
        
        self.__CtlsSet.SetCurrent(0)
        
        for inLbl in self.__InputLbls:
            inLbl.SetText('Not Connected')
        for src in self.SourceController.Sources:
            src = cast('Source', src)
            for inLbl in self.__InputLbls:
                if inLbl.Name.endswith(str(src.Input)):
                    inLbl.SetText(src.Name)
            
        for outLbl in self.__OutputLbls:
            outLbl.SetText('Not Connected')
        for dest in self.SourceController.Destinations:
            dest = cast('Destination', dest)
            for outLbl in self.__OutputLbls:
                if outLbl.Name.endswith(str(dest.Output)):
                    outLbl.SetText(dest.Name)
        
        @event(self.__CtlsSet.Objects, 'Pressed') # pragma: no cover
        def MatrixModeHandler(button: 'Button', action: str):
            self.__ModeHandler(button, action)
        
        @event(self.__DelBtn, ['Pressed','Released']) # pragma: no cover
        def MatrixDelAllTiesHandler(button: 'Button', action: str):
            self.__DeleteAllTiesHandler(button, action)
        
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __DeleteAllTiesHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            button.SetState(0)
            for row in self.__Rows.values():
                for btn in row.Objects:
                    btn.SetState(0)
            self.SourceController.MatrixSwitch(self.SourceController.BlankSource, 'All', 'untie')

    def __ModeHandler(self, button: 'Button', action: str):
        self.__CtlsSet.SetCurrent(button)
        if button.Name.endswith('AV'):
            self.Mode = 'AV'
        elif button.Name.endswith('Aud'):
            self.Mode = 'Aud'
        elif button.Name.endswith('Vid'):
            self.Mode = 'Vid'
        elif button.Name.endswith('Untie'):
            self.Mode = 'untie'

class MatrixRow:
    def __init__(self,
                 Matrix: 'MatrixController',
                 rowBtns: List['Button'],
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
        
        @event(self.Objects, 'Pressed') # pragma: no cover
        def matrixSelectHandler(button: 'Button', action: str):
            self.__MatrixSelectHandler(button, action)
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __MatrixSelectHandler(self, button: 'Button', action: str):
        # send switch commands
        if self.Matrix.Mode == "untie":
            self.Matrix.SourceController.MatrixSwitch(0, [self.MatrixOutput], self.Matrix.Mode)
        else:
            # Log("Selected button input - {}".format(button.Input))
            self.Matrix.SourceController.MatrixSwitch(button.Input, [self.MatrixOutput], self.Matrix.Mode)
        
        # set pressed button's feedback
        self.MakeTie(button, self.Matrix.Mode)
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __UpdateRowBtns(self, modBtn: 'Button', tieType: str="AV") -> None:
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
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def MakeTie(self, input: Union[int, 'Button'], tieType: str="AV") -> None:
        if not (tieType == 'AV' or tieType == 'Aud' or tieType == 'Vid' or tieType == 'untie'):
            raise ValueError("TieType must be one of 'AV', 'Aud', 'Vid', or 'untie")
        
        if input == 0:
            # for btn in self.Objects:
            #     btn.SetState(0)
            #     btn.SetText('')
            self.__UpdateRowBtns(None, tieType)
        else:
            if type(input) is int:
                for btn in self.Objects:
                    if btn.Input == input:
                        modBtn = btn
            elif type(input) is Button:
                modBtn = input
            else:
                raise TypeError('Input must be either an int or Button object')
            
            prevState = modBtn.State
            if (prevState == 2 and tieType == 'Vid') \
                or (prevState == 1 and tieType == 'Aud') \
                or prevState == 3:
                # now AV tie
                modBtn.SetState(3)
                modBtn.SetText('AV')
            else:
                modBtn.SetState(self.Matrix.StateDict[tieType])
                modBtn.SetText(tieType)
            
            if tieType == 'untie':
                @Wait(5) # pragma: no cover
                def untiedTextHandler():
                    modBtn.SetText('')
            
            self.__UpdateRowBtns(modBtn, tieType)