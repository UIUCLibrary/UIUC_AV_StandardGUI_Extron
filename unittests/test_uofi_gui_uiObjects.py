import unittest
import json
from typing import Dict

## test imports ----------------------------------------------------------------
from uofi_gui import GUIController
from uofi_gui.activityControls import ActivityController
from uofi_gui.uiObjects import ExUIDevice
from uofi_gui.sourceControls import SourceController
from uofi_gui.headerControls import HeaderController
from uofi_gui.techControls import TechMenuController
from uofi_gui.systemHardware import SystemStatusController
from uofi_gui.deviceControl import CameraController, DisplayController, AudioController
from uofi_gui.scheduleControls import AutoScheduleController
from uofi_gui.keyboardControl import KeyboardController
from uofi_gui.pinControl import PINController
import settings

from extronlib.device import UIDevice
from extronlib.ui import Button, Knob, Level, Slider, Label
from extronlib.system import MESet, Clock
## -----------------------------------------------------------------------------

class ExUIDevice_TestClass(unittest.TestCase): 
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = []
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        return super().setUp()
    
    def init_TP(self) -> None:
        self.TestTPs.append('TP001')
        self.TestUIController = ExUIDevice(self.TestGUIController, self.TestTPs[0])
        self.TestGUIController.TPs.append(self.TestUIController)
        self.TestGUIController.TP_Main = self.TestUIController
        
    def init_GUI(self) -> None:
        self.TestUIController.BuildAll(jsonPath=self.TestGUIController.CtlJSON)
        self.TestGUIController.Initialize()
    
    def getCtlDict(self) -> Dict:
        f = open('./emulatedFileSystem/SFTP{}'.format(self.TestGUIController.CtlJSON), 'r')
        ctlStr = f.read()
        f.close()
        ctlDict = json.loads(ctlStr)
        
        return ctlDict
    
    def test_ExUIDevice_Init(self):
        try:
            self.TestUIController = ExUIDevice(self.TestGUIController, 'TP001')
        except Exception as inst:
            self.fail("Initializing ExUIDevice raised {} unexpectedly!".format(type(inst)))
        
        self.assertIsInstance(self.TestUIController, ExUIDevice)
        self.assertIsInstance(self.TestUIController, UIDevice)
            
    def test_ExUIDevice_AddToGUI(self):
        try:
            self.init_TP()
        except Exception as inst:
            self.fail("Adding ExUIDevice to GUIController raised {} unexpectedly!".format(type(inst)))
            
        self.assertEqual(self.TestUIController, self.TestGUIController.TP_Main)
        self.assertEqual(self.TestUIController, self.TestGUIController.TPs[0])
        self.assertEqual(len(self.TestGUIController.TPs), 1)
        
    def test_ExUIDevice_Properties(self):
        self.init_TP()
        
        # GUIHost
        self.assertIsInstance(self.TestUIController.GUIHost, GUIController)
        self.assertIs(self.TestUIController.GUIHost, self.TestGUIController)
        
        # ID
        self.assertIsInstance(self.TestUIController.Id, str)
        self.assertEqual(self.TestUIController.Id, 'TP001')
        
        # TP_Lights
        self.assertIsInstance(self.TestUIController.TP_Lights, Button)
        self.assertTrue(hasattr(self.TestUIController.TP_Lights, 'StateIds'))
        self.assertIsInstance(self.TestUIController.TP_Lights.StateIds, dict)
        self.assertEqual(len(self.TestUIController.TP_Lights.StateIds), 3)
        
        # Btns
        self.assertIsInstance(self.TestUIController.Btns, dict)
        self.assertEqual(len(self.TestUIController.Btns), 0)
        
        # Btn_Grps
        self.assertIsInstance(self.TestUIController.Btn_Grps, dict)
        self.assertEqual(len(self.TestUIController.Btn_Grps), 0)
        
        # Knobs
        self.assertIsInstance(self.TestUIController.Knobs, dict)
        self.assertEqual(len(self.TestUIController.Knobs), 0)
        
        # Lvls
        self.assertIsInstance(self.TestUIController.Lvls, dict)
        self.assertEqual(len(self.TestUIController.Lvls), 0)
        
        # Slds
        self.assertIsInstance(self.TestUIController.Slds, dict)
        self.assertEqual(len(self.TestUIController.Slds), 0)
        
        # Lbls
        self.assertIsInstance(self.TestUIController.Lbls, dict)
        self.assertEqual(len(self.TestUIController.Lbls), 0)
        
        # ModalPageList
        self.assertIsInstance(self.TestUIController.ModalPageList, list)
        self.assertEqual(len(self.TestUIController.ModalPageList), 5)
        
        # PopoverPageList
        self.assertIsInstance(self.TestUIController.PopoverPageList, list)
        self.assertEqual(len(self.TestUIController.PopoverPageList), 8)
        
        # PopupGroupList
        self.assertIsInstance(self.TestUIController.PopupGroupList, list)
        self.assertEqual(len(self.TestUIController.PopupGroupList), 8)
    
    def test_ExUIDevice_InitializeUIControllers(self):
        self.init_TP()
        self.TestUIController.BuildAll(jsonPath=self.TestGUIController.CtlJSON)
        self.TestGUIController.ActCtl = ActivityController(self.TestGUIController)
        
        try:
            self.TestUIController.InitializeUIControllers()
        except Exception as inst:
            self.fail("InitializedUIControllers raised {} unexpectedly!".format(type(inst)))
        
        self.assertIsInstance(self.TestUIController.SrcCtl, SourceController)
        self.assertIsInstance(self.TestUIController.HdrCtl, HeaderController)
        self.assertIsInstance(self.TestUIController.TechCtl, TechMenuController)
        self.assertIsInstance(self.TestUIController.StatusCtl, SystemStatusController)
        self.assertIsInstance(self.TestUIController.CamCtl, CameraController)
        self.assertIsInstance(self.TestUIController.DispCtl, DisplayController)
        self.assertIsInstance(self.TestUIController.AudioCtl, AudioController)
        self.assertIsInstance(self.TestUIController.KBCtl, KeyboardController)
        self.assertIsInstance(self.TestUIController.TechPINCtl, PINController)
    
    def test_ExUIDevice_BlinkLights(self):
        self.init_TP()
        
        test_rate = \
            [
                'Slow',
                'Medium',
                'Fast',
                'Medium',
                'Slow'
            ]
        
        test_state_list = \
            [
                ['red','green'],
                ['red', 'off'],
                ['green', 'off'],
                ['green', 'red', 'off'],
                None
            ]
            
        test_timeout = \
            [
                0,
                2,
                30,
                120,
                360
            ]
        
        for i in range(len(test_rate)):
            with self.subTest(i=i):
                try:
                    self.TestUIController.BlinkLights(test_rate[i], test_state_list[i], test_timeout[i])
                except Exception as inst:
                    self.fail("BlinkLights ({}) raised {} unexpectedly!".format(i, type(inst)))
    
    def test_ExUIDevice_BlinkLights_BadRate(self):
        self.init_TP()
        
        with self.assertRaises(ValueError):
            self.TestUIController.BlinkLights('Blinky', ['red', 'off'])
        
    def test_ExUIDevice_LightsOff(self):
        self.init_TP()
        try:
            self.TestUIController.LightsOff()
        except Exception as inst:
            self.fail("LightsOff raised {} unexpectedly!".format(type(inst)))
    
    def test_ExUIDevice_BuildButtons_Path(self):
        self.init_TP()

        # load controls.json
        ctlDict = self.getCtlDict()
        
        # get length of button dict
        btnLen = len(ctlDict['buttons'])
        
        # attempt to build buttons
        try:
            self.TestUIController.BuildButtons(jsonPath=self.TestGUIController.CtlJSON)
        except Exception as inst:
            self.fail("BuildButtons raised {} unexpectedly!".format(type(inst)))
        
        # test button dicts
        self.assertIsInstance(self.TestUIController.Btns, dict)
        self.assertEqual(len(self.TestUIController.Btns), btnLen)
        
        for btnName in self.TestUIController.Btns:
            with self.subTest(i=btnName):
                self.assertIsInstance(self.TestUIController.Btns[btnName], Button)
        
    def test_ExUIDevice_BuildButtons_Obj(self):
        self.init_TP()

        # load controls.json
        ctlDict = self.getCtlDict()
        
        # get length of button dict
        btnLen = len(ctlDict['buttons'])
        
        # attempt to build buttons
        try:
            self.TestUIController.BuildButtons(jsonObj=ctlDict)
        except Exception as inst:
            self.fail("BuildButtons raised {} unexpectedly!".format(type(inst)))
        
        # test button dicts
        self.assertIsInstance(self.TestUIController.Btns, dict)
        self.assertEqual(len(self.TestUIController.Btns), btnLen)
        
        for btnName in self.TestUIController.Btns:
            with self.subTest(i=btnName):
                self.assertIsInstance(self.TestUIController.Btns[btnName], Button)
    
    def test_ExUIDevice_BuildButtons_Neither(self):
        self.init_TP()
        
        with self.assertRaises(ValueError):
            self.TestUIController.BuildButtons()
            
    def test_ExUIDevice_BuildButtons_BadPath(self):
        self.init_TP()
        
        with self.assertRaises(ValueError):
            self.TestUIController.BuildButtons(jsonPath='./bad/path/to/nonexistent.file')
    
    def test_ExUIDevice_BuildButtonGroups_Path(self):
        self.init_TP()

        # load controls.json
        ctlDict = self.getCtlDict()
        
        # get length of button group dict
        btnGrpLen = len(ctlDict['buttonGroups'])
        
        self.TestUIController.BuildButtons(jsonPath=self.TestGUIController.CtlJSON)
        # attempt to build buttons
        try:
            self.TestUIController.BuildButtonGroups(jsonPath=self.TestGUIController.CtlJSON)
        except Exception as inst:
            self.fail("BuildButtonGroups raised {} unexpectedly!".format(type(inst)))
        
        # test button dicts
        self.assertIsInstance(self.TestUIController.Btn_Grps, dict)
        self.assertEqual(len(self.TestUIController.Btn_Grps), btnGrpLen)
        
        for btnName in self.TestUIController.Btn_Grps:
            with self.subTest(i=btnName):
                self.assertIsInstance(self.TestUIController.Btn_Grps[btnName], MESet)
                
    def test_ExUIDevice_BuildButtonGroups_Obj(self):
        self.init_TP()

        # load controls.json
        ctlDict = self.getCtlDict()
        
        # get length of button group dict
        btnGrpLen = len(ctlDict['buttonGroups'])
        
        self.TestUIController.BuildButtons(jsonObj=ctlDict)
        # attempt to build buttons
        try:
            self.TestUIController.BuildButtonGroups(jsonObj=ctlDict)
        except Exception as inst:
            self.fail("BuildButtonGroups raised {} unexpectedly!".format(type(inst)))
        
        # test button dicts
        self.assertIsInstance(self.TestUIController.Btn_Grps, dict)
        self.assertEqual(len(self.TestUIController.Btn_Grps), btnGrpLen)
        
        for btnGrpName in self.TestUIController.Btn_Grps:
            with self.subTest(i=btnGrpName):
                self.assertIsInstance(self.TestUIController.Btn_Grps[btnGrpName], MESet)
    
    def test_ExUIDevice_BuildButtonGroups_Neither(self):
        self.init_TP()
        
        with self.assertRaises(ValueError):
            self.TestUIController.BuildButtonGroups()
            
    def test_ExUIDevice_BuildButtonGroups_BadPath(self):
        self.init_TP()
        
        with self.assertRaises(ValueError):
            self.TestUIController.BuildButtonGroups(jsonPath='./bad/path/to/nonexistent.file')
    
    def test_ExUIDevice_BuildKnobs_Path(self):
        self.init_TP()

        # load controls.json
        ctlDict = self.getCtlDict()
        
        # get length of button dict
        knobLen = len(ctlDict['knobs'])
        
        # attempt to build buttons
        try:
            self.TestUIController.BuildKnobs(jsonPath=self.TestGUIController.CtlJSON)
        except Exception as inst:
            self.fail("BuildKnobs raised {} unexpectedly!".format(type(inst)))
        
        # test button dicts
        self.assertIsInstance(self.TestUIController.Knobs, dict)
        self.assertEqual(len(self.TestUIController.Knobs), knobLen)
        
        for knobName in self.TestUIController.Knobs:
            with self.subTest(i=knobName):
                self.assertIsInstance(self.TestUIController.Knobs[knobName], Knob)
    
    def test_ExUIDevice_BuildKnobs_Obj(self):
        self.init_TP()

        # load controls.json
        ctlDict = self.getCtlDict()
        
        # get length of button dict
        knobLen = len(ctlDict['knobs'])
        
        # attempt to build buttons
        try:
            self.TestUIController.BuildKnobs(jsonObj=ctlDict)
        except Exception as inst:
            self.fail("BuildKnobs raised {} unexpectedly!".format(type(inst)))
        
        # test button dicts
        self.assertIsInstance(self.TestUIController.Knobs, dict)
        self.assertEqual(len(self.TestUIController.Knobs), knobLen)
        
        for knobName in self.TestUIController.Knobs:
            with self.subTest(i=knobName):
                self.assertIsInstance(self.TestUIController.Knobs[knobName], Knob)
    
    def test_ExUIDevice_BuildKnobs_Neither(self):
        self.init_TP()
        
        with self.assertRaises(ValueError):
            self.TestUIController.BuildKnobs()
            
    def test_ExUIDevice_BuildKnobs_BadPath(self):
        self.init_TP()
        
        with self.assertRaises(ValueError):
            self.TestUIController.BuildKnobs(jsonPath='./bad/path/to/nonexistent.file')
    
    def test_ExUIDevice_BuildLevels_Path(self):
        self.init_TP()

        # load controls.json
        ctlDict = self.getCtlDict()
        
        # get length of button dict
        lvlLen = len(ctlDict['levels'])
        
        # attempt to build buttons
        try:
            self.TestUIController.BuildLevels(jsonPath=self.TestGUIController.CtlJSON)
        except Exception as inst:
            self.fail("BuildLevels raised {} unexpectedly!".format(type(inst)))
        
        # test button dicts
        self.assertIsInstance(self.TestUIController.Lvls, dict)
        self.assertEqual(len(self.TestUIController.Lvls), lvlLen)
        
        for lvlName in self.TestUIController.Lvls:
            with self.subTest(i=lvlName):
                self.assertIsInstance(self.TestUIController.Lvls[lvlName], Level)
    
    def test_ExUIDevice_BuildLevels_Obj(self):
        self.init_TP()

        # load controls.json
        ctlDict = self.getCtlDict()
        
        # get length of button dict
        lvlLen = len(ctlDict['levels'])
        
        # attempt to build buttons
        try:
            self.TestUIController.BuildLevels(jsonObj=ctlDict)
        except Exception as inst:
            self.fail("BuildLevels raised {} unexpectedly!".format(type(inst)))
        
        # test button dicts
        self.assertIsInstance(self.TestUIController.Lvls, dict)
        self.assertEqual(len(self.TestUIController.Lvls), lvlLen)
        
        for lvlName in self.TestUIController.Lvls:
            with self.subTest(i=lvlName):
                self.assertIsInstance(self.TestUIController.Lvls[lvlName], Level)
    
    def test_ExUIDevice_BuildLevels_Neither(self):
        self.init_TP()
        
        with self.assertRaises(ValueError):
            self.TestUIController.BuildLevels()
            
    def test_ExUIDevice_BuildLevels_BadPath(self):
        self.init_TP()
        
        with self.assertRaises(ValueError):
            self.TestUIController.BuildLevels(jsonPath='./bad/path/to/nonexistent.file')
    
    def test_ExUIDevice_BuildSliders_Path(self):
        self.init_TP()

        # load controls.json
        ctlDict = self.getCtlDict()
        
        # get length of button dict
        sldLen = len(ctlDict['sliders'])
        
        # attempt to build buttons
        try:
            self.TestUIController.BuildSliders(jsonPath=self.TestGUIController.CtlJSON)
        except Exception as inst:
            self.fail("BuildSliders raised {} unexpectedly!".format(type(inst)))
        
        # test button dicts
        self.assertIsInstance(self.TestUIController.Slds, dict)
        self.assertEqual(len(self.TestUIController.Slds), sldLen)
        
        for sldName in self.TestUIController.Slds:
            with self.subTest(i=sldName):
                self.assertIsInstance(self.TestUIController.Slds[sldName], Slider)
    
    def test_ExUIDevice_BuildSliders_Obj(self):
        self.init_TP()

        # load controls.json
        ctlDict = self.getCtlDict()
        
        # get length of button dict
        sldLen = len(ctlDict['sliders'])
        
        # attempt to build buttons
        try:
            self.TestUIController.BuildSliders(jsonObj=ctlDict)
        except Exception as inst:
            self.fail("BuildSliders raised {} unexpectedly!".format(type(inst)))
        
        # test button dicts
        self.assertIsInstance(self.TestUIController.Slds, dict)
        self.assertEqual(len(self.TestUIController.Slds), sldLen)
        
        for sldName in self.TestUIController.Slds:
            with self.subTest(i=sldName):
                self.assertIsInstance(self.TestUIController.Slds[sldName], Slider)
    
    def test_ExUIDevice_BuildSliders_Neither(self):
        self.init_TP()
        
        with self.assertRaises(ValueError):
            self.TestUIController.BuildSliders()
            
    def test_ExUIDevice_BuildSliders_BadPath(self):
        self.init_TP()
        
        with self.assertRaises(ValueError):
            self.TestUIController.BuildSliders(jsonPath='./bad/path/to/nonexistent.file')
    
    def test_ExUIDevice_BuildLabels_Path(self):
        self.init_TP()

        # load controls.json
        ctlDict = self.getCtlDict()
        
        # get length of button dict
        lblLen = len(ctlDict['labels'])
        
        # attempt to build buttons
        try:
            self.TestUIController.BuildLabels(jsonPath=self.TestGUIController.CtlJSON)
        except Exception as inst:
            self.fail("BuildLabels raised {} unexpectedly!".format(type(inst)))
        
        # test button dicts
        self.assertIsInstance(self.TestUIController.Lbls, dict)
        self.assertEqual(len(self.TestUIController.Lbls), lblLen)
        
        for lblName in self.TestUIController.Lbls:
            with self.subTest(i=lblName):
                self.assertIsInstance(self.TestUIController.Lbls[lblName], Label)
    
    def test_ExUIDevice_BuildLabels_Obj(self):
        self.init_TP()

        # load controls.json
        ctlDict = self.getCtlDict()
        
        # get length of button dict
        lblLen = len(ctlDict['labels'])
        
        # attempt to build buttons
        try:
            self.TestUIController.BuildLabels(jsonObj=ctlDict)
        except Exception as inst:
            self.fail("BuildLabels raised {} unexpectedly!".format(type(inst)))
        
        # test button dicts
        self.assertIsInstance(self.TestUIController.Lbls, dict)
        self.assertEqual(len(self.TestUIController.Lbls), lblLen)
        
        for lblName in self.TestUIController.Lbls:
            with self.subTest(i=lblName):
                self.assertIsInstance(self.TestUIController.Lbls[lblName], Label)
    
    def test_ExUIDevice_BuildLabels_Neither(self):
        self.init_TP()
        
        with self.assertRaises(ValueError):
            self.TestUIController.BuildLabels()
            
    def test_ExUIDevice_BuildLabels_BadPath(self):
        self.init_TP()
        
        with self.assertRaises(ValueError):
            self.TestUIController.BuildLabels(jsonPath='./bad/path/to/nonexistent.file')
    
    def test_ExUIDevice_BuildAll_Path(self):
        self.init_TP()
        
        try:
            self.TestUIController.BuildAll(jsonPath=self.TestGUIController.CtlJSON)
        except Exception as inst:
            self.fail("BuildAll raised {} unexpectedly!".format(type(inst)))
            
    def test_ExUIDevice_BuildAll_Obj(self):
        self.init_TP()
        
        # load controls.json
        ctlDict = self.getCtlDict()

        try:
            self.TestUIController.BuildAll(jsonObj=ctlDict)
        except Exception as inst:
            self.fail("BuildAll raised {} unexpectedly!".format(type(inst)))
    
    
if __name__ == '__main__':
    unittest.main()