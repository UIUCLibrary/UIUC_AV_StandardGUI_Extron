import unittest
from typing import Dict, Tuple, List, Callable, Union

## test imports ----------------------------------------------------------------
import extronlib.device
import extronlib.system
import extronlib.ui
import uofi_gui.sourceControls as SrcCtl
import uofi_gui.activityControls as ActCtl
import uofi_gui.uiObjects as UI
import settings
import vars
## -----------------------------------------------------------------------------
 
class SourceController_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.Host = extronlib.device.UIDevice('TP001')
        
        self.TP_Btns = UI.BuildButtons(self.Host, jsonPath='controls.json')
        self.TP_Btn_Grps = UI.BuildButtonGroups(self.TP_Btns, jsonPath="controls.json")
        self.TP_Lbls = UI.BuildLabels(self.Host, jsonPath='controls.json')
        self.TP_Lvls = UI.BuildLevels(self.Host, jsonPath='controls.json')
        
        self.SourceButtons = \
            {
                "select": self.TP_Btn_Grps['Source-Select'],
                "indicator": self.TP_Btn_Grps['Source-Indicator'],
                "arrows": [
                    self.TP_Btns['SourceMenu-Prev'],
                    self.TP_Btns['SourceMenu-Next']
                ]
            }
        self.MatrixDict = \
            {
                'btns': 
                    [
                        self.TP_Btns['Tech-Matrix-1,1'],
                        self.TP_Btns['Tech-Matrix-2,1'],
                        self.TP_Btns['Tech-Matrix-3,1'],
                        self.TP_Btns['Tech-Matrix-4,1'],
                        self.TP_Btns['Tech-Matrix-5,1'],
                        self.TP_Btns['Tech-Matrix-6,1'],
                        self.TP_Btns['Tech-Matrix-7,1'],
                        self.TP_Btns['Tech-Matrix-8,1'],
                        self.TP_Btns['Tech-Matrix-9,1'],
                        self.TP_Btns['Tech-Matrix-10,1'],
                        self.TP_Btns['Tech-Matrix-11,1'],
                        self.TP_Btns['Tech-Matrix-12,1'],
                        self.TP_Btns['Tech-Matrix-1,2'],
                        self.TP_Btns['Tech-Matrix-2,2'],
                        self.TP_Btns['Tech-Matrix-3,2'],
                        self.TP_Btns['Tech-Matrix-4,2'],
                        self.TP_Btns['Tech-Matrix-5,2'],
                        self.TP_Btns['Tech-Matrix-6,2'],
                        self.TP_Btns['Tech-Matrix-7,2'],
                        self.TP_Btns['Tech-Matrix-8,2'],
                        self.TP_Btns['Tech-Matrix-9,2'],
                        self.TP_Btns['Tech-Matrix-10,2'],
                        self.TP_Btns['Tech-Matrix-11,2'],
                        self.TP_Btns['Tech-Matrix-12,2'],
                        self.TP_Btns['Tech-Matrix-1,3'],
                        self.TP_Btns['Tech-Matrix-2,3'],
                        self.TP_Btns['Tech-Matrix-3,3'],
                        self.TP_Btns['Tech-Matrix-4,3'],
                        self.TP_Btns['Tech-Matrix-5,3'],
                        self.TP_Btns['Tech-Matrix-6,3'],
                        self.TP_Btns['Tech-Matrix-7,3'],
                        self.TP_Btns['Tech-Matrix-8,3'],
                        self.TP_Btns['Tech-Matrix-9,3'],
                        self.TP_Btns['Tech-Matrix-10,3'],
                        self.TP_Btns['Tech-Matrix-11,3'],
                        self.TP_Btns['Tech-Matrix-12,3'],
                        self.TP_Btns['Tech-Matrix-1,4'],
                        self.TP_Btns['Tech-Matrix-2,4'],
                        self.TP_Btns['Tech-Matrix-3,4'],
                        self.TP_Btns['Tech-Matrix-4,4'],
                        self.TP_Btns['Tech-Matrix-5,4'],
                        self.TP_Btns['Tech-Matrix-6,4'],
                        self.TP_Btns['Tech-Matrix-7,4'],
                        self.TP_Btns['Tech-Matrix-8,4'],
                        self.TP_Btns['Tech-Matrix-9,4'],
                        self.TP_Btns['Tech-Matrix-10,4'],
                        self.TP_Btns['Tech-Matrix-11,4'],
                        self.TP_Btns['Tech-Matrix-12,4']
                    ],
                'ctls': self.TP_Btn_Grps['Tech-Matrix-Mode'],
                'del': self.TP_Btns['Tech-Matrix-DeleteTies'],
                'labels': {
                    'input': 
                        [
                            self.TP_Lbls['MatrixLabel-In-1'],
                            self.TP_Lbls['MatrixLabel-In-2'],
                            self.TP_Lbls['MatrixLabel-In-3'],
                            self.TP_Lbls['MatrixLabel-In-4'],
                            self.TP_Lbls['MatrixLabel-In-5'],
                            self.TP_Lbls['MatrixLabel-In-6'],
                            self.TP_Lbls['MatrixLabel-In-7'],
                            self.TP_Lbls['MatrixLabel-In-8'],
                            self.TP_Lbls['MatrixLabel-In-9'],
                            self.TP_Lbls['MatrixLabel-In-10'],
                            self.TP_Lbls['MatrixLabel-In-11'],
                            self.TP_Lbls['MatrixLabel-In-12']
                        ],
                    'output': 
                        [
                            self.TP_Lbls['MatrixLabel-Out-1'],
                            self.TP_Lbls['MatrixLabel-Out-2'],
                            self.TP_Lbls['MatrixLabel-Out-3'],
                            self.TP_Lbls['MatrixLabel-Out-4'],
                            self.TP_Lbls['MatrixLabel-Out-5'],
                            self.TP_Lbls['MatrixLabel-Out-6']
                        ]
                }
            }
        self.Controller = SrcCtl.SourceController(self.Host,
                                             self.SourceButtons,
                                             self.MatrixDict,
                                             settings.sources,
                                             settings.destinations)
    
    def test_SourceController_PublicProperties(self): # configure a test case for each unit in the module
        
        self.assertEqual(self.Controller.UIHost, self.Host)
        self.assertIs(type(self.Controller.Sources), type([]))
        self.assertIs(type(self.Controller.Destinations), type([]))
        self.assertIs(type(self.Controller.PrimaryDestination), SrcCtl.Destination)
        self.assertIs(type(self.Controller.SelectedSource), SrcCtl.Source)
        
    def test_SourceController_PrivateProperties(self):
        self.assertIs(type(self.Controller._sourceBtns), extronlib.system.MESet)
        self.assertIs(type(self.Controller._sourceInds), extronlib.system.MESet)
        self.assertIs(type(self.Controller._arrowBtns), type([]))
        self.assertEqual(len(self.Controller._arrowBtns), 2)
        for item in self.Controller._arrowBtns:
            with self.subTest(item=item):
                self.assertIs(type(item), extronlib.ui.Button)
        self.assertIs(type(self.Controller._offset), int)
        #self.assertEqual(Controller._offset, 0)
        self.assertIs(type(self.Controller._advLayout), str)
        self.assertIs(type(self.Controller._none_source), SrcCtl.Source)
        self.assertIs(type(self.Controller._DisplaySrcList), type([]))
        self.assertIs(type(self.Controller._Matrix), SrcCtl.MatrixController)
    
    def test_SourceController_Prv_GetUIForAdvDest(self):
        rtn = self.Controller._GetUIForAdvDest(self.Controller.Destinations[0])
        self.assertIs(type(rtn), type({}))
        self.assertEqual(len(rtn), 6)
        for item in rtn.values():
            with self.subTest(item=item):
                self.assertIn(type(item), [extronlib.ui.Button, extronlib.ui.Label])
        
    def test_SourceController_Prv_GetPositionByBtnName(self):
        rtn = self.Controller._GetPositionByBtnName('Disp-Select-0,0')
        self.assertIs(type(rtn), SrcCtl.LayoutTuple)
        
    def test_SourceController_GetAdvShareLayout(self):
        rtn = self.Controller.GetAdvShareLayout()
        self.assertIs(type(rtn), str)
        self.assertRegex(rtn, r"Source-Control-Adv_\d+,\d+")
        
    def test_SourceController_GetDestination_Id(self):
        testID = 'PRJ001'
        
        rtn = self.Controller.GetDestination(id = testID)
        self.assertIs(type(rtn), SrcCtl.Destination)
        self.assertEqual(rtn.Id, testID)
        
    def test_SourceController_GetDestination_Name(self):
        testName = 'Projector'
        
        rtn = self.Controller.GetDestination(name = testName)
        self.assertIs(type(rtn), SrcCtl.Destination)
        self.assertEqual(rtn.Name, testName)
        
    def test_SourceController_GetDestinationIndexByID(self):
        testID = 'MON001'
        expectedVal = 1
        
        rtn = self.Controller.GetDestinationIndexByID(testID)
        self.assertIs(type(rtn), int)
        self.assertEqual(rtn, expectedVal)
        
    def test_SourceController_GetSource_Id(self):
        testID = 'PC001'
        
        rtn = self.Controller.GetSource(id = testID)
        self.assertIs(type(rtn), SrcCtl.Source)
        self.assertEqual(rtn.Id, testID)
        
    def test_SourceController_GetSource_Name(self):
        testName = 'Room PC'
        
        rtn = self.Controller.GetSource(name = testName)
        self.assertIs(type(rtn), SrcCtl.Source)
        self.assertEqual(rtn.Name, testName)
        
    def test_SourceController_GetSourceIndexByID(self):
        testID = 'WPD001'
        expectedVal = 3
        
        rtn = self.Controller.GetSourceIndexByID(testID)
        self.assertIs(type(rtn), int)
        self.assertEqual(rtn, expectedVal)
    
    def test_SourceController_SetPrimaryDestination(self):        
        testDest = self.Controller.Destinations[1]
        
        self.assertIsNot(self.Controller.PrimaryDestination, testDest)
        
        self.Controller.SetPrimaryDestination(testDest)
        
        self.assertIs(type(self.Controller.PrimaryDestination), SrcCtl.Destination)
        self.assertIs(self.Controller.PrimaryDestination, testDest)
        
    def test_SourceController_SelectSource_Source(self):
        testSrc = self.Controller.Sources[1]
        
        self.assertIsNot(self.Controller.SelectedSource, testSrc)
        
        self.Controller.SelectSource(testSrc)
        
        self.assertIs(type(self.Controller.SelectedSource), SrcCtl.Source)
        self.assertIs(self.Controller.SelectedSource, testSrc)
        
    def test_SourceController_SelectSource_StrName(self):
        testSrc = self.Controller.Sources[2]
        
        self.assertIsNot(self.Controller.SelectedSource, testSrc)
        
        self.Controller.SelectSource(testSrc.Name)
        
        self.assertIs(type(self.Controller.SelectedSource), SrcCtl.Source)
        self.assertIs(self.Controller.SelectedSource, testSrc)
        
    def test_SourceController_SelectSource_StrId(self):        
        testSrc = self.Controller.Sources[3]
        
        self.assertIsNot(self.Controller.SelectedSource, testSrc)
        
        self.Controller.SelectSource(testSrc.Id)
        
        self.assertIs(type(self.Controller.SelectedSource), SrcCtl.Source)
        self.assertIs(self.Controller.SelectedSource, testSrc)
    
    def test_SourceController_UpdateDisplaySourceList(self):
        ActModBtns = \
            {
                "select": self.TP_Btn_Grps['Activity-Select'],
                "indicator": self.TP_Btn_Grps['Activity-Indicator'],
                "end": self.TP_Btns['Shutdown-EndNow'],
                "cancel": self.TP_Btns['Shutdown-Cancel']
            }
        def StartupActions() -> None:
            pass

        def StartupSyncedActions(count: int) -> None:
            pass

        def SwitchActions() -> None:
            pass

        def SwitchSyncedActions(count: int) -> None:
            pass

        def ShutdownActions() -> None:
            pass

        def ShutdownSyncedActions(count: int) -> None:
            pass
        
        TransitionDict = \
            {
                "label": self.TP_Lbls['PowerTransLabel-State'],
                "level": self.TP_Lvls['PowerTransIndicator'],
                "count": self.TP_Lbls['PowerTransLabel-Count'],
                "start": {
                    "init": StartupActions,
                    "sync": StartupSyncedActions
                },
                "switch": {
                    "init": SwitchActions,
                    "sync": SwitchSyncedActions
                },
                "shutdown": {
                    "init": ShutdownActions,
                    "sync": ShutdownSyncedActions
                }
            }
        
        ActCtl.SOURCE_CONTROLLER = self.Controller
        
        ActivityController  = ActCtl.ActivityController(self.Host,
                                                        ActModBtns,
                                                        TransitionDict,
                                                        self.TP_Lbls['ShutdownConf-Count'],
                                                        self.TP_Lvls['ShutdownConfIndicator'])
        SrcCtl.ACTIVITY_CONTROLLER = ActivityController
        
        ActivityController.SystemSwitch('adv_share')
        
        self.Controller.UpdateDisplaySourceList()
        test1List = self.Controller._DisplaySrcList
        test1Len = len(test1List)
        
        ActivityController.SystemSwitch('share')
        
        self.Controller.UpdateDisplaySourceList()
        test2List = self.Controller._DisplaySrcList
        test2Len = len(test2List)
        
        self.assertNotEqual(test1Len, test2Len)
        self.assertNotEqual(test1List, test2List)
    
    def test_SourceController_UpdateSourceMenu(self):        
        self.assertGreaterEqual(len(self.Controller._DisplaySrcList), 6)
        self.Controller._offset = 0
        self.Controller.UpdateSourceMenu()
        
        arrowPrev = self.Controller._arrowBtns[0]
        arrowNext = self.Controller._arrowBtns[1]
        
        arrowPrevState1 = arrowPrev.Enabled
        arrowNextState1 = arrowNext.Enabled
        
        self.Controller._offset = 5
        self.Controller.UpdateSourceMenu()
        
        arrowPrevState2 = arrowPrev.Enabled
        arrowNextState2 = arrowNext.Enabled
        
        self.assertFalse(arrowPrevState1)
        self.assertTrue(arrowNextState1)
        
        self.assertTrue(arrowPrevState2)
        self.assertFalse(arrowNextState2)
    
    # TODO: Show Selected Source Test
    
    # TODO: Switch Sources Test
    
    # TODO: Matrix Switch Test
    
class MatrixController_TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.Host = extronlib.device.UIDevice('TP001')
        
        self.TP_Btns = UI.BuildButtons(self.Host, jsonPath='controls.json')
        self.TP_Btn_Grps = UI.BuildButtonGroups(self.TP_Btns, jsonPath="controls.json")
        self.TP_Lbls = UI.BuildLabels(self.Host, jsonPath='controls.json')
        self.TP_Lvls = UI.BuildLevels(self.Host, jsonPath='controls.json')
        
        self.SourceButtons = \
            {
                "select": self.TP_Btn_Grps['Source-Select'],
                "indicator": self.TP_Btn_Grps['Source-Indicator'],
                "arrows": [
                    self.TP_Btns['SourceMenu-Prev'],
                    self.TP_Btns['SourceMenu-Next']
                ]
            }
        self.MatrixDict = \
            {
                'btns': 
                    [
                        self.TP_Btns['Tech-Matrix-1,1'],
                        self.TP_Btns['Tech-Matrix-2,1'],
                        self.TP_Btns['Tech-Matrix-3,1'],
                        self.TP_Btns['Tech-Matrix-4,1'],
                        self.TP_Btns['Tech-Matrix-5,1'],
                        self.TP_Btns['Tech-Matrix-6,1'],
                        self.TP_Btns['Tech-Matrix-7,1'],
                        self.TP_Btns['Tech-Matrix-8,1'],
                        self.TP_Btns['Tech-Matrix-9,1'],
                        self.TP_Btns['Tech-Matrix-10,1'],
                        self.TP_Btns['Tech-Matrix-11,1'],
                        self.TP_Btns['Tech-Matrix-12,1'],
                        self.TP_Btns['Tech-Matrix-1,2'],
                        self.TP_Btns['Tech-Matrix-2,2'],
                        self.TP_Btns['Tech-Matrix-3,2'],
                        self.TP_Btns['Tech-Matrix-4,2'],
                        self.TP_Btns['Tech-Matrix-5,2'],
                        self.TP_Btns['Tech-Matrix-6,2'],
                        self.TP_Btns['Tech-Matrix-7,2'],
                        self.TP_Btns['Tech-Matrix-8,2'],
                        self.TP_Btns['Tech-Matrix-9,2'],
                        self.TP_Btns['Tech-Matrix-10,2'],
                        self.TP_Btns['Tech-Matrix-11,2'],
                        self.TP_Btns['Tech-Matrix-12,2'],
                        self.TP_Btns['Tech-Matrix-1,3'],
                        self.TP_Btns['Tech-Matrix-2,3'],
                        self.TP_Btns['Tech-Matrix-3,3'],
                        self.TP_Btns['Tech-Matrix-4,3'],
                        self.TP_Btns['Tech-Matrix-5,3'],
                        self.TP_Btns['Tech-Matrix-6,3'],
                        self.TP_Btns['Tech-Matrix-7,3'],
                        self.TP_Btns['Tech-Matrix-8,3'],
                        self.TP_Btns['Tech-Matrix-9,3'],
                        self.TP_Btns['Tech-Matrix-10,3'],
                        self.TP_Btns['Tech-Matrix-11,3'],
                        self.TP_Btns['Tech-Matrix-12,3'],
                        self.TP_Btns['Tech-Matrix-1,4'],
                        self.TP_Btns['Tech-Matrix-2,4'],
                        self.TP_Btns['Tech-Matrix-3,4'],
                        self.TP_Btns['Tech-Matrix-4,4'],
                        self.TP_Btns['Tech-Matrix-5,4'],
                        self.TP_Btns['Tech-Matrix-6,4'],
                        self.TP_Btns['Tech-Matrix-7,4'],
                        self.TP_Btns['Tech-Matrix-8,4'],
                        self.TP_Btns['Tech-Matrix-9,4'],
                        self.TP_Btns['Tech-Matrix-10,4'],
                        self.TP_Btns['Tech-Matrix-11,4'],
                        self.TP_Btns['Tech-Matrix-12,4']
                    ],
                'ctls': self.TP_Btn_Grps['Tech-Matrix-Mode'],
                'del': self.TP_Btns['Tech-Matrix-DeleteTies'],
                'labels': {
                    'input': 
                        [
                            self.TP_Lbls['MatrixLabel-In-1'],
                            self.TP_Lbls['MatrixLabel-In-2'],
                            self.TP_Lbls['MatrixLabel-In-3'],
                            self.TP_Lbls['MatrixLabel-In-4'],
                            self.TP_Lbls['MatrixLabel-In-5'],
                            self.TP_Lbls['MatrixLabel-In-6'],
                            self.TP_Lbls['MatrixLabel-In-7'],
                            self.TP_Lbls['MatrixLabel-In-8'],
                            self.TP_Lbls['MatrixLabel-In-9'],
                            self.TP_Lbls['MatrixLabel-In-10'],
                            self.TP_Lbls['MatrixLabel-In-11'],
                            self.TP_Lbls['MatrixLabel-In-12']
                        ],
                    'output': 
                        [
                            self.TP_Lbls['MatrixLabel-Out-1'],
                            self.TP_Lbls['MatrixLabel-Out-2'],
                            self.TP_Lbls['MatrixLabel-Out-3'],
                            self.TP_Lbls['MatrixLabel-Out-4'],
                            self.TP_Lbls['MatrixLabel-Out-5'],
                            self.TP_Lbls['MatrixLabel-Out-6']
                        ]
                }
            }
        self.AdvShareLayout = \
            [
                self.TP_Btns['Disp-Select-0,0'],
                self.TP_Btns['Disp-Ctl-0,0'],
                self.TP_Btns['Disp-Aud-0,0'],
                self.TP_Btns['Disp-Alert-0,0'],
                self.TP_Btns['Disp-Scn-0,0'],
                self.TP_Lbls['DispAdv-0,0'],
                self.TP_Btns['Disp-Select-1,0'],
                self.TP_Btns['Disp-Ctl-1,0'],
                self.TP_Btns['Disp-Aud-1,0'],
                self.TP_Btns['Disp-Alert-1,0'],
                self.TP_Btns['Disp-Scn-1,0'],
                self.TP_Lbls['DispAdv-1,0'],
                self.TP_Btns['Disp-Select-0,1'],
                self.TP_Btns['Disp-Ctl-0,1'],
                self.TP_Btns['Disp-Aud-0,1'],
                self.TP_Btns['Disp-Alert-0,1'],
                self.TP_Btns['Disp-Scn-0,1'],
                self.TP_Lbls['DispAdv-0,1'],
                self.TP_Btns['Disp-Select-1,1'],
                self.TP_Btns['Disp-Ctl-1,1'],
                self.TP_Btns['Disp-Aud-1,1'],
                self.TP_Btns['Disp-Alert-1,1'],
                self.TP_Btns['Disp-Scn-1,1'],
                self.TP_Lbls['DispAdv-1,1'],
                self.TP_Btns['Disp-Select-2,1'],
                self.TP_Btns['Disp-Ctl-2,1'],
                self.TP_Btns['Disp-Aud-2,1'],
                self.TP_Btns['Disp-Alert-2,1'],
                self.TP_Btns['Disp-Scn-2,1'],
                self.TP_Lbls['DispAdv-2,1'],
                self.TP_Btns['Disp-Select-3,1'],
                self.TP_Btns['Disp-Ctl-3,1'],
                self.TP_Btns['Disp-Aud-3,1'],
                self.TP_Btns['Disp-Alert-3,1'],
                self.TP_Btns['Disp-Scn-3,1'],
                self.TP_Lbls['DispAdv-3,1']
            ]
            
        self.Controller = SrcCtl.SourceController(self.Host,
                                                  self.SourceButtons,
                                                  self.AdvShareLayout,
                                                  self.MatrixDict,
                                                  settings.sources,
                                                  settings.destinations)
        
        self.MatrixController = SrcCtl.MatrixController(self.Controller,
                                                        self.MatrixDict['btns'],
                                                        self.MatrixDict['ctls'],
                                                        self.MatrixDict['del'],
                                                        self.MatrixDict['labels']['input'],
                                                        self.MatrixDict['labels']['output'])
    
    def test_MatrixController_PublicProperties(self): 
        self.assertEqual(self.MatrixController.SourceController, self.Controller)
        self.assertIn(self.MatrixController.Mode, ['AV', 'Aud', 'Vid', 'untie'])
        
    def test_MatrixController_PrivateProperties(self):
        self.assertEqual(self.MatrixController._ctls, self.MatrixDict['ctls'])
        self.assertEqual(self.MatrixController._del, self.MatrixDict['del'])
        self.assertEqual(self.MatrixController._inputLbls, self.MatrixDict['labels']['input'])
        self.assertEqual(self.MatrixController._outputLbls, self.MatrixDict['labels']['output'])
        self.assertIs(type(self.MatrixController._rows), type({}))
        self.assertGreater(len(self.MatrixController._rows), 0)
        self.assertIs(type(self.MatrixController._stateDict), type({}))
    
class Source_TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.Host = extronlib.device.UIDevice('TP001')
        
        self.TP_Btns = UI.BuildButtons(self.Host, jsonPath='controls.json')
        self.TP_Btn_Grps = UI.BuildButtonGroups(self.TP_Btns, jsonPath="controls.json")
        self.TP_Lbls = UI.BuildLabels(self.Host, jsonPath='controls.json')
        self.TP_Lvls = UI.BuildLevels(self.Host, jsonPath='controls.json')
        
        self.SourceButtons = \
            {
                "select": self.TP_Btn_Grps['Source-Select'],
                "indicator": self.TP_Btn_Grps['Source-Indicator'],
                "arrows": [
                    self.TP_Btns['SourceMenu-Prev'],
                    self.TP_Btns['SourceMenu-Next']
                ]
            }
        self.MatrixDict = \
            {
                'btns': 
                    [
                        self.TP_Btns['Tech-Matrix-1,1'],
                        self.TP_Btns['Tech-Matrix-2,1'],
                        self.TP_Btns['Tech-Matrix-3,1'],
                        self.TP_Btns['Tech-Matrix-4,1'],
                        self.TP_Btns['Tech-Matrix-5,1'],
                        self.TP_Btns['Tech-Matrix-6,1'],
                        self.TP_Btns['Tech-Matrix-7,1'],
                        self.TP_Btns['Tech-Matrix-8,1'],
                        self.TP_Btns['Tech-Matrix-9,1'],
                        self.TP_Btns['Tech-Matrix-10,1'],
                        self.TP_Btns['Tech-Matrix-11,1'],
                        self.TP_Btns['Tech-Matrix-12,1'],
                        self.TP_Btns['Tech-Matrix-1,2'],
                        self.TP_Btns['Tech-Matrix-2,2'],
                        self.TP_Btns['Tech-Matrix-3,2'],
                        self.TP_Btns['Tech-Matrix-4,2'],
                        self.TP_Btns['Tech-Matrix-5,2'],
                        self.TP_Btns['Tech-Matrix-6,2'],
                        self.TP_Btns['Tech-Matrix-7,2'],
                        self.TP_Btns['Tech-Matrix-8,2'],
                        self.TP_Btns['Tech-Matrix-9,2'],
                        self.TP_Btns['Tech-Matrix-10,2'],
                        self.TP_Btns['Tech-Matrix-11,2'],
                        self.TP_Btns['Tech-Matrix-12,2'],
                        self.TP_Btns['Tech-Matrix-1,3'],
                        self.TP_Btns['Tech-Matrix-2,3'],
                        self.TP_Btns['Tech-Matrix-3,3'],
                        self.TP_Btns['Tech-Matrix-4,3'],
                        self.TP_Btns['Tech-Matrix-5,3'],
                        self.TP_Btns['Tech-Matrix-6,3'],
                        self.TP_Btns['Tech-Matrix-7,3'],
                        self.TP_Btns['Tech-Matrix-8,3'],
                        self.TP_Btns['Tech-Matrix-9,3'],
                        self.TP_Btns['Tech-Matrix-10,3'],
                        self.TP_Btns['Tech-Matrix-11,3'],
                        self.TP_Btns['Tech-Matrix-12,3'],
                        self.TP_Btns['Tech-Matrix-1,4'],
                        self.TP_Btns['Tech-Matrix-2,4'],
                        self.TP_Btns['Tech-Matrix-3,4'],
                        self.TP_Btns['Tech-Matrix-4,4'],
                        self.TP_Btns['Tech-Matrix-5,4'],
                        self.TP_Btns['Tech-Matrix-6,4'],
                        self.TP_Btns['Tech-Matrix-7,4'],
                        self.TP_Btns['Tech-Matrix-8,4'],
                        self.TP_Btns['Tech-Matrix-9,4'],
                        self.TP_Btns['Tech-Matrix-10,4'],
                        self.TP_Btns['Tech-Matrix-11,4'],
                        self.TP_Btns['Tech-Matrix-12,4']
                    ],
                'ctls': self.TP_Btn_Grps['Tech-Matrix-Mode'],
                'del': self.TP_Btns['Tech-Matrix-DeleteTies'],
                'labels': {
                    'input': 
                        [
                            self.TP_Lbls['MatrixLabel-In-1'],
                            self.TP_Lbls['MatrixLabel-In-2'],
                            self.TP_Lbls['MatrixLabel-In-3'],
                            self.TP_Lbls['MatrixLabel-In-4'],
                            self.TP_Lbls['MatrixLabel-In-5'],
                            self.TP_Lbls['MatrixLabel-In-6'],
                            self.TP_Lbls['MatrixLabel-In-7'],
                            self.TP_Lbls['MatrixLabel-In-8'],
                            self.TP_Lbls['MatrixLabel-In-9'],
                            self.TP_Lbls['MatrixLabel-In-10'],
                            self.TP_Lbls['MatrixLabel-In-11'],
                            self.TP_Lbls['MatrixLabel-In-12']
                        ],
                    'output': 
                        [
                            self.TP_Lbls['MatrixLabel-Out-1'],
                            self.TP_Lbls['MatrixLabel-Out-2'],
                            self.TP_Lbls['MatrixLabel-Out-3'],
                            self.TP_Lbls['MatrixLabel-Out-4'],
                            self.TP_Lbls['MatrixLabel-Out-5'],
                            self.TP_Lbls['MatrixLabel-Out-6']
                        ]
                }
            }
        self.AdvShareLayout = \
            [
                self.TP_Btns['Disp-Select-0,0'],
                self.TP_Btns['Disp-Ctl-0,0'],
                self.TP_Btns['Disp-Aud-0,0'],
                self.TP_Btns['Disp-Alert-0,0'],
                self.TP_Btns['Disp-Scn-0,0'],
                self.TP_Lbls['DispAdv-0,0'],
                self.TP_Btns['Disp-Select-1,0'],
                self.TP_Btns['Disp-Ctl-1,0'],
                self.TP_Btns['Disp-Aud-1,0'],
                self.TP_Btns['Disp-Alert-1,0'],
                self.TP_Btns['Disp-Scn-1,0'],
                self.TP_Lbls['DispAdv-1,0'],
                self.TP_Btns['Disp-Select-0,1'],
                self.TP_Btns['Disp-Ctl-0,1'],
                self.TP_Btns['Disp-Aud-0,1'],
                self.TP_Btns['Disp-Alert-0,1'],
                self.TP_Btns['Disp-Scn-0,1'],
                self.TP_Lbls['DispAdv-0,1'],
                self.TP_Btns['Disp-Select-1,1'],
                self.TP_Btns['Disp-Ctl-1,1'],
                self.TP_Btns['Disp-Aud-1,1'],
                self.TP_Btns['Disp-Alert-1,1'],
                self.TP_Btns['Disp-Scn-1,1'],
                self.TP_Lbls['DispAdv-1,1'],
                self.TP_Btns['Disp-Select-2,1'],
                self.TP_Btns['Disp-Ctl-2,1'],
                self.TP_Btns['Disp-Aud-2,1'],
                self.TP_Btns['Disp-Alert-2,1'],
                self.TP_Btns['Disp-Scn-2,1'],
                self.TP_Lbls['DispAdv-2,1'],
                self.TP_Btns['Disp-Select-3,1'],
                self.TP_Btns['Disp-Ctl-3,1'],
                self.TP_Btns['Disp-Aud-3,1'],
                self.TP_Btns['Disp-Alert-3,1'],
                self.TP_Btns['Disp-Scn-3,1'],
                self.TP_Lbls['DispAdv-3,1']
            ]
            
        self.Controller = SrcCtl.SourceController(self.Host,
                                                  self.SourceButtons,
                                                  self.MatrixDict,
                                                  settings.sources,
                                                  settings.destinations)
        
        self.Source = SrcCtl.Source(self.Controller,
                                'WPD001',
                                'Wireless',
                                3,
                                1,
                                'Source alert text - test',
                                'WPD',
                                'WPD')
    
    def test_Source_PublicProperties(self):
        self.assertEqual(self.Source.SourceController, self.Controller)
        self.assertIs(type(self.Source.Id), type('a'))
        self.assertIs(type(self.Source.Icon), type(1))
        self.assertIs(type(self.Source.Input), type(1))
        self.assertIs(type(self.Source.AlertText), type('a'))
        self.assertIs(type(self.Source.AlertFlag), type(False))
        
    def test_Source_PrivateProperties(self):
        self.assertIs(type(self.Source.__DefaultAlert), type('a'))
        self.assertIs(type(self.Source.SourceControlPage), type('a'))
        self.assertIs(type(self.Source.AdvSourceControlPage), type('a'))
    
    # TODO: Append Alert test
    
    # TODO: Override Alert test
    
    # TODO: Reset Alert test
    
class Destination_TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.Host = extronlib.device.UIDevice('TP001')
        
        self.TP_Btns = UI.BuildButtons(self.Host, jsonPath='controls.json')
        self.TP_Btn_Grps = UI.BuildButtonGroups(self.TP_Btns, jsonPath="controls.json")
        self.TP_Lbls = UI.BuildLabels(self.Host, jsonPath='controls.json')
        self.TP_Lvls = UI.BuildLevels(self.Host, jsonPath='controls.json')
        
        self.SourceButtons = \
            {
                "select": self.TP_Btn_Grps['Source-Select'],
                "indicator": self.TP_Btn_Grps['Source-Indicator'],
                "arrows": [
                    self.TP_Btns['SourceMenu-Prev'],
                    self.TP_Btns['SourceMenu-Next']
                ]
            }
        self.MatrixDict = \
            {
                'btns': 
                    [
                        self.TP_Btns['Tech-Matrix-1,1'],
                        self.TP_Btns['Tech-Matrix-2,1'],
                        self.TP_Btns['Tech-Matrix-3,1'],
                        self.TP_Btns['Tech-Matrix-4,1'],
                        self.TP_Btns['Tech-Matrix-5,1'],
                        self.TP_Btns['Tech-Matrix-6,1'],
                        self.TP_Btns['Tech-Matrix-7,1'],
                        self.TP_Btns['Tech-Matrix-8,1'],
                        self.TP_Btns['Tech-Matrix-9,1'],
                        self.TP_Btns['Tech-Matrix-10,1'],
                        self.TP_Btns['Tech-Matrix-11,1'],
                        self.TP_Btns['Tech-Matrix-12,1'],
                        self.TP_Btns['Tech-Matrix-1,2'],
                        self.TP_Btns['Tech-Matrix-2,2'],
                        self.TP_Btns['Tech-Matrix-3,2'],
                        self.TP_Btns['Tech-Matrix-4,2'],
                        self.TP_Btns['Tech-Matrix-5,2'],
                        self.TP_Btns['Tech-Matrix-6,2'],
                        self.TP_Btns['Tech-Matrix-7,2'],
                        self.TP_Btns['Tech-Matrix-8,2'],
                        self.TP_Btns['Tech-Matrix-9,2'],
                        self.TP_Btns['Tech-Matrix-10,2'],
                        self.TP_Btns['Tech-Matrix-11,2'],
                        self.TP_Btns['Tech-Matrix-12,2'],
                        self.TP_Btns['Tech-Matrix-1,3'],
                        self.TP_Btns['Tech-Matrix-2,3'],
                        self.TP_Btns['Tech-Matrix-3,3'],
                        self.TP_Btns['Tech-Matrix-4,3'],
                        self.TP_Btns['Tech-Matrix-5,3'],
                        self.TP_Btns['Tech-Matrix-6,3'],
                        self.TP_Btns['Tech-Matrix-7,3'],
                        self.TP_Btns['Tech-Matrix-8,3'],
                        self.TP_Btns['Tech-Matrix-9,3'],
                        self.TP_Btns['Tech-Matrix-10,3'],
                        self.TP_Btns['Tech-Matrix-11,3'],
                        self.TP_Btns['Tech-Matrix-12,3'],
                        self.TP_Btns['Tech-Matrix-1,4'],
                        self.TP_Btns['Tech-Matrix-2,4'],
                        self.TP_Btns['Tech-Matrix-3,4'],
                        self.TP_Btns['Tech-Matrix-4,4'],
                        self.TP_Btns['Tech-Matrix-5,4'],
                        self.TP_Btns['Tech-Matrix-6,4'],
                        self.TP_Btns['Tech-Matrix-7,4'],
                        self.TP_Btns['Tech-Matrix-8,4'],
                        self.TP_Btns['Tech-Matrix-9,4'],
                        self.TP_Btns['Tech-Matrix-10,4'],
                        self.TP_Btns['Tech-Matrix-11,4'],
                        self.TP_Btns['Tech-Matrix-12,4']
                    ],
                'ctls': self.TP_Btn_Grps['Tech-Matrix-Mode'],
                'del': self.TP_Btns['Tech-Matrix-DeleteTies'],
                'labels': {
                    'input': 
                        [
                            self.TP_Lbls['MatrixLabel-In-1'],
                            self.TP_Lbls['MatrixLabel-In-2'],
                            self.TP_Lbls['MatrixLabel-In-3'],
                            self.TP_Lbls['MatrixLabel-In-4'],
                            self.TP_Lbls['MatrixLabel-In-5'],
                            self.TP_Lbls['MatrixLabel-In-6'],
                            self.TP_Lbls['MatrixLabel-In-7'],
                            self.TP_Lbls['MatrixLabel-In-8'],
                            self.TP_Lbls['MatrixLabel-In-9'],
                            self.TP_Lbls['MatrixLabel-In-10'],
                            self.TP_Lbls['MatrixLabel-In-11'],
                            self.TP_Lbls['MatrixLabel-In-12']
                        ],
                    'output': 
                        [
                            self.TP_Lbls['MatrixLabel-Out-1'],
                            self.TP_Lbls['MatrixLabel-Out-2'],
                            self.TP_Lbls['MatrixLabel-Out-3'],
                            self.TP_Lbls['MatrixLabel-Out-4'],
                            self.TP_Lbls['MatrixLabel-Out-5'],
                            self.TP_Lbls['MatrixLabel-Out-6']
                        ]
                }
            }
            
        ActModBtns = \
            {
                "select": self.TP_Btn_Grps['Activity-Select'],
                "indicator": self.TP_Btn_Grps['Activity-Indicator'],
                "end": self.TP_Btns['Shutdown-EndNow'],
                "cancel": self.TP_Btns['Shutdown-Cancel']
            }
        TransitionDict = \
            {
                "label": self.TP_Lbls['PowerTransLabel-State'],
                "level": self.TP_Lvls['PowerTransIndicator'],
                "count": self.TP_Lbls['PowerTransLabel-Count'],
                "start": {
                    "init": StartupActions,
                    "sync": StartupSyncedActions
                },
                "switch": {
                    "init": SwitchActions,
                    "sync": SwitchSyncedActions
                },
                "shutdown": {
                    "init": ShutdownActions,
                    "sync": ShutdownSyncedActions
                }
            }
            
        def StartupActions() -> None:
            pass

        def StartupSyncedActions(count: int) -> None:
            pass

        def SwitchActions() -> None:
            pass

        def SwitchSyncedActions(count: int) -> None:
            pass

        def ShutdownActions() -> None:
            pass

        def ShutdownSyncedActions(count: int) -> None:
            pass    
            
        vars.ActCtl = ActCtl.ActivityController(vars.TP_Main,
                                     ActModBtns,
                                     TransitionDict,
                                     self.TP_Lbls['ShutdownConf-Count'],
                                     self.TP_Lvls['ShutdownConfIndicator'])
            
        self.Controller = SrcCtl.SourceController(self.Host,
                                                  self.SourceButtons,
                                                  self.MatrixDict,
                                                  settings.sources,
                                                  settings.destinations)
        
        self.Destination = SrcCtl.Destination(self.Controller,
                                          'PRJ001',
                                          'Projector',
                                          3,
                                          'proj+scn',
                                          [1, 2],
                                          'WPD001',
                                          {
                                              'row': 0,
                                              'pos': 0
                                          })
        
    def test_Destination_PublicProperties(self):
        self.assertIs(self.Destination.SourceController, self.Controller)
        self.assertIs(type(self.Destination.Id), type('a'))
        self.assertIs(type(self.Destination.Name), type('a'))
        self.assertIs(type(self.Destination.Output), type(1))
        self.assertIs(type(self.Destination.AdvLayoutPosition), SrcCtl.LayoutTuple)
        self.assertIs(type(self.Destination.AssignedSource), type(None)) # in a brand new source object this shouldn't be set to an IO.Source object yet
        self.assertIs(type(self.Destination.GroupWorkSource), SrcCtl.Source)
    
    def test_Destination_PrivateProperties(self):
        self.assertIs(type(self.Destination._type), type(''))
        self.assertIs(type(self.Destination._relay), SrcCtl.RelayTuple)
        self.assertIs(type(self.Destination._AssignedVidInput), type(1))
        self.assertIs(type(self.Destination._AssignedAudInput), type(1))
        self.assertIs(type(self.Destination._AdvSelectBtn), type(None))
        self.assertIs(type(self.Destination._AdvCtlBtn), type(None))
        self.assertIs(type(self.Destination._AdvAudBtn), type(None))
        self.assertIs(type(self.Destination._AdvAlertBtn), type(None))
        self.assertIs(type(self.Destination._AdvScnBtn), type(None))
        self.assertIs(type(self.Destination._MatrixRow), type(None))
        self.assertIs(type(self.Destination._AlertTimer), type(None))
    
    # TODO: Assign Source test
    
    # TODO: Assign Matrix test
    
    # TODO: Get Matrix test
    
    # TODO: Assign Adv UI test
    
    # TODO: Update Adv UI test
    
class MatrixRow_TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.Host = extronlib.device.UIDevice('TP001')
        
        self.TP_Btns = UI.BuildButtons(self.Host, jsonPath='controls.json')
        self.TP_Btn_Grps = UI.BuildButtonGroups(self.TP_Btns, jsonPath="controls.json")
        self.TP_Lbls = UI.BuildLabels(self.Host, jsonPath='controls.json')
        self.TP_Lvls = UI.BuildLevels(self.Host, jsonPath='controls.json')
        
        self.SourceButtons = \
            {
                "select": self.TP_Btn_Grps['Source-Select'],
                "indicator": self.TP_Btn_Grps['Source-Indicator'],
                "arrows": [
                    self.TP_Btns['SourceMenu-Prev'],
                    self.TP_Btns['SourceMenu-Next']
                ]
            }
        self.MatrixDict = \
            {
                'btns': 
                    [
                        self.TP_Btns['Tech-Matrix-1,1'],
                        self.TP_Btns['Tech-Matrix-2,1'],
                        self.TP_Btns['Tech-Matrix-3,1'],
                        self.TP_Btns['Tech-Matrix-4,1'],
                        self.TP_Btns['Tech-Matrix-5,1'],
                        self.TP_Btns['Tech-Matrix-6,1'],
                        self.TP_Btns['Tech-Matrix-7,1'],
                        self.TP_Btns['Tech-Matrix-8,1'],
                        self.TP_Btns['Tech-Matrix-9,1'],
                        self.TP_Btns['Tech-Matrix-10,1'],
                        self.TP_Btns['Tech-Matrix-11,1'],
                        self.TP_Btns['Tech-Matrix-12,1'],
                        self.TP_Btns['Tech-Matrix-1,2'],
                        self.TP_Btns['Tech-Matrix-2,2'],
                        self.TP_Btns['Tech-Matrix-3,2'],
                        self.TP_Btns['Tech-Matrix-4,2'],
                        self.TP_Btns['Tech-Matrix-5,2'],
                        self.TP_Btns['Tech-Matrix-6,2'],
                        self.TP_Btns['Tech-Matrix-7,2'],
                        self.TP_Btns['Tech-Matrix-8,2'],
                        self.TP_Btns['Tech-Matrix-9,2'],
                        self.TP_Btns['Tech-Matrix-10,2'],
                        self.TP_Btns['Tech-Matrix-11,2'],
                        self.TP_Btns['Tech-Matrix-12,2'],
                        self.TP_Btns['Tech-Matrix-1,3'],
                        self.TP_Btns['Tech-Matrix-2,3'],
                        self.TP_Btns['Tech-Matrix-3,3'],
                        self.TP_Btns['Tech-Matrix-4,3'],
                        self.TP_Btns['Tech-Matrix-5,3'],
                        self.TP_Btns['Tech-Matrix-6,3'],
                        self.TP_Btns['Tech-Matrix-7,3'],
                        self.TP_Btns['Tech-Matrix-8,3'],
                        self.TP_Btns['Tech-Matrix-9,3'],
                        self.TP_Btns['Tech-Matrix-10,3'],
                        self.TP_Btns['Tech-Matrix-11,3'],
                        self.TP_Btns['Tech-Matrix-12,3'],
                        self.TP_Btns['Tech-Matrix-1,4'],
                        self.TP_Btns['Tech-Matrix-2,4'],
                        self.TP_Btns['Tech-Matrix-3,4'],
                        self.TP_Btns['Tech-Matrix-4,4'],
                        self.TP_Btns['Tech-Matrix-5,4'],
                        self.TP_Btns['Tech-Matrix-6,4'],
                        self.TP_Btns['Tech-Matrix-7,4'],
                        self.TP_Btns['Tech-Matrix-8,4'],
                        self.TP_Btns['Tech-Matrix-9,4'],
                        self.TP_Btns['Tech-Matrix-10,4'],
                        self.TP_Btns['Tech-Matrix-11,4'],
                        self.TP_Btns['Tech-Matrix-12,4']
                    ],
                'ctls': self.TP_Btn_Grps['Tech-Matrix-Mode'],
                'del': self.TP_Btns['Tech-Matrix-DeleteTies'],
                'labels': {
                    'input': 
                        [
                            self.TP_Lbls['MatrixLabel-In-1'],
                            self.TP_Lbls['MatrixLabel-In-2'],
                            self.TP_Lbls['MatrixLabel-In-3'],
                            self.TP_Lbls['MatrixLabel-In-4'],
                            self.TP_Lbls['MatrixLabel-In-5'],
                            self.TP_Lbls['MatrixLabel-In-6'],
                            self.TP_Lbls['MatrixLabel-In-7'],
                            self.TP_Lbls['MatrixLabel-In-8'],
                            self.TP_Lbls['MatrixLabel-In-9'],
                            self.TP_Lbls['MatrixLabel-In-10'],
                            self.TP_Lbls['MatrixLabel-In-11'],
                            self.TP_Lbls['MatrixLabel-In-12']
                        ],
                    'output': 
                        [
                            self.TP_Lbls['MatrixLabel-Out-1'],
                            self.TP_Lbls['MatrixLabel-Out-2'],
                            self.TP_Lbls['MatrixLabel-Out-3'],
                            self.TP_Lbls['MatrixLabel-Out-4'],
                            self.TP_Lbls['MatrixLabel-Out-5'],
                            self.TP_Lbls['MatrixLabel-Out-6']
                        ]
                }
            }
        self.AdvShareLayout = \
            [
                self.TP_Btns['Disp-Select-0,0'],
                self.TP_Btns['Disp-Ctl-0,0'],
                self.TP_Btns['Disp-Aud-0,0'],
                self.TP_Btns['Disp-Alert-0,0'],
                self.TP_Btns['Disp-Scn-0,0'],
                self.TP_Lbls['DispAdv-0,0'],
                self.TP_Btns['Disp-Select-1,0'],
                self.TP_Btns['Disp-Ctl-1,0'],
                self.TP_Btns['Disp-Aud-1,0'],
                self.TP_Btns['Disp-Alert-1,0'],
                self.TP_Btns['Disp-Scn-1,0'],
                self.TP_Lbls['DispAdv-1,0'],
                self.TP_Btns['Disp-Select-0,1'],
                self.TP_Btns['Disp-Ctl-0,1'],
                self.TP_Btns['Disp-Aud-0,1'],
                self.TP_Btns['Disp-Alert-0,1'],
                self.TP_Btns['Disp-Scn-0,1'],
                self.TP_Lbls['DispAdv-0,1'],
                self.TP_Btns['Disp-Select-1,1'],
                self.TP_Btns['Disp-Ctl-1,1'],
                self.TP_Btns['Disp-Aud-1,1'],
                self.TP_Btns['Disp-Alert-1,1'],
                self.TP_Btns['Disp-Scn-1,1'],
                self.TP_Lbls['DispAdv-1,1'],
                self.TP_Btns['Disp-Select-2,1'],
                self.TP_Btns['Disp-Ctl-2,1'],
                self.TP_Btns['Disp-Aud-2,1'],
                self.TP_Btns['Disp-Alert-2,1'],
                self.TP_Btns['Disp-Scn-2,1'],
                self.TP_Lbls['DispAdv-2,1'],
                self.TP_Btns['Disp-Select-3,1'],
                self.TP_Btns['Disp-Ctl-3,1'],
                self.TP_Btns['Disp-Aud-3,1'],
                self.TP_Btns['Disp-Alert-3,1'],
                self.TP_Btns['Disp-Scn-3,1'],
                self.TP_Lbls['DispAdv-3,1']
            ]
            
        self.Controller = SrcCtl.SourceController(self.Host,
                                                  self.SourceButtons,
                                                  self.AdvShareLayout,
                                                  self.MatrixDict,
                                                  settings.sources,
                                                  settings.destinations)
        
        self.MatrixController = SrcCtl.MatrixController(self.Controller,
                                                        self.MatrixDict['btns'],
                                                        self.MatrixDict['ctls'],
                                                        self.MatrixDict['del'],
                                                        self.MatrixDict['labels']['input'],
                                                        self.MatrixDict['labels']['output'])

        self.MatrixRow = SrcCtl.MatrixRow(self.MatrixController,
                                          self.MatrixDict['btns'][0:11],
                                          3)
    
    def test_MatrixRow_PublicProperties(self):
        self.assertIs(self.MatrixRow.Matrix, self.MatrixController)
        self.assertIs(type(self.MatrixRow.MatrixOutput), type(1))
        self.assertIs(type(self.MatrixRow.VidSelect), type(1))
        self.assertIs(type(self.MatrixRow.AudSelect), type(1))
        self.assertIs(type(self.MatrixRow.Objects), type([]))
    
    # TODO: Prv Update Row Btns test
    
    # TODO: Make Tie test
    
if __name__ == '__main__':
    unittest.main()