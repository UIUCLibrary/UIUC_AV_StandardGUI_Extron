from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING:
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    
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

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------

class AudioController:
    def __init__(self, UIHost: 'ExUIDevice') -> None:
        self.UIHost = UIHost
        self.GUIHost = self.UIHost.GUIHost
        self.DSP = self.GUIHost.Hardware[self.GUIHost.PrimaryDSPId]
        
        self.__step_sm = 1
        self.__step_lg = 3
        
        Log('Creating microphones dict')
        self.Microphones = {}
        for mic in self.GUIHost.Microphones:
            self.Microphones[str(mic['Number'])] = mic
            self.Microphones[str(mic['Number'])]['hw'] = self.GUIHost.Hardware.get(mic['Id'], None)
            self.Microphones[str(mic['Number'])]['mute'] = False
        self.__ProgMute = False
        
        Log('Creating levels and controls')
        self.__levels = {'prog': self.UIHost.Lvls['Audio-Lvl-Prog'], 'mics': {}}
        self.__levels['prog'].SetRange(self.DSP.Program['Range'][0],
                                       self.DSP.Program['Range'][1],
                                       self.DSP.Program['Step'])
        
        self.__labels = {}
        self.__mic_ctl_list = []
        self.__controls = \
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
        self.__controls['prog']['up'].CtlType = 'up'
        self.__controls['prog']['down'].CtlType = 'down'
        self.__controls['prog']['mute'].CtlType = 'mute'
        
        for i in range(1, len(self.GUIHost.Microphones) + 1):
            Log('Creating microphone controls {}'.format(str(i)))
            self.__controls['mics'][str(i)] = \
                {
                    'up': self.UIHost.Btns['Vol-Mic-{}-Up'.format(str(i))],
                    'down': self.UIHost.Btns['Vol-Mic-{}-Dn'.format(str(i))],
                    'mute': self.UIHost.Btns['Vol-Mic-{}-Mute'.format(str(i))]
                }
            self.__controls['mics'][str(i)]['up'].CtlType = 'up'
            self.__controls['mics'][str(i)]['down'].CtlType = 'down'
            self.__controls['mics'][str(i)]['mute'].CtlType = 'mute'
            self.__controls['mics'][str(i)]['up'].MicNum = i
            self.__controls['mics'][str(i)]['down'].MicNum = i
            self.__controls['mics'][str(i)]['mute'].MicNum = i
            self.__mic_ctl_list.extend(list(self.__controls['mics'][str(i)].values()))
            self.__levels['mics'][str(i)] = self.UIHost.Lvls['Audio-Lvl-Mic-{}'.format(str(i))]
            self.__levels['mics'][str(i)].SetRange(self.Microphones[str(i)]['Control']['level']['Range'][0],
                                                   self.Microphones[str(i)]['Control']['level']['Range'][1],
                                                   self.Microphones[str(i)]['Control']['level']['Step'])
            self.__labels[str(i)] = self.UIHost.Lbls['Aud-Mic-{}'.format(str(i))]
            self.__labels[str(i)].SetText(self.Microphones[str(i)]['Name'])
        
        Log('Creating events')
        # Program Buttons
        @event(list(self.__controls['prog'].values()), ['Pressed', 'Released', 'Repeated'])
        def ProgramControlHandler(button, action):
            level = self.__levels['prog']
            
            if action == 'Pressed':
                if button.CtlType == 'mute':
                    self.ProgMuteToggle()
                elif button.CtlType in ['up', 'down']:
                    button.SetState(1)
            elif action == 'Released':
                if button.CtlType in ['up', 'down']:
                    newLevelVal = self.AdjustLevel(level, button.CtlType, 'small')
                    self.ProgLevel(newLevelVal)
                    button.SetState(0)
            elif action == 'Repeated':
                newLevelVal = self.AdjustLevel(level, button.CtlType, 'large')
                self.ProgLevel(newLevelVal)
                
        # Mic Buttons
        @event(self.__mic_ctl_list, ['Pressed', 'Released', 'Repeated'])
        def MicControlHandler(button, action):
            level = self.__levels['mics'][str(button.MicNum)]
            
            if action == 'Pressed':
                if button.CtlType == 'mute':
                    self.MicMuteToggle(str(button.MicNum))
                elif button.CtlType in ['up', 'down']:
                    button.SetState(1)
            elif action == 'Released':
                if button.CtlType in ['up', 'down']:
                    newLevelVal = self.AdjustLevel(level, button.CtlType, 'small')
                    self.MicLevel(str(button.MicNum), newLevelVal)
                    button.SetState(0)
            elif action == 'Repeated':
                newLevelVal = self.AdjustLevel(level, button.CtlType, 'large')
                self.MicLevel(str(button.MicNum), newLevelVal)
                
        # All Mics Mute Button
        @event(self.__controls['all-mics'], ['Pressed'])
        def AllMicsMuteHandler(button, action):
            # Log('Original Mute State: {}'.format(self.AllMicsMute))
            self.AllMicsMute = not self.AllMicsMute 
            # Log('Updated Mute State: {}'.format(self.AllMicsMute))
    
    @property
    def AllMicsMute(self)->bool:
        test = True
        for mic in self.Microphones.values():
            if not mic['mute']:
                # Log('Microphone ({}) not muted'.format(mic['Id']))
                test = False
        return test
    
    @AllMicsMute.setter
    def AllMicsMute(self, state: Union[str, bool]):
        if not (type(state) is bool or (type(state) is str and state in ['on', 'off'])):
            raise TypeError('Mute State must be boolean or "on" or "off"')
        
        if state == True or state == 'on':
            Log('Muting all mics')
            state = True
        else:
            Log('Unmuting all mics')
            state = False
        
        for numStr in self.Microphones.keys():
            self.MicMute(numStr, state)
    
    def AllMicsMuteButtonState(self):
        if self.AllMicsMute:
            self.__controls['all-mics'].SetBlinking('Medium', [1,2])
        else:
            self.__controls['all-mics'].SetState(0)
    
    def AdjustLevel(self, level, direction: str='up', step: str='small'):
        if step == 'small':
            s = self.__step_sm
        elif step == 'large':
            s = self.__step_lg
        
        if direction == 'up':
            newLevel = level.Level + s
        elif direction == 'down':
            newLevel = level.Level - s
            
        level.SetLevel(newLevel)
        
        return newLevel
    
    def AudioStartUp(self):
        # Set default levels & unmute all sources
        self.__levels['prog'].SetLevel(self.DSP.Program['StartUp'])
        self.ProgLevel(self.DSP.Program['StartUp'])
        
        for numStr, mic in self.Microphones.items():
            self.__levels['mics'][numStr].SetLevel(mic['Control']['level']['StartUp'])
            self.MicLevel(numStr, mic['Control']['level']['StartUp'])
        
        self.ProgMute(False)
        self.AllMicsMute = False
    
    def AudioShutdown(self):
        # Mute all sources
        self.ProgMute(True)
        self.AllMicsMute = True
    
    def ProgMute(self, State: bool=False):
        if type(State) is not bool:
            raise TypeError('State must be an boolean')
        
        btn = self.__controls['prog']['mute']
        hwCmd = self.DSP.ProgramMuteCommand
        qual = hwCmd.get('qualifier', None)
        value = 'On' if State else 'Off'
        
        self.__ProgMute = State
        
        if State:
            btn.SetBlinking('Medium', [1,2])
        else:
            btn.SetState(0)
            
        self.DSP.interface.Set(hwCmd['command'], value, qual)
    
    def ProgMuteToggle(self):
        toggleState = not self.__ProgMute
        self.ProgMute(toggleState)
    
    def ProgLevel(self, Value: int):
        if type(Value) is not int:
            raise TypeError('Value must be an integer')
        
        hwCmd = self.DSP.ProgramLevelCommand
        qual = hwCmd.get('qualifier', None)
        
        self.DSP.interface.Set(hwCmd['command'], Value, qual)
    
    def MicMute(self, MicNum, State: bool=False):
        if type(State) is not bool:
            raise TypeError('State must be an boolean')
        
        mic = self.Microphones[str(MicNum)]
        btn = self.__controls['mics'][str(MicNum)]['mute']
        
        cmd = mic['Control']['mute']
        hw = self.GUIHost.Hardware[cmd['HwId']]
        hwCmd = getattr(hw, cmd['HwCmd'])
        qual = hwCmd.get('qualifier', None)
        value = 'On' if State else 'Off'
        
        mic['mute'] = State
        
        if State:
            btn.SetBlinking('Medium', [1,2])
        else:
            btn.SetState(0)
        
        hw.interface.Set(hwCmd['command'], value, qual)
        self.AllMicsMuteButtonState()
        
    def MicMuteToggle(self, MicNum):
        toggleState = not self.Microphones[str(MicNum)]['mute']
        self.MicMute(MicNum, toggleState)
    
    def MicLevel(self, MicNum, Value: int):
        if type(Value) is not int:
            raise TypeError('Value must be an integer')
        
        mic = self.Microphones[str(MicNum)]
        cmd = mic['Control']['level']
        hw = self.GUIHost.Hardware[cmd['HwId']]
        hwCmd = getattr(hw, cmd['HwCmd'])
        qual = hwCmd.get('qualifier', None)
        
        hw.interface.Set(hwCmd['command'], Value, qual)
    
    def AudioLevelFeedback(self, tag: Tuple, value: int):
        # Log("Audio Level Feedback - Tag: {}; Value: {}".format(tag, value))
        if tag[0] == 'prog':
            # Log('Prog Level Feedback')
            if not (self.__controls[tag[0]]['up'].PressedState or self.__controls[tag[0]]['down'].PressedState):
                self.__levels[tag[0]].SetLevel(int(value))
        elif tag[0] == 'mics':
            # Log('Mic Level Feedback')
            if not (self.__controls[tag[0]][tag[1]]['up'].PressedState or self.__controls[tag[0]][tag[1]]['down'].PressedState):
                self.__levels[tag[0]][tag[1]].SetLevel(int(value))
    
    def AudioMuteFeedback(self, tag: Tuple, state: str):
        # Log("Audio Mute Feedback - Tag: {}; State: {}".format(tag, state))
        if tag[0] == 'prog':
            # Log('Prog Mute Feedback')
            if state in ['On', 'on', 'Muted', 'muted']:
                # Log('Prog Mute On')
                if self.__controls[tag[0]]['mute'].BlinkState == 'Not blinking':
                    self.__controls[tag[0]]['mute'].SetBlinking('Medium', [1,2])
                self.__ProgMute = True
            elif state in ['Off', 'off', 'Unmuted', 'unmuted']:
                # Log('Prog Mute Off')
                if self.__controls[tag[0]]['mute'].BlinkState == 'Blinking':
                    self.__controls[tag[0]]['mute'].SetState(0)
                self.__ProgMute = False
        elif tag[0] == 'mics':
            # Log('Mic {} Mute Feedback'.format(tag[1]))
            if state in ['On', 'on', 'Muted', 'muted']:
                # Log('Mic {} Mute On'.format(tag[1]))
                if self.__controls[tag[0]][tag[1]]['mute'].BlinkState == 'Not blinking':
                    self.__controls[tag[0]][tag[1]]['mute'].SetBlinking('Medium', [1,2])
                self.Microphones[tag[1]]['mute'] = True
            elif state in ['Off', 'off', 'Unmuted', 'unmuted']:
                # Log('Mic {} Mute On'.format(tag[1]))
                if self.__controls[tag[0]][tag[1]]['mute'].BlinkState == 'Blinking':
                    self.__controls[tag[0]][tag[1]]['mute'].SetState(0)
                self.Microphones[tag[1]]['mute'] = False
            self.AllMicsMuteButtonState()

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------