import unittest

## test imports ================================================================
from utilityFunctions import TimeIntToStr, Log, DictValueSearchByKey, RunAsync, SortKeys
from extronlib.system import _ReadProgramLog, _ClearProgramLog
from datetime import datetime
## =============================================================================

class UtilityFunctions_TimeIntToStr_TestCase(unittest.TestCase):
    
    def test_TimeIntoToStr(self):
        self.assertTrue(callable(TimeIntToStr))
    
    def test_TimeIntToStr_unitless(self):
        
        test_values = [42, 155, 4897, 94518]
        expected = ['0:00:00:42','0:00:02:35','0:01:21:37','1:02:15:18']
        
        for i in range(len(test_values)):
            with self.subTest(i=i):
                try:
                    testOutput = TimeIntToStr(test_values[i], False)
                except Exception as inst:
                    self.fail("TimeIntToStr raised {} unexpectedly!".format(type(inst)))
                
                self.assertEqual(testOutput, expected[i])
        
    def test_TimeIntToStr_units(self):
        test_values = [1, 42, 117, 4897, 93678, 195273]
        expected = \
            [
                '1 second',
                '42 seconds',
                '1 minute, 57 seconds',
                '1 hour, 21 minutes, 37 seconds',
                '1 day, 2 hours, 1 minute, 18 seconds',
                '2 days, 6 hours, 14 minutes, 33 seconds'
            ]
        
        for i in range(len(test_values)):
            with self.subTest(i=i):
                try:
                    testOutput = TimeIntToStr(test_values[i], True)
                except Exception as inst:
                    self.fail("TimeIntToStr raised {} unexpectedly!".format(type(inst)))
                
                self.assertEqual(testOutput, expected[i])

class UtilityFunctions_Log_TestCase(unittest.TestCase):
    
    def test_Log(self):
        self.assertTrue(callable(Log))
        
        test_content = \
            [
                'Test String',
                ['test', 'list', 'of', 'values'],
                ['test', 'list', 'mixed', True, None, 1, 7.5],
                {'test': 'list', 'val1': 1, 2: 'val2'},
                datetime.now()
            ]
        test_levels = \
            [
                'info',
                'info',
                'error',
                'warning',
                'error'
            ]
        test_stack = \
            [
                True,
                False,
                True,
                False,
                True
            ]
        for i in range(len(test_content)):
            with self.subTest(i=i):
                _ClearProgramLog()
                try:
                    Log(test_content[i], test_levels[i], test_stack[i])
                except Exception as inst:
                    self.fail("Log raised {} unexpectedly!".format(type(inst)))
                logContent = _ReadProgramLog()
                self.assertIsInstance(logContent, str)
                self.assertGreater(len(logContent), 0)

class UtilityFunctions_RunAsync(unittest.TestCase):
    def setUp(self) -> None:
        self.test = False
        return super().setUp()
    
    @RunAsync
    def TestFunc(self):
        self.test = True
        
        self.assertTrue(self.test)
        
    def test_RunAsync(self):
        self.assertTrue(callable(RunAsync))
        try:
            self.TestFunc()
        except Exception as inst:
            self.fail('RunAsync wrapped function raised {} unexpectedly!'.format(type(inst)))
            
class UtilityFunctions_DictValueSearchByKey(unittest.TestCase):
    def setUp(self) -> None:
        self.TestDict = \
            {
                'CTL001': 'controller 1 - 2000',
                'TP001': 'touch panel 1 - 2001',
                'DSP001': 'digital signal processor 1 - 2002',
                'CAM001': 'camera 1 - 2003',
                'CAM002': 'camera 2 - 2004',
                'ENC001': 'encoder 1 - 2005',
                'ENC002': 'encoder 2 - 2006',
                'DEC001': 'decoder 1 - 2007',
                'DEC002': 'decoder 2 - 2008',
                'DEC003': 'decoder 3 - 2009',
                'DEC004': 'decoder 4 - 2010'
            }
        return super().setUp()
    
    def test_DictValueSearchByKey_MismatchedArgs(self):
        with self.assertRaises(ValueError):
            DictValueSearchByKey(self.TestDict, 'P0', False, True)
    
    def test_DictValueSearchByKey(self):
        self.assertTrue(callable(DictValueSearchByKey))
        
        search_terms = \
            [
                '001',
                'DEC',
                r'[A-Z]{2,3}[0-9]{3}',
                r'(?:DE|EN)(C\d{3})'
            ]
        search_regex = \
            [
                False,
                False,
                True,
                True
            ]
        search_capt = \
            [
                False,
                False,
                False,
                True
            ]
        expected_type = \
            [
                list,
                list,
                list,
                dict
            ]
        expected_length = \
            [
                6,
                4,
                11,
                4
            ]
        for i in range(len(search_terms)):
            with self.subTest(i=i):
                try:
                    output = DictValueSearchByKey(self.TestDict, search_terms[i], search_regex[i], search_capt[i])
                except Exception as inst:
                    self.fail('DictValueSearchByKey raised {} unexpectedly!'.format(type(inst)))
                self.assertIsInstance(output, expected_type[i])
                self.assertEqual(len(output), expected_length[i])

class UtilityFunctions_SortKeys_TestClass(unittest.TestCase):
    
    def test_UtilityFunctions_SortKeys_SortDaysOfWeek(self):
        
        # setup for test
        unsortedList = \
            [
                'Friday',
                'Sunday',
                'Wednesday',
                'Monday',
                'Thursday',
                'Saturday',
                'Tuesday'
            ]
            
        sortedList = \
            [
                'Monday', 
                'Tuesday', 
                'Wednesday', 
                'Thursday', 
                'Friday', 
                'Saturday', 
                'Sunday'
            ]
            
        self.assertNotEqual(unsortedList, sortedList)
        
        # exec method
        try:
            unsortedList.sort(key = SortKeys.SortDaysOfWeek)
        except Exception as inst:
            self.fail("List sorting raised {} unexpectedly!".format(type(inst)))
        
        # test outcomes 
        self.assertEqual(unsortedList, sortedList)

    def test_UtilityFunctions_SortKeys_HardwareSort(self):
        class testhardware:
            def __init__(self, Id) -> None:
                self.Id = Id
        
        tp = testhardware('TP001')
        prj1 = testhardware('PRJ001')
        prj2 = testhardware('PRJ002')
        ctl = testhardware('CTL001')
        unsortedList = \
            [
                tp,
                prj2,
                ctl,
                prj1
            ]
        sortedList = \
            [
                ctl,
                prj1,
                prj2,
                tp
            ]
        
        self.assertNotEqual(unsortedList, sortedList)
        
        try:
            unsortedList.sort(key = SortKeys.HardwareSort)
        except Exception as inst:
            self.fail("List sorting raised {} unexpectedly!".format(type(inst)))
            
        self.assertEqual(unsortedList, sortedList)
    
    def test_UtilityFunctions_SortKeys_HardwareSort_BadId(self):
        class testhardware:
            def __init__(self, Name) -> None:
                self.Name = Name
        
        tp = testhardware('TP001')
        prj1 = testhardware('PRJ001')
        prj2 = testhardware('PRJ002')
        ctl = testhardware('CTL001')
        unsortedList = \
            [
                tp,
                prj2,
                ctl,
                prj1
            ]
            
        with self.assertRaises(IndexError):
            unsortedList.sort(key = SortKeys.HardwareSort)
    
    def test_UtilityFunctions_SortKeys_StatusSort(self):
        class testbtn:
            def __init__(self, Name) -> None:
                self.Name = Name
        
        ds1 = testbtn('DeviceStatusIcon-1')
        ds2 = testbtn('DeviceStatusIcon-2')
        ds3 = testbtn('DeviceStatusIcon-3')
        ds4 = testbtn('DeviceStatusIcon-4')
        unsortedList = \
            [
                ds4,
                ds2,
                ds1,
                ds3
            ]
        sortedList = \
            [
                ds1,
                ds2,
                ds3,
                ds4
            ]
        
        self.assertNotEqual(unsortedList, sortedList)
        
        try:
            unsortedList.sort(key = SortKeys.StatusSort)
        except Exception as inst:
            self.fail("List sorting raised {} unexpectedly!".format(type(inst)))
            
        self.assertEqual(unsortedList, sortedList)
        
    def test_UtilityFunctions_SortKeys_StatusSort_BadName(self):
        class testbtn:
            def __init__(self, Id) -> None:
                self.Id = Id
        
        ds1 = testbtn('DeviceStatusIcon-1')
        ds2 = testbtn('DeviceStatusIcon-2')
        ds3 = testbtn('DeviceStatusIcon-3')
        ds4 = testbtn('DeviceStatusIcon-4')
        unsortedList = \
            [
                ds4,
                ds2,
                ds1,
                ds3
            ]
            
        with self.assertRaises(IndexError):
            unsortedList.sort(key = SortKeys.StatusSort)

    def test_UtilityFunctions_SortKeys_StatusSort_BadMatch(self):
        class testbtn:
            def __init__(self, Name) -> None:
                self.Name = Name
        
        ds1 = testbtn('OtherStatusIcon-1')
        ds2 = testbtn('OtherStatusIcon-2')
        ds3 = testbtn('OtherStatusIcon-3')
        ds4 = testbtn('OtherStatusIcon-4')
        unsortedList = \
            [
                ds4,
                ds2,
                ds1,
                ds3
            ]
            
        with self.assertRaises(ValueError):
            unsortedList.sort(key = SortKeys.StatusSort)

if __name__ == '__main__':
    unittest.main()