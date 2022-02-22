from argon2 import Parameters
import wx
import pandas as pd

from STMMacroQueue.Functions.RHK import Initialize

from inspect import getmembers, isfunction, signature,getcomments
from GUIDesign import MacroDialog
import inspect
import Functions.RHK as RHKFunctions
import json
from GUIDesign import MacroSettingsDialog
import os

class SettingsDialog(wx.Dialog):

    def __init__(self, parent, SettingsDict,DefaultSettingsType,title='Settings', ExpandOutput=False):
        super(SettingsDialog, self).__init__(None,title=title)
        self.ExpandOutput=ExpandOutput
        self.SettingsDict = SettingsDict
        self.DefaultSettingsType = DefaultSettingsType
        self.parent = parent
        self.InitUI()
        self.Centre()
        self.SetSize((-1,-1))
        self.SetTitle(title)
        # self.Bind( wx.EVT_INIT_DIALOG, self.InitUI )
        self.Show()

        

    def InitUI(self,event=None):

        #set up panel and sizers
        panel = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.VSCROLL  )
        panel.SetScrollRate(5,5)
        # sb = wx.StaticBox(panel, label = 'Settings')
        sbs = wx.FlexGridSizer(4)
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        def RemoveNonNumbers(String,Default):
            AcceptableList = ['0','1','2','3','4','5','6','7','8','9','.']
            if self.ExpandOutput:
                AcceptableList.append(',')
            NewString = ''.join([digit for digit in String if digit in AcceptableList])
            WasAlreadyNumerical = (len(NewString) == len(String))
            if len(NewString)==0:
                NewString = Default
                WasAlreadyNumerical = False
            return NewString, WasAlreadyNumerical
        #create static texts for setting labels
        self.CtrlDict = {}
        for label,value in self.SettingsDict.items():
            SettingLabel = wx.StaticText(panel, label = f"{label} :")
            if self.DefaultSettingsType[label][0] == "Numerical":
                self.CtrlDict[label]  = wx.TextCtrl(panel, wx.ID_ANY, value = f"{value}")
                def NumericalOnlyFunction(ThisLabel):
                    def NumericalOnly(event):
                        NumberString, WasAlreadyNumerical = RemoveNonNumbers(self.CtrlDict[ThisLabel].GetValue(),f'{self.DefaultSettingsDict[ThisLabel]}')
                        if not WasAlreadyNumerical and NumberString != "":
                            self.CtrlDict[ThisLabel].SetValue(f"{NumberString}")
                        return NumericalOnly
                self.CtrlDict[label].Bind( wx.EVT_TEXT, NumericalOnlyFunction(label))
            elif self.DefaultSettingsType[label][0] == "Choice":
                Choices = self.DefaultSettingsType[label][1]
                self.CtrlDict[label] = wx.Choice( panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, Choices )
                if value in Choices:
                    self.CtrlDict[label].SetStringSelection(value)
                else:
                    self.CtrlDict[label].SetSelection(0)
            sbs.Add(SettingLabel, 0, wx.ALL, 5)
            sbs.Add(self.CtrlDict[label], 0, wx.ALL|wx.EXPAND, 5)


        #set panel sizer
        panel.SetSizer(sbs)


        #create apply and close buttons and add them to horizontal sizer
        applyButton = wx.Button(self, label = 'Apply', size=(100,20))
        closeButton = wx.Button(self, label = 'Close', size=(100,20))
        hbox.Add(applyButton, wx.ID_ANY, wx.ALL, border = 10)
        hbox.Add(closeButton, wx.ID_ANY, wx.ALL, border = 10)

        #add panel and horizontal sizer to vertical sizer
        #and then set sizer for dialog box
        vbox.Add(panel, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox, flag=wx.EXPAND)

        self.SetSizer(vbox)

        #bind button events to functions
        def SetValues(event):
            for label,value in self.SettingsDict.items():
                if self.DefaultSettingsType[label][0] == "Numerical":
                    CtrlValue = self.CtrlDict[label].GetValue()
                    if self.ExpandOutput:
                        CtrlValue = CtrlValue.split(',')
                    else:
                        CtrlValue = [CtrlValue]
                    for index,value in enumerate(CtrlValue):
                        if float(value)%1 == 0:
                            CtrlValue[index] = int(value)
                        else:
                            CtrlValue[index] = float(value)
                elif self.DefaultSettingsType[label][0] == "Choice":
                    CtrlValue = [self.CtrlDict[label].GetStringSelection()]
                if not self.ExpandOutput:
                    CtrlValue = CtrlValue[0]
                self.SettingsDict[label] = CtrlValue
            self.Destroy()
            pass
        applyButton.Bind(wx.EVT_BUTTON, SetValues)
        closeButton.Bind(wx.EVT_BUTTON, lambda event: self.Close())

        def OnExit(event):
            AnyChanges = False
            for label,value in self.SettingsDict.items():
                if self.DefaultSettingsType[label][0] == "Numerical":
                    CtrlValue = self.CtrlDict[label].GetValue()
                elif self.DefaultSettingsType[label][0] == "Choice":
                    CtrlValue = self.CtrlDict[label].GetStringSelection()
                if f"{self.SettingsDict[label]}" != CtrlValue:
                    AnyChanges = True
            if AnyChanges:
                #check to make sure they dont want to apply these settings, then close
                resp = wx.MessageBox('Any changes you made will not be saved, click OK to continue', 'Warning!',wx.OK|wx.CANCEL)
                if resp == wx.OK:
                    self.Destroy()
                else:
                    pass
            else:
                self.Destroy()
        self.Bind(wx.EVT_CLOSE, OnExit)



class MyMacroDialog ( MacroDialog ):
    TheQueue = []
    def __init__(self, parent,SettingsDict):
        super().__init__(parent)
        self.SettingsDict = SettingsDict
        self.SetFunctionButtons()

    def SetFunctionButtons(self):
        AddFunctionButtonSizer = wx.FlexGridSizer( 0, 3, 0, 0 )
        AddFunctionButtonSizer.AddGrowableCol( 0 )
        AddFunctionButtonSizer.AddGrowableCol( 1 )
        AddFunctionButtonSizer.SetFlexibleDirection( wx.BOTH )
        AddFunctionButtonSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        self.FunctionInfoList = {}
        for Name,Function in getmembers(RHKFunctions, isfunction):
            if Name != "Initialize" and Name != "OnClose" and Name != "OnCancel":
                Name = Name.replace("_"," ")
                FunctionButton = wx.Button( self.m_FunctionButtonScrolledWindow, wx.ID_ANY, Name, wx.DefaultPosition, wx.DefaultSize, 0 )
                FunctionButton.SetMinSize( wx.Size( 150,-1 ) )
                AddFunctionButtonSizer.Add( FunctionButton, 0, wx.ALL, 5 )
                Parameters = {Key:{"DefaultValue":Value,"Tooltip":"","Frozen":False} for Key,Value in zip(inspect.getfullargspec(Function)[0],inspect.getfullargspec(Function)[3])} if len(inspect.getfullargspec(Function)[0]) > 0 else {}
                Comments = getcomments(Function)
                if Comments is not None:
                    for line in Comments.splitlines():
                        for parameter in Parameters.keys():
                            ParameterIndex = line.find(parameter)
                            if ParameterIndex != -1:
                                EqualSignIndex = line[ParameterIndex+len(parameter):].find("=")
                                Parameters[parameter]['Tooltip'] = line[ParameterIndex+len(parameter)+EqualSignIndex+1:]
                
                FunctionButton.Bind(wx.EVT_BUTTON, self.AddFunctionToQueue)


                FunctionButton
                FunctionInfo = [FunctionButton,Function,Parameters]
                self.FunctionInfoList[Name] = FunctionInfo
            
        
        self.m_FunctionNameSizer = wx.FlexGridSizer( 0, 1, -6, 0 )
        self.m_FunctionNameSizer.AddGrowableCol( 0 )
        self.m_FunctionNameSizer.SetFlexibleDirection( wx.BOTH )
        self.m_FunctionNameSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        self.m_FunctionQueueScrolledWindow.SetSizer(self.m_FunctionNameSizer)




        self.m_FunctionButtonScrolledWindow.SetSizer( AddFunctionButtonSizer )
        self.m_FunctionButtonScrolledWindow.Layout()
        AddFunctionButtonSizer.Fit( self.m_FunctionButtonScrolledWindow )
        return
    def AddFunctionToQueue(self,event):
        FunctionLabel = event.GetEventObject().GetLabel()
        FunctionInfo = self.FunctionInfoList[FunctionLabel]
        YBitmapSize = 20
        m_FunctionWindow = wx.Panel( self.m_FunctionQueueScrolledWindow, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1,-1), wx.TAB_TRAVERSAL )
        m_FunctionWindow.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) )
        m_FunctionWindow.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
        bSizer1 = wx.FlexGridSizer( 1, 10, 0, 0 )
        bSizer1.SetFlexibleDirection( wx.BOTH )
        bSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        bSizer1.AddGrowableCol(0)
        # bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
        m_FunctionWindow.Hide()


        m_FunctionNameText = wx.StaticText( m_FunctionWindow, wx.ID_ANY, FunctionLabel, wx.DefaultPosition, wx.Size( -1,YBitmapSize), wx.ALIGN_CENTER_HORIZONTAL)
        # m_FunctionNameText.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
        bSizer1.Add( m_FunctionNameText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2 )

        Text = wx.StaticText( m_FunctionWindow, wx.ID_ANY, "", wx.DefaultPosition, wx.Size( 10,YBitmapSize), wx.ALIGN_CENTER_HORIZONTAL)
        bSizer1.Add( Text, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2 )

        m_Up = wx.BitmapButton( m_FunctionWindow, wx.ID_ANY, self.Parent.UpBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        bSizer1.Add( m_Up, 0, wx.ALL|wx.ALIGN_CENTER, 2 )

        def MoveUp(event):
            ThisPanel = event.GetEventObject().GetParent()
            for ThisIndex,(Label, Function, Parameters, Panel, NameText) in enumerate(self.TheQueue):
                Index = ThisIndex
                if ThisPanel.GetId() == Panel.GetId():
                    break
            if Index == 0:
                pass
            else:
                Function = self.TheQueue.pop(Index)
                self.TheQueue.insert(Index-1,Function)
                self.m_FunctionNameSizer.Remove(Index)
                self.m_FunctionNameSizer.Insert(Index-1,ThisPanel, 0, wx.ALL|wx.EXPAND, 5)
                self.m_FunctionQueueScrolledWindow.FitInside()
        m_Up.Bind( wx.EVT_BUTTON, MoveUp)

        m_Down = wx.BitmapButton( m_FunctionWindow, wx.ID_ANY, self.Parent.DownBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        bSizer1.Add( m_Down, 0, wx.ALL|wx.ALIGN_CENTER, 2 )
        def MoveDown(event):
            ThisPanel = event.GetEventObject().GetParent()
            for ThisIndex,(Label, Function, Parameters, Panel, NameText) in enumerate(self.TheQueue):
                Index = ThisIndex
                if ThisPanel.GetId() == Panel.GetId():
                    break
            if Index == len(self.TheQueue)-1:
                pass
            else:
                Function = self.TheQueue.pop(Index)
                self.TheQueue.insert(Index+1,Function)
                self.m_FunctionNameSizer.Remove(Index)
                self.m_FunctionNameSizer.Insert(Index+1,ThisPanel, 0, wx.ALL|wx.EXPAND, 5)
                self.m_FunctionQueueScrolledWindow.FitInside()
        m_Down.Bind( wx.EVT_BUTTON, MoveDown)
            
        m_Remove = wx.BitmapButton( m_FunctionWindow, wx.ID_ANY, self.Parent.RemoveBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        bSizer1.Add( m_Remove, 0, wx.ALL|wx.ALIGN_CENTER, 2 )
        def Remove(event):
            ThisPanel = event.GetEventObject().GetParent()
            for ThisIndex,(Label, Function, Parameters, Panel, NameText) in enumerate(self.TheQueue):
                Index = ThisIndex
                if ThisPanel.GetId() == Panel.GetId():
                    break
            self.TheQueue.pop(Index)
            ThisPanel.Destroy()
            self.m_FunctionQueueScrolledWindow.FitInside()
        m_Remove.Bind( wx.EVT_BUTTON, Remove)


        

        

        # m_FunctionWindow.SetToolTip(thisSettingString)
        for child in m_FunctionWindow.GetChildren():
            child.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
        #         child.SetToolTip(thisSettingString)


        m_FunctionWindow.SetSizer( bSizer1 )
        m_FunctionWindow.Layout()
        bSizer1.Fit( m_FunctionWindow )
        # fgSizer3.Add( self.m_FunctionWindow, 1, wx.EXPAND |wx.ALL, 2 )

        m_FunctionWindow.Show()
        self.TheQueue.append([FunctionLabel,FunctionInfo[2],FunctionInfo[0],m_FunctionWindow,m_FunctionNameText])
        self.m_FunctionNameSizer.Add( m_FunctionWindow, 0, wx.ALL|wx.EXPAND, 5 )
        self.m_FunctionQueueScrolledWindow.FitInside()
        
    def OnRFunctionClick(self, event):
        ThisText = event.GetEventObject()
        if ThisText.GetLabel() != "panel":
            ThisText = ThisText.GetParent()
        for ThisIndex,(Label, Function, Parameters, Panel, NameText) in enumerate(self.TheQueue):
            Index = ThisIndex
            if ThisText.GetId() == Panel.GetId():
                break
        """Setup and Open a popup menu."""
        popupmenu = wx.Menu()
        menuItem = popupmenu.Append(-1, 'Move Up')
        def MoveUp(event):
            Function = self.TheQueue.pop(Index)
            self.TheQueue.insert(Index-1,Function)
            self.m_FunctionNameSizer.Remove(Index)
            self.m_FunctionNameSizer.Insert(Index-1,ThisText, 0, wx.ALL|wx.EXPAND, 5)
            self.m_FunctionQueueScrolledWindow.FitInside()
            pass
        self.Bind(wx.EVT_MENU, MoveUp, menuItem)
        if Index == 0:
            menuItem.Enable(False)
        
        menuItem = popupmenu.Append(-1, 'Move Down')
        def MoveDown(event):
            Function = self.TheQueue.pop(Index)
            self.TheQueue.insert(Index+1,Function)
            self.m_FunctionNameSizer.Remove(Index)
            self.m_FunctionNameSizer.Insert(Index+1,ThisText, 0, wx.ALL|wx.EXPAND, 5)
            self.m_FunctionQueueScrolledWindow.FitInside()

        self.Bind(wx.EVT_MENU, MoveDown, menuItem)
        if Index == len(self.TheQueue)-1:
            menuItem.Enable(False)



        menuItem = popupmenu.Append(-1, 'Remove')
        def Remove(event):
            self.TheQueue.pop(Index)
            ThisText.Destroy()
            self.m_FunctionQueueScrolledWindow.FitInside()
        self.Bind(wx.EVT_MENU, Remove, menuItem)

        menuItem = popupmenu.Append(-1, 'Clear All Below')
        def RemoveBelow(event):
            for RemoveIndex,(Label, Function, Parameters, RemovePanel, NameText) in enumerate(self.TheQueue):
                if RemoveIndex > Index:
                    RemovePanel.Destroy()
            self.TheQueue = self.TheQueue[:Index+1]
            self.m_FunctionQueueScrolledWindow.FitInside()
            # print(self.m_FunctionNameSizer.GetChildren())
            # print(len(self.m_FunctionNameSizer.GetChildren()))
        self.Bind(wx.EVT_MENU, RemoveBelow, menuItem)
        if Index == len(self.TheQueue)-1:
            menuItem.Enable(False)
        # Show menu
        # XPos = int(np.ceil(ThisText.GetTextExtent(ThisText.GetLabel()).GetWidth()/2+ThisText.GetSize()[0]/2))
        # if event.GetX() > XPos:
        #     XPos = event.GetX()
        # ThisText.PopupMenu(popupmenu,XPos,event.GetY())
        ThisText.PopupMenu(popupmenu,event.GetX()+20,event.GetY())
        return
    def Accept(self, event):
        TheMacro = [[Name,Parameters] for Name,Parameters, Function, Panel, NameText in self.TheQueue]
        self.OnExit(None)
        self.Parent.DefineMacroSettings(TheMacro)
        # ThisMacroSettingsDialog = MyMacroSettingsDialog(self.Parent,TheMacro)
        # ThisMacroSettingsDialog.ShowModal()
        return
    def OnExit(self, event):
        self.Destroy()
        return


class MyMacroSettingsDialog(MacroSettingsDialog):
    TheMacroCtrls = {}
    def __init__(self, parent, TheMacro):
        super().__init__(parent)
        self.TheMacro = TheMacro
        self.SetParameterPanels()
    def SetParameterPanels(self):
        m_MacroSettingScrolledWindowSizer = wx.FlexGridSizer( 0, 1, 0, 0 )
        m_MacroSettingScrolledWindowSizer.SetFlexibleDirection( wx.BOTH )
        m_MacroSettingScrolledWindowSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        for Name,Parameters in self.TheMacro:
            FunctionPanel = wx.Panel( self.m_MacroSettingScrolledWindow, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL|wx.EXPAND )
            FunctionPanel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) )

            FunctionSizer = wx.FlexGridSizer( 1, 0, 0, 0 )
            FunctionSizer.AddGrowableRow( 0 )
            FunctionSizer.AddGrowableCol( 0 )
            FunctionSizer.SetFlexibleDirection( wx.BOTH )
            FunctionSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
            self.m_FunctionText = wx.StaticText( FunctionPanel, wx.ID_ANY, Name, wx.DefaultPosition, wx.DefaultSize, 0 )
            self.m_FunctionText.Wrap( -1 )
            # self.m_FunctionText.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Arial" ) )

            FunctionSizer.Add( self.m_FunctionText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
            FunctionsParametersSizer = wx.FlexGridSizer( 1, 0, 0, 0 )
            FunctionsParametersSizer.SetFlexibleDirection( wx.BOTH )
            FunctionsParametersSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

            self.TheMacroCtrls[Name] = {}
            if len(Parameters) > 0:
                for ParameterName,ParameterInfo in Parameters.items():

                    self.ParameterPanel = wx.Panel( FunctionPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
                    self.ParameterPanel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )
                    self.ParameterPanel.SetMinSize( wx.Size( 250,60 ) )

                    ParameterSizer = wx.FlexGridSizer( 0, 1, 0, 0 )
                    ParameterSizer.SetFlexibleDirection( wx.BOTH )
                    ParameterSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

                    DefaultValueSizer = wx.FlexGridSizer( 0, 2, 0, 0 )
                    DefaultValueSizer.AddGrowableCol( 0 )
                    DefaultValueSizer.SetFlexibleDirection( wx.BOTH )
                    DefaultValueSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

                    self.ParameterNameText = wx.StaticText( self.ParameterPanel, wx.ID_ANY, ParameterName, wx.DefaultPosition, wx.Size( -1,15 ), 0 )
                    self.ParameterNameText.Wrap( -1 )

                    self.ParameterNameText.SetMinSize( wx.Size( 120,15 ) )

                    DefaultValueSizer.Add( self.ParameterNameText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )

                    ParameterDefaultValueText = wx.TextCtrl( self.ParameterPanel, wx.ID_ANY, f"{ParameterInfo['DefaultValue']}", wx.DefaultPosition, wx.DefaultSize, 0 )
                    DefaultValueSizer.Add( ParameterDefaultValueText, 0, wx.ALL, 5 )


                    ParameterSizer.Add( DefaultValueSizer, 1, wx.EXPAND, 5 )

                    FreezeParameterCheck = wx.CheckBox( self.ParameterPanel, wx.ID_ANY, u"Freeze Parameter", wx.DefaultPosition, wx.DefaultSize, 0 )
                    FreezeParameterCheck.SetMinSize( wx.Size( 110,15 ) )

                    ParameterSizer.Add( FreezeParameterCheck, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


                    self.ParameterPanel.SetSizer( ParameterSizer )
                    self.ParameterPanel.Layout()
                    ParameterSizer.Fit( self.ParameterPanel )
                    FunctionsParametersSizer.Add( self.ParameterPanel, 1, wx.EXPAND |wx.ALL, 5 )

                    Tooltip = ParameterInfo.pop("Tooltip")
                    self.ParameterPanel.SetToolTip(Tooltip)
                    for child in self.ParameterPanel.GetChildren():
                        # child.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
                        child.SetToolTip(Tooltip)
                    self.TheMacroCtrls[Name][ParameterName] = [ParameterDefaultValueText,FreezeParameterCheck] 


            FunctionSizer.Add( FunctionsParametersSizer, 1, wx.EXPAND, 5 )
            FunctionPanel.SetSizer( FunctionSizer )
            FunctionPanel.Layout()
            FunctionSizer.Fit( FunctionPanel )
            m_MacroSettingScrolledWindowSizer.Add( FunctionPanel, 1, wx.ALL|wx.EXPAND, 5 )


        self.m_MacroSettingScrolledWindow.SetSizer( m_MacroSettingScrolledWindowSizer )
        self.m_MacroSettingScrolledWindow.Layout()
        m_MacroSettingScrolledWindowSizer.Fit( self.m_MacroSettingScrolledWindow )
    def SaveMacro(self, event):
        self.UpdateTheMacro()
        MacroName = self.m_MacroTextCtrl.GetValue()

        if len(MacroName) == 0:
            MyMessage = wx.MessageDialog(self,message=f"Macro Name cannot be empty.",caption="Warning - Invalid Macro Name")
            MyMessage.ShowModal()
        else:
            def WriteFile(AllTheMacros):
                os.makedirs("Macros",exist_ok=True)
                with open(MacroPath, 'w') as fp:
                    json.dump(AllTheMacros, fp,indent=2)
                self.Parent.MakeFunctionButtons()
                self.Destroy()
            MacroPath = self.Parent.MacroPath
            if os.path.exists(MacroPath):
                with open(MacroPath, 'r') as fp:
                    AllTheMacros = json.load(fp)
                if MacroName in AllTheMacros.keys():
                    MyMessage = wx.MessageDialog(self,message=f"There is already a macro named {MacroName}.\nWould you like to overwrite?",caption="Warning - Overwrite Macro",style=wx.YES_NO)
                    YesOrNo = MyMessage.ShowModal()
                    if YesOrNo == wx.ID_YES:
                        AllTheMacros[MacroName] = self.TheMacro
                        WriteFile(AllTheMacros)
                else:
                    AllTheMacros[MacroName] = self.TheMacro
                    WriteFile(AllTheMacros)
            else:
                WriteFile({MacroName:self.TheMacro})

    def UpdateTheMacro(self):
        for Name,Parameters in self.TheMacro:
            if len(Parameters) > 0:
                for ParameterName,ParameterInfo in Parameters.items():
                    Parameters[ParameterName]['DefaultValue'] = self.TheMacroCtrls[Name][ParameterName][0].GetValue()
                    Parameters[ParameterName]['Frozen'] = self.TheMacroCtrls[Name][ParameterName][1].GetValue()