from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable, cast
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    from uofi_gui.sourceControls import SourceController, MatrixRow, LayoutTuple, RelayTuple
    from extronlib.ui import Button, Knob, Label, Level, Slider

from collections import namedtuple
from extronlib import event
from uofi_gui.sourceControls.sources import Source
from hardware.mersive_solstice_pod import PodFeedbackHelper

MatrixTuple = namedtuple('MatrixTuple', ['Vid', 'Aud'])

class Destination:
    def __init__(self,
                 SrcCtl: 'SourceController',
                 id: str,
                 name: str,
                 output: int,
                 destType: str,
                 rly: 'RelayTuple',
                 groupWrkSrc: str,
                 advLayout: 'LayoutTuple') -> None:
        
        self.SourceController = SrcCtl
        self.Id = id
        self.Name = name
        self.Output = output
        self.AdvLayoutPosition = advLayout
        self.GroupWorkSource = self.SourceController.GetSource(id = groupWrkSrc)
        self.Type = destType
        
        self.__Mute = False
        self.__Relay = rly
        self.__AssignedVidSource = self.SourceController.BlankSource
        self.__AssignedAudSource = self.SourceController.BlankSource
        self.__AdvSelectBtn = None
        self.__AdvCtlBtn = None
        self.__AdvAudBtn = None
        self.__AdvAlertBtn = None
        self.__AdvScnBtn = None
        self.__AdvLabel = None
        self.__MatrixRow = None
    
    @property
    def AssignedSource(self) -> MatrixTuple:
        return MatrixTuple(Vid=self.__AssignedVidSource, Aud=self.__AssignedAudSource)
    
    @property
    def AssignedInput(self) -> MatrixTuple:
        return MatrixTuple(Vid=self.__AssignedVidInput, Aud=self.__AssignedAudInput)
    
    @property
    def __AssignedVidInput(self) -> int:
        return self.__AssignedVidSource.Input
    
    @property
    def __AssignedAudInput(self) -> int:
        return self.__AssignedAudSource.Input
    
    @property
    def Mute(self) -> bool:
        return self.__Mute
    
    @Mute.setter
    def Mute(self, state: Union[bool, int, str]):
        setState = (state in ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE'])
        self.__Mute = setState
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __SelectHandler(self, button: 'Button', action: str):
        self.SourceController.SwitchSources(self.SourceController.SelectedSource, [self])
    
    def __SourceControlHandler(self, button: 'Button', action: str):
        # configure source control page
        modal = 'Modal-SrcCtl-{}'.format(self.AssignedSource.Vid.AdvSourceControlPage)
        
        if modal == 'Modal-SrcCtl-WPD':
            PodFeedbackHelper(self.SourceController.UIHost, self.AssignedSource.Vid.Id, blank_on_fail=True)
        
        # show source control page
        self.SourceController.UIHost.ShowPopup(modal)
        self.SourceController.OpenControlPopup = {
            'page': modal,
            'source': self.AssignedSource.Vid
        }
    
    def __AudioHandler(self, button: 'Button', action: str):
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
            and self.Type == 'mon':
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
    
    def __AlertHandler(self, button: 'Button', action: str):
        self.SourceController.UIHost.Lbls['SourceAlertLabel'].SetText(self.AssignedSource.Vid.AlertText)
        self.SourceController.UIHost.ShowPopup('Modal-SrcErr')
    
    def __ScreenHandler(self, button: 'Button', action: str):
        # Configure Screen Control Modal
        # TODO: Configure screen control modal
        # Show Screen Control Modal
        self.SourceController.UIHost.ShowPopup('Modal-ScnCtl')
    
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def ToggleMute(self) -> None:
        self.__Mute = not self.__Mute
    
    def AssignMatrixRow(self, row: 'MatrixRow') -> None:
        self.__MatrixRow = row
    
    def AssignInput(self, input: 'int') -> None:
        self.AssignMatrixByInput(input, 'AV')
        
    def AssignSource(self, source: 'Source') -> None:
        self.AssignMatrixBySource(source, 'AV')
    
    def AssignMatrixByInput(self, input: int, tieType: str='AV') -> None:
        if type(input) is not int:
            raise ValueError('Input must be an integer')
        
        inputSrc = self.SourceController.GetSourceByInput(input)
            
        self.AssignMatrixBySource(inputSrc, tieType)
    
    def AssignMatrixBySource(self, source: 'Source', tieType: str='AV') -> None:
        if not (tieType == 'Aud' or tieType == 'Vid' or tieType == 'AV' or tieType == 'untie'):
            raise ValueError("TieType must either be 'AV', 'Aud', 'Vid', or 'untie'. Provided TieType: {}".format(tieType))
        
        if type(source) is not Source:
            raise ValueError('Source must be a Source object')
        
        if tieType == 'Vid' or tieType == 'AV':
            self.__AssignedVidSource = source
        if tieType == 'Aud' or tieType == 'AV':
            self.__AssignedAudSource = source
            
        self.UpdateAdvUI()
        
        self.__MatrixRow.MakeTie(source.Input, tieType)

    def AssignAdvUI(self, ui: Dict[str, Union['Button', 'Label']]) -> None:
        self.__AdvSelectBtn = ui['select']
        self.__AdvCtlBtn = ui['ctl']
        self.__AdvAudBtn = ui['aud']
        self.__AdvAlertBtn = ui['alert']
        self.__AdvScnBtn = ui['scn']
        self.__AdvLabel = ui['label']
        
        # set distination label text
        self.__AdvLabel.SetText(self.Name)
        
        # clear selected source text
        self.__AdvSelectBtn.SetText("") 
        
        @event(self.__AdvSelectBtn, 'Pressed') # pragma: no cover
        def advSelectHandler(button: 'Button', action: str):
            self.__SelectHandler(button, action)
            
        # Source Control Buttons
        self.__AdvCtlBtn.SetVisible(False)
        self.__AdvCtlBtn.SetEnable(False)
        
        @event(self.__AdvCtlBtn, 'Pressed') # pragma: no cover
        def advSrcCtlHandler(button: 'Button', action: str):
            self.__SourceControlHandler(button, action)
        
        # Destination Audio Buttons
        self.__AdvAudBtn.SetState(1)
        
        @event(self.__AdvAudBtn, ['Tapped', 'Released']) # pragma: no cover
        def advAudHandler(button: 'Button', action: str):
            self.__AudioHandler(button, action)
        
        # Destination Alert Buttons
        self.__AdvAlertBtn.SetVisible(False)
        self.__AdvAlertBtn.SetEnable(False)
        
        @event(self.__AdvAlertBtn, 'Pressed') # pragma: no cover
        def advAlertHandler(button: 'Button', action: str):
            self.__AlertHandler(button, action)
        
        # Screen Control Buttons
        if self.Type == "proj+scn":
            self.__AdvScnBtn.SetVisible(True)
            self.__AdvScnBtn.SetEnable(True)
        else:
            self.__AdvScnBtn.SetVisible(False)
            self.__AdvScnBtn.SetEnable(False)
            
        @event(self.__AdvScnBtn, 'Pressed') # pragma: no cover
        def advScnHandler(button: 'Button', action: str):
            self.__ScreenHandler(button, action)
    
    def UpdateAdvUI(self) -> None:
        vidSrc = self.AssignedSource.Vid
        vidSrc = cast('Source', vidSrc)
        self.__AdvSelectBtn.SetText(vidSrc.Name)
        
        if vidSrc.AdvSourceControlPage == None:
            self.__AdvCtlBtn.SetVisible(False)
            self.__AdvCtlBtn.SetEnable(False)
        else:
            self.__AdvCtlBtn.SetVisible(True)
            self.__AdvCtlBtn.SetEnable(True)
            
    def AdvSourceAlertHandler(self) -> None:
        if self.AssignedSource != None and self.AssignedSource.Vid.AlertFlag:
            self.__AdvAlertBtn.SetVisible(True)
            self.__AdvAlertBtn.SetEnable(True)
            self.__AdvAlertBtn.SetBlinking('Medium', [0,1])
        else:
            self.__AdvAlertBtn.SetVisible(False)
            self.__AdvAlertBtn.SetEnable(False)
            self.__AdvAlertBtn.SetState(1)
            