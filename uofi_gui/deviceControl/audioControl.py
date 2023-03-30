from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    from extronlib.ui import Button
    
## Begin ControlScript Import --------------------------------------------------
from extronlib import event
from extronlib.ui import Level

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from utilityFunctions import DictValueSearchByKey, Log, RunAsync, debug

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class AudioController:
    def __init__(self, UIHost: 'ExUIDevice') -> None:
        self.UIHost = UIHost
        self.GUIHost = self.UIHost.GUIHost
        self.DSP = self.GUIHost.Hardware[self.GUIHost.PrimaryDSPId]
        
        self.Microphones = {}
        for mic in self.GUIHost.Microphones:
            self.Microphones[str(mic['Number'])] = mic
            self.Microphones[str(mic['Number'])]['hw'] = self.GUIHost.Hardware.get(mic['Id'], None)
            self.Microphones[str(mic['Number'])]['mute'] = False
        
        self.__StepSm = 1
        self.__StepLg = 3
        
        self.__ProgMute = False
        
        self.__Levels = {'prog': self.UIHost.Lvls['Audio-Lvl-Prog'], 'mics': {}}
        self.__Levels['prog'].SetRange(self.DSP.Program['Range'][0],
                                       self.DSP.Program['Range'][1],
                                       self.DSP.Program['Step'])
        
        self.__Labels = {}
        self.__MicCtlList = []
        self.__Controls = \
            {
                'prog': 
                    {
                        'up': self.UIHost.Btns['Vol-Prog-Up'],
                        'down': self.UIHost.Btns['Vol-Prog-Dn'],
                        'mute': self.UIHost.Btns['Vol-Prog-Mute']
                    },
                'mics': {},
                'all-mics': self.UIHost.Btns['Vol-AllMics-Mute']
            }
        self.__Controls['prog']['up'].CtlType = 'up'
        self.__Controls['prog']['down'].CtlType = 'down'
        self.__Controls['prog']['mute'].CtlType = 'mute'
        
        for i in range(1, len(self.GUIHost.Microphones) + 1):
            self.__Controls['mics'][str(i)] = \
                {
                    'up': self.UIHost.Btns['Vol-Mic-{}-Up'.format(str(i))],
                    'down': self.UIHost.Btns['Vol-Mic-{}-Dn'.format(str(i))],
                    'mute': self.UIHost.Btns['Vol-Mic-{}-Mute'.format(str(i))]
                }
            self.__Controls['mics'][str(i)]['up'].CtlType = 'up'
            self.__Controls['mics'][str(i)]['down'].CtlType = 'down'
            self.__Controls['mics'][str(i)]['mute'].CtlType = 'mute'
            self.__Controls['mics'][str(i)]['up'].MicNum = i
            self.__Controls['mics'][str(i)]['down'].MicNum = i
            self.__Controls['mics'][str(i)]['mute'].MicNum = i
            self.__MicCtlList.extend(list(self.__Controls['mics'][str(i)].values()))
            self.__Levels['mics'][str(i)] = self.UIHost.Lvls['Audio-Lvl-Mic-{}'.format(str(i))]
            self.__Levels['mics'][str(i)].SetRange(self.Microphones[str(i)]['Control']['level']['Range'][0],
                                                   self.Microphones[str(i)]['Control']['level']['Range'][1],
                                                   self.Microphones[str(i)]['Control']['level']['Step'])
            self.__Labels[str(i)] = self.UIHost.Lbls['Aud-Mic-{}'.format(str(i))]
            self.__Labels[str(i)].SetText(self.Microphones[str(i)]['Name'])
        
        # Program Buttons
        @event(list(self.__Controls['prog'].values()), ['Pressed', 'Released', 'Repeated']) # pragma: no cover
        def ProgramControlHandler(button: 'Button', action: str):
            self.__ProgramControlHandler(button, action)
                
        # Mic Buttons
        @event(self.__MicCtlList, ['Pressed', 'Released', 'Repeated']) # pragma: no cover
        def MicControlHandler(button: 'Button', action: str):
            self.__MicControlHandler(button, action)
                
        # All Mics Mute Button
        @event(self.__Controls['all-mics'], ['Pressed']) # pragma: no cover
        def AllMicsMuteHandler(button: 'Button', action: str):
            self.ToggleAllMicsMute()
    
    @property
    def AllMicsMute(self)->bool:
        test = True
        for mic in self.Microphones.values():
            if not mic['mute']:
                test = False
        return test
    
    @AllMicsMute.setter
    def AllMicsMute(self, state: Union[int, str, bool]):
        if type(state) not in [int, str, bool]:
            raise TypeError('Mute State must be boolean, int, or string mute state')
        
        setState = (state in ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE'])
        
        for numStr in self.Microphones.keys():
            self.MicMute = (int(numStr), setState)
    
    @property
    def MicMute(self)->Dict[int, bool]:
        rtnDict = {}
        for num, mic in self.Microphones.items():
            rtnDict[num] = mic['mute']
        return rtnDict
    
    @MicMute.setter
    def MicMute(self, value: Tuple[int, Union[str, int, bool]]):
        if type(value) is not tuple:
            raise TypeError('Value must be a Tuple')
        if type(value[0]) is not int or type(value[1]) not in [str, int, bool]:
            raise TypeError('Value must be a Tuple with index [0] being a int (Mic Number) and index [1] being a mute state')
        
        MicNum = value[0]
        State = value[1]
        
        setState = (State in ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE'])
        
        mic = self.Microphones[str(MicNum)]
        btn = self.__Controls['mics'][str(MicNum)]['mute']
        
        cmd = mic['Control']['mute']
        hw = self.GUIHost.Hardware[cmd['HwId']]
        hwCmd = getattr(hw, cmd['HwCmd'])
        qual = hwCmd.get('qualifier', None)
        value = 'On' if setState else 'Off'
        
        mic['mute'] = setState
        
        if setState:
            btn.SetBlinking('Medium', [1,2])
        else:
            btn.SetState(0)
        
        hw.interface.Set(hwCmd['command'], value, qual)
        self.AllMicsMuteButtonState()
    
    @property
    def MicLevel(self)->Dict[int, Union[int, float]]:
        rtnDict = {}
        for num, mic in self.Microphones.items():
            cmd = mic['Control']['level']
            hw = self.GUIHost.Hardware[cmd['HwId']]
            hwCmd = getattr(hw, cmd['HwCmd'])
            qual = hwCmd.get('qualifier', None)
            
            rtnDict[num] = hw.interface.ReadStatus(hwCmd['command'], qual)
        return rtnDict
    
    @MicLevel.setter
    def MicLevel(self, value: Tuple[int, Union[int, float]]):
        #def MicLevel(self, MicNum, Value: int):
        if type(value) is not tuple:
            raise TypeError('Value must be a Tuple')
        if type(value[0]) is not int or type(value[1]) not in [int, float]:
            raise TypeError('Value must be a Tuple with index [0] being a int (Mic Number) and index [1] being an int or float level')
        
        MicNum = value[0]
        Value = value[1]
        
        mic = self.Microphones[str(MicNum)]
        
        cmd = mic['Control']['level']
        hw = self.GUIHost.Hardware[cmd['HwId']]
        hwCmd = getattr(hw, cmd['HwCmd'])
        qual = hwCmd.get('qualifier', None)
        
        hw.interface.Set(hwCmd['command'], Value, qual)
    
    @property
    def ProgMute(self)->bool:
        return self.__ProgMute
    
    @ProgMute.setter
    def ProgMute(self, State: Union[str, int, bool]):
        setState = (State in ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE'])
        
        btn = self.__Controls['prog']['mute']
        hwCmd = self.DSP.ProgramMuteCommand
        qual = hwCmd.get('qualifier', None)
        value = 'On' if setState else 'Off'
        
        self.__ProgMute = setState
        
        if setState:
            btn.SetBlinking('Medium', [1,2])
        else:
            btn.SetState(0)
            
        self.DSP.interface.Set(hwCmd['command'], value, qual)
        
    @property
    def ProgLevel(self)->float:
        hwCmd = self.DSP.ProgramLevelCommand
        qual = hwCmd.get('qualifier', None)
        
        return self.DSP.interface.ReadStatus(hwCmd['command'], qual)
    
    @ProgLevel.setter
    def ProgLevel(self, Level: Union[int, float]):
        if type(Level) not in [int, float]:
            raise TypeError('Level must be an integer')
        
        hwCmd = self.DSP.ProgramLevelCommand
        qual = hwCmd.get('qualifier', None)
        
        self.DSP.interface.Set(hwCmd['command'], Level, qual)
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __ProgramControlHandler(self, button: 'Button', action: str):
        level = self.__Levels['prog']
        
        if action == 'Pressed':
            if button.CtlType == 'mute':
                self.ToggleProgMute()
            elif button.CtlType in ['up', 'down']:
                button.SetState(1)
        elif action == 'Released':
            if button.CtlType in ['up', 'down']:
                self.ProgLevel = self.AdjustLevel(level, button.CtlType, 'small')
                button.SetState(0)
        elif action == 'Repeated':
            if button.CtlType in ['up', 'down']:
                self.ProgLevel = self.AdjustLevel(level, button.CtlType, 'large')
            
    def __MicControlHandler(self, button: 'Button', action: str):
        level = self.__Levels['mics'][str(button.MicNum)]
        
        if action == 'Pressed':
            if button.CtlType == 'mute':
                self.ToggleMicMute(button.MicNum)
            elif button.CtlType in ['up', 'down']:
                button.SetState(1)
        elif action == 'Released':
            if button.CtlType in ['up', 'down']:
                self.MicLevel = (button.MicNum, self.AdjustLevel(level, button.CtlType, 'small'))
                button.SetState(0)
        elif action == 'Repeated':
            if button.CtlType in ['up', 'down']:
                self.MicLevel = (button.MicNum, self.AdjustLevel(level, button.CtlType, 'large'))
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def AllMicsMuteButtonState(self):
        if self.AllMicsMute:
            self.__Controls['all-mics'].SetBlinking('Medium', [1,2])
        else:
            self.__Controls['all-mics'].SetState(0)
    
    def AdjustLevel(self, level, direction: str='up', step: str='small'):
        if type(level) is not Level:
            raise TypeError('Level must be a Level object')
        if type(direction) is not str:
            raise TypeError('Direction must be a string')
        if type(step) is not str:
            raise TypeError('Step must be a string')
        
        if step == 'small':
            s = self.__StepSm
        elif step == 'large':
            s = self.__StepLg
        else:
            raise ValueError('Step must be either "large" or "small"')
            
        if direction == 'up':
            newLevel = level.Level + s
        elif direction == 'down':
            newLevel = level.Level - s
        else:
            raise ValueError('Direction must either be "up" or "down"')
            
        level.SetLevel(newLevel)
        
        return newLevel
    
    def AudioStartUp(self):
        # Set default levels & unmute all sources
        self.__Levels['prog'].SetLevel(self.DSP.Program['StartUp'])
        self.ProgLevel = self.DSP.Program['StartUp'] 
        
        for numStr, mic in self.Microphones.items():
            self.__Levels['mics'][numStr].SetLevel(mic['Control']['level']['StartUp'])
            self.MicLevel = (int(numStr), mic['Control']['level']['StartUp'])
        
        # Unmute all sources
        self.ProgMute = False
        self.AllMicsMute = False
    
    def AudioShutdown(self):
        # Mute all sources
        self.ProgMute = True
        self.AllMicsMute = True
    
    def ToggleProgMute(self):
        self.ProgMute = not self.__ProgMute
        
    def ToggleMicMute(self, MicNum: int):
        self.MicMute = (MicNum, not self.Microphones[str(MicNum)]['mute'])
    
    def ToggleAllMicsMute(self):
        self.AllMicsMute = not self.AllMicsMute 
    
    def AudioLevelFeedback(self, tag: Tuple, value: int):
        # Log("Audio Level Feedback - Tag: {}; Value: {}".format(tag, value))
        if tag[0] == 'prog':
            # Log('Prog Level Feedback')
            if not (self.__Controls[tag[0]]['up'].PressedState or self.__Controls[tag[0]]['down'].PressedState):
                self.__Levels[tag[0]].SetLevel(int(value))
        elif tag[0] == 'mics':
            # Log('Mic Level Feedback')
            if not (self.__Controls[tag[0]][str(tag[1])]['up'].PressedState or self.__Controls[tag[0]][str(tag[1])]['down'].PressedState):
                self.__Levels[tag[0]][str(tag[1])].SetLevel(int(value))
    
    def AudioMuteFeedback(self, tag: Tuple[str, Union[str, int]], state: Union[str, int, bool]):
        # Log("Audio Mute Feedback - Tag: {}; State: {}".format(tag, state))
        if tag[0] == 'prog':
            # Log('Prog Mute Feedback')
            if state in ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE']:
                # Log('Prog Mute On')
                self.__Controls[tag[0]]['mute'].SetBlinking('Medium', [1,2])
                self.__ProgMute = True
            else:
                # Log('Prog Mute Off')
                self.__Controls[tag[0]]['mute'].SetState(0)
                self.__ProgMute = False
        elif tag[0] == 'mics':
            # Log('Mic {} Mute Feedback'.format(tag[1]))
            if state in ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE']:
                # Log('Mic {} Mute On'.format(tag[1]))
                self.__Controls[tag[0]][str(tag[1])]['mute'].SetBlinking('Medium', [1,2])
                self.Microphones[str(tag[1])]['mute'] = True
            else:
                # Log('Mic {} Mute On'.format(tag[1]))
                self.__Controls[tag[0]][str(tag[1])]['mute'].SetState(0)
                self.Microphones[str(tag[1])]['mute'] = False
            self.AllMicsMuteButtonState()

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------