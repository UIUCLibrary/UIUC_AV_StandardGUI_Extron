from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    from extronlib.ui import Button, Knob, Label, Level, Slider

## Begin ControlScript Import --------------------------------------------------
from extronlib import event

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from utilityFunctions import DictValueSearchByKey, Log, RunAsync, debug

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

class PINController:
    def __init__(self,
                 UIHost: 'ExUIDevice',
                 pinCode: str,
                 destPage: str,
                 openFn: Callable) -> None:
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
        self._pinPadBtns = \
            {
                "numPad": DictValueSearchByKey(self.UIHost.Btns, r'PIN-\d', regex=True),
                "backspace": self.UIHost.Btns['PIN-Del'],
                "cancel": self.UIHost.Btns['PIN-Cancel']
            }
        self._pinLbl = self.UIHost.Lbls['PIN-Label']
        self._destPage = destPage
        self._destPageFn = openFn
        self._startBtn = self.UIHost.Btns['Header-Settings']
        
        self.maskPIN()

        @event(self._pinPadBtns['numPad'], ['Pressed','Released'])
        def UpdatePIN(button: 'Button', action: str):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                val = button.ID - 9000
                    # pin button IDs should start at 9000 and be in numerical order
                self._currentPIN = self._currentPIN + str(val)
                self.maskPIN() #remask pin after change
                if (self._currentPIN == self.PIN):
                    self.UIHost.ShowPopup("PIN Outcome Success", 2)
                    # clean up and go to destination page while success popup is up
                    self.UIHost.ShowPage(self._destPage)
                    self._destPageFn()
                    self.UIHost.HidePopup("PIN Code")
                elif (len(self._currentPIN) >= 10):
                    self.UIHost.ShowPopup("PIN Outcome Failure", 2)
                    # clean up and go back to pin page while failure popup is up
                    self.resetPIN()
                button.SetState(0)
        
        @event(self._pinPadBtns['backspace'], ['Pressed','Released'])
        def BackspacePIN(button: 'Button', action: str):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                self._currentPIN = self._currentPIN[:-1] # remove last character of current pin
                self.maskPIN()  # remask pin after change
                button.SetState(0)

        @event(self._pinPadBtns['cancel'], ['Pressed','Released'])
        def CancelBtnHandler(button: 'Button', action: str):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                self.hidePINMenu()
                button.SetState(0)

        @event(self._startBtn, 'Held')
        # triggers on startBtn defined long press, 3 sec recommended
        def StartBtnHandler(button: 'Button', action: str):
            button.SetState(0)
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
        self.maskPIN()
    
    def showPINMenu(self) -> None:
        """Displays Pin Modal"""
        self.resetPIN()
        self.UIHost.ShowPopup("PIN Code")
        
    def hidePINMenu(self) -> None:
        """Hides PIN Modal"""
        self.UIHost.HidePopup("PIN Code")

## End Function Definitions ----------------------------------------------------


