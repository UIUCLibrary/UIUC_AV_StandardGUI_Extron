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
## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

class PINController:
    def __init__(self,
                 UIHost: UIDevice,
                 startBtn: Button,
                 pinBtns: Dict[str, Union[List[Button], Button]],
                 pinLbl: Label,
                 pinCode: str,
                 destPage: str) -> None:
        """Initializes the PIN Security Controller

        Args:
            UIHost (extronlib.device): UIHost to which the buttons are assigned
            startBtn (extronlib.ui.Button): the button object which triggers the pin code module
            pinBtns (Dict[List[extronlib.ui.Button], extronlib.ui.Button, extronlib.ui.Button]): dictionary containing pin page
                buttons such as:
                {
                    "numPad":
                        [
                            TP_Btns['PIN-0'],
                            TP_Btns['PIN-1'],
                            TP_Btns['PIN-2'],
                            TP_Btns['PIN-3'],
                            TP_Btns['PIN-4'],
                            TP_Btns['PIN-5'],
                            TP_Btns['PIN-6'], 
                            TP_Btns['PIN-7'],
                            TP_Btns['PIN-8'],
                            TP_Btns['PIN-9']
                        ],
                "backspace": TP_Btns['PIN-Del'],
                "cancel": TP_Btns['PIN-Cancel']
                }
            pinLbl (extronlib.ui.Label): the label object which will contain masked user feedback
            pinCode (str): the master pin value to match against
            destPage (str): the page to show on successful pin auth

        Returns:
            bool: true on success, false on failure
        """
        # Public Properties
        self.UIHost = UIHost
        self.PIN = pinCode
        
        # Private Properties
        self._currentPIN = ""
        self._pinPadBtns = pinBtns
        self._pinLbl = pinLbl
        self._destPage = destPage
        self._startBtn = startBtn
        
        self.maskPIN()

        @event(self._pinPadBtns['numPad'], 'Pressed')
        def UpdatePIN(button, action):
            print(type(button))
            val = button.ID - 9000
                # pin button IDs should start at 9000 and be in numerical order
            self._currentPIN = self._currentPIN + str(val)
            self.maskPIN() #remask pin after change
            if (self._currentPIN == self.PIN):
                self.UIHost.ShowPopup("PIN Outcome Success", 2)
                # clean up and go to destination page while success popup is up
                self.UIHost.ShowPage(self._destPage)
                self.UIHost.HidePopup("PIN Code")
            elif (len(self._currentPIN) >= 10):
                self.UIHost.ShowPopup("PIN Outcome Failure", 2)
                # clean up and go back to pin page while failure popup is up
                self.resetPIN()
        
        @event(pinBtns['backspace'], 'Pressed')
        def BackspacePIN(button, action):
            self._currentPIN = self._currentPIN[:-1] # remove last character of current pin
            self.maskPIN()  # remask pin after change

        @event(pinBtns['cancel'], 'Pressed')
        def CancelBtnHandler(button, action):
            self.hidePINMenu()

        @event(self._startBtn, 'Held')
        # triggers on startBtn defined long press, 3 sec recommended
        def StartBtnHandler(button, action):
            self.showPINMenu()
    
    def maskPIN(self) -> None:
        """Generates and sets Masked PIN feedback"""    

        mask = ""
        while (len(mask) < len(self._currentPIN)):
            mask = mask + "*"
        self._pinLbl.SetText(mask)
        
    def resetPIN(self) -> None:
        """Resets the currently input PIN code"""
        self._currentPIN = ''
        self.maskPIN
    
    def showPINMenu(self) -> None:
        """Displays Pin Modal"""
        self.resetPIN
        self.UIHost.ShowPopup("PIN Code")
        
    def hidePINMenu(self) -> None:
        """Hides PIN Modal"""
        self.UIHost.HidePopup("PIN Code")

## End Function Definitions ----------------------------------------------------


