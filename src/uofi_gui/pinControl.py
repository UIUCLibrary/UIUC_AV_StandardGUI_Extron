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
from DevelopmentProject.src.modules.helper.UtilityFunctions import DictValueSearchByKey, Log, RunAsync, debug

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
        # Public Properties
        self.UIHost = UIHost
        self.PIN = pinCode
        
        # Private Properties
        self.__CurrentPIN = ""
        self.__PINPadBtns = \
            {
                "numPad": DictValueSearchByKey(self.UIHost.Btns, r'PIN-\d', regex=True),
                "backspace": self.UIHost.Btns['PIN-Del'],
                "cancel": self.UIHost.Btns['PIN-Cancel']
            }
        self.__PINLbl = self.UIHost.Lbls['PIN-Label']
        self.__DestPage = destPage
        self.__DestPageFn = openFn
        self.__StartBtn = self.UIHost.Btns['Header-Settings']
        
        self.__MaskPIN()

        @event(self.__PINPadBtns['numPad'], ['Pressed','Released']) # pragma: no cover
        def UpdatePINHandler(button: 'Button', action: str):
            self.__UpdatePINHandler(button, action)
        
        @event(self.__PINPadBtns['backspace'], ['Pressed','Released']) # pragma: no cover
        def BackspacePINHandler(button: 'Button', action: str):
            self.__BackspacePINHandler(button, action)

        @event(self.__PINPadBtns['cancel'], ['Pressed','Released']) # pragma: no cover
        def CancelBtnHandler(button: 'Button', action: str):
            self.__CancelBtnHandler(button, action)

        @event(self.__StartBtn, 'Held') # pragma: no cover
        # triggers on startBtn defined long press, 3 sec recommended
        def StartBtnHandler(button: 'Button', action: str):
            self.__StartBtnHandler(button, action)
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __UpdatePINHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            val = button.ID - 9000
                # pin button IDs should start at 9000 and be in numerical order
            self.__CurrentPIN = self.__CurrentPIN + str(val)
            self.__MaskPIN() #remask pin after change
            if (self.__CurrentPIN == self.PIN):
                self.UIHost.ShowPopup("PIN Outcome Success", 2)
                # clean up and go to destination page while success popup is up
                self.UIHost.ShowPage(self.__DestPage)
                self.__DestPageFn()
                self.UIHost.HidePopup("PIN Code")
            elif (len(self.__CurrentPIN) >= 10):
                self.UIHost.ShowPopup("PIN Outcome Failure", 2)
                # clean up and go back to pin page while failure popup is up
                self.ResetPIN()
            button.SetState(0)
    
    def __BackspacePINHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            self.__CurrentPIN = self.__CurrentPIN[:-1] # remove last character of current pin
            self.__MaskPIN()  # remask pin after change
            button.SetState(0)
    
    def __CancelBtnHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            self.HidePINMenu()
            button.SetState(0)
    
    def __StartBtnHandler(self, button: 'Button', action: str):
        button.SetState(0)
        self.ShowPINMenu()
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __MaskPIN(self) -> None:
        """Generates and sets Masked PIN feedback"""    

        mask = ""
        while (len(mask) < len(self.__CurrentPIN)):
            mask = mask + "*"
        self.__PINLbl.SetText(mask)
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def ResetPIN(self) -> None:
        """Resets the currently input PIN code"""
        self.__CurrentPIN = ''
        self.__MaskPIN()
    
    def ShowPINMenu(self) -> None:
        """Displays Pin Modal"""
        self.ResetPIN()
        self.UIHost.ShowPopup("PIN Code")
        
    def HidePINMenu(self) -> None:
        """Hides PIN Modal"""
        self.UIHost.HidePopup("PIN Code")

## End Function Definitions ----------------------------------------------------


