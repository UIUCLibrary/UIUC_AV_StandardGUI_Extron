import unittest

## test imports ================================================================
import utilityFunctions
## =============================================================================

class UtilityFunctions_TimeIntToStr_TestCase(unittest.TestCase):
    
    def test_TimeIntToStr_unitless(self):
        
        test_values = [42, 155, 4897, 94518]
        expected = ['0:00:00:42','0:00:02:35','0:01:21:37','1:02:15:18']
        
        for i in range(len(test_values)):
            with self.subTest(i=i):
                testOutput = utilityFunctions.TimeIntToStr(test_values[i], False)
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
                self.assertEqual(utilityFunctions.TimeIntToStr(test_values[i]), expected[i])
        
if __name__ == '__main__':
    unittest.main()