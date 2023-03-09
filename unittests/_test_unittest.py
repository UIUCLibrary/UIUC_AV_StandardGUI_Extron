import unittest

## test imports ----------------------------------------------------------------
from extronlib.system import Wait
## -----------------------------------------------------------------------------

class Unittest_TestClass(unittest.TestCase): # rename for module to be tested
    
    def test_Success(self):
        self.assertEqual(1, 1)
        
    def test_Failure(self): 
        self.assertEqual(1, 2)
        
    def test_Wait_Decorator(self):
        @Wait(1)
        def WaitHandler():
            self.assertEqual(1, 2)
    
    def wait_callable(self):
        self.assertEqual(1, 1)
        
    def test_Wait_Callable(self):
        Wait(1, self.wait_callable)
    
if __name__ == '__main__':
    unittest.main()