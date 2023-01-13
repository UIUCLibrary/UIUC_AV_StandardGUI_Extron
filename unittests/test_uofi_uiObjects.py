import unittest

## test imports ----------------------------------------------------------------
import extronlib.device
import uofi_gui.uiObjects as UI
## -----------------------------------------------------------------------------

class UIObjects_BuiltButtons_TestClass(unittest.TestCase): 
    def setUp(self) -> None:
        self.Host = extronlib.device.UIDevice('TP001')
        self.test_dict = \
            {
                "buttons": [
                    {
                    "Name": "Disp-Select-0,0",
                    "ID": 6001,
                    "holdTime": None,
                    "repeatTime": None
                    },
                    {
                    "Name": "Disp-Ctl-0,0",
                    "ID": 6002,
                    "holdTime": None,
                    "repeatTime": None
                    },
                    {
                    "Name": "Disp-Aud-0,0",
                    "ID": 6003,
                    "holdTime": None,
                    "repeatTime": None
                    },
                    {
                    "Name": "Disp-Scn-0,0",
                    "ID": 6004,
                    "holdTime": None,
                    "repeatTime": None
                    },
                    {
                    "Name": "Disp-Alert-0,0",
                    "ID": 6005,
                    "holdTime": None,
                    "repeatTime": None
                    }
                ]
            }
        self.test_path = 'test_controls.json'
        self.test_bad_path = 'no_such_file.json'
    
    def test_BuildButtons_Path(self):
        btnDict = UI.BuildButtons(self.Host, jsonPath=self.test_path)
        self.assertEqual(type(btnDict), type({}))

    def test_BuildButtons_Dict(self):
        btnDict = UI.BuildButtons(self.Host, jsonObj=self.test_dict)
        print(btnDict)
        self.assertEqual(type(btnDict), type({}))
        
    def test_BuildButtons_BadPath(self):
        with self.assertRaises(ValueError, msg='Specified file does not exist'):
            UI.BuildButtons(self.Host, jsonPath=self.test_bad_path)
            
    def test_BuildButtons_NoDict(self):
        with self.assertRaises(ValueError, msg='Either jsonObj or jsonPath must be specified'):
            UI.BuildButtons(self.Host)
            
    def test_BuildButtons_BadHost(self):
        with self.assertRaises(TypeError, msg='UIHost must be an extronlib.device.UIDevice object'):
            UI.BuildButtons('host', jsonPath=self.test_path)
    
if __name__ == '__main__':
    unittest.main()