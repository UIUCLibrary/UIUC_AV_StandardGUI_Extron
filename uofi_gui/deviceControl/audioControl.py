from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    
## Begin ControlScript Import --------------------------------------------------
from extronlib import event
from extronlib.ui import Button, Label, Level

## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------

import math

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
        
        self.__GainControls = \
            {
                'inputs': [
                    {
                        'up': self.UIHost.Btns['AudIn1-Gain-Up'],
                        'down': self.UIHost.Btns['AudIn1-Gain-Dn'],
                        'phantom': self.UIHost.Btns['AudIn1-Phantom'],
                        'dBLbl': self.UIHost.Lbls['AudIn1-Gain'],
                        'inputLbl': self.UIHost.Lbls['AudIn1-Label']
                    },
                    {
                        'up': self.UIHost.Btns['AudIn2-Gain-Up'],
                        'down': self.UIHost.Btns['AudIn2-Gain-Dn'],
                        'phantom': self.UIHost.Btns['AudIn2-Phantom'],
                        'dBLbl': self.UIHost.Lbls['AudIn2-Gain'],
                        'inputLbl': self.UIHost.Lbls['AudIn2-Label']
                    },
                    {
                        'up': self.UIHost.Btns['AudIn3-Gain-Up'],
                        'down': self.UIHost.Btns['AudIn3-Gain-Dn'],
                        'phantom': self.UIHost.Btns['AudIn3-Phantom'],
                        'dBLbl': self.UIHost.Lbls['AudIn3-Gain'],
                        'inputLbl': self.UIHost.Lbls['AudIn3-Label']
                    },
                    {
                        'up': self.UIHost.Btns['AudIn4-Gain-Up'],
                        'down': self.UIHost.Btns['AudIn4-Gain-Dn'],
                        'phantom': self.UIHost.Btns['AudIn4-Phantom'],
                        'dBLbl': self.UIHost.Lbls['AudIn4-Gain'],
                        'inputLbl': self.UIHost.Lbls['AudIn4-Label']
                    },
                    {
                        'up': self.UIHost.Btns['AudIn5-Gain-Up'],
                        'down': self.UIHost.Btns['AudIn5-Gain-Dn'],
                        'phantom': self.UIHost.Btns['AudIn5-Phantom'],
                        'dBLbl': self.UIHost.Lbls['AudIn5-Gain'],
                        'inputLbl': self.UIHost.Lbls['AudIn5-Label']
                    },
                    {
                        'up': self.UIHost.Btns['AudIn6-Gain-Up'],
                        'down': self.UIHost.Btns['AudIn6-Gain-Dn'],
                        'phantom': self.UIHost.Btns['AudIn6-Phantom'],
                        'dBLbl': self.UIHost.Lbls['AudIn6-Gain'],
                        'inputLbl': self.UIHost.Lbls['AudIn6-Label']
                    }
                ],
                'page':
                    {
                        'next': self.UIHost.Btns['AudioInput-Page-Up'],
                        'prev': self.UIHost.Btns['AudioInput-Page-Down'],
                        'currentLbl': self.UIHost.Lbls['AudioInput-Page-Current'],
                        'maxLbl': self.UIHost.Lbls['AudioInput-Page-Max'],
                        'divLbl': self.UIHost.Lbls['AudioInput-Page-Div']
                    }                    
            }
        
        self.__GainControlLists = \
            {
                'up': [],
                'down': [],
                'phantom': [],
                'dBLbl': [],
                'inputLbl': []
            }
        for inputDict in self.__GainControls['inputs']:
            for key in inputDict.keys():
                if type(inputDict[key]) is Button:
                    inputDict[key].CtlType = key
                if key == 'dBLbl':
                    inputDict[key].GainVal = 0
                inputDict[key].InputIndex = self.__GainControls['inputs'].index(inputDict)
                self.__GainControlLists[key].append(inputDict[key])
        
        self.__GainPageIndex = 0
        
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
            
        # Gain Buttons
        gainCtls = []
        gainCtls.extend(self.__GainControlLists['up'])
        gainCtls.extend(self.__GainControlLists['down'])
        @event(gainCtls, ['Pressed', 'Released', 'Repeated']) # pragma: no cover
        def GainControlsHandler(button: 'Button', action: str):
            self.__InputGainHandler(button, action)
            
        # Phantom Power Buttons
        @event(self.__GainControlLists['phantom'], ['Pressed']) # pragma: no cover
        def PhantomControlsHandler(button: 'Button', action: str):
            self.__InputPhantomHandler(button, action)
            
        # Gain Controls Pagination Buttons
        @event([self.__GainControls['page']['next'], self.__GainControls['page']['prev']], ['Pressed', 'Released']) # pragma: no cover
        def GainControlPaginationHandler(button: 'Button', action: str):
            self.__PaginationHandler(button, action)
    
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
    
    @property
    def __InputCount(self) -> int:
        return len(self.DSP.InputControls)
    
    @property
    def __GainPageCount(self) -> int:
        return math.ceil(self.__InputCount / 6)
    
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
    
    def __PaginationHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            button.SetState(0)
            if button.Name.endswith('Up'):
                # do page up
                self.__GainPageIndex += 1
                if self.__GainPageIndex >= self.__GainPageCount:
                    self.__GainPageIndex = self.__GainPageCount
            elif button.Name.endswith('Down'):
                # do page down
                self.__GainPageIndex -= 1
                if self.__GainPageIndex < 0:
                    self.__GainPageIndex = 0
                    
        self.__UpdatePagination()
        self.__ShowInputState()
        
    def __InputGainHandler(self, button: 'Button', action: str):
        inputIndex = button.InputIndex + (self.__GainPageIndex * 6)
        #Log('Gain Control: {}, {}'.format(button.CtlType, inputIndex))
        if not button.Enabled: # pragma: no cover
            return
        
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released' or action == 'Repeated':
            if action == 'Released':
                button.SetState(0)
            elif action == 'Repeated':
                self.UIHost.Click()
            cmd = self.DSP.InputControls[inputIndex]['GainCommand']
            block = self.DSP.InputControls[inputIndex]['Block']
            channel = self.DSP.InputControls[inputIndex]['Channel']
            qual = self.__GetCmdQualifier(cmd, block, channel)
            newVal = self.AdjustGain(self.__GainControlLists['dBLbl'][inputIndex], button.CtlType)
            self.DSP.interface.Set(cmd, newVal, qual)
    
    def __InputPhantomHandler(self, button: 'Button', action: str):
        inputIndex = button.InputIndex + (self.__GainPageIndex * 6)
        # Log('Phantom Control: {}, {}'.format(button.State, inputIndex))
        
        cmd = self.DSP.InputControls[inputIndex]['PhantomCommand']
        block = self.DSP.InputControls[inputIndex]['Block']
        channel = self.DSP.InputControls[inputIndex]['Channel']
        qual = self.__GetCmdQualifier(cmd, block, channel)
        
        if button.State == 0:
            self.DSP.interface.Set(cmd, 'On', qual)
            button.SetState(1)
        elif button.State == 1:
            self.DSP.interface.Set(cmd, 'Off', qual)
            button.SetState(0)
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __UpdatePagination(self):
        if self.__GainPageCount == 1:
            # No page flips. Show no pagination
            self.__GainControls['page']['next'].SetEnable(False)
            self.__GainControls['page']['next'].SetVisible(False)
            self.__GainControls['page']['prev'].SetEnable(False)
            self.__GainControls['page']['prev'].SetVisible(False)
            
            self.__GainControls['page']['currentLbl'].SetVisible(False)
            self.__GainControls['page']['maxLbl'].SetVisible(False)
            self.__GainControls['page']['divLbl'].SetVisible(False)
            
        elif self.__GainPageCount > 1 and self.__GainPageIndex == 0:
            # Show page flips, disable prev button
            self.__GainControls['page']['next'].SetEnable(True)
            self.__GainControls['page']['next'].SetVisible(True)
            self.__GainControls['page']['prev'].SetEnable(False)
            self.__GainControls['page']['prev'].SetVisible(True)
            
            self.__GainControls['page']['next'].SetState(0)
            self.__GainControls['page']['prev'].SetState(2)
            
            self.__GainControls['page']['currentLbl'].SetVisible(True)
            self.__GainControls['page']['currentLbl'].SetText(str(self.__GainPageIndex + 1))
            self.__GainControls['page']['maxLbl'].SetVisible(True)
            self.__GainControls['page']['maxLbl'].SetText(str(self.__GainPageCount))
            self.__GainControls['page']['divLbl'].SetVisible(True)
            
        elif self.__GainPageCount > 1 and (self.__GainPageIndex + 1) == self.__GainPageCount:
            # Show page flips, disable next button
            self.__GainControls['page']['next'].SetEnable(False)
            self.__GainControls['page']['next'].SetVisible(True)
            self.__GainControls['page']['prev'].SetEnable(True)
            self.__GainControls['page']['prev'].SetVisible(True)
            
            self.__GainControls['page']['next'].SetState(2)
            self.__GainControls['page']['prev'].SetState(0)
            
            self.__GainControls['page']['currentLbl'].SetVisible(True)
            self.__GainControls['page']['currentLbl'].SetText(str(self.__GainPageIndex + 1))
            self.__GainControls['page']['maxLbl'].SetVisible(True)
            self.__GainControls['page']['maxLbl'].SetText(str(self.__GainPageCount))
            self.__GainControls['page']['divLbl'].SetVisible(True)
            
        elif self.__GainPageCount > 1:
            # Show page flips, both arrows enabled
            self.__GainControls['page']['next'].SetEnable(True)
            self.__GainControls['page']['next'].SetVisible(True)
            self.__GainControls['page']['prev'].SetEnable(True)
            self.__GainControls['page']['prev'].SetVisible(True)
            
            self.__GainControls['page']['next'].SetState(0)
            self.__GainControls['page']['prev'].SetState(0)
            
            self.__GainControls['page']['currentLbl'].SetVisible(True)
            self.__GainControls['page']['currentLbl'].SetText(str(self.__GainPageIndex + 1))
            self.__GainControls['page']['maxLbl'].SetVisible(True)
            self.__GainControls['page']['maxLbl'].SetText(str(self.__GainPageCount))
            self.__GainControls['page']['divLbl'].SetVisible(True)
    
    # def __ClearInputState(self):
    #     for key in self.__GainControlLists.keys():
    #         for ctl in self.__GainControlLists[key]:
    #             if type(ctl) is Button:
    #                 ctl.SetEnable(False)
    #                 ctl.SetState(2)
    #             elif type(ctl) is Label and key == 'dBLbl':
    #                 ctl.SetText('--')
    #             elif type(ctl) is Label and key == 'inputLbl':
    #                 ctl.SetText('No Input Configured')
    
    def __GetCmdQualifier(self, command: str, block: str, channel: Union[str, int]) -> dict:
        if self.DSP.Manufacturer == "Biamp":
            return {'Instance Tag': str(block), 'Channel': str(channel)}
        elif self.DSP.Manufacturer == "BSS":
            if command == 'Gain':
                id = 4 + ((int(channel) - 1) * 6)
            elif command == 'PhantomSwitch':
                id = 5 + ((int(channel) - 1) * 6)
            else:
                raise ValueError('BSS DSP Command ({}) not configured'.format(command))
            return {'HiQAddress': str(block), 'ID': id}
        else:
            raise ValueError('DSP Manufacturer ({}) not configured'.format(self.DSP.Manufacturer))
    
    def __ShowInputState(self):
        mfg = self.DSP.Manufacturer
        # self.__ClearInputState()
        
        indexStart = self.__GainPageIndex * 6
        indexEnd = ((self.__GainPageIndex + 1) * 6) # add one because range() is non-inclusive of the end index value
        Log('Loading Audio Tech Page: {} - {}'.format(indexStart, indexEnd))
        displayList = []
        for i in range(indexStart, indexEnd):
            if i >= self.__InputCount:
                break
            displayList.append(self.DSP.InputControls[i])
            
        if len(displayList) < 6:
            loadRange = len(displayList)
        else:
            loadRange = 6
            
        for j in range(loadRange):
            input = displayList[j]
            inputLbl = self.__GainControlLists['inputLbl'][j]
            dbLbl = self.__GainControlLists['dBLbl'][j]
            upBtn = self.__GainControlLists['up'][j]
            dnBtn = self.__GainControlLists['down'][j]
            phantomBtn = self.__GainControlLists['phantom'][j]
            
            inputLbl.SetText(input['Name'])
            
            upBtn.Block = input['Block']
            upBtn.Channel = input['Channel']
            upBtn.Cmd = input['GainCommand']
            dnBtn.Block = input['Block']
            dnBtn.Channel = input['Channel']
            dnBtn.Cmd = input['GainCommand']
            phantomBtn.Block = input['Block']
            phantomBtn.Channel = input['Channel']
            phantomBtn.Cmd = input['PhantomCommand']
            
            # get initial values
            qual_dB = self.__GetCmdQualifier(input['GainCommand'], input['Block'], input['Channel'])
            dB = self.DSP.interface.ReadStatus(input['GainCommand'], qual_dB)
            Log('dB Value: {}'.format(dB))
            if dB is None:
                self.DSP.interface.Update(input['GainCommand'], qual_dB)
                dB = self.DSP.interface.ReadStatus(input['GainCommand'], qual_dB)
                Log('Retry dB Value: {}'.format(dB))
            
            if mfg == 'BSS':
                dB = (dB/100)*48
            
            downEnable = True
            upEnable = True
            if dB == 0 or dB is None:
                dbLbl.SetText('0dB')
                dbLbl.GainVal = dB
                downEnable = False
                dB = 0
            elif dB > 0:
                dbLbl.SetText('+{}dB'.format(dB))
                dbLbl.GainVal = dB
            
            if mfg == 'Biamp' and dB >= 66:
                upEnable = False
            if mfg == 'BSS' and dB >= 48:
                upEnable = False
            
            if upEnable:
                upBtn.SetState(0)
            else:
                upBtn.SetState(2)
            upBtn.SetEnable(upEnable)
            if downEnable:
                dnBtn.SetState(0)
            else:
                dnBtn.SetState(2)
            dnBtn.SetEnable(downEnable)
                
            qual_phan = self.__GetCmdQualifier(input['PhantomCommand'], input['Block'], input['Channel'])
            phantom = self.DSP.interface.ReadStatus(input['PhantomCommand'], qual_phan)
            if phantom is None:
                self.DSP.interface.Update(input['PhantomCommand'], qual_phan)
                phantom = self.DSP.interface.ReadStatus(input['PhantomCommand'], qual_phan)
            setState = (phantom in ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE'])
            
            phantomBtn.SetState(int(setState))
            phantomBtn.SetEnable(True)
    
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
    
    def AdjustGain(self, gain, direction: str='up'):
        if type(gain) is not Label:
            raise TypeError('Level must be a Gain Label object')
        if type(direction) is not str:
            raise TypeError('Direction must be a string')
        
        mfg = self.DSP.Manufacturer
        inputIndex = self.__GainControlLists['dBLbl'].index(gain)
        
        if direction == 'up':
            newGain = gain.GainVal + 6
        elif direction == 'down':
            newGain = gain.GainVal - 6
        else:
            raise ValueError('Direction must either be "up" or "down"')
        
        downEnable = True
        upEnable = True
        
        if newGain <= 0:
            # disable down arrow
            downEnable = False
            newGain = 0
        
        if mfg == 'Biamp':
            newLevel = newGain
            if newGain >= 66:
                upEnable = False
        elif mfg == 'BSS':
            # BSS require gain in a percentage value
            newLevel = (newGain / 48) * 100
            if newGain >= 48:
                upEnable = False
        
        
        gain.GainVal = newGain
        
        self.__GainControlLists['down'][inputIndex].SetEnable(downEnable)
        if downEnable:
            self.__GainControlLists['down'][inputIndex].SetState(0)
        else:
            self.__GainControlLists['down'][inputIndex].SetState(2)
            
        self.__GainControlLists['up'][inputIndex].SetEnable(upEnable)
        if upEnable:
            self.__GainControlLists['up'][inputIndex].SetState(0)
        else:
            self.__GainControlLists['up'][inputIndex].SetState(2)
        
        if newGain == 0:
            gain.SetText("0dB")
        elif newGain > 0:
            gain.SetText('+{}dB'.format(newGain))
        
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
    
    def ResetGainPage(self):
        self.__GainPageIndex = 0
        self.__UpdatePagination()
        self.__ShowInputState()
    
    def AudioLevelFeedback(self, tag: Tuple, value: int):
        Log("Audio Level Feedback - Tag: {}; Value: {}".format(tag, value))
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

    def AudioGainFeedback(self, qualifier, value):
        Log('Gain Feedback Received: qual={}; val={}'.format(qualifier, value))
        mfg = self.DSP.Manufacturer
        
        feedbackIndex = None
        for inputCtl in self.DSP.InputControls:
            if mfg == 'Biamp' and inputCtl['Block'] == qualifier['Instance Tag'] and inputCtl['Channel'] == qualifier['Channel']:
                feedbackIndex = self.DSP.InputControls.index(inputCtl)
            elif mfg == 'BSS' and inputCtl['Block'] == qualifier['HiQAddress'] and (4 + ((int(inputCtl['Channel']) - 1) * 6)) == qualifier['ID']:
                feedbackIndex = self.DSP.InputControls.index(inputCtl)
        
        if mfg == 'Biamp':
            value = int(value)
        elif mfg == 'BSS':
            value = (int(value)/100) * 48
        
        if value == 0:
            self.__GainControlLists['dBLbl'][feedbackIndex].SetText("0dB")
        elif value > 0:
            self.__GainControlLists['dBLbl'][feedbackIndex].SetText('+{}dB'.format(value))

        downEnable = True
        upEnable = True
        if value <= 0:
            # disable down arrow
            downEnable = False
        
        if mfg == 'Biamp' and value >= 66:
            upEnable = False
        elif mfg == 'BSS' and value >= 48:
            upEnable = False
            
        self.__GainControlLists['up'][feedbackIndex].SetEnable(upEnable)
        if upEnable:
            self.__GainControlLists['up'][feedbackIndex].SetState(0)
        else:
            self.__GainControlLists['up'][feedbackIndex].SetState(2)
            
        self.__GainControlLists['down'][feedbackIndex].SetEnable(downEnable)
        if downEnable:
            self.__GainControlLists['down'][feedbackIndex].SetState(0)
        else:
            self.__GainControlLists['down'][feedbackIndex].SetState(2)
        
    def AudioPhantomFeedback(self, qualifier, value):
        Log('Phantom Feedback Received: qual={}; val={}'.format(qualifier, value))
        mfg = self.DSP.Manufacturer
        
        feedbackIndex = None
        for inputCtl in self.DSP.InputControls:
            if mfg == 'Biamp' and inputCtl['Block'] == qualifier['Instance Tag'] and inputCtl['Channel'] == qualifier['Channel']:
                feedbackIndex = self.DSP.InputControls.index(inputCtl)
            elif mfg == 'BSS' and inputCtl['Block'] == qualifier['HiQAddress'] and (4 + ((int(inputCtl['Channel']) - 1) * 6)) == qualifier['ID']:
                feedbackIndex = self.DSP.InputControls.index(inputCtl)
                
        setState = (value in ['on', 'On', 'ON', 1, True])
        
        self.__GainControlLists['phantom'][feedbackIndex].SetState(int(setState))
        
## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------

## End Function Definitions ----------------------------------------------------