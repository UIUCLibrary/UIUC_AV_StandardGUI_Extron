import unittest
from typing import Dict, Tuple, List, Callable, Union

## test imports ----------------------------------------------------------------
from uofi_gui import GUIController
from uofi_gui.activityControls import ActivityController
from uofi_gui.uiObjects import ExUIDevice
from uofi_gui.sourceControls import SourceController, Source, Destination, MatrixController, MatrixRow
import settings

from extronlib.ui import Button
from extronlib.system import MESet
## -----------------------------------------------------------------------------
 
class SourceController_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestGUIController = GUIController(settings, self.TestCtls, self.TestTPs)
        self.TestGUIController.Initialize()
        self.TestUIController = self.TestGUIController.TP_Main
        self.TestSourceController = self.TestUIController.SrcCtl
        return super().setUp()
    
    def test_SourceController_Type(self):
        self.assertIsInstance(self.TestSourceController, SourceController)
    
    def test_SourceController_Properties(self): # configure a test case for each unit in the module
        # UIHost
        with self.subTest(param='UIHost'):
            self.assertIsInstance(self.TestSourceController.UIHost, ExUIDevice)
        
        # GUIHost
        with self.subTest(param='GUIHost'):
            self.assertIsInstance(self.TestSourceController.GUIHost, GUIController)
        
        # Sources
        with self.subTest(param='Sources'):
            self.assertIsInstance(self.TestSourceController.Sources, list)
            for item in self.TestSourceController.Sources:
                with self.subTest(iter=item.Name):
                    self.assertIsInstance(item, Source)
        
        # Destinations
        with self.subTest(param='Destinations'):
            self.assertIsInstance(self.TestSourceController.Destinations, list)
            for item in self.TestSourceController.Destinations:
                with self.subTest(iter=item.Name):
                    self.assertIsInstance(item, Destination)
        
        # PrimaryDestination
        with self.subTest(param='PrimaryDestination'):
            self.assertIsInstance(self.TestSourceController.PrimaryDestination, Destination)
            
        # SelectedSource
        with self.subTest(param='SelectedSource'):
            self.assertIsNone(self.TestSourceController.SelectedSource) # this inits as none
        
        # Privacy
        with self.subTest(param="Privacy"):
            self.assertFalse(self.TestSourceController.Privacy)
        
        # OpenControlPopup
        with self.subTest(param='OpenControlPopup'):
            self.assertIsNone(self.TestSourceController.OpenControlPopup)
            
        # BlankSource
        with self.subTest(param='BlankSource'):
            self.assertIsInstance(self.TestSourceController.BlankSource, Source)
        
    def test_SourceController_PRIV_Properties(self):
        # __SourceBtns
        with self.subTest(param='__SourceBtns'):
            self.assertIsInstance(self.TestSourceController._SourceController__SourceBtns, MESet)
        
        # __SourceInds
        with self.subTest(param='__SourceInds'):
            self.assertIsInstance(self.TestSourceController._SourceController__SourceInds, MESet)
        
        # __ArrowBtns
        with self.subTest(param='__ArrowBtns'):
            self.assertIsInstance(self.TestSourceController._SourceController__ArrowBtns, list)
            for btn in self.TestSourceController._SourceController__ArrowBtns:
                with self.subTest(btn=btn.Name):
                    self.assertIsInstance(btn, Button)
        
        # __PrivacyBtn
        with self.subTest(param='__PrivacyBtn'):
            self.assertIsInstance(self.TestSourceController._SourceController__PrivacyBtn, Button)
        
        # __ReturnToGroupBtn
        with self.subTest(param='__ReturnToGroupBtn'):
            self.assertIsInstance(self.TestSourceController._SourceController__ReturnToGroupBtn, Button)
        
        # __Offset
        with self.subTest(param='__Offset'):
            self.assertIsInstance(self.TestSourceController._SourceController__Offset, int)
        
        # __AdvLayout
        with self.subTest(param='__AdvLayout'):
            self.assertIsInstance(self.TestSourceController._SourceController__AdvLayout, str)
        
        # __Matrix
        with self.subTest(param='__Matrix'):
            self.assertIsInstance(self.TestSourceController._SourceController__Matrix, MatrixController)
    
    # def test_SourceController_PRIV_GetUIForAdvDest(self):
    #     # TODO: fix these to dunder
    #     rtn = self.Controller._GetUIForAdvDest(self.Controller.Destinations[0])
    #     self.assertIs(type(rtn), type({}))
    #     self.assertEqual(len(rtn), 6)
    #     for item in rtn.values():
    #         with self.subTest(item=item):
    #             self.assertIn(type(item), [extronlib.ui.Button, extronlib.ui.Label])
        
    # def test_SourceController_PRIV_GetPositionByBtnName(self):
    #     # TODO: fix these to dunder
    #     rtn = self.Controller._GetPositionByBtnName('Disp-Select-0,0')
    #     self.assertIs(type(rtn), SrcCtl.LayoutTuple)
        
    # def test_SourceController_GetAdvShareLayout(self):
    #     rtn = self.Controller.GetAdvShareLayout()
    #     self.assertIs(type(rtn), str)
    #     self.assertRegex(rtn, r"Source-Control-Adv_\d+,\d+")
        
    # def test_SourceController_GetDestination_Id(self):
    #     testID = 'PRJ001'
        
    #     rtn = self.Controller.GetDestination(id = testID)
    #     self.assertIs(type(rtn), SrcCtl.Destination)
    #     self.assertEqual(rtn.Id, testID)
        
    # def test_SourceController_GetDestination_Name(self):
    #     testName = 'Projector'
        
    #     rtn = self.Controller.GetDestination(name = testName)
    #     self.assertIs(type(rtn), SrcCtl.Destination)
    #     self.assertEqual(rtn.Name, testName)
        
    # def test_SourceController_GetDestinationIndexByID(self):
    #     testID = 'MON001'
    #     expectedVal = 1
        
    #     rtn = self.Controller.GetDestinationIndexByID(testID)
    #     self.assertIs(type(rtn), int)
    #     self.assertEqual(rtn, expectedVal)
        
    # def test_SourceController_GetSource_Id(self):
    #     testID = 'PC001'
        
    #     rtn = self.Controller.GetSource(id = testID)
    #     self.assertIs(type(rtn), SrcCtl.Source)
    #     self.assertEqual(rtn.Id, testID)
        
    # def test_SourceController_GetSource_Name(self):
    #     testName = 'Room PC'
        
    #     rtn = self.Controller.GetSource(name = testName)
    #     self.assertIs(type(rtn), SrcCtl.Source)
    #     self.assertEqual(rtn.Name, testName)
        
    # def test_SourceController_GetSourceIndexByID(self):
    #     testID = 'WPD001'
    #     expectedVal = 3
        
    #     rtn = self.Controller.GetSourceIndexByID(testID)
    #     self.assertIs(type(rtn), int)
    #     self.assertEqual(rtn, expectedVal)
    
    # def test_SourceController_SetPrimaryDestination(self):        
    #     testDest = self.Controller.Destinations[1]
        
    #     self.assertIsNot(self.Controller.PrimaryDestination, testDest)
        
    #     self.Controller.SetPrimaryDestination(testDest)
        
    #     self.assertIs(type(self.Controller.PrimaryDestination), SrcCtl.Destination)
    #     self.assertIs(self.Controller.PrimaryDestination, testDest)
        
    # def test_SourceController_SelectSource_Source(self):
    #     testSrc = self.Controller.Sources[1]
        
    #     self.assertIsNot(self.Controller.SelectedSource, testSrc)
        
    #     self.Controller.SelectSource(testSrc)
        
    #     self.assertIs(type(self.Controller.SelectedSource), SrcCtl.Source)
    #     self.assertIs(self.Controller.SelectedSource, testSrc)
        
    # def test_SourceController_SelectSource_StrName(self):
    #     testSrc = self.Controller.Sources[2]
        
    #     self.assertIsNot(self.Controller.SelectedSource, testSrc)
        
    #     self.Controller.SelectSource(testSrc.Name)
        
    #     self.assertIs(type(self.Controller.SelectedSource), SrcCtl.Source)
    #     self.assertIs(self.Controller.SelectedSource, testSrc)
        
    # def test_SourceController_SelectSource_StrId(self):        
    #     testSrc = self.Controller.Sources[3]
        
    #     self.assertIsNot(self.Controller.SelectedSource, testSrc)
        
    #     self.Controller.SelectSource(testSrc.Id)
        
    #     self.assertIs(type(self.Controller.SelectedSource), SrcCtl.Source)
    #     self.assertIs(self.Controller.SelectedSource, testSrc)
    
    # def test_SourceController_UpdateDisplaySourceList(self):
    #     pass
    
    # def test_SourceController_UpdateSourceMenu(self):        
    #     self.assertGreaterEqual(len(self.Controller._DisplaySrcList), 6)
    #     self.Controller._offset = 0
    #     self.Controller.UpdateSourceMenu()
        
    #     arrowPrev = self.Controller._arrowBtns[0]
    #     arrowNext = self.Controller._arrowBtns[1]
        
    #     arrowPrevState1 = arrowPrev.Enabled
    #     arrowNextState1 = arrowNext.Enabled
        
    #     self.Controller._offset = 5
    #     self.Controller.UpdateSourceMenu()
        
    #     arrowPrevState2 = arrowPrev.Enabled
    #     arrowNextState2 = arrowNext.Enabled
        
    #     self.assertFalse(arrowPrevState1)
    #     self.assertTrue(arrowNextState1)
        
    #     self.assertTrue(arrowPrevState2)
    #     self.assertFalse(arrowNextState2)
    
    # TODO: Show Selected Source Test
    
    # TODO: Switch Sources Test
    
    # TODO: Matrix Switch Test
    
# class MatrixController_TestClass(unittest.TestCase):
#     def setUp(self) -> None:
#         return super().setUp()
    
#     def test_MatrixController_Properties(self): 
#         self.assertEqual(self.MatrixController.SourceController, self.Controller)
#         self.assertIn(self.MatrixController.Mode, ['AV', 'Aud', 'Vid', 'untie'])
        
#     def test_MatrixController_PRIV_Properties(self):
#         # TODO: fix these to dunder
#         self.assertEqual(self.MatrixController._ctls, self.MatrixDict['ctls'])
#         self.assertEqual(self.MatrixController._del, self.MatrixDict['del'])
#         self.assertEqual(self.MatrixController._inputLbls, self.MatrixDict['labels']['input'])
#         self.assertEqual(self.MatrixController._outputLbls, self.MatrixDict['labels']['output'])
#         self.assertIs(type(self.MatrixController._rows), type({}))
#         self.assertGreater(len(self.MatrixController._rows), 0)
#         self.assertIs(type(self.MatrixController._stateDict), type({}))
    
# class Source_TestClass(unittest.TestCase):
#     def setUp(self) -> None:
#         return super().setUp()
    
#     def test_Source_Properties(self):
#         self.assertEqual(self.Source.SourceController, self.Controller)
#         self.assertIs(type(self.Source.Id), type('a'))
#         self.assertIs(type(self.Source.Icon), type(1))
#         self.assertIs(type(self.Source.Input), type(1))
#         self.assertIs(type(self.Source.AlertText), type('a'))
#         self.assertIs(type(self.Source.AlertFlag), type(False))
        
#     def test_Source_PRIV_Properties(self):
#         # TODO: fix these to dunder
#         self.assertIs(type(self.Source.__DefaultAlert), type('a'))
#         self.assertIs(type(self.Source.SourceControlPage), type('a'))
#         self.assertIs(type(self.Source.AdvSourceControlPage), type('a'))
    
#     # TODO: Append Alert test
    
#     # TODO: Override Alert test
    
#     # TODO: Reset Alert test
    
# class Destination_TestClass(unittest.TestCase):
#     def setUp(self) -> None:
#         return super().setUp()
        
#     def test_Destination_Properties(self):
#         self.assertIs(self.Destination.SourceController, self.Controller)
#         self.assertIs(type(self.Destination.Id), type('a'))
#         self.assertIs(type(self.Destination.Name), type('a'))
#         self.assertIs(type(self.Destination.Output), type(1))
#         self.assertIs(type(self.Destination.AdvLayoutPosition), SrcCtl.LayoutTuple)
#         self.assertIs(type(self.Destination.AssignedSource), type(None)) # in a brand new source object this shouldn't be set to an IO.Source object yet
#         self.assertIs(type(self.Destination.GroupWorkSource), SrcCtl.Source)
    
#     def test_Destination_PRIV_Properties(self):
#         # TODO: fix these to dunder
#         self.assertIs(type(self.Destination._type), type(''))
#         self.assertIs(type(self.Destination._relay), SrcCtl.RelayTuple)
#         self.assertIs(type(self.Destination._AssignedVidInput), type(1))
#         self.assertIs(type(self.Destination._AssignedAudInput), type(1))
#         self.assertIs(type(self.Destination._AdvSelectBtn), type(None))
#         self.assertIs(type(self.Destination._AdvCtlBtn), type(None))
#         self.assertIs(type(self.Destination._AdvAudBtn), type(None))
#         self.assertIs(type(self.Destination._AdvAlertBtn), type(None))
#         self.assertIs(type(self.Destination._AdvScnBtn), type(None))
#         self.assertIs(type(self.Destination._MatrixRow), type(None))
#         self.assertIs(type(self.Destination._AlertTimer), type(None))
    
#     # TODO: Assign Source test
    
#     # TODO: Assign Matrix test
    
#     # TODO: Get Matrix test
    
#     # TODO: Assign Adv UI test
    
#     # TODO: Update Adv UI test
    
# class MatrixRow_TestClass(unittest.TestCase):
#     def setUp(self) -> None:
#         return super().setUp()
    
#     def test_MatrixRow_Properties(self):
#         self.assertIs(self.MatrixRow.Matrix, self.MatrixController)
#         self.assertIs(type(self.MatrixRow.MatrixOutput), type(1))
#         self.assertIs(type(self.MatrixRow.VidSelect), type(1))
#         self.assertIs(type(self.MatrixRow.AudSelect), type(1))
#         self.assertIs(type(self.MatrixRow.Objects), type([]))
    
#     # TODO: Private properties?
    
#     # TODO: Prv Update Row Btns test
    
#     # TODO: Make Tie test
    
if __name__ == '__main__':
    unittest.main()