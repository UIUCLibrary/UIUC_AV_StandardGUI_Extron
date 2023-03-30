import unittest
import os

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

class CameraController_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestCamController = self.TestUIController.CamCtl
        return super().setUp()
    
    def tearDown(self):
        if os.path.exists('./emulatedFileSystem/SFTP/user/states/camera_presets.json'):
            os.remove('./emulatedFileSystem/SFTP/user/states/camera_presets.json')
    
    def test_CameraController_Init_BadCamHardwareMatch(self):
        settings.cameras.append({'Id':'CAM003', 'Name':'Bad Camera', 'Input': 3})
        with self.assertRaises(KeyError):
            self.BadGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
            self.BadGUIController.Initialize()
        settings.cameras.pop()
    
    def test_CameraController_Type(self):
        self.assertIsInstance(self.TestCamController, CameraController)
    
    def test_CameraController_Properties(self):
        # UIHost
        with self.subTest(param='UIHost'):
            self.assertIsInstance(self.TestCamController.UIHost, (UIDevice, ExUIDevice))
        
        # GUIHost
        with self.subTest(param='GUIHost'):
            self.assertIsInstance(self.TestCamController.GUIHost, GUIController)
        
        # Cameras
        with self.subTest(param='Cameras'):
            self.assertIsInstance(self.TestCamController.Cameras, dict)
            for key, value in self.TestCamController.Cameras.items():
                with self.subTest(key=key, value=value):
                    self.assertIsInstance(key, str)
                    self.assertIsInstance(value, dict)
    
    def test_CameraController_PRIV_Properties(self):
        # __PresetsFilePath
        with self.subTest(param='__PresetsFilePath'):
            self.assertIsInstance(self.TestCamController._CameraController__PresetsFilePath, str)
            
        # __Switcher
        with self.subTest(param='__Switcher'):
            self.assertIsInstance(self.TestCamController._CameraController__Switcher, SystemHardwareController)
        
        # __DefaultCamera
        with self.subTest(param='__DefaultCamera'):
            self.assertIsInstance(self.TestCamController._CameraController__DefaultCamera, Button)
        
        # __SelectBtns
        with self.subTest(param='__SelectBtns'):
            self.assertIsInstance(self.TestCamController._CameraController__SelectBtns, MESet)
        
        # __PresetBtns
        with self.subTest(param='__PresetBtns'):
            self.assertIsInstance(self.TestCamController._CameraController__PresetBtns, list)
            for value in self.TestCamController._CameraController__PresetBtns:
                with self.subTest(value=value):
                    self.assertIsInstance(value, Button)
        
        # __HomeBtn
        with self.subTest(param='__HomeBtn'):
            self.assertIsInstance(self.TestCamController._CameraController__HomeBtn, Button)
        
        # __ControlsBtns
        with self.subTest(param='__ControlsBtns'):
            self.assertIsInstance(self.TestCamController._CameraController__ControlsBtns, list)
            for value in self.TestCamController._CameraController__ControlsBtns:
                with self.subTest(value=value):
                    self.assertIsInstance(value, Button)
        
        # __EditorTitle
        with self.subTest(param='__EditorTitle'):
            self.assertIsInstance(self.TestCamController._CameraController__EditorTitle, Label)
        
        # __EditorName
        with self.subTest(param='__EditorName'):
            self.assertIsInstance(self.TestCamController._CameraController__EditorName, Button)
        
        # __EditorHome
        with self.subTest(param='__EditorHome'):
            self.assertIsInstance(self.TestCamController._CameraController__EditorHome, Button)
        
        # __EditorSave
        with self.subTest(param='__EditorSave'):
            self.assertIsInstance(self.TestCamController._CameraController__EditorSave, Button)
        
        # __EditorCancel
        with self.subTest(param='__EditorCancel'):
            self.assertIsInstance(self.TestCamController._CameraController__EditorCancel, Button)
    
    def test_CameraController_EventHandler_CamSelectBtnHandler(self):
        btnList = self.TestCamController._CameraController__SelectBtns.Objects
        actList = ['Pressed', 'Released']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestCamController._CameraController__CamSelectBtnHandler(btn, act)
                    except Exception as inst:
                        self.fail('__CamSelectBtnHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_CameraController_EventHandler_PresetBtnHandler(self):
        btnList = self.TestCamController._CameraController__PresetBtns
        actList = ['Pressed', 'Tapped', 'Held']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestCamController._CameraController__PresetBtnHandler(btn, act)
                    except Exception as inst:
                        self.fail('__PresetBtnHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_CameraController_EventHandler_HomeBtnHandler(self):
        presetList = self.TestCamController._CameraController__PresetBtns
        btnList = [self.TestCamController._CameraController__HomeBtn]
        actList = ['Pressed', 'Tapped', 'Held']
        
        for pre in presetList:
            for btn in btnList:
                for act in actList:
                    with self.subTest(button=btn.Name, action=act, preset=pre):
                        self.TestCamController._CameraController__PresetBtnHandler(pre, 'Held')
                        try:
                            self.TestCamController._CameraController__HomeBtnHandler(btn, act)
                        except Exception as inst:
                            self.fail('__HomeBtnHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_CameraController_EventHandler_CamCtlHandler(self):
        btnList = self.TestCamController._CameraController__ControlsBtns
        actList = ['Pressed', 'Released']
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestCamController._CameraController__CamCtlHandler(btn, act)
                    except Exception as inst:
                        self.fail('__CamCtlHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_CameraController_Eventhandler_EditorNameHandler(self):
        presetList = self.TestCamController._CameraController__PresetBtns
        btnList = [self.TestCamController._CameraController__EditorName]
        actList = ['Pressed', 'Released']
        
        for pre in presetList:
            for btn in btnList:
                for act in actList:
                    with self.subTest(button=btn.Name, action=act, preset=pre.Name):
                        self.TestCamController._CameraController__PresetBtnHandler(pre, 'Held')
                        try:
                            self.TestCamController._CameraController__EditorNameHandler(btn, act)
                        except Exception as inst:
                            self.fail('__EditorNameHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_CameraController_EventHandler_EditorHomeHandler(self):
        presetList = self.TestCamController._CameraController__PresetBtns
        btnList = [self.TestCamController._CameraController__EditorHome]
        actList = ['Pressed', 'Released']
        
        for pre in presetList:
            for btn in btnList:
                for act in actList:
                    with self.subTest(button=btn.Name, action=act, preset=pre.Name):
                        self.TestCamController._CameraController__PresetBtnHandler(pre, 'Held')
                        try:
                            self.TestCamController._CameraController__EditorHomeHandler(btn, act)
                        except Exception as inst:
                            self.fail('__EditorHomeHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_CameraController_EventHandler_EditorSaveHandler(self):
        presetList = self.TestCamController._CameraController__PresetBtns
        btnList = [self.TestCamController._CameraController__EditorSave]
        actList = ['Pressed', 'Released']
        
        for pre in presetList:
            for btn in btnList:
                for act in actList:
                    with self.subTest(button=btn.Name, action=act, preset=pre.Name):
                        self.TestCamController._CameraController__PresetBtnHandler(pre, 'Held')
                        try:
                            self.TestCamController._CameraController__EditorSaveHandler(btn, act)
                        except Exception as inst:
                            self.fail('__EditorSaveHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_CameraController_EventHandler_EditorCancelHandler(self):
        presetList = self.TestCamController._CameraController__PresetBtns
        btnList = [self.TestCamController._CameraController__EditorCancel]
        actList = ['Pressed', 'Released']
        
        for pre in presetList:
            for btn in btnList:
                for act in actList:
                    with self.subTest(button=btn.Name, action=act, preset=pre.Name):
                        self.TestCamController._CameraController__PresetBtnHandler(pre, 'Held')
                        try:
                            self.TestCamController._CameraController__EditorCancelHandler(btn, act)
                        except Exception as inst:
                            self.fail('__EditorCancelHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_CameraController_SavePresetStates(self):
        import shutil
        
        with self.subTest(condition='Save - No Existing Presets'):
            if File.Exists(self.TestCamController._CameraController__PresetsFilePath):
                File.DeleteFile(self.TestCamController._CameraController__PresetsFilePath)
            try:
                self.TestCamController.SavePresetStates()
            except Exception as inst:
                self.fail('SavePresetStates raised {} unexpectedly!'.format(type(inst)))
                
        with self.subTest(condition='Save - Existing Presets'):
            shutil.copyfile('./emulatedFileSystem/SFTP/user/states/test_states/test_camera_presets_1.json', './emulatedFileSystem/SFTP/user/states/test_camera_presets_write.json')
            self.TestCamController._CameraController__PresetsFilePath = '/user/states/test_camera_presets_write.json'
            try:
                self.TestCamController.SavePresetStates()
            except Exception as inst:
                self.fail("__SaveSchedule() raised {} unexpectedly!".format(type(inst)))
            os.remove('./emulatedFileSystem/SFTP/user/states/test_camera_presets_write.json')
        
        with self.subTest(condition='Save - Some Existing Presets'):
            os.remove('./emulatedFileSystem/SFTP/user/states/test_camera_presets_write.json')
            shutil.copyfile('./emulatedFileSystem/SFTP/user/states/test_states/test_camera_presets_2.json', './emulatedFileSystem/SFTP/user/states/test_camera_presets_write.json')
            self.TestCamController._CameraController__PresetsFilePath = '/user/states/test_camera_presets_write.json'
            try:
                self.TestCamController.SavePresetStates()
            except Exception as inst:
                self.fail("__SaveSchedule() raised {} unexpectedly!".format(type(inst)))
            os.remove('./emulatedFileSystem/SFTP/user/states/test_camera_presets_write.json')
    
    def test_CameraController_LoadPresetStates_NoFile(self):
        try:
            self.TestCamController.LoadPresetStates()
        except Exception as inst:
            self.fail('LoadPresetStates raised {} unexpectedly!'.format(type(inst)))
    
    def test_CameraController_LoadPresetStates_TestFile(self):
        self.TestCamController._CameraController__PresetsFilePath = '/user/states/test_states/test_camera_presets_1.json'
        try:
            self.TestCamController.LoadPresetStates()
        except Exception as inst:
            self.fail('LoadPresetStates raised {} unexpectedly!'.format(type(inst)))
    
    def test_CameraController_UpdatePreset(self):
        try:
            self.TestCamController.UpdatePreset('Test Text', self.TestCamController._CameraController__EditorName)
        except Exception as inst:
            self.fail('UpdatePreset raised {} unexpectedly!'.format(type(inst)))
        self.assertEqual(self.TestCamController._CameraController__EditorName.PresetText, 'Test Text')
    
    def test_CameraController_UpdatePresetButtons(self):
        try:
            self.TestCamController.UpdatePresetButtons()
        except Exception as inst:
            self.fail('UpdatePresetButtons raised {} unexpectedly!'.format(type(inst)))
    
    def test_CameraController_SelectDefaultCamera(self):
        try:
            self.TestCamController.SelectDefaultCamera()
        except Exception as inst:
            self.fail('SelectDefaultCamera raised {} unexpectedly!'.format(type(inst)))
    
    def test_CameraController_SendCameraHome(self):
        camList = list(self.TestCamController.Cameras.values())
        
        for cam in camList:
            with self.subTest(camera=cam['Name'], method='byId'):
                try:
                    self.TestCamController.SendCameraHome(cam['Id'])
                except Exception as inst:
                    self.fail('SendCameraHome (id) raised {} unexpectedly!'.format(type(inst)))
            with self.subTest(camera=cam['Name'], method='byHw'):
                try:
                    self.TestCamController.SendCameraHome(cam['Hw'])
                except Exception as inst:
                    self.fail('SendCameraHome raised {} unexpectedly!'.format(type(inst)))
    
    def test_CameraController_SendCameraHome_AllCamera(self):
        try:
            self.TestCamController.SendCameraHome()
        except Exception as inst:
            self.fail('SendCameraHome raised {} unexpectedly!'.format(type(inst)))
            
    def test_CameraController_SendCameraHome_BadCamera(self):
        with self.assertRaises(KeyError):
            self.TestCamController.SendCameraHome('CAM005')
            
    def test_CameraController_SendCameraHome_BadType(self):
        contextList = [True, 1, 2.5, ['list'], {'dict': 'value'}]
        for con in contextList:
            with self.subTest(context=con):
                with self.assertRaises(TypeError):
                    self.TestCamController.SendCameraHome(con)
        
class DisplayController_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
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
    
class AudioController_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
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
            self.assertIsInstance(self.TestAudController.GUIHost, GUIController)
        
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
        stateList = ['on', True, None, (1), [1, 2], {'Level': 5}]
        
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
    
if __name__ == '__main__':
    unittest.main()