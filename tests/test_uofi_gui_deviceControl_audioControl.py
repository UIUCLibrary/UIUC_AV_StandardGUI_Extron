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

import unittest
from unittest.mock import MagicMock
import os
import importlib

import sys
sys.path.append(".\\src")
sys.path.append(".\\tests")
sys.path.append(".\\tests\\reqs")


## test imports ----------------------------------------------------------------
from uofi_gui import SystemController
from uofi_gui.uiObjects import ExUIDevice
from DevelopmentProject.src.modules.project.systemHardware import SystemHardwareController
from uofi_gui.deviceControl import AudioController, CameraController, DisplayController
from uofi_gui.sourceControls import Destination
import test_settings as settings

from extronlib.device import UIDevice
from extronlib.ui import Button, Label, Level, Slider
from extronlib.system import MESet, File
## -----------------------------------------------------------------------------

class AudioController_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        importlib.reload(settings)
        self.TestGUIController = SystemController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestAudController = self.TestUIController.AudioCtl
        return super().setUp()
    
    def test_AudioController_Type(self):
        self.assertIsInstance(self.TestAudController, AudioController)
    
    def test_AudioController_Properties(self):
        # UIHost
        with self.subTest(param='UIHost'):
            self.assertIsInstance(self.TestAudController.UIHost, (UIDevice, ExUIDevice))
        
        # GUIHost
        with self.subTest(param='GUIHost'):
            self.assertIsInstance(self.TestAudController.GUIHost, SystemController)
        
        # DSP
        with self.subTest(param='DSP'):
            self.assertIsInstance(self.TestAudController.DSP, SystemHardwareController)
        
        # Microphones
        with self.subTest(param='Microphones'):
            self.assertIsInstance(self.TestAudController.Microphones, dict)
            for key, value in self.TestAudController.Microphones.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, dict)
        
        # AllMicsMute
        with self.subTest(param='AllMicsMute'):
            self.assertIsInstance(self.TestAudController.AllMicsMute, bool)
        
        # MicMute
        with self.subTest(param='MicMute'):
            self.assertIsInstance(self.TestAudController.MicMute, dict)
            for key, value in self.TestAudController.MicMute.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, bool)
        
        # MicLevel
        with self.subTest(param='MicLevel'):
            self.assertIsInstance(self.TestAudController.MicLevel, dict)
            for key, value in self.TestAudController.MicLevel.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, (int, float, type(None)))
        
        # ProgMute
        with self.subTest(param='ProgMute'):
            self.assertIsInstance(self.TestAudController.ProgMute, bool)
        
        # ProgLevel
        with self.subTest(param='ProgLevel'):
            self.assertIsInstance(self.TestAudController.ProgLevel, (int, float, type(None)))
    
    def test_AudioController_PRIV_Properties(self):
        # __StepSm
        with self.subTest(param='__StepSm'):
            self.assertIsInstance(self.TestAudController._AudioController__StepSm, int)
        
        # __StepLg
        with self.subTest(param='__StepLg'):
            self.assertIsInstance(self.TestAudController._AudioController__StepLg, int)
        
        # __ProgMute
        with self.subTest(param='__ProgMute'):
            self.assertIsInstance(self.TestAudController._AudioController__ProgMute, bool)
        
        # __Levels
        with self.subTest(param='__Levels'):
            self.assertIsInstance(self.TestAudController._AudioController__Levels, dict)
            for key, value in self.TestAudController._AudioController__Levels.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, (Level, dict))
                    if type(value) is dict:
                        for key2, value2 in value.items():
                            with self.subTest(key2=key2, value2=value2):
                                self.assertIsInstance(key2, str)
                                self.assertIsInstance(value2, Level)
        
        # __Labels
        with self.subTest(param='__Labels'):
            self.assertIsInstance(self.TestAudController._AudioController__Labels, dict)
            for key, value in self.TestAudController._AudioController__Labels.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, Label)
        
        # __MicCtlList
        with self.subTest(param='__MicCtlList'):
            self.assertIsInstance(self.TestAudController._AudioController__MicCtlList, list)
            for value in self.TestAudController._AudioController__MicCtlList:
                with self.subTest(value=value):
                    self.assertIsInstance(value, Button)
        
        # __Controls
        with self.subTest(param='__Controls'):
            self.assertIsInstance(self.TestAudController._AudioController__Controls, dict)
            for key, value in self.TestAudController._AudioController__Controls.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, (dict, Button))
                    if type(value) is dict:
                        for key2, value2 in value.items():
                            with self.subTest(key2=key2, value2=value2):
                                self.assertIsInstance(key2, str)
                                self.assertIsInstance(value2, (dict, Button))
                                if type(value2) is dict:
                                    for key3, value3 in value2.items():
                                        with self.subTest(key3=key3, value3=value3):
                                            self.assertIsInstance(key3, str)
                                            self.assertIsInstance(value3, Button)
        
        # __GainControls
        with self.subTest(param='__GainControls'):
            self.assertIsInstance(self.TestAudController._AudioController__GainControls, dict)
            for key1, value1 in self.TestAudController._AudioController__GainControls.items():
                with self.subTest(key1=key1, value1=value1):
                    self.assertIsInstance(key1, str)
                    self.assertIsInstance(value1, (dict, list))
                    if type(value1) is dict:
                        for key2, value2 in value1.items():
                            with self.subTest(key2=key2, value2=value2):
                                self.assertIsInstance(key2, str)
                                self.assertIsInstance(value2, (Button, Label))
                    elif type(value1) is list:
                        for item in value1:
                            with self.subTest(item=item):
                                self.assertIsInstance(item, dict)
                                for key3, value3 in item.items():
                                    with self.subTest(key3=key3, value3=value3):
                                        self.assertIsInstance(key3, str)
                                        self.assertIsInstance(value3, (Button, Label))
                                        
        # __GainControlLists
        with self.subTest(param='__GainControlsLists'):
            self.assertIsInstance(self.TestAudController._AudioController__GainControlLists, dict)
            for key, value in self.TestAudController._AudioController__GainControlLists.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, list)
                    for item in value:
                        with self.subTest(item=item):
                            self.assertIsInstance(item, (Button, Label))
                            
        # __GainPageIndex
        with self.subTest(param='__GainPageIndex'):
            self.assertIsInstance(self.TestAudController._AudioController__GainPageIndex, int)
            
        # __InputCount
        with self.subTest(param='__InputCount'):
            self.assertIsInstance(self.TestAudController._AudioController__InputCount, int)
            
        # __GainPageCount
        with self.subTest(param='__GainPageCount'):
            self.assertIsInstance(self.TestAudController._AudioController__GainPageCount, int)
    
    def test_AudioController_EventHandler_ProgramControlHandler(self):
        btnList = list(self.TestAudController._AudioController__Controls['prog'].values())
        actList = ['Pressed', 'Released', 'Repeated']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestAudController._AudioController__ProgramControlHandler(btn, act)
                    except Exception as inst:
                        self.fail('__ProgramControlHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_EventHandler_MicControlHandler(self):
        btnList = self.TestAudController._AudioController__MicCtlList
        actList = ['Pressed', 'Released', 'Repeated']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestAudController._AudioController__MicControlHandler(btn, act)
                    except Exception as inst:
                        self.fail('__MicControlHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_EventHandler_PaginationHandler(self):
        btnList = [self.TestAudController._AudioController__GainControls['page']['next'], self.TestAudController._AudioController__GainControls['page']['prev']]
        actList = ['Pressed', 'Released']
        conList = range(self.TestAudController._AudioController__GainPageCount)
        
        for con in conList:
            for btn in btnList:
                for act in actList:
                    with self.subTest(button=btn.Name, action=act, context=con):
                        try:
                            self.TestAudController._AudioController__GainPageIndex = con
                            self.TestAudController._AudioController__PaginationHandler(btn, act)
                        except Exception as inst:
                            self.fail('__PaginationHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_EventHandler_InputGainHandler(self):
        btnList = []
        btnList.extend(self.TestAudController._AudioController__GainControlLists['up'])
        btnList.extend(self.TestAudController._AudioController__GainControlLists['down'])
        actList = ['Pressed', 'Released', 'Repeated']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestAudController._AudioController__InputGainHandler(btn, act)
                    except Exception as inst:
                        self.fail('__InputGainHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_EventHandler_InputPhantomHandler(self):
        btnList = self.TestAudController._AudioController__GainControlLists['phantom']
        actList = ['Pressed', 'Released']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestAudController._AudioController__InputPhantomHandler(btn, act)
                    except Exception as inst:
                        self.fail('__InputPhantomHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_DynProp_AllMicsMute(self):
        stateList = ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE', 'off', 'Off', 'OFF', 0, False, 'Unmute', 'unmute', 'UNMUTE']
        
        for state in stateList:
            with self.subTest(state=state):
                try:
                    self.TestAudController.AllMicsMute = state
                except Exception as inst:
                    self.fail('AllMicsMute setter raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_DynProp_AllMicsMute_BadInput(self):
        stateList = [('1', False), [1, True], {2: 'mute'}, 1.1]
        
        for state in stateList:
            with self.subTest(state=state):
                with self.assertRaises(TypeError):
                    self.TestAudController.AllMicsMute = state
                    
    def test_AudioController_DynProp_ProgMute(self):
        stateList = ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE', 'off', 'Off', 'OFF', 0, False, 'Unmute', 'unmute', 'UNMUTE']
        
        for state in stateList:
            with self.subTest(state=state):
                try:
                    self.TestAudController.ProgMute = state
                except Exception as inst:
                    self.fail('ProgMute setter raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_DynProp_ProgLevel(self):
        stateList = [1, 2.5, 15, 67.333]
        
        for state in stateList:
            with self.subTest(state=state):
                try:
                    self.TestAudController.ProgLevel = state
                except Exception as inst:
                    self.fail('ProgLevel setter raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_DynProp_ProgLevel_BadInput(self):
        stateList = ['on', True, None, (1,), [1, 2], {'Level': 5}]
        
        for state in stateList:
            with self.subTest(state=state):
                with self.assertRaises(TypeError):
                    self.TestAudController.ProgLevel = state
    
    def test_AudioController_DynProp_MicMute(self):
        stateList = ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE', 'off', 'Off', 'OFF', 0, False, 'Unmute', 'unmute', 'UNMUTE']
        
        for micNum in range(1,3):
            for state in stateList:
                with self.subTest(state=state, mic=micNum):
                    try:
                        self.TestAudController.MicMute = (micNum, state)
                    except Exception as inst:
                        self.fail('MicMute setter raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_DynProp_MicMute_BadMic(self):
        stateList = ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE', 'off', 'Off', 'OFF', 0, False, 'Unmute', 'unmute', 'UNMUTE']
        
        for state in stateList:
            with self.subTest(state=state):
                with self.assertRaises(KeyError):
                    self.TestAudController.MicMute = (3, state)
    
    def test_AudioController_DynProp_MicMute_BadInput(self):
        contextList = ['on', True, ('1', False), 0, 1, [1, True], {2: 'mute'}]
        
        for con in contextList:
            with self.subTest(context=con):
                with self.assertRaises(TypeError):
                    self.TestAudController.MicMute = con
        
    def test_AudioController_DynProp_MicLevel(self):
        stateList = [1, 2.5, 15, 67.333]
        
        for micNum in range(1,3):
            for state in stateList:
                with self.subTest(state=state, mic=micNum):
                    try:
                        self.TestAudController.MicLevel = (micNum, state)
                    except Exception as inst:
                        self.fail('MicLevel setter raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_DynProp_MicLevel_BadMic(self):
        stateList = ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE', 'off', 'Off', 'OFF', 0, False, 'Unmute', 'unmute', 'UNMUTE']
        
        for state in stateList:
            with self.subTest(state=state):
                with self.assertRaises(KeyError):
                    self.TestAudController.MicMute = (3, state)
    
    def test_AudioController_DynProp_MicLevel_BadInput(self):
        contextList = ['on', True, ('1', False), 0, 1, [1, True], {2: 'mute'}]
        
        for con in contextList:
            with self.subTest(context=con):
                with self.assertRaises(TypeError):
                    self.TestAudController.MicLevel = con
    
    def test_AudioController_PRIV_UpdatePagination_Multipage(self):
        inputControls = self.TestAudController.DSP.InputControls
        while self.TestAudController._AudioController__GainPageCount < 3:
            self.TestAudController.DSP.InputControls.extend(inputControls)
        for i in range(self.TestAudController._AudioController__GainPageCount):
            with self.subTest(pageindex=i):
                try:
                    self.TestAudController._AudioController__GainPageIndex = i
                    self.TestAudController._AudioController__UpdatePagination()
                except Exception as inst:
                    self.fail('__UpdatePagination raised {} unexpectedly!'.format(type(inst)))
                    
    def test_AudioController_PRIV_UpdatePagination_SinglePage(self):
        while self.TestAudController._AudioController__GainPageCount > 1:
            self.TestAudController.DSP.InputControls.pop()
        try:
            self.TestAudController._AudioController__IndexPageIndex = 0
            self.TestAudController._AudioController__UpdatePagination()
        except Exception as inst:
            self.fail('__UpdatePagination raised {} unexpectedly!'.format(type(inst)))
    
    # def test_AudioController_PRIV_ClearInputState(self):
    #     pass
    
    def test_AudioController_PRIV_GetCmdQualifier(self):
        mfgList = ['Biamp', 'BSS']
        commandList = ['Gain', 'PhantomSwitch']
        blockList = ['AECInput1', 'AECInput2']
        channelList = [1, 2, '3', '4']
        
        resultDict = \
            {
                'Biamp': 
                    {
                        'Gain': 
                            {
                                'AECInput1': 
                                    {
                                        1: {'Instance Tag': 'AECInput1', 'Channel': '1'},
                                        2: {'Instance Tag': 'AECInput1', 'Channel': '2'},
                                        '3': {'Instance Tag': 'AECInput1', 'Channel': '3'},
                                        '4': {'Instance Tag': 'AECInput1', 'Channel': '4'}
                                    },
                                'AECInput2': 
                                    {
                                        1: {'Instance Tag': 'AECInput2', 'Channel': '1'},
                                        2: {'Instance Tag': 'AECInput2', 'Channel': '2'},
                                        '3': {'Instance Tag': 'AECInput2', 'Channel': '3'},
                                        '4': {'Instance Tag': 'AECInput2', 'Channel': '4'}
                                    }
                            },
                        'PhantomSwitch': 
                            {
                                'AECInput1': 
                                    {
                                        1: {'Instance Tag': 'AECInput1', 'Channel': '1'},
                                        2: {'Instance Tag': 'AECInput1', 'Channel': '2'},
                                        '3': {'Instance Tag': 'AECInput1', 'Channel': '3'},
                                        '4': {'Instance Tag': 'AECInput1', 'Channel': '4'}
                                    },
                                'AECInput2': 
                                    {
                                        1: {'Instance Tag': 'AECInput2', 'Channel': '1'},
                                        2: {'Instance Tag': 'AECInput2', 'Channel': '2'},
                                        '3': {'Instance Tag': 'AECInput2', 'Channel': '3'},
                                        '4': {'Instance Tag': 'AECInput2', 'Channel': '4'}
                                    }
                            },
                    },
                'BSS': 
                    {
                        'Gain': 
                            {
                                'AECInput1': 
                                    {
                                        1: {'HiQAddress': 'AECInput1', 'ID': 4},
                                        2: {'HiQAddress': 'AECInput1', 'ID': 10},
                                        '3': {'HiQAddress': 'AECInput1', 'ID': 16},
                                        '4': {'HiQAddress': 'AECInput1', 'ID': 22}
                                    },
                                'AECInput2': 
                                    {
                                        1: {'HiQAddress': 'AECInput2', 'ID': 4},
                                        2: {'HiQAddress': 'AECInput2', 'ID': 10},
                                        '3': {'HiQAddress': 'AECInput2', 'ID': 16},
                                        '4': {'HiQAddress': 'AECInput2', 'ID': 22}
                                    }
                            },
                        'PhantomSwitch': 
                            {
                                'AECInput1': 
                                    {
                                        1: {'HiQAddress': 'AECInput1', 'ID': 5},
                                        2: {'HiQAddress': 'AECInput1', 'ID': 11},
                                        '3': {'HiQAddress': 'AECInput1', 'ID': 17},
                                        '4': {'HiQAddress': 'AECInput1', 'ID': 23}
                                    },
                                'AECInput2': 
                                    {
                                        1: {'HiQAddress': 'AECInput2', 'ID': 5},
                                        2: {'HiQAddress': 'AECInput2', 'ID': 11},
                                        '3': {'HiQAddress': 'AECInput2', 'ID': 17},
                                        '4': {'HiQAddress': 'AECInput2', 'ID': 23}
                                    }
                            },
                    }
            }
        
        for mfg in mfgList:
            for command in commandList:
                for block in blockList:
                    for channel in channelList:
                        with self.subTest(mfg=mfg, command=command, block=block, channel=channel):
                            self.TestAudController.DSP.Manufacturer = mfg
                            try:
                                res = self.TestAudController._AudioController__GetCmdQualifier(command, block, channel)
                            except Exception as inst:
                                self.fail('__GetCmdQualifier raised {} unexpectedly!'.format(type(inst)))
                            self.assertEqual(res, resultDict[mfg][command][block][channel])
    
    def test_AudioController_PRIV_GetCmdQualifier_BadBSSCmd(self):
        self.TestAudController.DSP.Manufacturer = 'BSS'
        with self.assertRaises(ValueError):
            self.TestAudController._AudioController__GetCmdQualifier('BadCommand', 'Block', '1')
    
    def test_AudioController_PRIV_GetCmdQualifier_BadMfg(self):
        self.TestAudController.DSP.Manufacturer = 'Other'
        with self.assertRaises(ValueError):
            self.TestAudController._AudioController__GetCmdQualifier('AECGain', 'Block', '1')
    
    def test_AudioController_PRIV_ShowInputState(self):
        self.DSP = MagicMock()
        self.DSP.InputControls = \
            [
                {
                    'Name': 'Program L',
                    'Block': 'AecInput1',
                    'Channel': '1',
                    'GainCommand': 'AECGain',
                    'PhantomCommand': 'AECPhantomPower'
                },
                {
                    'Name': 'Program R',
                    'Block': 'AecInput1',
                    'Channel': '2',
                    'GainCommand': 'AECGain',
                    'PhantomCommand': 'AECPhantomPower'
                },
                {
                    'Name': 'Mic - RF001',
                    'Block': 'AecInput1',
                    'Channel': '3',
                    'GainCommand': 'AECGain',
                    'PhantomCommand': 'AECPhantomPower'
                },
                {
                    'Name': 'Unused Input',
                    'Block': 'AecInput1',
                    'Channel': '4',
                    'GainCommand': 'AECGain',
                    'PhantomCommand': 'AECPhantomPower'
                },
                {
                    'Name': 'Input 5',
                    'Block': 'AecInput1',
                    'Channel': '5',
                    'GainCommand': 'AECGain',
                    'PhantomCommand': 'AECPhantomPower'
                },
                {
                    'Name': 'Input 6',
                    'Block': 'AecInput1',
                    'Channel': '6',
                    'GainCommand': 'AECGain',
                    'PhantomCommand': 'AECPhantomPower'
                },
                {
                    'Name': 'Input 7',
                    'Block': 'AecInput1',
                    'Channel': '7',
                    'GainCommand': 'AECGain',
                    'PhantomCommand': 'AECPhantomPower'
                },
                {
                    'Name': 'Input 8',
                    'Block': 'AecInput1',
                    'Channel': '8',
                    'GainCommand': 'AECGain',
                    'PhantomCommand': 'AECPhantomPower'
                },
                {
                    'Name': 'Input 9',
                    'Block': 'AecInput1',
                    'Channel': '9',
                    'GainCommand': 'AECGain',
                    'PhantomCommand': 'AECPhantomPower'
                },
                {
                    'Name': 'Input 10',
                    'Block': 'AecInput1',
                    'Channel': '10',
                    'GainCommand': 'AECGain',
                    'PhantomCommand': 'AECPhantomPower'
                },
                # {
                #     'Name': 'Input 11',
                #     'Block': 'AecInput1',
                #     'Channel': '11',
                #     'GainCommand': 'AECGain',
                #     'PhantomCommand': 'AECPhantomPower'
                # },
                # {
                #     'Name': 'Input 12',
                #     'Block': 'AecInput1',
                #     'Channel': '12',
                #     'GainCommand': 'AECGain',
                #     'PhantomCommand': 'AECPhantomPower'
                # }
            ]
        
        mfgList = ['Biamp', 'BSS']
        indexList = [0, 1]
        dataList = [(None, None), (0, 'On'), (24, 'Off'), (36, 'On'), (66, 'On')]
        
        for mfg in mfgList:
            self.DSP.Manufacturer = mfg
            for index in indexList:
                self.TestAudController._AudioController__GainPageIndex = index
                for data in dataList:
                    self.DSP.interface.ReadStatus.side_effect = lambda x: data(0) if bool(x.find('Gain')+1) else data(1)
                    try:
                        self.TestAudController._AudioController__ShowInputState()
                    except Exception as inst:
                        self.fail('__ShowInputState raised {} unexpectedly'.format(type(inst)))
    
    def test_AudioController_AllMicsMuteButtonState(self):
        contextList = ['on', 'off']
        
        for con in contextList:
            with self.subTest(context=con):
                self.TestAudController.AllMicsMute = con
                try:
                    self.TestAudController.AllMicsMuteButtonState()
                except Exception as inst:
                    self.fail('Method raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_AdjustLevel(self):
        testLevel = Level(self.TestUIController, 'testLevel')
        directionList = ['up', 'down', None]
        stepList = ['small', 'large', None]
        expectedDict = \
            {
                'up': {
                    'small': 11,
                    'large': 13,
                    None: 11
                },
                'down': {
                    'small': 9,
                    'large': 7,
                    None: 9
                },
                None: {
                    'small': 11,
                    'large': 13,
                    None: 11
                }
            }
        for dir in directionList:
            for step in stepList:
                with self.subTest(direction=dir, step=step):
                    testLevel.SetLevel(10)
                    try:
                        if dir is None and step is not None:
                            rtn = self.TestAudController.AdjustLevel(testLevel, step=step)
                        elif step is None and dir is not None:
                            rtn = self.TestAudController.AdjustLevel(testLevel, direction=dir)
                        elif dir is None and step is None:
                            rtn = self.TestAudController.AdjustLevel(testLevel)
                        else:
                            rtn = self.TestAudController.AdjustLevel(testLevel, dir, step)
                        
                    except Exception as inst:
                        self.fail('AdjustLevel raised {} unexpectedly!'.format(type(inst)))
                        
                    self.assertEqual(rtn, expectedDict[dir][step])
    
    def test_AudioController_AdjustLevel_BadInput(self):
        testLevel = Level(self.TestUIController, 'testLevel')
        
        with self.subTest(param='Bad Level'):
            with self.assertRaises(TypeError):
                self.TestAudController.AdjustLevel('levelCtl')
        
        with self.subTest(param='Bad Direction'):
            with self.assertRaises(TypeError):
                self.TestAudController.AdjustLevel(testLevel, direction=1)
        
        with self.subTest(param='Bad Step'):
            with self.assertRaises(TypeError):
                self.TestAudController.AdjustLevel(testLevel, step=1)
        
        with self.subTest(param='Unknown Direction'):
            with self.assertRaises(ValueError):
                self.TestAudController.AdjustLevel(testLevel, direction="left")
        
        with self.subTest(param='Unknown Step'):
            with self.assertRaises(ValueError):
                self.TestAudController.AdjustLevel(testLevel, step="big")
    
    def test_AudioController_AdjustGain(self):
        mfgList = ['Biamp', 'BSS']
        gain = self.TestUIController.Lbls['AudIn1-Gain']
        directionList = ['up', 'down']
        gainList = [0, 6, 12, 24, 66]
        
        for mfg in mfgList:
            self.TestAudController.DSP.Manufacturer = mfg
            for dir in directionList:
                for val in gainList:
                    with self.subTest(mfg=mfg, direction=dir, value=val):
                        gain.GainVal = val
                        try:
                            res = self.TestAudController.AdjustGain(gain, dir)
                        except Exception as inst:
                            self.fail('AdjustGain raised {} unexpectedly!'.format(type(inst)))
                        
                        if mfg == 'BSS':
                            if dir == 'up':
                                self.assertEqual(res, ((val+6)/48)*100)
                                self.assertEqual(gain.GainVal, val+6)
                            elif dir == 'down':
                                if val != 0:
                                    self.assertEqual(res, ((val-6)/48)*100)
                                    self.assertEqual(gain.GainVal, val-6)
                                else:
                                    self.assertEqual(res, 0)
                                    self.assertEqual(gain.GainVal, 0)
                        else:
                            if dir == 'up':
                                self.assertEqual(res, val+6)
                                self.assertEqual(gain.GainVal, val+6)
                            elif dir == 'down':
                                if val != 0:
                                    self.assertEqual(res, val-6)
                                    self.assertEqual(gain.GainVal, val-6)
                                else:
                                    self.assertEqual(res, 0)
                                    self.assertEqual(gain.GainVal, 0)
    
    def test_AudioController_AdjustGain_BadGainObj(self):
        with self.assertRaises(TypeError):
            self.TestAudController.AdjustGain('string')
            
    def test_AudioController_AdjustGain_BadDirectionObj(self):
        gain = self.TestUIController.Lbls['AudIn1-Gain']
        with self.assertRaises(TypeError):
            self.TestAudController.AdjustGain(gain, 1)
            
    def test_AudioController_AdjustGain_BadDirectionStr(self):
        gain = self.TestUIController.Lbls['AudIn1-Gain']
        with self.assertRaises(ValueError):
            self.TestAudController.AdjustGain(gain, "raise")
    
    def test_AudioController_AudioStartUp(self):
        try:
            self.TestAudController.AudioStartUp()
        except Exception as inst:
            self.fail('AudioStartUp raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_AudioShutdown(self):
        try:
            self.TestAudController.AudioShutdown()
        except Exception as inst:
            self.fail('AudioShutdown raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_ToggleProgMute(self):
        preState = self.TestAudController.ProgMute
        try:
            self.TestAudController.ToggleProgMute()
        except Exception as inst:
            self.fail('ToggleProgMute raised {} unexpectedly!'.format(type(inst)))
            
        self.assertNotEqual(preState, self.TestAudController.ProgMute)
        
        preState = self.TestAudController.ProgMute
        try:
            self.TestAudController.ToggleProgMute()
        except Exception as inst:
            self.fail('ToggleProgMute raised {} unexpectedly!'.format(type(inst)))
            
        self.assertNotEqual(preState, self.TestAudController.ProgMute)
    
    def test_AudioController_ToggleMicMute(self):
        for i in range(1,3):
            with self.subTest(micNum=i):
                preState = self.TestAudController.MicMute[str(i)]
                try:
                    self.TestAudController.ToggleMicMute(i)
                except Exception as inst:
                    self.fail('ToggleMicMute raised {} unexpectedly!'.format(type(inst)))
                    
                self.assertNotEqual(preState, self.TestAudController.MicMute[str(i)])
                
                preState = self.TestAudController.MicMute[str(i)]
                try:
                    self.TestAudController.ToggleMicMute(i)
                except Exception as inst:
                    self.fail('ToggleMicMute raised {} unexpectedly!'.format(type(inst)))
                    
                self.assertNotEqual(preState, self.TestAudController.MicMute[str(i)])
    
    def test_AudioController_ToggleAllMicsMute(self):
        preState = self.TestAudController.AllMicsMute
        try:
            self.TestAudController.ToggleAllMicsMute()
        except Exception as inst:
            self.fail('ToggleAllMicsMute raised {} unexpectedly!'.format(type(inst)))
            
        self.assertNotEqual(preState, self.TestAudController.AllMicsMute)
        
        preState = self.TestAudController.AllMicsMute
        try:
            self.TestAudController.ToggleAllMicsMute()
        except Exception as inst:
            self.fail('ToggleAllMicsMute raised {} unexpectedly!'.format(type(inst)))
            
        self.assertNotEqual(preState, self.TestAudController.AllMicsMute)
    
    def test_AudioController_ResetGainPage(self):
        try:
            self.TestAudController.ResetGainPage()
        except Exception as inst:
            self.fail('ResetGainPage raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_AudioLevelFeedback(self):
        tagList = [('prog',), ('mics', 1), ('mics', 2), ('mics', '1'), ('mics', '2')]
        valueList = [1, 3, 15]
        for tag in tagList:
            for value in valueList:
                with self.subTest(tag=tag, value=value):
                    try:
                        self.TestAudController.AudioLevelFeedback(tag, value)
                    except Exception as inst:
                        self.fail('AudioLevelFeedback raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_AudioMuteFeedback(self):
        tagList = [('prog',), ('mics', 1), ('mics', 2), ('mics', '1'), ('mics', '2')]
        valueList = ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE', 'off', 'Off', 'OFF', 0, False, 'Unmute', 'unmute', 'UNMUTE']
        for tag in tagList:
            for value in valueList:
                with self.subTest(tag=tag, value=value):
                    try:
                        self.TestAudController.AudioMuteFeedback(tag, value)
                    except Exception as inst:
                        self.fail('AudioMuteFeedback raised {} unexpectedly!'.format(type(inst)))
    
    def test_AudioController_AudioGainFeedback(self):
        mfgList = ['Biamp', 'BSS']
        qualList = {'Biamp':[{'Instance Tag': 'AecInput1', 'Channel': '1'}, {'Instance Tag': 'AecInput1', 'Channel': '2'}], 'BSS':[{'HiQAddress': 'AecInput1', 'ID': 4}]}
        valueList = {'Biamp':[0, 6, 36, 60], 'BSS':[0, 50, 100]}
        
        for mfg in mfgList:
            for qual in qualList[mfg]:
                for val in valueList[mfg]:
                    with self.subTest(mfg=mfg, qaulifier=qual, value=val):
                        self.TestAudController.DSP.Manufacturer = mfg
                        try:
                            self.TestAudController.AudioGainFeedback(qual, val)
                        except Exception as inst:
                            self.fail('AudioGainFeedback raised {} unexpectedly!'.format(type(inst)))
        
        
    def test_AudioController_AudioPhantomFeedback(self):
        mfgList = ['Biamp', 'BSS']
        qualList = {'Biamp':[{'Instance Tag': 'AecInput1', 'Channel': '1'}, {'Instance Tag': 'AecInput1', 'Channel': '2'}], 'BSS':[{'HiQAddress': 'AecInput1', 'ID': 4}]}
        valueList = ['On', 'Off']
        
        for mfg in mfgList:
            for qual in qualList[mfg]:
                for val in valueList:
                    with self.subTest(mfg=mfg, qaulifier=qual, value=val):
                        self.TestAudController.DSP.Manufacturer = mfg
                        try:
                            self.TestAudController.AudioPhantomFeedback(qual, val)
                        except Exception as inst:
                            self.fail('AudioPhantomFeedback raised {} unexpectedly!'.format(type(inst)))
    
if __name__ == '__main__':
    unittest.main()