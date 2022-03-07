from numpy import array
import wx
from inspect import getmembers, isfunction,getcomments
from GUIDesign import MacroDialog
import inspect
import Functions.RHK as RHKFunctions
import json
from GUIDesign import MacroSettingsDialog
import os
from functools import partial
import numpy as np

from GUIDesign import StartMacroDialog
from STMMacroQueue.GUIDesign import ChooseSoftware
import pandas as pd
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
    def __init__(self, parent,MacroName="",InitalMacro=[]):
        super().__init__(parent)
        self.TheQueue = []
        self.SetFunctionButtons()
        for Function in InitalMacro:
            self.AddFunctionToQueue(None,Function)
        self.m_MacroTextCtrl.SetValue(MacroName)

    def SetFunctionButtons(self):
        AddFunctionButtonSizer = wx.FlexGridSizer( 0, 3, 0, 0 )
        AddFunctionButtonSizer.AddGrowableCol( 0 )
        AddFunctionButtonSizer.AddGrowableCol( 1 )
        AddFunctionButtonSizer.SetFlexibleDirection( wx.BOTH )
        AddFunctionButtonSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        self.FunctionInfoList = {}
        FunctionList = getmembers(self.Parent.Functions[self.Parent.Software], isfunction) + getmembers(self.Parent.Functions["General"], isfunction)
        def GetValueType(Value):
            ValueType = type(Value)
            if ValueType == list or Value == tuple:
                return "Choice"
            if ValueType == bool:
                return "Boolean"
            if ValueType == str:
                return "String"
            try:
                FloatValue = float(Value)
                return "Numerical"
            except:
                raise TypeError(f'The default variable, {Value}, cannot be put into one of the type categories.  It is of type {ValueType}.')
        for Name,Function in FunctionList:
            if Name != "Initialize" and Name != "OnClose" and Name != "OnCancel":
                Name = Name.replace("_"," ")
                FunctionButton = wx.Button( self.m_FunctionButtonScrolledWindow, wx.ID_ANY, Name, wx.DefaultPosition, wx.DefaultSize, 0 )
                FunctionButton.SetMinSize( wx.Size( 150,-1 ) )
                AddFunctionButtonSizer.Add( FunctionButton, 0, wx.ALL, 5 )
                Parameters = {Key:{"DefaultValue":Value,"Tooltip":"","Frozen":False,"ValueType":GetValueType(Value)} for Key,Value in zip(inspect.getfullargspec(Function)[0],inspect.getfullargspec(Function)[3])} if len(inspect.getfullargspec(Function)[0]) > 0 else {}
                for ParameterName in Parameters.keys():
                    if Parameters[ParameterName]["ValueType"] == "Choice":
                        Parameters[ParameterName]["DefaultList"] = Parameters[ParameterName]['DefaultValue']
                        Parameters[ParameterName]["DefaultValue"] = Parameters[ParameterName]['DefaultValue'][0]
                    
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
    def AddFunctionToQueue(self,event=None,Function=None):
        Included = True
        if Function is None:
            FunctionLabel = event.GetEventObject().GetLabel()
            FunctionInfo = self.FunctionInfoList[FunctionLabel].copy()
        else:
            FunctionLabel, ParametersDict, Included = Function
            FunctionInfo = self.FunctionInfoList[FunctionLabel].copy()
            for ParameterName in ParametersDict.keys():
                if FunctionInfo[2][ParameterName]["ValueType"] == "Choice":
                    # List = FunctionInfo[2][ParameterName]['DefaultValue']
                    # Item = ParametersDict[ParameterName]['DefaultValue']
                    # List.remove(Item)
                    # List.insert(0,Item)
                    FunctionInfo[2][ParameterName]["DefaultList"] = FunctionInfo[2][ParameterName]['DefaultValue']
                    FunctionInfo[2][ParameterName] = {**FunctionInfo[2][ParameterName],**ParametersDict[ParameterName]}
                else:
                    FunctionInfo[2][ParameterName] = {**FunctionInfo[2][ParameterName],**ParametersDict[ParameterName]}
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
            for ThisIndex,(Label, Function, Parameters, Panel, NameText,Included) in enumerate(self.TheQueue):
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
            for ThisIndex,(Label, Function, Parameters, Panel, NameText,Included) in enumerate(self.TheQueue):
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
            for ThisIndex,(Label, Function, Parameters, Panel, NameText,Included) in enumerate(self.TheQueue):
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
        self.TheQueue.append([FunctionLabel,FunctionInfo[2],FunctionInfo[0],m_FunctionWindow,m_FunctionNameText,Included])
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
        TheMacro = [[Name,Parameters,Included] for Name,Parameters, Function, Panel, NameText,Included in self.TheQueue]
        self.OnExit(None)
        self.Parent.DefineMacroSettings(self.m_MacroTextCtrl.GetValue(),TheMacro)
        return
    def OnExit(self, event):
        self.Destroy()
        return


class MyMacroSettingsDialog(MacroSettingsDialog):
    def __init__(self, parent, Name, TheMacro):
        super().__init__(parent)
        self.TheMacro = TheMacro
        self.TheMacroCtrls = {}
        self.m_MacroTextCtrl.SetValue(Name)
        self.SetParameterPanels()

    def SetParameterPanels(self):
        m_MacroSettingScrolledWindowSizer = wx.FlexGridSizer( 0, 1, 0, 0 )
        m_MacroSettingScrolledWindowSizer.SetFlexibleDirection( wx.BOTH )
        m_MacroSettingScrolledWindowSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        for Name,Parameters,Included in self.TheMacro:
            FunctionPanel = wx.Panel( self.m_MacroSettingScrolledWindow, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL|wx.EXPAND )
            FunctionPanel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) )

            FunctionSizer = wx.FlexGridSizer( 1, 0, 0, 0 )
            FunctionSizer.AddGrowableRow( 0 )
            FunctionSizer.AddGrowableCol( 0 )
            FunctionSizer.SetFlexibleDirection( wx.BOTH )
            FunctionSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
            m_FunctionTextCheck = wx.CheckBox( FunctionPanel, wx.ID_ANY, Name, wx.DefaultPosition, wx.DefaultSize, 0 )
            m_FunctionTextCheck.SetValue(Included)
            m_FunctionTextCheck.SetToolTip(f"Checked to include {Name} in the Macro by default.")

            FunctionSizer.Add( m_FunctionTextCheck, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
            FunctionsParametersSizer = wx.FlexGridSizer( 1, 0, 0, 0 )
            FunctionsParametersSizer.SetFlexibleDirection( wx.BOTH )
            FunctionsParametersSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

            self.TheMacroCtrls[Name] = {}
            if len(Parameters) > 0:
                for ParameterName,ParameterInfo in Parameters.items():
                    Tooltip = ParameterInfo.pop("Tooltip")

                    self.ParameterPanel = wx.Panel( FunctionPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
                    self.ParameterPanel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )
                    self.ParameterPanel.SetMinSize( wx.Size( 250,60 ) )
                    self.ParameterPanel.SetToolTip(Tooltip)

                    ParameterSizer = wx.FlexGridSizer( 0, 1, 0, 0 )
                    ParameterSizer.SetFlexibleDirection( wx.BOTH )
                    ParameterSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

                    DefaultValueSizer = wx.FlexGridSizer( 0, 2, 0, 0 )
                    DefaultValueSizer.AddGrowableCol( 0 )
                    DefaultValueSizer.SetFlexibleDirection( wx.BOTH )
                    DefaultValueSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

                    self.ParameterNameText = wx.StaticText( self.ParameterPanel, wx.ID_ANY, ParameterName, wx.DefaultPosition, wx.Size( -1,15 ), 0 )
                    self.ParameterNameText.Wrap( -1 )
                    self.ParameterNameText.SetToolTip(Tooltip)

                    self.ParameterNameText.SetMinSize( wx.Size( 120,15 ) )

                    DefaultValueSizer.Add( self.ParameterNameText, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )

                    if ParameterInfo['ValueType'] == 'Numerical':
                        ParameterDefaultValueText = wx.TextCtrl( self.ParameterPanel, wx.ID_ANY, f"{ParameterInfo['DefaultValue']}", wx.DefaultPosition, wx.DefaultSize, 0 )
                    elif ParameterInfo['ValueType'] == 'Boolean':
                        ParameterDefaultValueText = wx.CheckBox( self.ParameterPanel, wx.ID_ANY, "", wx.DefaultPosition, wx.DefaultSize, 0 )
                        ParameterDefaultValueText.SetValue(ParameterInfo['DefaultValue'])
                    elif ParameterInfo['ValueType'] == 'String':
                        ParameterDefaultValueText = wx.TextCtrl( self.ParameterPanel, wx.ID_ANY, ParameterInfo['DefaultValue'], wx.DefaultPosition, wx.DefaultSize, 0 )
                    elif ParameterInfo['ValueType'] == 'Choice':
                        ParameterDefaultValueText = wx.Choice( self.ParameterPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, ParameterInfo['DefaultList'] )
                        ParameterDefaultValueText.SetStringSelection(ParameterInfo['DefaultValue'])
                    ParameterDefaultValueText.SetToolTip(f"Set the Default value for {ParameterName}."+"\n"+Tooltip)
                    DefaultValueSizer.Add( ParameterDefaultValueText, 1, wx.ALL, 5 )


                    ParameterSizer.Add( DefaultValueSizer, 1, wx.EXPAND, 5 )

                    FreezeParameterCheck = wx.CheckBox( self.ParameterPanel, wx.ID_ANY, u"Freeze Parameter", wx.DefaultPosition, wx.DefaultSize, 0 )
                    FreezeParameterCheck.SetMinSize( wx.Size( 110,15 ) )
                    FreezeParameterCheck.SetToolTip(f"Always use the default parameter for {ParameterName}."+"\n"+Tooltip)
                    FreezeParameterCheck.SetValue(ParameterInfo["Frozen"])

                    ParameterSizer.Add( FreezeParameterCheck, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


                    self.ParameterPanel.SetSizer( ParameterSizer )
                    self.ParameterPanel.Layout()
                    ParameterSizer.Fit( self.ParameterPanel )
                    FunctionsParametersSizer.Add( self.ParameterPanel, 1, wx.EXPAND |wx.ALL, 5 )

                    self.TheMacroCtrls[Name][ParameterName] = [ParameterDefaultValueText,FreezeParameterCheck] 
            self.TheMacroCtrls[Name]["__Included__"] = m_FunctionTextCheck 


            FunctionSizer.Add( FunctionsParametersSizer, 1, wx.EXPAND, 5 )
            FunctionPanel.SetSizer( FunctionSizer )
            FunctionPanel.Layout()
            FunctionSizer.Fit( FunctionPanel )
            m_MacroSettingScrolledWindowSizer.Add( FunctionPanel, 1, wx.ALL|wx.EXPAND, 5 )


        self.m_MacroSettingScrolledWindow.SetSizer( m_MacroSettingScrolledWindowSizer )
        self.m_MacroSettingScrolledWindow.Layout()
        m_MacroSettingScrolledWindowSizer.Fit( self.m_MacroSettingScrolledWindow )
        # m_MacroSettingScrolledWindowSizer.Layout()
        Size = m_MacroSettingScrolledWindowSizer.GetSize()
        ButtomSize = self.BottomPanel.GetSize()
        TopSize = self.TopPanel.GetSize()
        Width = Size[0]+50
        Height = Size[1]+ButtomSize[1]+TopSize[1]+20
        self.SetSize(Width,Height)
        self.Center()

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
                    json.dump(AllTheMacros, fp,indent=1)
                self.Parent.MakeFunctionButtons()
                self.Destroy()
            MacroPath = self.Parent.MacroPath
            if os.path.exists(MacroPath):
                with open(MacroPath, 'r') as fp:
                    AllTheMacros = json.load(fp)
                if MacroName in AllTheMacros.keys() and not self.TheMacro == AllTheMacros[MacroName]:
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
    def OnBack(self, event):
        self.UpdateTheMacro()
        MacroName = self.m_MacroTextCtrl.GetValue()
        TheMacro=self.TheMacro
        self.Destroy()
        ThisMacroDialog = MyMacroDialog(self.Parent,MacroName=MacroName,InitalMacro=TheMacro)
        ThisMacroDialog.ShowModal()
        return
    def UpdateTheMacro(self):
        for i,(Name,Parameters,Included) in enumerate(self.TheMacro):
            if len(Parameters) > 0:
                for ParameterName,ParameterInfo in Parameters.items():
                    if ParameterInfo['ValueType'] == "Choice":
                        Parameters[ParameterName]['DefaultValue'] = self.TheMacroCtrls[Name][ParameterName][0].GetStringSelection()
                    else:
                        Parameters[ParameterName]['DefaultValue'] = self.TheMacroCtrls[Name][ParameterName][0].GetValue()
                    Parameters[ParameterName]['Frozen'] = self.TheMacroCtrls[Name][ParameterName][1].GetValue()
            self.TheMacro[i][2] = self.TheMacroCtrls[Name]["__Included__"].GetValue()

class MyStartMacroDialog(StartMacroDialog):
    def __init__(self, parent,MacroLabel,TheDefaultMacro,EdittingMode = False,Index=None):
        super().__init__(parent)
        self.SetTitle(MacroLabel)
        self.QueueIndex = Index
        self.MacroName = MacroLabel
        self.EdittingMode = EdittingMode
        self.TheStartMacroCtrls = {}
        self.TheDefaultMacro = TheDefaultMacro
        self.ProcessMacro(TheDefaultMacro)
        self.SetParameterPanels()
        self.UpdateFunctionTooltips()
        if EdittingMode:
            self.StartButton.SetLabel('Save Changes')

    def ProcessMacro(self,DefaultMacro):
        def GetValueType(Value):
            ValueType = type(Value)
            if ValueType == list or Value == tuple:
                return "Choice"
            if ValueType == bool:
                return "Boolean"
            if ValueType == str:
                return "String"
            try:
                FloatValue = float(Value)
                return "Numerical"
            except:
                raise TypeError(f'The default variable, {Value}, cannot be put into one of the type categories.  It is of type {ValueType}.')
        self.TheFunctionInfos = {}
        FunctionList = getmembers(self.Parent.Functions[self.Parent.Software], isfunction) + getmembers(self.Parent.Functions["General"], isfunction)
        for FunctionName,Function in FunctionList:
            # if FunctionName != "Initialize" and FunctionName != "OnClose" and FunctionName != "OnCancel":
            FunctionName = FunctionName.replace("_"," ")
            Parameters = {Key:{"DefaultValue":Value,"Tooltip":"","ValueType":GetValueType(Value)} for Key,Value in zip(inspect.getfullargspec(Function)[0],inspect.getfullargspec(Function)[3])} if len(inspect.getfullargspec(Function)[0]) > 0 else {}
            Comments = getcomments(Function)
            if Comments is not None:
                for line in Comments.splitlines():
                    for parameter in Parameters.keys():
                        ParameterIndex = line.find(parameter)
                        if ParameterIndex != -1:
                            EqualSignIndex = line[ParameterIndex+len(parameter):].find("=")
                            Parameters[parameter]['Tooltip'] = line[ParameterIndex+len(parameter)+EqualSignIndex+1:]
            self.TheFunctionInfos[FunctionName] = [Function,Parameters.copy()]
        self.TheMacro = []
        for Name,Parameters,Included in DefaultMacro:
            for ParameterName, Info in Parameters.items():
                Info["DefaultToolTip"] =  self.TheFunctionInfos[Name][1][ParameterName]["Tooltip"]
                Info["ValueType"] =  self.TheFunctionInfos[Name][1][ParameterName]["ValueType"]
                Info["NCalls"] = 1
                if Info['ValueType'] == "Numerical":
                    TranslatedText,Numbers, NCalls = self.TranslateNumerical(Info['DefaultValue'],Info['DefaultValue'])
                    Info["Value"] = Numbers
                    Info["NCalls"] = NCalls
                elif Info['ValueType'] == "Choice":
                    Info["Value"] = Info["DefaultValue"]
                else:
                    Info["Value"] = Info["DefaultValue"]

            ThisFunction = {"Name":Name,"Parameters":Parameters,"Included":Included}
            self.TheMacro.append(ThisFunction)
        
    def UpdateFunctionTooltips(self):
        NTotalCalls = 1
        for FunctionCtrls, FunctionInfo in zip(self.TheStartMacroCtrls.values(),self.TheMacro):
            Name = FunctionInfo['Name']
            Included = FunctionInfo['Included']
            Parameters = FunctionInfo['Parameters']
            FunctionPanel = FunctionCtrls[0]
            m_FunctionTextCheck = FunctionCtrls[1]
            NFucntionCalls = 1
            for ParameterName, Info in Parameters.items():
                NCalls = Info['NCalls']
                NFucntionCalls *= NCalls

            if Included:
                NTotalCalls *= NFucntionCalls
                if NTotalCalls == 1:
                    FunctionPanel.SetToolTip(f"{Name} will be called a total of {NTotalCalls} time.")
                    m_FunctionTextCheck.SetToolTip(f"{Name} will be called a total of {NTotalCalls} time.")
                if NTotalCalls > 1:
                    if NFucntionCalls == 1:
                        FunctionPanel.SetToolTip(f"{Name} will be called a total of {NTotalCalls} times.")
                        m_FunctionTextCheck.SetToolTip(f"{Name} will be called a total of {NTotalCalls} times.")
                    else:
                        FunctionPanel.SetToolTip(f"{Name} will be called a total of {NTotalCalls} times with {NFucntionCalls} different parameters.")
                        m_FunctionTextCheck.SetToolTip(f"{Name} will be called a total of {NTotalCalls} times with {NFucntionCalls} different parameters.")
            else:
                FunctionPanel.SetToolTip(f"{Name} will not be called.")
                m_FunctionTextCheck.SetToolTip(f"{Name} will not be called.")

    def SetParameterPanels(self):
        m_MacroSettingScrolledWindowSizer = wx.FlexGridSizer( 0, 1, 0, 0 )
        m_MacroSettingScrolledWindowSizer.SetFlexibleDirection( wx.BOTH )
        m_MacroSettingScrolledWindowSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )




        for Function in self.TheMacro:
            Name = Function["Name"]
            Parameters = Function["Parameters"]
            Included = Function["Included"]
            FunctionPanel = wx.Panel( self.m_MacroSettingScrolledWindow, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL|wx.EXPAND )
            FunctionPanel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) )

            FunctionSizer = wx.FlexGridSizer( 1, 0, 0, 0 )
            FunctionSizer.AddGrowableRow( 0 )
            FunctionSizer.AddGrowableCol( 0 )
            FunctionSizer.SetFlexibleDirection( wx.BOTH )
            FunctionSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
            m_FunctionTextCheck = wx.CheckBox( FunctionPanel, wx.ID_ANY, Name, wx.DefaultPosition, wx.DefaultSize, 0 )
            m_FunctionTextCheck.SetValue(Included)

            def TextCheckFunction(Name,ThisFunction,event):
                Checked = event.GetEventObject().GetValue()
                ThisFunction["Included"] = Checked
                Parameters = self.TheStartMacroCtrls[Name][2]
                for ParameterName,ParameterInfo in Parameters.items():
                    self.TheStartMacroCtrls[Name][2][ParameterName][1].Enable(Checked)
                self.UpdateFunctionTooltips()
            ThisTextCheckFunction = partial(TextCheckFunction,Name,Function)
            m_FunctionTextCheck.Bind( wx.EVT_CHECKBOX, ThisTextCheckFunction )
            # m_FunctionText.Wrap( -1 )
            

            FunctionSizer.Add( m_FunctionTextCheck, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
            FunctionsParametersSizer = wx.FlexGridSizer( 1, 0, 0, 0 )
            FunctionsParametersSizer.SetFlexibleDirection( wx.BOTH )
            FunctionsParametersSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

            self.TheStartMacroCtrls[Name] = [FunctionPanel,m_FunctionTextCheck,{}]
            if len(Parameters) > 0:
                for ParameterName,ParameterInfo in Parameters.items():
                    if not ParameterInfo['Frozen']:
                        ParameterInfo = {**self.TheFunctionInfos[Name][1][ParameterName],**ParameterInfo}
                        Tooltip = ParameterInfo["Tooltip"]
                        if len(Tooltip) > 0:
                            Tooltip += "\n" 
                        Tooltip += f"{ParameterInfo['DefaultValue']}"

                        ParameterPanel = wx.Panel( FunctionPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
                        ParameterPanel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )
                        ParameterPanel.SetMinSize( wx.Size( 250,-1 ) )

                        DefaultValueSizer = wx.FlexGridSizer( 0, 2, 0, 0 )
                        DefaultValueSizer.AddGrowableCol( 0 )
                        DefaultValueSizer.SetFlexibleDirection( wx.BOTH )
                        DefaultValueSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

                        ParameterNameText = wx.StaticText( ParameterPanel, wx.ID_ANY, ParameterName, wx.DefaultPosition, wx.Size( -1,15 ), 0 )
                        ParameterNameText.Wrap( -1 )

                        ParameterNameText.SetMinSize( wx.Size( 120,15 ) )
                        DefaultValueSizer.Add( ParameterNameText, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )

                        def RemoveNonNumbers(Name,DefaultValue,ThisFunction,ParameterName,event):
                            ThisTextCtrl =event.GetEventObject()
                            Text = ThisTextCtrl.GetValue()
                            if not  self.EdittingMode:
                                AcceptableList = ['0','1','2','3','4','5','6','7','8','9','.',',','e','E','-',';']
                            else:
                                AcceptableList = ['0','1','2','3','4','5','6','7','8','9','.','e','E','-']
                            NewText = ''.join([digit for digit in Text if digit in AcceptableList])
                            if NewText != Text:
                                ThisTextCtrl.SetValue(NewText)
                            else:
                                ThisPanel = event.GetEventObject().GetParent()
                                OldToolTip = ThisTextCtrl.GetToolTip().GetTip()
                                if '\n' in OldToolTip:
                                    FirstLine = OldToolTip[:OldToolTip.find("\n")]
                                    FirstLine += "\n"
                                else:
                                    FirstLine = ""
                                TranslatedText,Numbers, NCalls = self.TranslateNumerical(Text,DefaultValue)
                                ThisFunction['Parameters'][ParameterName]['Value'] = Numbers
                                ThisFunction['Parameters'][ParameterName]['NCalls'] = NCalls
                                Tooltip = FirstLine + f"{TranslatedText}"
                                ThisPanel.SetToolTip(Tooltip)
                                for child in ThisPanel.GetChildren():
                                    child.SetToolTip(Tooltip)
                            self.UpdateFunctionTooltips()
                        def UpdateParameters(Name,ThisFunction,ParameterName,event):
                            Value = event.GetEventObject().GetValue()
                            ThisPanel = event.GetEventObject().GetParent()

                            OldToolTip = event.GetEventObject().GetToolTip().GetTip()
                            if '\n' in OldToolTip:
                                FirstLine = OldToolTip[:OldToolTip.find("\n")]
                                FirstLine += "\n"
                            else:
                                FirstLine = ""
                            ThisFunction['Parameters'][ParameterName]['Value'] = Value
                            ThisFunction['Parameters'][ParameterName]['NCalls'] = 1
                            Tooltip = FirstLine + f"{Value}"
                            ThisPanel.SetToolTip(Tooltip)
                            for child in ThisPanel.GetChildren():
                                child.SetToolTip(Tooltip)
                        def UpdateChoiceParameters(Name,ThisFunction,ParameterName,event):
                            Value = event.GetEventObject().GetStringSelection()
                            ThisPanel = event.GetEventObject().GetParent()

                            OldToolTip = event.GetEventObject().GetToolTip().GetTip()
                            if '\n' in OldToolTip:
                                FirstLine = OldToolTip[:OldToolTip.find("\n")]
                                FirstLine += "\n"
                            else:
                                FirstLine = ""
                            ThisFunction['Parameters'][ParameterName]['Value'] = Value
                            ThisFunction['Parameters'][ParameterName]['NCalls'] = 1
                            Tooltip = FirstLine + f"{Value}"
                            ThisPanel.SetToolTip(Tooltip)
                            for child in ThisPanel.GetChildren():
                                child.SetToolTip(Tooltip)
                        if ParameterInfo['ValueType'] == 'Numerical':
                            ParameterValueText = wx.TextCtrl( ParameterPanel, wx.ID_ANY, f"{ParameterInfo['DefaultValue']}", wx.DefaultPosition, wx.DefaultSize, 0 )
                            ThisRemoveNonNumbers = partial(RemoveNonNumbers,Name,f"{ParameterInfo['DefaultValue']}",Function,ParameterName)
                            ParameterValueText.Bind( wx.EVT_TEXT, ThisRemoveNonNumbers)
                        elif ParameterInfo['ValueType'] == 'Choice':
                            ParameterValueText = wx.Choice( ParameterPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.TheFunctionInfos[Name][1][ParameterName]['DefaultValue'])
                            ParameterValueText.SetStringSelection(ParameterInfo['DefaultValue'])
                            ThisUpdateParameters = partial(UpdateChoiceParameters,Name,Function,ParameterName)
                            ParameterValueText.Bind( wx.EVT_CHOICE, ThisUpdateParameters)
                        elif ParameterInfo['ValueType'] == 'Boolean':
                            ParameterValueText = wx.CheckBox( ParameterPanel, wx.ID_ANY, "", wx.DefaultPosition, wx.DefaultSize, 0 )
                            ParameterValueText.SetValue(ParameterInfo['DefaultValue'])
                            ThisUpdateParameters = partial(UpdateParameters,Name,Function,ParameterName)
                            ParameterValueText.Bind( wx.EVT_CHECKBOX, ThisUpdateParameters)
                        elif ParameterInfo['ValueType'] == 'String':
                            ParameterValueText = wx.TextCtrl( ParameterPanel, wx.ID_ANY, ParameterInfo['DefaultValue'], wx.DefaultPosition, wx.DefaultSize, 0 )
                            ParameterValueText.SetValue(ParameterInfo['DefaultValue'])
                            ThisUpdateParameters = partial(UpdateParameters,Name,Function,ParameterName)
                            ParameterValueText.Bind( wx.EVT_TEXT, ThisUpdateParameters)
                        DefaultValueSizer.Add( ParameterValueText, 1, wx.ALL, 5 )


                        # ParameterSizer.Add( DefaultValueSizer, 1, wx.EXPAND, 5 )



                        ParameterPanel.SetSizer( DefaultValueSizer )
                        ParameterPanel.Layout()
                        ParameterPanel.SetToolTip(Tooltip)
                        for child in ParameterPanel.GetChildren():
                            child.SetToolTip(Tooltip)
                        DefaultValueSizer.Fit( ParameterPanel )
                        FunctionsParametersSizer.Add( ParameterPanel, 1, wx.EXPAND |wx.ALL, 5 )

                        self.TheStartMacroCtrls[Name][2][ParameterName] = [ParameterPanel,ParameterValueText] 
            else:
                ParameterPanel = wx.Panel( FunctionPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
                ParameterPanel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) )
                ParameterPanel.SetMinSize( wx.Size( 250,-1 ) )
                # BlankText = wx.StaticText( ParameterPanel, wx.ID_ANY, "", wx.DefaultPosition, wx.Size( -1,15 ), 0 )
                # FunctionsParametersSizer.Add( BlankText, 1, wx.EXPAND |wx.ALL, 5 )
                FunctionsParametersSizer.Add( ParameterPanel, 1, wx.EXPAND |wx.ALL, 5 )
                
            FunctionSizer.Add( FunctionsParametersSizer, 1, wx.EXPAND, 5 )
            FunctionPanel.SetSizer( FunctionSizer )
            FunctionPanel.Layout()
            FunctionSizer.Fit( FunctionPanel )
            m_MacroSettingScrolledWindowSizer.Add( FunctionPanel, 1, wx.ALL|wx.EXPAND, 5 )


        self.m_MacroSettingScrolledWindow.SetSizer( m_MacroSettingScrolledWindowSizer )
        self.m_MacroSettingScrolledWindow.Layout()
        m_MacroSettingScrolledWindowSizer.Fit( self.m_MacroSettingScrolledWindow )
        # m_MacroSettingScrolledWindowSizer.Layout()
        Size = m_MacroSettingScrolledWindowSizer.GetSize()
        ButtomSize = self.BottomPanel.GetSize()
        Width = Size[0]+30
        Height = Size[1]+ButtomSize[1]+100
        self.SetSize(Width,Height)
        self.Center()
    def TranslateNumerical(self,OldString,DefaultValue):
        def ScrubNumber(String):
            
            AcceptableChar = [',',';','e','E'] if not self.EdittingMode else ['e','E']
            while len(String) > 0 and String[0] in AcceptableChar:
                String = String[1:]
            AcceptableChar = [',',';','e','E','-'] if not self.EdittingMode else ['e','E','-']
            while len(String) > 0 and String[-1] in ['.',',',';','e','E','-']:
                String = String[:-1]
            return String
        def CleanNumber(String):
            String = ScrubNumber(String)
            try:
                a = float(String)
                return String
            except:
                return None
        
        OldString = ScrubNumber(OldString)
        while OldString is None or len(OldString) == 0:
            OldString = ScrubNumber(DefaultValue)

        # Comment out this replace line if you only want ; to do np.arange
        OldString = OldString.replace(",",";")
        if ',' in OldString:
            NewString = OldString.replace(";",",")
            NewString = NewString.split(',')
            NewString = [CleanNumber(Item) for Item in NewString if CleanNumber(Item) is not None]
            Numbers = [float(X) if float(X)%1 != 0 else int(X) for X in NewString if len(X)>0]
            NewString = [f"{X}" for X in Numbers]
            NCalls = len(NewString)
            NewString = ','.join(NewString)
        elif ';' in OldString:
            NewString = OldString.split(';')
            NewString = [CleanNumber(Item) for Item in NewString if CleanNumber(Item) is not None]
            if len(NewString) == 3 and float(NewString[0]) < float(NewString[1]) and float(NewString[2]) != 0 and float(NewString[2]) < (float(NewString[1])-float(NewString[0])) and float(NewString[2]) > 0:
                NewString = [float(X) for X in NewString]
                NewString[1] += NewString[2]/1000
                NewString = np.arange(*NewString)
                Numbers = [float(X) if float(X)%1 != 0 else int(float(X)) for X in NewString]
                NewString = [f"{X}" for X in Numbers]
            else:
                Numbers = [float(X) if float(X)%1 != 0 else int(float(X)) for X in NewString if len(X)>0]
                NewString = [f"{X}" for X in Numbers]
            NCalls = len(NewString)
            NewString = ','.join(NewString)
        else:
            NCalls = 1
            NewString = CleanNumber(OldString)
            while NewString is None or len(NewString) == 0:
                NewString = ScrubNumber(DefaultValue)
            Numbers = [float(NewString)]
        if NCalls == 0:
            NewString = ScrubNumber(DefaultValue)
            while NewString is None or len(NewString) == 0:
                NewString = ScrubNumber(DefaultValue)
            Numbers = [float(NewString)]
            NCalls = 1
        return NewString,Numbers,NCalls

    def AddToQueue(self, event=None):
        if not self.EdittingMode:
            self.Parent.AddMacroToQueue(self.TheMacro,self.MacroName)
        else:
            ThisMacro = []
            for Function in self.TheMacro:
                Parameters = {key:value['Value'][0] for key,value in Function['Parameters'].items()}
                FunctionInfo = {'Name':Function['Name'],'Parameters':Parameters}
                ThisMacro.append([FunctionInfo,Function['Included']])
            

            self.Parent.TheQueue[self.QueueIndex][0] = ThisMacro
        self.Destroy()
        pass
    def OnCancel(self, event):
        self.Destroy()


class MyChooseSoftwareDialog(ChooseSoftware):
    def __init__(self, parent):
        super().__init__(parent)
        self.SavedSettingsFile = self.Parent.SavedSettingsFile
    def OnRHK(self, event=None):
        self.SetSoftware("RHK")
    def OnCreaTec(self, event=None):
        self.SetSoftware("CreaTec")
    def OnSXM(self, event=None):
        self.SetSoftware("SXM")
    def SetSoftware(self,software):
        self.Parent.m_RHKmenuItem.Check(False)
        self.Parent.m_CreaTecmenuItem.Check(False)
        self.Parent.m_SXMmenuItem.Check(False)
        if software == "RHK":
            self.Parent.m_RHKmenuItem.Check(True)
        if software == "CreaTec":
            self.Parent.m_CreaTecmenuItem.Check(True)
        if software == "SXM":
            self.Parent.m_SXMmenuItem.Check(True)
        self.Parent.Software = software
        self.Parent.MacroPath = self.Parent.MacroPaths[software]
        self.Parent.MakeFunctionButtons()
        SettingsDict = {"Software":software}
        pd.Series(SettingsDict).to_csv(self.SavedSettingsFile,header=False)
        self.Parent.MakeFunctionButtons()
        self.Parent.IncomingQueue.put(["SoftwareChange",software])
        self.Destroy()