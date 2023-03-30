from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    from extronlib.ui import Button

## Begin ControlScript Import --------------------------------------------------
from extronlib import event
from extronlib.system import Timer

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
## Begin Class Definitions -----------------------------------------------------

class KeyboardController:
    def __init__(self, UIHost: 'ExUIDevice') -> None:
        self.UIHost = UIHost
        
        self.CapsLock = False
        self.Shift = False
        self.Text = ''
        self.Callback = None
        
        self.__KBDict = \
            {
                'tilda': ('`', '~'),
                '1': ('1', '!'),
                '2': ('2', '@'),
                '3': ('3', '#'),
                '4': ('4', '$'),
                '5': ('5', '%'),
                '6': ('6', '^'),
                '7': ('7', '&'),
                '8': ('8', '*'),
                '9': ('9', '('),
                '0': ('0', ')'),
                'dash': ('-', '_'),
                'equals': ('=', '+'),
                'q': ('q', 'Q'),
                'w': ('w', 'W'),
                'e': ('e', 'E'),
                'r': ('r', 'R'),
                't': ('t', 'T'),
                'y': ('y', 'Y'),
                'u': ('u', 'U'),
                'i': ('i', 'I'),
                'o': ('o', 'O'),
                'p': ('p', 'P'),
                'openBracket': ('[', '{'),
                'closeBracket': (']', '}'),
                'backslash': ('\\','|'),
                'a': ('a', 'A'),
                's': ('s', 'S'),
                'd': ('d', 'D'),
                'f': ('f', 'F'),
                'g': ('g', 'G'),
                'h': ('h', 'H'),
                'j': ('j', 'J'),
                'k': ('k', 'K'),
                'l': ('l', 'L'),
                'semicolon': (';', ':'),
                'apostrophy': ("'", '"'),
                'z': ('z', 'Z'),
                'x': ('x', 'X'),
                'c': ('c', 'C'),
                'v': ('v', 'V'),
                'b': ('b', 'B'),
                'n': ('n', 'N'),
                'm': ('m', 'M'),
                'comma': (',', '<'),
                'period': ('.', '>'),
                'slash': ('/', '?'),
                'space': (' ', ' ')
            }
            
        self.__CharBtns = []
        for key in self.__KBDict:
            btn = self.UIHost.Btns['KB-{}'.format(key)]
            btn.char = self.__KBDict[key]
            btn.SetText(btn.char[0])
            self.__CharBtns.append(btn)
        
        self.__SaveBtn = self.UIHost.Btns['KB-save']
        self.__CancelBtn = self.UIHost.Btns['KB-cancel']
        self.__LeftBtn = self.UIHost.Btns['KB-left']
        self.__LeftBtn.shift = -1
        self.__RightBtn = self.UIHost.Btns['KB-right']
        self.__RightBtn.shift = 1
        self.__ShiftBtn = self.UIHost.Btns['KB-shift']
        self.__CapsBtn = self.UIHost.Btns['KB-caps']
        self.__BSBtn = self.UIHost.Btns['KB-bs']
        self.__DelBtn = self.UIHost.Btns['KB-del']
        
        self.__TextLbl = self.UIHost.Lbls['KB-Editor']
        
        self.__Cursor = ('\u2502','\u2588')
        self.__Pos = 0
        self.__CursorTimer = Timer(0.5, self.__CursorTimerHandler)
        self.__CursorTimer.Stop()
        
        @event(self.__CharBtns, ['Pressed', 'Released']) # pragma: no cover
        def charBtnHandler(button: 'Button', action: str):
            self.__CharBtnHandler(button, action)
        
        @event(self.__ShiftBtn, ['Pressed', 'Released']) # pragma: no cover
        def shiftBtnHandler(button: 'Button', action: str):
            self.__ShiftBtnHandler(button, action)
        
        @event(self.__CapsBtn, ['Pressed', 'Released']) # pragma: no cover
        def capsLockBtnHandler(button: 'Button', action: str):
            self.__CapsLockBtnHandler(button, action)
                    
        @event([self.__LeftBtn, self.__RightBtn], ['Pressed', 'Released']) # pragma: no cover
        def arrowBtnHandler(button: 'Button', action: str):
            self.__ArrowBtnHandler(button, action)
                
        @event(self.__BSBtn, ['Pressed', 'Released']) # pragma: no cover
        def backspaceBtnHandler(button: 'Button', action: str):
            self.__BackspaceBtnHandler(button, action)
                
        @event(self.__DelBtn, ['Pressed', 'Released']) # pragma: no cover
        def deleteBtnHandler(button: 'Button', action: str):
            self.__DeleteBtnHandler(button, action)
                
        @event(self.__SaveBtn, ['Pressed', 'Released']) # pragma: no cover
        def saveBtnHandler(button: 'Button', action: str):
            self.__SaveBtnHandler(button, action)
        
        @event(self.__CancelBtn, ['Pressed', 'Released']) # pragma: no cover
        def cancelBtnHandler(button: 'Button', action: str):
            self.__CancelBtnHandler(button, action)

    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __CharBtnHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            button.SetState(0)

            self.__InsertChar(button.char[self.__CharIndex()])
            self.__TextLbl.SetText(self.__CursorString())
            
            # unshift after character entry
            if self.Shift:
                self.Shift = False
                self.__ShiftBtn.SetState(0)
                self.__UpdateKeyboardState()
    
    def __ShiftBtnHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            if self.Shift:
                button.SetState(0)
            else:
                button.SetState(1)
        elif action == 'Released':
            self.Shift = not self.Shift
            self.__UpdateKeyboardState()
            if self.Shift:
                button.SetState(1)
            else:
                button.SetState(0)
    
    def __CapsLockBtnHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            if self.CapsLock:
                button.SetState(0)
            else:
                button.SetState(1)
        elif action == 'Released':
            self.CapsLock = not self.CapsLock
            self.__UpdateKeyboardState()
            if self.CapsLock:
                button.SetState(1)
            else:
                button.SetState(0)
    
    def __ArrowBtnHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            button.SetState(0)
            self.__Pos += button.shift
            if self.__Pos < 0:
                self.__Pos = 0
            elif self.__Pos > (len(self.Text)):
                self.__Pos = (len(self.Text))
            self.__TextLbl.SetText(self.__CursorString())
    
    def __BackspaceBtnHandler(self, button: 'Button',  action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            button.SetState(0)
            self.__RemoveChar(-1)
            self.__TextLbl.SetText(self.__CursorString())
    
    def __DeleteBtnHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            button.SetState(0)
            self.__RemoveChar(1)
            self.__TextLbl.SetText(self.__CursorString())
    
    def __SaveBtnHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            button.SetState(0)
            self.Save()
    
    def __CancelBtnHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            button.SetState(0)
            self.Close()
    
    def __CursorTimerHandler(self, timer: 'Timer', count: int):
        self.__TextLbl.SetText(self.__CursorString(count % 2))
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __CharIndex(self):
        index = False
        if self.CapsLock:
            index = not index
        if self.Shift:
            index = not index
        
        return int(index == True)
    
    def __CursorString(self, cursorInd = 0):
        return self.Text[:self.__Pos] + self.__Cursor[cursorInd] + self.Text[self.__Pos:]
    
    def __InsertChar(self, char: str):
        self.Text = self.Text[:self.__Pos] + char + self.Text[self.__Pos:]
        self.__Pos += len(char)
        
    def __RemoveChar(self, count: int):
        if count > 0:
            if self.__Pos < (len(self.Text)):
                self.Text = self.Text[:self.__Pos] + self.Text[(self.__Pos + count):]
            else: # pragma: no cover
                # not covering this because coverage can't tell this has run.
                # see test_uofi_keyboardControl.py for more information
                pass # cursor is at the end of the string, there is nothing to remove
        elif count < 0:
            if self.__Pos >=0 and (self.__Pos + count) >= 0:
                self.Text = self.Text[:(self.__Pos + count)] + self.Text[self.__Pos:]
            else:
                pass # cursor is at the beginning of the string
            self.__Pos += count # fix Position after removing characters infront of the cursor
            if self.__Pos < 0: # fixes Position if it becomes less than zero
                self.__Pos = 0
        
    def __UpdateKeyboardState(self):
        index = self.__CharIndex()
        for charBtn in self.__CharBtns:
            charBtn.SetText(charBtn.char[index])
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def Open(self, Text: str='', Callback: Callable=None):
        self.Callback = Callback
        self.__ShiftBtn.SetState(0)
        self.__CapsBtn.SetState(0)
        self.Shift = False
        self.CapsLock = False
        
        self.__CursorTimer.Restart()
        
        self.__UpdateKeyboardState()
        
        self.__Pos = len(Text)
        self.Text = Text
        
        self.__TextLbl.SetText(self.__CursorString())
        
        self.UIHost.ShowPopup('Keyboard')
        
    def Save(self):
        self.Callback(self.Text)
        self.Close()
        
    def Close(self):
        self.Callback = None
        self.__CursorTimer.Stop()
        self.UIHost.HidePopup('Keyboard')
    
## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



