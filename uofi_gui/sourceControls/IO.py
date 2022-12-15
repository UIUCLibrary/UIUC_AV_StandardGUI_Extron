## Begin ControlScript Import --------------------------------------------------
from extronlib import event, Version
from extronlib.device import eBUSDevice, ProcessorDevice, UIDevice
from extronlib.interface import (CircuitBreakerInterface, ContactInterface,
    DigitalInputInterface, DigitalIOInterface, EthernetClientInterface,
    EthernetServerInterfaceEx, FlexIOInterface, IRInterface, PoEInterface,
    RelayInterface, SerialInterface, SWACReceptacleInterface, SWPowerInterface,
    VolumeInterface)
from extronlib.ui import Button, Knob, Label, Level, Slider
from extronlib.system import (Email, Clock, MESet, Timer, Wait, File, RFile,
    ProgramLog, SaveProgramLog, Ping, WakeOnLan, SetAutomaticTime, SetTimeZone)

print(Version()) ## Sanity check ControlScript Import
## End ControlScript Import ----------------------------------------------------

from typing import Dict, Tuple, List, Callable, Union
from collections import namedtuple
from uofi_gui.sourceControls import SourceController
import vars

RelayTuple = namedtuple('RelayTuple', ['Up', 'Down'])
LayoutTuple = namedtuple('LayoutTuple', ['Row', 'Pos'])
MatrixTuple = namedtuple('MatrixTuple', ['Vid', 'Aud'])

class Source:
    def __init__(self,
                 SrcCtl: SourceController,
                 id: str,
                 name: str,
                 icon: int,
                 input: int,
                 alert: int,
                 srcCtl: str=None,
                 advSrcCtl: str=None) -> None:
        
        self.SourceController = SrcCtl
        self.Id = id
        self.Name = name
        self.Icon = icon
        self.Input = input
        self.AlertText = alert
        self.AlertFlag = False
        
        self._defaultAlert = alert
        self._sourceControlPage = srcCtl
        self._advSourceControlPage = advSrcCtl
        
    def AppendAlert(self, msg: str, raiseFlag: bool=False) -> None:
        self.AlertText = "{existing}\n{append}".format(existing = self.AlertText, append = msg)
        if raiseFlag:
            self.AlertFlag = True
        
    def OverrideAlert(self, msg: str, raiseFlag: bool=False) -> None:
        self.AlertText = msg
        if raiseFlag:
            self.AlertFlag = True
        
    def ResetAlert(self, raiseFlag: bool=False) -> None:
        self.AlertText = self._defaultAlert
        if raiseFlag:
            self.AlertFlag = True
        
class Destination:
    def __init__(self,
                 SrcCtl: SourceController,
                 id: str,
                 name: str,
                 output: int,
                 destType: str,
                 rly: List,
                 groupWrkSrc: str,
                 advLayout: Dict[str, int]) -> None:
        
        self.SourceController = SrcCtl
        self.Id = id
        self.Name = name
        self.Output = output
        self.AdvLayoutPosition = LayoutTuple(Row=advLayout['row'], Pos=advLayout['pos'])
        self.AssignedSource = None
        self.GroupWorkSource = self.SourceController.GetSource(id = groupWrkSrc)
        
        self._type = destType
        self._relay = RelayTuple(Up=rly[0], Down=rly[1])
        self._AssignedVidInput = 0
        self._AssignedAudInput = 0
        self._AdvSelectBtn = None
        self._AdvCtlBtn = None
        self._AdvAudBtn = None
        self._AdvAlertBtn = None
        self._AdvScnBtn = None
        self._MatrixRow = None
        
    def AssignSource(self, source: Source) -> None:
        self.AssignedSource = source
        self._AssignedVidInput = source.Input
        self._AssignedAudInput = source.Input
        self.UpdateAdvUI()
        
    def AssignMatrix(self, input: int, tieType: str='AV') -> None:
        if tieType != 'Aud' or tieType != 'Vid' or tieType != 'AV':
            raise ValueError("TieType must either be 'AV', 'Aud', or 'Vid'")
        self.AssignedSource = None
        self.UpdateAdvUI()
        if tieType == 'Vid' or tieType == 'AV':
            self._AssignedVidInput = input
        if tieType == 'Aud' or tieType == 'AV':
            self._AssignedAudInput = input
            
    def GetMatrix(self) -> None:
        return MatrixTuple(Vid=self._AssignedVidInput, Aud=self._AssignedAudInput)
    
    def AssignAdvUI(self, ui: Dict[str, Union[Button, Label]]) -> None:
        self._AdvSelectBtn = ui['select']
        self._AdvCtlBtn = ui['ctl']
        self._AdvAudBtn = ui['aud']
        self._AdvAlertBtn = ui['alert']
        self._AdvScnBtn = ui['scn']
        self._AdvLabel = ui['label']
        
        # set distination label text
        self._AdvLabel.SetText(self.Name)
        
        # clear selected source text
        self._AdvSelectBtn.SetText("") 
        
        @event(self._AdvSelectBtn, 'Pressed')
        def advSelectHandler(button, action):
            curSource = self.SourceController.SelectedSource
            self.SourceController.SwitchSources(curSource, [self])
            self.UpdateAdvUI()
            
        # Source Control Buttons
        self._AdvCtlBtn.SetVisible(False)
        self._AdvCtlBtn.Enabled(False)
        
        @event(self._AdvCtlBtn, 'Pressed')
        def advSrcCtrHandler(button, action):
            # configure source control page
            # TODO: configure the source control page
            
            # show source control page
            self.SourceController.UIHost.ShowPage(self.AssignedSource._advSourceControlPage)
        
        # Destination Audio Buttons
        self._AdvAudBtn.SetState(1)
        
        @event(self._AdvAudBtn, ['Tapped', 'Released'])
        def advAudHandler(button, action):
            if action == "Tapped":
                # TODO: handle system audio changes
                if button.State == 0: # system audio unmuted
                    pass # deselect this destination as the system audio follow
                elif button.State == 1: # system audio muted
                    pass # select this destination as the system audio follow, deselect any other destination as the system audio follow
                elif button.State == 2: # local audio unmuted
                    pass # mute local audio
                elif button.State == 3: # local audio muted
                    pass # unmute local audio
            elif action == "Released":
                if (button.State == 0 or button.State == 1) \
                and self._type == 'mon':
                    # TODO: if this destination is the system audio follow, unfollow
                    muteState = 0 # TODO: get current mute state of the destination monitor
                    if muteState:
                        # TODO: set destination to unmute
                        button.SetState(2)
                    else:
                        # TODO: set mute
                        button.SetState(3)
                elif (button.State == 2 or button.State == 3):
                    button.SetState(1)
        
        # Destination Alert Buttons
        self._AdvAlertBtn.SetVisible(False)
        self._AdvAlertBtn.Enabled(False)
        
        @event(self._AdvAlertBtn, 'Pressed')
        def destAlertHandler(button, action):
            vars.TP_Lbls['SourceAlertLabel'] = self.AssignedSource.AlertText
            self.SourceController.UIHost.ShowPopup('Modal-SrcErr')
            
        @Timer(2)
        def SourceAlertHandler(timer, count) -> None:
            # Does current source for this destination have an alert flag
            if self.AssignedSource.AlertFlag:
                self._AdvAlertBtn.SetVisible(True)
                self._AdvAlertBtn.Enabled(True)
                self._AdvAlertBtn.SetBlinking('Medium', [0,1])
                if self.SourceController.PrimaryDestination == self and vars.ActCtl.CurrentActivity != 'adv_share':
                    vars.TP_Lbls['SourceAlertLabel'] = self.AssignedSource.AlertText
            else:
                self._AdvAlertBtn.SetVisible(False)
                self._AdvAlertBtn.Enabled(False)
                self._AdvAlertBtn.SetState(1)
                if self.SourceController.PrimaryDestination == self and vars.ActCtl.CurrentActivity != 'adv_share':
                    vars.TP_Lbls['SourceAlertLabel'] = ''
        
        # Screen Control Buttons
        if self._type == "proj+scn":
            self._AdvScnBtn.SetVisible(True)
            self._AdvScnBtn.Enabled(True)
        else:
            self._AdvScnBtn.SetVisible(False)
            self._AdvScnBtn.Enabled(False)
            
        @event(self._AdvScnBtn, 'Pressed')
        def destScnHandler(button, action):
            # Configure Screen Control Modal
            # TODO: Configure screen control modal
            # Show Screen Control Modal
            self.SourceController.UIHost.ShowPopup('Modal-ScnCtl')
    
    def UpdateAdvUI(self) -> None:
        curSource = self.SourceController.SelectedSource
        
        self._AdvSelectBtn.SetText(curSource.Name)
        
        if curSource.advSrcCtl == None:
            self._AdvCtlBtn.SetVisible(False)
            self._AdvCtlBtn.Enabled(False)
        else:
            self._AdvCtlBtn.SetVisible(True)
            self._AdvCtlBtn.Enabled(True)
            
        # TODO: Update other Adv UI Buttons
