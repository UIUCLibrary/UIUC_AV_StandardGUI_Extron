from typing import TYPE_CHECKING, Dict, Tuple, List, Union, Callable, cast
if TYPE_CHECKING: # pragma: no cover
    from uofi_gui import GUIController
    from uofi_gui.uiObjects import ExUIDevice

## Begin ControlScript Import --------------------------------------------------
from extronlib import event
from extronlib.ui import Button
from extronlib.system import Wait
## End ControlScript Import ----------------------------------------------------
##
## Begin Python Imports --------------------------------------------------------
from collections import namedtuple

## End Python Imports ----------------------------------------------------------
##
## Begin User Import -----------------------------------------------------------
#### Custom Code Modules
from uofi_gui.sourceControls.destinations import Destination, Source, MatrixTuple
# from uofi_gui.sourceControls.sources import Source
from uofi_gui.sourceControls.matrix import MatrixController, MatrixRow

from hardware.mersive_solstice_pod import PodFeedbackHelper

from utilityFunctions import Log, RunAsync, debug, DictValueSearchByKey

#### Extron Global Scripter Modules

## End User Import -------------------------------------------------------------
##
## Begin Class Definitions -----------------------------------------------------
RelayTuple = namedtuple('RelayTuple', ['Up', 'Down'])
LayoutTuple = namedtuple('LayoutTuple', ['Row', 'Pos'])

class SourceController:
    def __init__(self, UIHost: 'ExUIDevice') -> None:
        
        # Public Properties
        # Log('Set Public Properties')
        self.UIHost = UIHost
        self.GUIHost = self.UIHost.GUIHost
        self.UIHost.Lbls['SourceAlertLabel'].SetText('')
        
        self.Sources = []
        for src in self.GUIHost.Sources:
            srcObj = Source(self,
                            src['id'], 
                            src['name'], 
                            src['icon'], 
                            src['input'], 
                            src['alert'],
                            src['src-ctl'], 
                            src['adv-src-ctl'])
            self.Sources.append(srcObj)
            if src.get('srcObj') is None:
                src['srcObj'] = {}
            src['srcObj'][self.UIHost.Id] = srcObj
        
        self.BlankSource = Source(self, 'none', 'None', 0, 0, None, None)
            
        self.Destinations = []
        for dest in self.GUIHost.Destinations:
            if type(dest['rly']) != type(None):
                dest_relay = RelayTuple(Up=dest['rly'][0], Down=dest['rly'][1])
            else:
                dest_relay = RelayTuple(Up=None, Down=None)
            destObj = Destination(self,
                                  dest['id'],
                                  dest['name'],
                                  dest['output'],
                                  dest['type'],
                                  dest_relay,
                                  dest['group-work-src'],
                                  LayoutTuple(Row=dest['adv-layout']['row'], Pos=dest['adv-layout']['pos']))
            self.Destinations.append(destObj)
            if dest.get('destObj') is None:
                dest['destObj'] = {}
            dest['destObj'][self.UIHost.Id] = destObj
        
        self.PrimaryDestination = self.GetDestination(id = self.GUIHost.PrimaryDestinationId)
        self.SelectedSource = None
        self.OpenControlPopup = None
        
        # Private Properties
        # Log('Set Private Properties')
        self.__SourceBtns = self.UIHost.Btn_Grps['Source-Select']
        self.__SourceInds = self.UIHost.Btn_Grps['Source-Indicator']
        self.__ArrowBtns = \
            [
                self.UIHost.Btns['SourceMenu-Prev'],
                self.UIHost.Btns['SourceMenu-Next']
            ]
        self.__PrivacyBtn = self.UIHost.Btns['Privacy-Display-Mute']
        self.__SendToAllBtn = self.UIHost.Btns['Send-To-All']
        self.__ReturnToGroupBtn = self.UIHost.Btns['Return-To-Group']
        self.__ModalCloseBtn = self.UIHost.Btns['Modal-Close']
        self.__WPDClearPostsBtn = self.UIHost.Btns['WPD-ClearPosts']
        self.__WPDClearAllBtn = self.UIHost.Btns['WPD-ClearAll']
        self.__Offset = 0
        self.__AdvLayout = self.GetAdvShareLayout()
        self.__DisplaySrcList = []
        self.__Privacy = False
        self.__Matrix = MatrixController(self,
                                        DictValueSearchByKey(self.UIHost.Btns, r'Tech-Matrix-\d+,\d+', regex=True),
                                        self.UIHost.Btn_Grps['Tech-Matrix-Mode'],
                                        self.UIHost.Btns['Tech-Matrix-DeleteTies'],
                                        DictValueSearchByKey(self.UIHost.Lbls, r'MatrixLabel-In-\d+', regex=True),
                                        DictValueSearchByKey(self.UIHost.Lbls, r'MatrixLabel-Out-\d+', regex=True))
        
        for dest in self.Destinations: # Set advanced gui buttons for each destination
            dest.AssignAdvUI(self.__GetUIForAdvDest(dest))
            
        self.MatrixSwitch(0, 'All', 'untie')
        
        # Configure Source Selection Buttons
        @event(self.__SourceBtns.Objects, 'Pressed') # pragma: no cover
        def SourceBtnHandler(button: 'Button', action: str):
            self.__SourceBtnHandler(button, action)

        @event(self.__ArrowBtns, 'Pressed') # pragma: no cover
        def SourcePageHandler(button: 'Button', action: str):
            self.__SourcePageHandler(button, action)

        @event(self.__ModalCloseBtn, 'Pressed') # pragma: no cover
        def ModalCloseHandler(button: 'Button', action: str):
            self.__ModalCloseHandler(button, action)
            
        @event(self.__PrivacyBtn, 'Pressed') # pragma: no cover
        def PrivacyHandler(button: 'Button', action: str):
            self.TogglePrivacy()
    
        @event(self.__SendToAllBtn, ['Pressed', 'Released']) # pragma: no cover
        def SendToAllHandler(button: 'Button', action: str):
            self.__SendToAllHandler(button, action)
                    
        @event(self.__ReturnToGroupBtn, ['Pressed', 'Released']) # pragma: no cover
        def ReturnToGroupHandler(button: 'Button', action: str):
            self.__ReturnToGroupHandler(button, action)
                    
        @event(self.__WPDClearPostsBtn, ['Pressed', 'Released']) # pragma: no cover
        def WPDClearPostsHandler(button: 'Button', action: str):
            self.__WPDClearPostsHandler(button, action)
                
        @event(self.__WPDClearAllBtn, ['Pressed', 'Released']) # pragma: no cover
        def WPDClearAllHandler(button: 'Button', action: str):
            self.__WPDClearAllHandler(button, action)
    
    @property
    def Privacy(self) -> bool:
        return self.__Privacy
    
    @Privacy.setter
    def Privacy(self, state):
        setState = (state in ['on', 'On', 'ON', 1, True, 'Mute', 'mute', 'MUTE'])
        self.__Privacy = setState
        
        privBtn = self.__PrivacyBtn
        privBtn = cast('Button', privBtn)
        
        if self.__Privacy:
            privBtn.SetBlinking('Medium', [1,2])
            for d in self.Destinations:
                d = cast('Destination', d)
                if d.Type != 'conf':
                    d.Mute = 'On'
        else:
            privBtn.SetState(0)
            for d in self.Destinations:
                d = cast('Destination', d)
                if d.Type != 'conf':
                    d.Mute = 'Off'
    
    # Event Handlers +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __SourceBtnHandler(self, button: 'Button', action: str):
        self.UIHost.Lbls['SourceAlertLabel'].SetText('')
        
        # capture last character of button.Name and convert to index
        btnIndex = int(button.Name[-1:]) - 1
        
        # Update button state
        self.__SourceBtns.SetCurrent(button)
        
        # Update source indicator
        self.__SourceInds.SetCurrent(self.__SourceInds.Objects[btnIndex])

        # Get Source Index, Update Selected Source Object
        srcIndex = btnIndex + self.__Offset
        self.SelectSource(self.__DisplaySrcList[srcIndex])

        # advanced share doesn't switch until destination has been selected
        # all other activities switch immediately
        if self.GUIHost.ActCtl.CurrentActivity != "adv_share":
            if self.GUIHost.ActCtl.CurrentActivity == 'share':
                self.SwitchSources(self.SelectedSource)
            elif self.GUIHost.ActCtl.CurrentActivity == 'group_work':
                self.SwitchSources(self.SelectedSource, [self.PrimaryDestination])
                
            page = self.SelectedSource.SourceControlPage 
            if page == 'PC':
                page = '{p}_{c}'.format(p=page, c=len(self.GUIHost.Cameras))
            elif page == 'WPD':
                PodFeedbackHelper(self.UIHost, self.SelectedSource.Id, blank_on_fail=True)
            
            self.UIHost.ShowPopup("Source-Control-{}".format(page))
    
    def __SourcePageHandler(self, button: 'Button', action: str):
        # capture last 4 characters of button.Name
        btnAction = button.Name[-4:]
        # determine if we are adding or removing offset
        if btnAction == "Prev":
            if self.__Offset > 0:
                self.__Offset -= 1
        elif btnAction == "Next":
            if (self.__Offset + 5) < len(self.__DisplaySrcList):
                self.__Offset += 1
        # update the displayed source menu
        self.UpdateSourceMenu()
            
    def __ModalCloseHandler(self, button: 'Button', action: str):
        self.UIHost.HidePopup('Modal-SrcCtl-WPD')
        self.UIHost.HidePopup('Modal-SrcCtl-Camera')
        self.UIHost.HidePopup('Modal-SrcErr')
        self.UIHost.HidePopup('Modal-ScnCtl')
        self.OpenControlPopup = None
            
    def __SendToAllHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            self.SwitchSources(self.SelectedSource)
            @Wait(3) # pragma: no cover
            def SendToAllBtnFeedbackWait():
                button.SetState(0)
        
    def __ReturnToGroupHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            self.SelectSource(self.PrimaryDestination.GroupWorkSource)
            for dest in self.Destinations:
                self.SwitchSources(dest.GroupWorkSource, [dest])
            
            @Wait(3) # pragma: no cover
            def SendToAllBtnFeedbackWait():
                button.SetState(0)
    
    def __WPDClearPostsHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            button.SetState(0)
            if self.GUIHost.ActCtl.CurrentActivity != 'adv_share':
                srcId = self.SelectedSource.Id
            else:
                srcId = self.OpenControlPopup['source'].Id
                
            curHW = self.GUIHost.Hardware.get(srcId, None)
            
            if curHW is not None:
                curHW.interface.Set('ClearPosts', value=None, qualifier={'hw': curHW})
            else:
                raise KeyError("Hardware not found for Source - {}".format(srcId))
    
    def __WPDClearAllHandler(self, button: 'Button', action: str):
        if action == 'Pressed':
            button.SetState(1)
        elif action == 'Released':
            button.SetState(0)
            if self.GUIHost.ActCtl.CurrentActivity != 'adv_share':
                srcId = self.SelectedSource.Id
            else:
                srcId = self.OpenControlPopup['source'].Id
                
            curHW = self.GUIHost.Hardware.get(srcId, None)
            
            if curHW is not None:
                curHW.interface.Set('BootUsers', value=None, qualifier={'hw': curHW})
            else:
                raise KeyError("Hardware not found for Source - {}".format(srcId))
                
    # Private Methods ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def __GetUIForAdvDest(self, dest: Destination) -> Dict[str, Button]:
        
        destDict = {}
        
        location = dest.AdvLayoutPosition
        
        if type(location) is not LayoutTuple: 
            raise LookupError("Provided Destination Object ({}) not found in Destinations."
                            .format(dest.Name))
        
        try:           
            destDict['select'] = self.UIHost.Btns['Disp-Select-{p},{r}'.format(p = location.Pos, r = location.Row)]
            destDict['ctl'] = self.UIHost.Btns['Disp-Ctl-{p},{r}'.format(p = location.Pos, r = location.Row)]
            destDict['aud'] = self.UIHost.Btns['Disp-Aud-{p},{r}'.format(p = location.Pos, r = location.Row)]
            destDict['alert'] = self.UIHost.Btns['Disp-Alert-{p},{r}'.format(p = location.Pos, r = location.Row)]
            destDict['scn'] = self.UIHost.Btns['Disp-Scn-{p},{r}'.format(p = location.Pos, r = location.Row)]
            destDict['label'] = self.UIHost.Lbls['DispAdv-{p},{r}'.format(p = location.Pos, r = location.Row)]
            return destDict
        except:
            raise KeyError("At least one destination button not found.")
    
    # def __GetPositionByBtnName(self, btnName: str) -> LayoutTuple:
    #     btnLoc = btnName[-3:]
    #     btnPR = btnLoc.split(',')
    #     return LayoutTuple(Row = btnPR[1], Pos = btnPR[0])
    
    # Public Methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def SourceAlertHandler(self) -> None:
        # Log('Checking Alerts for Src ({})'.format(self.SelectedSource.Name))
        # Does currently selected source have an alert flag
        if self.SelectedSource is not None and self.SelectedSource.AlertFlag:
            # Log('Alerts Found for Src ({})'.format(self.SelectedSource.Name))
            txt = self.SelectedSource.AlertText
            # Log('Text to set: {} ({})'.format(txt, type(txt)))
            self.UIHost.Lbls['SourceAlertLabel'].SetText(txt)
        else:
            # Log('Alerts Found for Src ({})'.format(self.SelectedSource.Name))
            self.UIHost.Lbls['SourceAlertLabel'].SetText('')
    
    def TogglePrivacy(self) -> None:
        self.Privacy = not self.Privacy
    
    def GetAdvShareLayout(self) -> str:
        layout = {}
        for dest in self.Destinations:
            r = str(dest.AdvLayoutPosition.Row)
            if r not in layout:
                layout[r] = [dest]
            else:
                layout[r].append(dest)
                
        rows = []
        i = 0
        while i < len(layout.keys()):
            rows.append(len(layout[str(i)]))
            i += 1
        rows.reverse()
        
        return "Source-Control-Adv_{}".format(",".join(str(r) for r in rows))
    
    def GetDestination(self, id: str=None, name: str=None) -> Destination:
        if id == None and name == None:
            raise ValueError("Either Id or Name must be provided")
        if id != None:
            for dest in self.Destinations:
                if dest.Id == id:
                    return dest
        if name != None:
            for dest in self.Destinations:
                if dest.Name == name:
                    return dest
        raise LookupError('Provided Name ({}) or Id ({}) not found'.format(name, id))
                
    def GetDestinationByOutput(self, outputNum: int) -> Destination:
        for dest in self.Destinations:
            if dest.Output == outputNum:
                return dest
        raise LookupError("Provided Output ({}) is not configured to a destination".format(outputNum))
    
    def GetDestinationIndexByID(self, id: str) -> int:
        """Get Destination Index from ID.

        Args:
            id (str): Destination ID string
        
        Raises:
            LookupError: raised if ID is not found in list

        Returns:
            int: Returns destination dict index
        """    
        for dest in self.Destinations:
            if id == dest.Id:
                return self.Destinations.index(dest)
        ## if we get here then there was no valid index for the id
        raise LookupError("Provided ID ({}) not found".format(id))
                
    def GetSource(self, id: str=None, name: str=None) -> Source:
        if id == None and name == None:
            raise ValueError("Either Id or Name must be provided")
        if id != None:
            for src in self.Sources:
                if src.Id == id:
                    return src
        if name != None:
            for src in self.Sources:
                if src.Name == name:
                    return src
        raise LookupError('Provided Name ({}) or Id ({}) not found'.format(name, id))
                
    def GetSourceByInput(self, inputNum: int) -> Source:
        for src in self.Sources:
            if src.Input == inputNum:
                return src
        raise LookupError("Provided Input ({}) is not configured to a source".format(inputNum))
    
    def GetSourceIndexByID(self, id: str) -> int:
        """Get Source Index from ID.

        Args:
            id (str): Source ID string
        
        Raises:
            LookupError: raised if ID is not found in list

        Returns:
            int: Returns source list index
        """    
        i = 0
        for src in self.__DisplaySrcList:
            if id == src.Id:
                return i
            i += 1
        ## if we get here then there was no valid index for the id
        raise LookupError("Provided Id ({}) not found".format(id))
    
    def SetPrimaryDestination(self, dest: Destination) -> None:
        # Log('Set Primary Destination - {}'.format(dest), stack=True)
        
        if type(dest) != Destination:
            raise TypeError("Object of class Destination must be provided")
        self.PrimaryDestination = dest
        
    def SelectSource(self, src: Union[Source, str]) -> None:
        if type(src) is Source:
            # Log('Select Source - {}'.format(src.Name), stack=True)
            self.SelectedSource = src
        elif type(src) is str:
            srcObj = self.GetSource(id = src, name = src)
            # Log('Select Source - {}'.format(srcObj.Name), stack=True)
            self.SelectedSource = srcObj
        else:
            raise TypeError('Source must either be a Source object or string Source Id')
    
    def UpdateDisplaySourceList(self) -> None:
        """Get the current source list

        Returns:
            List: The list of currently displayable source definitions
        """    
        srcList = []
        
        if self.GUIHost.ActCtl.CurrentActivity == 'adv_share':
            srcList.append(self.BlankSource)
        srcList.extend(self.Sources)
        
        self.__DisplaySrcList = srcList
        
    def UpdateSourceMenu(self) -> None:
        """Updates the formatting of the source menu. Use when the number of sources
        or the pagination of the source bar changes
        """    
        # Log('Updating Source Menu', stack=True)
        
        self.UpdateDisplaySourceList()
        
        offsetIter = self.__Offset
        # Log('Source Control Offset - {}'.format(self._offset))
        for btn in self.__SourceBtns.Objects:
            if offsetIter >= len(self.__DisplaySrcList):
                break # we have reached the end of the Display-able source list and need to break out of the loop
            btn_to_config = self.__DisplaySrcList[offsetIter]
            offState = int('{}0'.format(btn_to_config.Icon))
            onState = int('{}1'.format(btn_to_config.Icon))
            self.__SourceBtns.SetStates(btn, offState, onState)
            btn.SetText(str(btn_to_config.Name))
            offsetIter += 1
        self.__SourceBtns.SetCurrent(None)
        self.__SourceInds.SetCurrent(None)
        
        if len(self.__DisplaySrcList) <= 5:
            self.UIHost.ShowPopup('Menu-Source-{}'.format(len(self.__DisplaySrcList)))
        else:
            # enable/disable previous arrow
            if self.__Offset == 0:
                self.__ArrowBtns[0].SetEnable(False)
                self.__ArrowBtns[0].SetState(2)
            else:
                self.__ArrowBtns[0].SetEnable(True)
                self.__ArrowBtns[0].SetState(0)
            # enable/disable next arrow
            if (self.__Offset + 5) >= len(self.__DisplaySrcList):
                self.__ArrowBtns[1].SetEnable(False)
                self.__ArrowBtns[1].SetState(2)
            else:
                self.__ArrowBtns[1].SetEnable(True)
                self.__ArrowBtns[1].SetState(0)
            
            self.UIHost.ShowPopup('Menu-Source-5+')

        # reset currently selected source
        if self.SelectedSource is not None:
            currentSourceIndex = self.GetSourceIndexByID(self.SelectedSource.Id)
        else:
            currentSourceIndex = 0
        # Log('Current Source Index - {}'.format(currentSourceIndex))
        
        btnIndex = currentSourceIndex - self.__Offset
        # Log('Button Index - {}'.format(btnIndex))
        # if btnIndex > 4:
        #     raise KeyError("Button Index Out of Range")
        
        if btnIndex >= 0 and btnIndex <= 4:
            self.__SourceBtns.SetCurrent(self.__SourceBtns.Objects[btnIndex])
            self.__SourceInds.SetCurrent(self.__SourceInds.Objects[btnIndex])
        
    def ShowSelectedSource(self) -> None:
        # Log('Show Selected Source', stack=True)
        if len(self.__DisplaySrcList) > 5 and self.SelectedSource is not None:
            curSourceIndex = self.__DisplaySrcList.index(self.SelectedSource)
            
            print('Current Source Index: {}'.format(curSourceIndex))
            if curSourceIndex < self.__Offset:
                self.__Offset -= (self.__Offset - curSourceIndex)
            elif curSourceIndex >= (self.__Offset + 5):
                self.__Offset = curSourceIndex - 4
            
        self.UpdateSourceMenu()
    
    @RunAsync # pragma: no cover
    def SwitchSources(self, src: Union[Source, str], dest: Union[str, List[Union[Destination, str]]]='All') -> None:
        # Not checking this for code coverage as I can't get it to check asyc functions
        # TODO: Figure out why this function has turned into a complete mess
        if type(dest) == str and dest != 'All':
            raise TypeError("Destination string must be 'All' or a list of Destination objects, names, and/or IDs")
        
        # Log('Switch Sources - Src Type: {}, Dest Type: {}'.format(type(src), type(dest)), stack=True)
        
        if type(src) is str:
            srcObj = self.GetSource(id = src, name = src)
        elif type(src) is Source:
            srcObj = src
        else:
            raise TypeError('Src must be either a string or Source object.')
        
        if type(dest) is str and dest == 'All':
            # Log('Source Switch - Destination: All, Source: {}'.format(srcObj.Name))
            for d in self.Destinations:
                d = cast('Destination', d)
                d.AssignSource(srcObj)
                self.__Matrix.Hardware.interface.Set('MatrixTieCommand', 
                                                    value=None,
                                                    qualifier={'Input': srcObj.Input, 
                                                            'Output': d.Output,
                                                            'Tie Type': 'Audio/Video'})
                if self.GUIHost.ActCtl.CurrentActivity in ['adv_share']:
                        d.AdvSourceAlertHandler()
        elif type(dest) is list:
            for d in dest:
                if type(d) == Destination:
                    # Log('Source Switch - Destination: {}, Source: {}'.format(d.Name, srcObj.Name))
                    d.AssignSource(srcObj)
                    self.__Matrix.Hardware.interface.Set('MatrixTieCommand', 
                                                        value=None,
                                                        qualifier={'Input': srcObj.Input, 
                                                                   'Output': d.Output,
                                                                   'Tie Type': 'Audio/Video'})
                    if self.GUIHost.ActCtl.CurrentActivity in ['adv_share']:
                        d.AdvSourceAlertHandler()
                elif type(d) == str:
                    dObj = self.GetDestination(id = d, name = d)
                    # Log('Source Switch - Destination: {}, Source: {}'.format(dObj.Name, srcObj.Name))
                    dObj.AssignSource(srcObj)
                    self.__Matrix.Hardware.interface.Set('MatrixTieCommand',  
                                                        value=None,
                                                        qualifier={'Input': srcObj.Input, 
                                                                   'Output': dObj.Output,
                                                                   'Tie Type': 'Audio/Video'})
                    if self.GUIHost.ActCtl.CurrentActivity in ['adv_share']:
                        dObj.AdvSourceAlertHandler()
        else:
            raise TypeError("Destination must either be 'All' or a list of Destination objects, names, IDs, or switcher output integers")
                    
        if self.GUIHost.ActCtl.CurrentActivity in ['share', 'group_work']:
            self.SourceAlertHandler()

    @RunAsync # pragma: no cover
    def MatrixSwitch(self, src: Union[Source, str, int], dest: Union[str, List[Union[Destination, str, int]]]='All', mode: str='AV') -> None:
        # Not checking this for code coverage as I can't get it to check asyc functions
        if type(dest) == str and dest != 'All':
            raise TypeError("Destination must either be 'All' or a list of Destination objects, names, IDs, or switcher output integers")
        
        cmdDict = \
            {
                'Aud': 'Audio',
                'Vid': 'Video',
                'AV': 'Audio/Video'
            }
            
        if type(src) == str:
            srcObj = self.GetSource(id = src, name = src)
            srcNum = srcObj.Input
        elif type(src) == Source:
            srcNum = src.Input
            srcObj = src
        elif type(src) == int:
            srcNum = src
            srcObj = self.GetSourceByInput(src)
        else:
            raise TypeError("Source must be a source object, source name string, source Id string, or switcher input integers")
        
        if mode == 'untie':
            cmdInput = 0
            cmdTieType = 'Audio/Video'
            # TODO: May have to check for existing ties before knowing if this will work
        else:
            cmdInput = srcNum
            cmdTieType = cmdDict[mode]
        
        # Log('Source Object ({}) - Input: {}'.format(srcObj, srcNum))
        
        if type(dest) is str and dest == 'All':
            for d in self.Destinations:
                d = cast('Destination', d)
                d.AssignMatrixBySource(srcObj, mode)
                self.__Matrix.Hardware.interface.Set('MatrixTieCommand', 
                                                    value=None, 
                                                    qualifier={'Input': cmdInput, 
                                                            'Output': d.Output,
                                                            'Tie Type': cmdTieType})
        elif type(dest) is list:
            for d in dest:
                if type(d) == Destination:
                    d.AssignMatrixBySource(srcObj, mode)
                    destNum = d.Output
                elif type(d) == str:
                    destObj = self.GetDestination(id = d, name = d)
                    destObj.AssignMatrixBySource(srcObj, mode)
                    destNum = destObj.Output
                elif type(d) == int:
                    destObj = self.GetDestinationByOutput(d)
                    if destObj is not None:
                        #destObj.AssignSource(srcObj)
                        destObj.AssignMatrixBySource(srcObj, mode)
                    destNum = d
                self.__Matrix.Hardware.interface.Set('MatrixTieCommand', 
                                                    value=None, 
                                                    qualifier={'Input': cmdInput, 
                                                               'Output': destNum,
                                                               'Tie Type': cmdTieType})
        else:
            raise TypeError("Destination must either be 'All' or a list of Destination objects, names, IDs, or switcher output integers")

## End Class Definitions -------------------------------------------------------
##
## Begin Function Definitions --------------------------------------------------


## End Function Definitions ----------------------------------------------------



