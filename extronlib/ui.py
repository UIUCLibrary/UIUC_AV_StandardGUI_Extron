import extronlib.device
from typing import Dict, Tuple, List, Union

## CLASS DEFINITIONS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Button:
    _ada_blinkRates = ['Slow', 'Medium', 'Fast']
    _dummy_ID = 42000
    def __init__(self,
                 Host: Union[extronlib.device.UIDevice,
                             extronlib.device.eBUSDevice,
                             extronlib.device.ProcessorDevice,
                             extronlib.device.SPDevice],
                 ID: Union[int, str],
                 holdTime: float=None,
                 repeatTime: float=None) -> None:
        """Representation of Hard/Soft buttons

        A button may trigger several events depending on the configuration; however, Touch Panels only issue Pressed and Released messages to the control processor. Other events (e.g., Held, Repeated) are timer driven within the Button instance.

        Parameters:	
            UIHost (extronlib.device) – Device object hosting this UIObject\n
            ID (int,string) – ID or Name of the UIObject\n
            holdTime (float) – Time for Held event. Held event is triggered only once if the button is pressed and held beyond this time. If holdTime is given, it must be a floating point number specifying period of time in seconds of button being pressed and held to trigger Held event.\n
            repeatTime (float) – Time for Repeated event. After holdTime expires, the Repeated event is triggered for every additional repeatTime of button being held. If repeatTime is given, it must be a floating point number specifying time in seconds of button being held.
        
        Note - If button is released before holdTime expires, a Tapped event is triggered instead of a Released event. If the button is released after holdTime expires, there will be no Tapped event.
        """
        
        ## Untracked Events
        # Held
        # Pressed
        # Released
        # Repeated
        # Tapped
        
        self.BlinkState = 'Not blinking'
        self.Enabled = True
        self.Host = Host
        if type(ID) == type(1):
            self.ID = ID
            self.Name = 'Dummy Name'
        elif type(ID) == type(''):
            self.ID = self._dummy_ID
            self._dummy_ID += 1
            self.Name = ID
        else:
            raise ValueError("ID must be either an int ID or string Name")
        self.PressedState = False
        self.State = 0
        self.Visible = True
        self._holdTime = holdTime
        self._repeatTime = repeatTime
        self._customBlink = None
        self._blinkRate = None
        self._blinkStates = None
        self._text = 'Dummy Button Text'
        
    def CustomBlink(self, rate: float, stateList: List[int]) -> None:
        """Make the button cycle through each of the states provided.

        Parameters:	
            rate (float) – duration of time in seconds for one visual state to stay until replaced by the next visual state.
            stateList (list of ints) – list of visual states that this button blinks among.
        """
        self._blinkStates = stateList
        self.BlinkState = 'Blinking'
        self._blinkRate = "Custom"
        self._customBlink = rate
        
    def SetBlinking(self, rate: str, stateList: List[int]) -> None:
        if rate in self._ada_blinkRates:
            self._blinkRate = rate
            self.BlinkState = 'Blinking'
            self._customBlink = None
            self._blinkStates = stateList
        else:
            raise ValueError("Rate must be one of 'Slow', 'Medium', or 'Fast'")
    
    def SetEnable(self, enabled: bool) -> None:
        """Enable or disable a UI control object.

        Parameters:	enable (bool) – True to enable the object or False to disable it.
        """
        self.Enabled = enabled
        
    def SetState(self, state: int) -> None:
        """Set the current visual state

        Parameters:	State (int) – visual state number
        
        Note - Setting the current state stops button from blinking, if it is running. (SetBlinking())
        """
        self.State = state
        self.BlinkState = 'Not blinking'
        
    def SetText(self, text: str) -> None:
        """Specify text to display on the UIObject"""
        self._text = text
        
    def SetVisible(self, visible: bool) -> None:
        """Change the visibility of a UI control object."""
        self.Visible = visible
    
class Knob:
    def __init__(self,
                 Host: Union[extronlib.device.UIDevice,
                             extronlib.device.eBUSDevice,
                             extronlib.device.ProcessorDevice,
                             extronlib.device.SPDevice],
                 ID: int) -> None:
        """Knob is a rotary control that has 36 steps for a full revolution

        Parameters:	
            UIHost (extronlib.device) – Device object hosting this UIObject\n
            ID (int) – ID of the UIObject
        """
        ## Untracked Events
        # Turned
        
        self.Host = Host
        self.ID = ID
    
class Label:
    _dummy_ID = 43000
    def __init__(self,
                 Host: Union[extronlib.device.UIDevice,
                             extronlib.device.eBUSDevice,
                             extronlib.device.ProcessorDevice,
                             extronlib.device.SPDevice],
                 ID: Union[int, str]) -> None:
        """Label object displays text string on the screen

        Parameters:	
            UIHost (extronlib.device) – Device object hosting this UIObject\n
            ID (int, string) – ID or Name of the UIObject
        """
        
        self.Host = Host
        if type(ID) == type(1):
            self.ID = ID
            self.Name = 'Dummy Name'
        elif type(ID) == type(''):
            self.ID = self._dummy_ID
            self._dummy_ID += 1
            self.Name = ID
        else:
            raise ValueError("ID must be either an int ID or string Name")
        self.Visible = True
        self._text = "Dummy Label Text"
            
    def SetText(self, text: str) -> None:
        """Specify text to display on the UIObject"""
        self._text = text
        
    def SetVisible(self, visible: bool) -> None:
        """Change the visibility of a UI control object."""
        self.Visible = visible
    
class Level:
    _dummy_ID = 44000
    def __init__(self,
                 UIHost: Union[extronlib.device.UIDevice,
                             extronlib.device.eBUSDevice,
                             extronlib.device.ProcessorDevice,
                             extronlib.device.SPDevice],
                 ID: Union[int, str]) -> None:
        """This module defines interfaces of Level UI.

        Parameters:	
            UIHost (extronlib.device) – Device object hosting this UIObject\n
            ID (int, string) – ID or Name of the UIObject
        """
        self.Host = UIHost
        if type(ID) == type(1):
            self.ID = ID
            self.Name = 'Dummy Name'
        elif type(ID) == type(''):
            self.ID = self._dummy_ID
            self._dummy_ID += 1
            self.Name = ID
        else:
            raise ValueError("ID must be either an int ID or string Name")
        self.Level = 0
        self.Max = 100
        self.Min = 0
        self.Visible = True
        self._step = 1

    def Dec(self) -> None:
        """Nudge the level down a step."""
        self.Level -= self._step
        if self.Level < self.Min:
            self.Level = self.Min
            
    def Inc(self) -> None:
        """Nudge the level up a step."""
        self.Level += self._step
        if self.Level > self.Max:
            self.Level = self.Max
    
    def SetLevel(self, Level: int) -> None:
        """Set the current level.

        Parameters:	Level (int) – Discrete value of the level object
        """
        self.Level = Level
        if self.Level < self.Min:
            self.Level = self.Min
        if self.Level > self.Max:
            self.Level = self.Max
            
    def SetRange(self, Min: int, Max: int, Step: int=1) -> None:
        """Set level object’s allowed range and the step size.

        Parameters:	
            Min (int) – Minimum level\n
            Max (int) – Maximum level\n
            Step (int) – Optional step size for Inc() and Dec().
        
        Note
            The default range is 0 - 100 with a step size of 1.\n
            For multi-state levels, you must set the level range to match the number of states in the level.
        """
        if Min >= Max:
            raise ValueError('Min must be less than max')
        self.Min = Min
        self.Max = Max
        self._step = Step
        
    def SetVisible(self, visible: bool) -> None:
        """Change the visibility of a UI control object."""
        self.Visible = visible
    
class Slider:
    _dummy_ID = 45000
    def __init__(self, 
                 UIHost: Union[extronlib.device.UIDevice,
                             extronlib.device.eBUSDevice,
                             extronlib.device.ProcessorDevice,
                             extronlib.device.SPDevice],
                 ID: Union[int, str]) -> None:
        """This module defines interfaces of Slider UI.

        Parameters:	
            UIHost (UIDevice) – Device object hosting this UIObject\n
            ID (int, string) – ID or Name of the UIObject
        """
        ## Untracked Events
        # Changed
        # Pressed
        # Released
        
        self.Enabled = True
        self.Fill = 0
        self.Host = UIHost
        if type(ID) == type(1):
            self.ID = ID
            self.Name = 'Dummy Name'
        elif type(ID) == type(''):
            self.ID = self._dummy_ID
            self._dummy_ID += 1
            self.Name = ID
        else:
            raise ValueError("ID must be either an int ID or string Name")
        self.Max = 100
        self.Min = 0
        self.Step = 1
        self.Visible = True
        
    def SetEnable(self, enable: bool) -> None:
        """Enable or disable a UI control object.

        Parameters:	enable (bool) – True to enable the object or False to disable it.
        """
        self.Enabled = enable
    
    def SetFill(self, Fill: Union[int, float]) -> None:
        self.Fill = Fill
    
    def SetRange(self, Min: Union[int, float], Max: Union[int, float], Step: Union[int, float]=1) -> None:
        """Set slider object’s allowed range and the step size.

        Parameters:	
            Min (int, float) – Minimum level
            Max (int, float) – Maximum level
            Step (int, float) – Optional step size.
        
        Note - The default range is 0 - 100 with a step size of 1.
        """
        if Min > Max:
            raise ValueError('Min must be smaller than Max')
        self.Min = Min
        self.Max = Max
        self.Step = Step
        
    def SetVisible(self, visible: bool) -> None:
        """Change the visibility of a UI control object.

        Parameters:	visible (bool) – True to make the object visible or False to hide it.
        """
        self.Visible = visible
    
## +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++