from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable
if TYPE_CHECKING:
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice
    from uofi_gui.sourceControls import SourceController, Source, LayoutTuple, RelayTuple, MatrixTuple
    from extronlib.ui import Button, Knob, Label, Level, Slider

from extronlib import event

from hardware.mersive_solstice_pod import PodFeedbackHelper

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
        self.AssignedSource = None
        self.GroupWorkSource = self.SourceController.GetSource(id = groupWrkSrc)
        self.Mute = False
        
        self._type = destType
        self._relay = rly
        self._AssignedVidInput = 0
        self._AssignedAudInput = 0
        self._AdvSelectBtn = None
        self._AdvCtlBtn = None
        self._AdvAudBtn = None
        self._AdvAlertBtn = None
        self._AdvScnBtn = None
        self._MatrixRow = None
    
    def ToggleDestinationMute(self) -> None:
        # Log('Toggle Destination Mute ({})'.format(self.Name), stack=True)
        if self.Mute:
            self.UnmuteDestination()
        else:
            self.MuteDestination
    
    def MuteDestination(self) -> None:
        # Log('Destination Mute On ({})'.format(self.Name), stack=True)
        self.Mute = True
    
    def UnmuteDestination(self) -> None:
        # Log('Destination Mute Off ({})'.format(self.Name), stack=True)
        self.Mute = False
        
    def AssignSource(self, source: 'Source') -> None:
        self.AssignedSource = source
        self._AssignedVidInput = source.Input
        self._AssignedAudInput = source.Input
        self.UpdateAdvUI()
        
    def AssignMatrix(self, input: int, tieType: str='AV') -> None:
        if not (tieType == 'Aud' or tieType == 'Vid' or tieType == 'AV' or tieType == 'untie'):
            raise ValueError("TieType must either be 'AV', 'Aud', 'Vid', or 'untie'. Provided TieType: {}".format(tieType))
        
        if tieType == 'AV' or tieType == 'Vid':
            self.AssignedSource = self.SourceController.GetSourceByInput(input)
        else:
            self.AssignedSource = self.SourceController._none_source
            
        if tieType == 'Vid' or tieType == 'AV':
            self._AssignedVidInput = input
        if tieType == 'Aud' or tieType == 'AV':
            self._AssignedAudInput = input
            
        self.UpdateAdvUI()
            
    def GetMatrix(self) -> None:
        return MatrixTuple(Vid=self._AssignedVidInput, Aud=self._AssignedAudInput)
    
    def AssignAdvUI(self, ui: Dict[str, Union['Button', 'Label']]) -> None:
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
        def advSelectHandler(button: 'Button', action: str):
            # Log('Adv Select Handler - Source: {}, Destination: {}'
            #                      .format(self.SourceController.SelectedSource.Name,
            #                              self.Name))
            self.SourceController.SwitchSources(self.SourceController.SelectedSource,
                                                [self])
            #self.AssignSource(curSource)
            
        # Source Control Buttons
        self._AdvCtlBtn.SetVisible(False)
        self._AdvCtlBtn.SetEnable(False)
        
        @event(self._AdvCtlBtn, 'Pressed')
        def advSrcCtrHandler(button: 'Button', action: str):
            # configure source control page
            modal = 'Modal-SrcCtl-{}'.format(self.AssignedSource.AdvSourceControlPage)
            
            if modal == 'Modal-SrcCtl-WPD':
                PodFeedbackHelper(self.SourceController.UIHost, self.AssignedSource.Id, blank_on_fail=True)
            
            # show source control page
            self.SourceController.UIHost.ShowPopup(modal)
            self.SourceController.OpenControlPopup = {
                'page': modal,
                'source': self.AssignedSource
            }
        
        # Destination Audio Buttons
        self._AdvAudBtn.SetState(1)
        
        @event(self._AdvAudBtn, ['Tapped', 'Released'])
        def advAudHandler(button: 'Button', action: str):
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
        self._AdvAlertBtn.SetEnable(False)
        
        @event(self._AdvAlertBtn, 'Pressed')
        def destAlertHandler(button: 'Button', action: str):
            self.SourceController.UIHost.Lbls['SourceAlertLabel'].SetText(self.AssignedSource.AlertText)
            self.SourceController.UIHost.ShowPopup('Modal-SrcErr')
        
        # Screen Control Buttons
        if self._type == "proj+scn":
            self._AdvScnBtn.SetVisible(True)
            self._AdvScnBtn.SetEnable(True)
        else:
            self._AdvScnBtn.SetVisible(False)
            self._AdvScnBtn.SetEnable(False)
            
        @event(self._AdvScnBtn, 'Pressed')
        def destScnHandler(button: 'Button', action: str):
            # Configure Screen Control Modal
            # TODO: Configure screen control modal
            # Show Screen Control Modal
            self.SourceController.UIHost.ShowPopup('Modal-ScnCtl')
    
    def UpdateAdvUI(self) -> None:
        # Log('Updating Advanced UI - Dest: {}, Source {}'.format(self.Name, self.AssignedSource.Name))
        
        self._AdvSelectBtn.SetText(self.AssignedSource.Name)
        
        if self.AssignedSource.AdvSourceControlPage == None:
            self._AdvCtlBtn.SetVisible(False)
            self._AdvCtlBtn.SetEnable(False)
        else:
            self._AdvCtlBtn.SetVisible(True)
            self._AdvCtlBtn.SetEnable(True)
            
    def AdvSourceAlertHandler(self) -> None:
        # Log('Checking alerts for Src ({})'.format(self.AssignedSource.Name))
        # Does current source for this destination have an alert flag
        if self.AssignedSource != None and self.AssignedSource.AlertFlag:
            # Log('Alerts Found for Src ({})'.format(self.AssignedSource.Name))
            self._AdvAlertBtn.SetVisible(True)
            self._AdvAlertBtn.SetEnable(True)
            self._AdvAlertBtn.SetBlinking('Medium', [0,1])
        else:
            # Log('No Alerts Found for Src ({})'.format(self.AssignedSource.Name))
            self._AdvAlertBtn.SetVisible(False)
            self._AdvAlertBtn.SetEnable(False)
            self._AdvAlertBtn.SetState(1)
            