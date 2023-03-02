import unittest

## test imports ----------------------------------------------------------------
from uofi_gui import GUIController
import settings
## -----------------------------------------------------------------------------

class GUIController_TestClass(unittest.TestCase):
    def setUp(self) -> None:
        print('Setting Up')
        self.TestCtls = ['CTL001']
        self.TestTPs = ['TP001']
        self.TestController = GUIController(settings, self.TestCtls, self.TestTPs)
        return super().setUp()
    
    def test_Initilize(self):
        self.assertTrue(self.TestController.Initialize())
    
if __name__ == '__main__':
    unittest.main()