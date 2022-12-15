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
from typing import Dict, Tuple, List, Union
import re

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
import utilityFunctions as utFn
import settings
import uofi_gui.sourceControls as srcCtl

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

matrix_mode = 'AV'
stateDict = {
    'AV': 3,
    'Aud': 2,
    'Vid': 1,
    'untie': 0
}

def InitManualMatrix(UIHost: UIDevice,
                     matrixBtns: List[Button],
                     matrixCtls: MESet,
                     matrixDelAll: Button,
                     inputLabels: List[Label],
                     outputLabels: List[Label]):
    
    @event(matrixBtns, 'Pressed')
    def matrixSelectHandler(button: Button, action: str):
        global matrix_mode, stateDict
        
        regex = r"Tech-Matrix-(\d+),(\d+)"
        re_match = re.match(regex, button.Name)
        # 0 is full match, 1 is input, 2 is output
        input = re_match.group(1)
        output = re_match.group(2)
        
        # send switch commands
        if matrix_mode == "untie":
            srcCtl.MatrixSwitchSources(0, output)
        else:
            srcCtl.MatrixSwitchSources(input, output, matrix_mode)
        
        # set pressed button's feedback
        button.SetState(stateDict[matrix_mode])
        button.SetText(matrix_mode)
        
        # fix other buttons in output row
        if matrix_mode != 'untie':
            for btn in matrixBtns:
                re_affected_match = re.match(regex, btn.Name)
                # 0 is full match, 1 is input, 2 is output
                # Match any button in same output row other than the button which triggered the matrix action
                if re_affected_match.group(2) == output and re_affected_match.group(1) != input:
                    if matrix_mode == 'AV':
                        btn.SetState(0) # untie everything else in output row
                        btn.SetText('')
                    elif matrix_mode == 'Aud':
                        if btn.State == 2: # Button has Audio tie, untie button
                            btn.SetState(0)
                            btn.SetText('')
                        elif btn.State == 3: # Button has AV tie, untie audio only
                            btn.SetState(1)
                            btn.SetText('Vid')
                    elif matrix_mode == 'Vid':
                        if btn.State == 1: # Button has Video tie, untie button
                            btn.SetState(0)
                            btn.SetText('')
                        elif btn.State == 3: # Button has AV tie, untie video only
                            btn.SetState(2)
                            btn.SetText('Aud')
            
    
    @event(matrixCtls.Objects, 'Pressed')
    def matrixModeHandler(button: Button, action: str):
        global matrix_mode
        if button.Name.endswith('AV'):
            matrix_mode = 'AV'
        elif button.Name.endswith('Audio'):
            matrix_mode = 'Aud'
        elif button.Name.endswith('Vid'):
            matrix_mode = 'Vid'
        elif button.Name.endswith('Untie'):
            matrix_mode = 'untie'
            
    @event(matrixDelAll, 'Pressed')
    def matrixDelAllTiesHandler(button: Button, action: str):
        for matrixBtn in matrixBtns:
            matrixBtn.SetState(0)

        srcCtl.MatrixSwitchSources(0, 'all')

    for inLbl in inputLabels:
        inLbl.SetText('Not Connected')
    for src in settings.sources:
        inputLabels[src['input'] - 1].SetText(src['name'])
        
    for outLbl in outputLabels:
        outLbl.SetText('Not Connected')
    for dest in settings.destinations:
        outputLabels[dest['output'] - 1].SetText(dest['Name'])
        
    # TODO: figure out how best to use device feedback to ensure the Matrix display stays updated
    

## End Function Definitions ----------------------------------------------------
##
## Begin Script Definition -----------------------------------------------------
if __name__ == "__main__": ## this module does not run as a script
    pass
## End Script Definition -------------------------------------------------------


