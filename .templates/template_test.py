import unittest

## test imports ----------------------------------------------------------------

## -----------------------------------------------------------------------------

class Class_TestClass(unittest.TestCase): # rename for module to be tested
    def setUp(self) -> None:
        self.TestClass = someClass
        return super().setUp()
    
    def test_Class_Properties(self): 
        # Property
        with self.subTest(param='Property'):
            self.assertIsInstance(self.TestClass.Property, PropertyClass)
            
    def test_Class_PRIV_Properties(self):
        # __PrivProp
        with self.subTest(param='__PrivProp'):
            self.assertIsInstance(self.TestClass._someClass__PrivProp, PrivPropClass)
            
    def test_Class_EventHandler_TestHandler(self):
        btnList = []
        actList = []
        
        for btn in btnList:
            for act in actList:
                with self.subTest(button=btn.Name, action=act):
                    try:
                        self.TestClass._someClass__TestHandler(btn, act)
                    except Exception as inst:
                        self.fail('__TestHandler raised {} unexpectedly!'.format(type(inst)))
    
    def test_Class_PRIV_Method(self):
        try:
            self.TestClass._someClass__Method()
        except Exception as inst:
            self.fail('__Method raised {} unexpectedly!'.format(type(inst)))
    
    def test_Class_Method(self):
        try:
            self.TestClass.Method()
        except Exception as inst:
            self.fail('Method raised {} unexpectedly!'.format(type(inst)))
    
if __name__ == '__main__':
    unittest.main()