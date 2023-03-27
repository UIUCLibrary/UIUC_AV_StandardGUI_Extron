import unittest

## test imports ----------------------------------------------------------------

## -----------------------------------------------------------------------------

class TestClass(unittest.TestCase): # rename for module to be tested
    
    def test_Case(self): # configure a test case for each function in the module
        # set up test environment
        # get outputs
        # assert outputs against expectations
        pass
    
if __name__ == '__main__':
    unittest.main()