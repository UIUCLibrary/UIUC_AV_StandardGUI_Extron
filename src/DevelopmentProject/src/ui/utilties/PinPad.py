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

## Begin Imports ---------------------------------------------------------------

#### Type Checking
from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import SystemController
    from uofi_gui.uiObjects import ExUIDevice
    from extronlib.ui import Button, Knob, Label, Level, Slider

#### Python imports

#### Extron Library Imports
from extronlib import event

#### Project imports
from modules.helper.CommonUtilities import Logger, DictValueSearchByKey, RunAsync, debug

## End Imports -----------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class PINController:
    def __init__(self,
                 UIHost: 'ExUIDevice') -> None:
        # Public Properties
        self.UIHost = UIHost
        self.PIN = None
        self.Callback = None
        
        # Private Properties
        self.__CurrentPIN = ""
        self.__PINPadBtns = \
            {
                "numPad": DictValueSearchByKey(self.UIHost.Btns, r'PIN-\d', regex=True),
                "backspace": self.UIHost.Btns['PIN-Del'],
                "cancel": self.UIHost.Btns['PIN-Cancel']
            }
        self.__PINLbl = self.UIHost.Lbls['PIN-Label']

        @event(self.__PINPadBtns['numPad'], ['Pressed','Released']) # pragma: no cover
        def UpdatePINHandler(button: 'Button', action: str):
            self.__UpdatePINHandler(button, action)
        
        @event(self.__PINPadBtns['backspace'], ['Pressed','Released']) # pragma: no cover
        def BackspacePINHandler(button: 'Button', action: str):
            self.__BackspacePINHandler(button, action)

        @event(self.__PINPadBtns['cancel'], ['Pressed','Released']) # pragma: no cover
        def CancelBtnHandler(button: 'Button', action: str):
            self.__CancelBtnHandler(button, action)
    
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
                self.Close(success=True)
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
            self.Close()
            button.SetState(0)
    
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
    
    def Open(self, PIN: str, Callback: Callable=None) -> None:
        """Displays Pin Modal"""
        self.Callback = Callback
        
        # validate pin
        if type(PIN) is str:
            for character in PIN:
                if not character.isnumeric():
                    raise ValueError('All PIN Characters must be numeric')
        else:
            raise TypeError('PIN must be a string of numeric characters')
        
        self.ResetPIN()
        self.UIHost.ShowPopup("PIN Code")
        
    def Close(self, success: bool=False) -> None:
        """Hides PIN Modal"""
        
        if success:
            self.Callback()
        
        self.Callback = None
        self.PIN = None
        
        self.ResetPIN()
        
        self.UIHost.HidePopup("PIN Code")

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



