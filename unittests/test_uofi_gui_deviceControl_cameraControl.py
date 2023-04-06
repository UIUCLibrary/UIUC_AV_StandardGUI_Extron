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

class CameraController_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        importlib.reload(settings)
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

if __name__ == '__main__':
    unittest.main()