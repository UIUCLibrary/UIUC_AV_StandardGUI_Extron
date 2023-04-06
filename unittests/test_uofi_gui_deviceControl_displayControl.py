import unittest
import os
import importlib

## test imports ----------------------------------------------------------------
from uofi_gui import GUIController
from uofi_gui.uiObjects import ExUIDevice
from uofi_gui.systemHardware import SystemHardwareController
from uofi_gui.deviceControl import AudioController, CameraController, DisplayController
from uofi_gui.sourceControls import Destination
import test_settings as settings

from extronlib.device import UIDevice
from extronlib.ui import Button, Label, Level, Slider
from extronlib.system import MESet, File
## -----------------------------------------------------------------------------

class DisplayController_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        importlib.reload(settings)
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestDispController = self.TestUIController.DispCtl
        return super().setUp()
    
    def test_DisplayController_Type(self):
        self.assertIsInstance(self.TestDispController, DisplayController)
    
    def test_DisplayController_InitOtherTypes(self):
        settings.destinations = \
            [
                {
                    'id': 'MON003',
                    'name': 'Confidence Monitor',
                    'output': 1,
                    'type': 'c-conf',
                    'rly': None,
                    'group-work-src': 'WPD001',
                    'adv-layout': {
                        "row": 0,
                        "pos": 1
                    }
                },
                {
                    "id": "PRJ001",
                    "name": "Projector",
                    "output": 3,
                    "type": "proj",
                    "rly": [1, 2],
                    "group-work-src": "WPD001",
                    "adv-layout": {
                        "row": 0,
                        "pos": 0
                    }
                },
                {
                    "id": "MON001",
                    "name": "North Monitor",
                    "output": 2,
                    "type": "mon",
                    "rly": None,
                    "group-work-src": "WPD002",
                    "adv-layout": {
                        "row": 1,
                        "pos": 0
                    }
                },
                {
                    "id": "MON002",
                    "name": "South Monitor",
                    "output": 4,
                    "type": "mon",
                    "rly": None,
                    "group-work-src": "WPD003",
                    "adv-layout": {
                        "row": 1,
                        "pos": 1
                    }
                }
            ]
        GUIC = GUIController(settings, self.TestCtls, self.TestTPs)
        GUIC.Initialize()
        self.assertIsInstance(GUIC.TP_Main.DispCtl, DisplayController)
    
    
    def test_DisplayController_Properties(self):
        # UIHost
        with self.subTest(param='UIHost'):
            self.assertIsInstance(self.TestDispController.UIHost, (UIDevice, ExUIDevice))
        
        # GUIHost
        with self.subTest(param='GUIHost'):
            self.assertIsInstance(self.TestDispController.GUIHost, GUIController)
        
        # Destinations
        with self.subTest(param='Destinations'):
            self.assertIsInstance(self.TestDispController.Destinations, dict)
            for key, value in self.TestDispController.Destinations.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, dict)
        
        # DisplayMute
        with self.subTest(param='DisplayMute'):
            self.assertIsInstance(self.TestDispController.DisplayMute, dict)
            for key, value in self.TestDispController.DisplayMute.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, bool)
        
        # DisplayVolume
        with self.subTest(param='DisplayVolume'):
            self.assertIsInstance(self.TestDispController.DisplayVolume, dict)
            for key, value in self.TestDispController.DisplayVolume.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, (int, float, type(None)))
    
    def test_DisplayController_PRIV_Properties(self):
        # __Labels
        with self.subTest(param='__Labels'):
            self.assertIsInstance(self.TestDispController._DisplayController__Labels, dict)
            for key, value in self.TestDispController._DisplayController__Labels.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, dict)
                    for key2, value2 in value.items():
                        with self.subTest(key2=key2, value2=value2):
                            self.assertIsInstance(key2, str)
                            self.assertIsInstance(value2, Label)
        
        # __Controls
        with self.subTest(param='__Controls'):
            self.assertIsInstance(self.TestDispController._DisplayController__Controls, dict)
            for key, value in self.TestDispController._DisplayController__Controls.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, dict)
                    for key2, value2 in value.items():
                        with self.subTest(key2=key2, value2=value2):
                            self.assertIsInstance(key2, str)
                            self.assertIsInstance(value2, (dict, Button))
                            if type(value2) is dict:
                                for key3, value3 in value2.items():
                                    with self.subTest(key3=key3, value3=value3):
                                        self.assertIsInstance(key3, str)
                                        self.assertIsInstance(value3, (Button, Slider))
        
        # __ControlList
        with self.subTest(param='__ControlList'):
            self.assertIsInstance(self.TestDispController._DisplayController__ControlList, list)
            for value in self.TestDispController._DisplayController__ControlList:
                with self.subTest(value=value):
                    self.assertIsInstance(value, (Button, Slider))
    
    def test_DisplayController_EventHandler_SliderFillHandler(self):
        btnList = [ctl for ctl in self.TestDispController._DisplayController__ControlList if type(ctl) is Slider]
        actList = ['Changed']
        contextList = [1, 7.5, 50, 75]
        
        for btn in btnList:
            for act in actList:
                for con in contextList:
                    with self.subTest(button=btn.Name, action=act, context=con):
                        try:
                            self.TestDispController._DisplayController__SliderFillHandler(btn, act, con)
                        except Exception as inst:
                            self.fail('__SliderFillHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_DisplayController_EventHandler_DisplayControlButtonHandler(self):
        btnList = self.TestDispController._DisplayController__ControlList
        actList = ['Pressed', 'Released']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestDispController._DisplayController__DisplayControlButtonHandler(btn, act)
                    except Exception as inst:
                        self.fail('__DisplayControlButtonHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_DisplayController_DynProp_DisplayMute(self):
        destList = ['MON001', 'MON002', 'PRJ001', self.TestUIController.SrcCtl.GetDestination(id='MON001'), self.TestUIController.SrcCtl.GetDestination(id='MON002'), self.TestUIController.SrcCtl.GetDestination(id='PRJ001')]
        contextList = ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE', 'off', 'Off', 'OFF', 0, False, 'Unmute', 'unmute', 'UNMUTE']
        
        for dest in destList:
            for con in contextList:
                with self.subTest(destination=dest, context=con):
                    self.TestDispController.DisplayMute = (dest, con)
    
    def test_DisplayController_DynProp_DisplayMute_BadInput(self):
        contextList = ['on', True, (1, False), 0, 1, ['MON001', True], {'PRJ001': 'mute'}]
        
        for con in contextList:
            with self.subTest(context=con):
                with self.assertRaises(TypeError):
                    self.TestDispController.DisplayMute = con
    
    def test_DisplayController_DynProp_DisplayVolume(self):
        destList = ['MON001', 'MON002', 'PRJ001', self.TestUIController.SrcCtl.GetDestination(id='MON001'), self.TestUIController.SrcCtl.GetDestination(id='MON002'), self.TestUIController.SrcCtl.GetDestination(id='PRJ001')]
        contextList = [1, 2.5, 15, 67.333]
        
        for dest in destList:
            for con in contextList:
                with self.subTest(destination=dest, context=con):
                    self.TestDispController.DisplayVolume = (dest, con)
    
    def test_DisplayController_DynProp_DisplayVolume_BadInput(self):
        contextList = ['on', True, (1, False), 0, 1, ['MON001', True], {'PRJ001': 'mute'}]
        
        for con in contextList:
            with self.subTest(context=con):
                with self.assertRaises(TypeError):
                    self.TestDispController.DisplayVolume = con
    
    def test_DisplayController_SetDisplayPower_Strings(self):
        testList = ['On', 'Off']
        for test in testList:
            for con in ['MON001', 'MON002', 'PRJ001']:
                with self.subTest(context=con, test=test):
                    try:
                        self.TestDispController.SetDisplayPower(con, test)
                    except Exception as inst:
                        self.fail('SetDisplayPower raised {} unexpectedly!'.format(type(inst)))
    
    def test_DisplayController_SetDisplayPower_Destinations(self):
        testList = ['On', 'Off']
        for test in testList:
            for con in [dest for dest in self.TestUIController.SrcCtl.Destinations if dest.Id in ['MON001', 'MON002', 'PRJ001']]:
                with self.subTest(context=con.Id, test=test):
                    try:
                        self.TestDispController.SetDisplayPower(con, test)
                    except Exception as inst:
                        self.fail('SetDisplayPower raised {} unexpectedly!'.format(type(inst)))
    
    def test_DisplayController_SetDisplayPower_BadDest(self):
        for con in [1, ('MON001',), ['MON001','MON001'], True, 2.5]:
            with self.subTest(context=con):
                with self.assertRaises(TypeError):
                    self.TestDispController.SetDisplayPower(con)
                    
    def test_DisplayController_SetDisplayPower_NoHardware(self):
        with self.assertRaises(LookupError):
            self.TestDispController.SetDisplayPower('MON003')
    
    def test_DisplayController_SetDisplaySource_Strings(self):
        for con in ['MON001', 'MON002', 'PRJ001']:
            with self.subTest(context=con):
                try:
                    self.TestDispController.SetDisplaySource(con)
                except Exception as inst:
                    self.fail('SetDisplaySource raised {} unexpectedly!'.format(type(inst)))

    def test_DisplayController_SetDisplaySource_Destinations(self):
        for con in [dest for dest in self.TestUIController.SrcCtl.Destinations if dest.Id in ['MON001', 'MON002', 'PRJ001']]:
            with self.subTest(context=con.Id):
                try:
                    self.TestDispController.SetDisplaySource(con)
                except Exception as inst:
                    self.fail('SetDisplaySource raised {} unexpectedly!'.format(type(inst)))
    
    def test_DisplayController_SetDisplaySource_BadDest(self):
        for con in [1, ('MON001',), ['MON001','MON001'], True, 2.5]:
            with self.subTest(context=con):
                with self.assertRaises(TypeError):
                    self.TestDispController.SetDisplaySource(con)
                    
    def test_DisplayController_SetDisplaySource_NoHardware(self):
        with self.assertRaises(LookupError):
            self.TestDispController.SetDisplaySource('MON003')
    
    def test_DisplayController_DisplayPowerFeedback(self):
        contextList = ['MON001', 'MON002', 'PRJ001']
        stateList = ['On', 'on', 'Power On', 'Off', 'off', 'Power Off', 'Standby (Power Save)', 'Suspend (Power Save)', 'Warming', 'Warming up', 'Cooling', 'Cooling down']
        for con in contextList:
            for state in stateList:
                with self.subTest(context=con, state=state):
                    try:
                        self.TestDispController.DisplayPowerFeedback(con, state)
                    except Exception as inst:
                        self.fail('DisplayPowerFeedback raised {} unexpectedly!'.format(type(inst)))
    
    def test_DisplayController_DisplayPowerFeedback_BadState(self):
        with self.assertRaises(ValueError):
            self.TestDispController.DisplayPowerFeedback('MON001', 'invalid-state')
    
    def test_DisplayController_DisplayMuteFeedback(self):
        contextList = ['MON001', 'MON002']
        stateList = ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE', 'off', 'Off', 'OFF', 0, False, 'Unmute', 'unmute', 'UNMUTE']
        for con in contextList:
            for state in stateList:
                with self.subTest(context=con, state=state):
                    try:
                        self.TestDispController.DisplayMuteFeedback(con, state)
                    except Exception as inst:
                        self.fail('DisplayMuteFeedback raised {} unexpectedly!'.format(type(inst)))
    
    def test_DisplayController_DisplayVolumeFeedback(self):
        contextList = ['MON001', 'MON002']
        valueList = [0, 1.5, 15, 50]
        for con in contextList:
            for value in valueList:
                with self.subTest(context=con, value=value):
                    try:
                        self.TestDispController.DisplayVolumeFeedback(con, value)
                    except Exception as inst:
                        self.fail('DisplayVolumeFeedback raised {} unexpectedly!'.format(type(inst)))
    
if __name__ == '__main__':
    unittest.main()