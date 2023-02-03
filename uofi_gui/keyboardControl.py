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
from typing import Dict, Tuple, List, Callable

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
import utilityFunctions
import settings
import vars

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class KeyboardController:
    def __init__(self, UIHost: UIDevice) -> None:
        self.UIHost = UIHost
        
        self.__kbDict = \
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
        self.__charBtns = []
        for key in self.__kbDict:
            btn = vars.TP_Btns['KB-{}'.format(key)]
            btn.char = self.__kbDict[key]
            btn.SetText(btn.char[0])
            self.__charBtns.append(btn)
        
        self.__saveBtn = vars.TP_Btns['KB-save']
        self.__cancelBtn = vars.TP_Btns['KB-cancel']
        self.__leftBtn = vars.TP_Btns['KB-left']
        self.__leftBtn.shift = -1
        self.__rightBtn = vars.TP_Btns['KB-right']
        self.__rightBtn.shift = 1
        self.__shiftBtn = vars.TP_Btns['KB-shift']
        self.__capsBtn = vars.TP_Btns['KB-caps']
        self.__bsBtn = vars.TP_Btns['KB-bs']
        self.__delBtn = vars.TP_Btns['KB-del']
        
        self.__textLbl = vars.TP_Lbls['KB-Editor']
        
        self.__cursor = ('\u2502','\u2588')
        self.__pos = 0
        self.__cursorTimer = Timer(0.5, self.__cursorTimerHandler)
        self.__cursorTimer.Stop()
        
        self.CapsLock = False
        self.Shift = False
        self.Text = ''
        self.Callback = None
        
        @event(self.__charBtns, ['Pressed', 'Released'])
        def charBtnHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                button.SetState(0)

                self.__insertChar(button.char[self.__charIndex()])
                self.__textLbl.SetText(self.__cursorString())
                
                # unshift after character entry
                if self.Shift:
                    self.Shift = False
                    self.__shiftBtn.SetState(0)
                    self.__updateKeyboardState()
        
        @event(self.__shiftBtn, ['Pressed', 'Released'])
        def shiftBtnHandler(button, action):
            if action == 'Pressed':
                if self.Shift:
                    button.SetState(0)
                else:
                    button.SetState(1)
            elif action == 'Released':
                self.Shift = not self.Shift
                self.__updateKeyboardState()
                if self.Shift:
                    button.SetState(1)
                else:
                    button.SetState(0)
        
        @event(self.__capsBtn, ['Pressed', 'Released'])
        def capsLockBtnHandler(button, action):
            if action == 'Pressed':
                if self.CapsLock:
                    button.SetState(0)
                else:
                    button.SetState(1)
            elif action == 'Released':
                self.CapsLock = not self.CapsLock
                self.__updateKeyboardState()
                if self.CapsLock:
                    button.SetState(1)
                else:
                    button.SetState(0)
                    
        @event([self.__leftBtn, self.__rightBtn], ['Pressed', 'Released'])
        def arrowBtnHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                button.SetState(0)
                self.__pos += button.shift
                if self.__pos < 0:
                    self.__pos = 0
                elif self.__pos > (len(self.Text) + 1):
                    self.__pos = (len(self.Text) + 1)
                self.__textLbl.SetText(self.__cursorString())
                
        @event(self.__bsBtn, ['Pressed', 'Released'])
        def backspaceBtnHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                button.SetState(0)
                self.__removeChar(-1)
                self.__textLbl.SetText(self.__cursorString())
                
        @event(self.__delBtn, ['Pressed', 'Released'])
        def deleteBtnHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                button.SetState(0)
                self.__removeChar(1)
                self.__textLbl.SetText(self.__cursorString())
                
        @event(self.__saveBtn, ['Pressed', 'Released'])
        def saveBtnHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                button.SetState(0)
                self.Save()
        
        @event(self.__cancelBtn, ['Pressed', 'Released'])
        def cancelBtnHandler(button, action):
            if action == 'Pressed':
                button.SetState(1)
            elif action == 'Released':
                button.SetState(0)
                self.Close()

    def __charIndex(self):
        index = False
        if self.CapsLock:
            index = not index
        if self.Shift:
            index = not index
        
        return int(index == True)
    
    def __cursorTimerHandler(self, timer, count):
        self.__textLbl.SetText(self.__cursorString(count % 2))
    
    def __cursorString(self, cursorInd = 0):
        return self.Text[:self.__pos] + self.__cursor[cursorInd] + self.Text[self.__pos:]
    
    def __insertChar(self, char: str):
        self.Text = self.Text[:self.__pos] + char + self.Text[self.__pos:]
        self.__pos += len(char)
        
    def __removeChar(self, count: int):
        if count > 0:
            self.Text = self.Text[:self.__pos] + self.Text[(self.__pos + count):]
            if self.__pos > (len(self.Text) + 1):
                self.__pos = (len(self.Text) + 1)
        elif count < 0:
            self.Text = self.Text[:(self.__pos + count)] + self.Text[self.__pos:]
            self.__pos += count
            if self.__pos < 0:
                self.__pos = 0
        
    def __updateKeyboardState(self):
        index = self.__charIndex()
        for charBtn in self.__charBtns:
            charBtn.SetText(charBtn.char[index])
            
    def Open(self, Text: str='', Callback: Callable=None):
        self.Callback = Callback
        self.__shiftBtn.SetState(0)
        self.__capsBtn.SetState(0)
        self.Shift = False
        self.CapsLock = False
        
        self.__cursorTimer.Restart()
        
        self.__updateKeyboardState()
        
        self.__pos = len(Text)
        self.Text = Text
        
        self.__textLbl.SetText(self.__cursorString())
        
        self.UIHost.ShowPopup('Keyboard')
        
    def Save(self):
        self.Callback(self.Text)
        self.Close()
        
    def Close(self):
        self.Callback = None
        self.__cursorTimer.Stop()
        self.UIHost.HidePopup('Keyboard')
    
## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------



