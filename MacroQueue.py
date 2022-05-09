import wx
import os
import sys
import pandas as pd
import pyvisa
import SXMRemote
import time
import socket
# from shutil import copytree,rmtree
# from functools import partial
# import win32com.client
# import plotly.graph_objects as go
# import plotly.express as px
import multiprocessing as mp
import numpy as np
# from math import log10 , floor
import queue
import GUIDesign
import threading


import wx

# from STMMacroQueue.GUIDesign import MacroSettingsDialog
from time import time as timer

from Dialogs import MyMacroDialog as MacroDialog
from Dialogs import MyMacroSettingsDialog as MacroSettingsDialog
from Dialogs import MyStartMacroDialog as StartMacroDialog
from Dialogs import MyChooseSoftwareDialog as ChooseSoftwareDialog
# from GUIDesign import MacroSettingsDialog

from Macros import *

# from GUIDesign import MacroDialog
from inspect import getmembers, isfunction


import Functions.RHK as RHKFunctions
import Functions.CreaTec as CreaTecFunctions
import Functions.SXM as SXMFunctions
import Functions.General as GeneralFunctions

import json


IconFileName = "MacroQueueIcon.ico"


# BUG:
# Function in macro twice??  (I use function name as dict key in start dialog.  Replace dict with (ordered) list)

# TODO:
# Decrease minimum y size
# Allow the macro buttons and the Pause/Clear button to disappear when the size is smaller
# Allow for changes in functions when reading a old macro file.  Start with default.
# Show number of items in queue in status bar

# Pause after disconnect
# Autoadd connect after disconnect
# Remove Status bar 3 when scan is canceled.

# np arange stop responding when len > ~100,000

# RHK functions
# Cancel Scan
# Scan - Only top down
# RHK Scan doesn't stop???
# Set Speed (nm/s, line time, pixel time)
# Set position option (absolute or relative)
# Set default save folder


# Createc
# Function to change recorded channels.  No longer change it during scan or dIdV scan


# ETC
    # Get scan speed / size / NLines during Initialize
    # When the single macro is added to the queue, add a estimated time to each function (Usually zero for non-scan functions)
    # Add to macro tooltip: "\n \n This will finish at 6:05 pm today" 
        # \n This will finish at 6:05 pm tomorrow"
        # \n This will finish at 6:05 pm 3/16/2022"

# Don't hold m_FunctionWindow,m_FunctionNameText in self.TheQueue.  The text only needs to be MacroLabel.  The window is only used to set the tooltip


# Have a log dialog that can be opened (but doesn't have to be).  The log dialog shows whatever is printed (or the equivlant)

# SciT notation
# Ramping & scanning : set status bar 3
# Progress bar: https://stackoverflow.com/questions/1883528/wxpython-progress-bar

# Createc Scan time wrong.  Factor of 2.  Forward and back?


# Write the help dialog


# Check dialog when opening souce when frozen   #  What did I mean when I wrote this???

# Save PDF
# Email


# In the createc Scan, when I get the Y pixels, it crashes if I haven't set it?  There's no default value? 
# On close, I cancel the scan.  Should I try to prevent that?


class MainFrame(GUIDesign.MyFrame):
    MacroPaths = {"RHK":"Macros//RHKMacro.json","CreaTec":"Macros//CreaTecMacro.json","SXM":"Macros//SXMMacro.json"}

# Scanning, fine motion, course motion, dI/dV scans, point spectra, tip form, 
    Functions = {"RHK":RHKFunctions,"CreaTec":CreaTecFunctions,"SXM":SXMFunctions,"General":GeneralFunctions}
    TheQueue = []
    AddToQueue = []
    Paused = True
    Running = False

    def __init__(self):
        application_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
        os.chdir(os.path.realpath(application_path))
        self.SavedSettingsFile = 'MacroQueueSettings.csv'

        mp.set_start_method('spawn')
        self.OutgoingQueue = mp.Queue()
        self.IncomingQueue = mp.Queue()
        self.Process = threading.Thread(target=Thread, args=(self,self.IncomingQueue,self.OutgoingQueue))
        self.Process.start()
        # Starts Thread with Incoming & Outgoing Queue.  Any time-consuming calculations/measurements should be made on this thread.

        # The GUIDesign is defined in GUIDesign.py as the class MyFrame. It was made with wxFormBuilder
        GUIDesign.MyFrame.__init__(self, parent=None) 
        icon_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), IconFileName)
        if os.path.exists(icon_file):
            icon = wx.Icon(icon_file)
            self.SetIcon(icon)

        # Read the saved settings file here
        if os.path.exists(self.SavedSettingsFile):
            SettingsSeries = pd.read_csv(self.SavedSettingsFile,names=['key','value'])
            self.SettingsDict = SettingsSeries.set_index('key').T.iloc[0].to_dict()
            self.Software = self.SettingsDict["Software"]
            ThisChooseSoftwareDialog = ChooseSoftwareDialog(self)
            ThisChooseSoftwareDialog.SetSoftware(self.Software)
        else:
            ThisChooseSoftwareDialog = ChooseSoftwareDialog(self)
            ThisChooseSoftwareDialog.ShowModal()

        
        YBitmapSize = 20
        self.DownBitmap = wx.Bitmap( u"Bitmaps/DownArrow.bmp", wx.BITMAP_TYPE_ANY).ConvertToImage().Scale(20,YBitmapSize).ConvertToBitmap()
        self.UpBitmap = wx.Bitmap( u"Bitmaps/UpArrow.bmp", wx.BITMAP_TYPE_ANY).ConvertToImage().Scale(20,YBitmapSize).ConvertToBitmap()
        self.RemoveBitmap = wx.Bitmap( u"Bitmaps/Remove.bmp", wx.BITMAP_TYPE_ANY).ConvertToImage().Scale(20,YBitmapSize).ConvertToBitmap()
        self.m_FunctionNameSizer = wx.FlexGridSizer( 0, 1, -6, 0 )
        self.m_FunctionNameSizer.AddGrowableCol( 0 )
        self.m_FunctionNameSizer.SetFlexibleDirection( wx.BOTH )
        self.m_FunctionNameSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        self.m_QueueWindow.SetSizer(self.m_FunctionNameSizer)
        dt = MyPanelDropTarget(self.m_QueueWindow,self)
        self.m_QueueWindow.SetDropTarget(dt)
        def OnQueueSize(event):
            # self.m_QueueWindow.Layout()
            self.m_QueueWindow.FitInside()
        self.m_QueueWindow.Bind( wx.EVT_SIZE, OnQueueSize )
        self.AddConnectToQueue()
        self.Show()

    def CheckQueue(self,event):
        try:
            Message = self.OutgoingQueue.get(False)
            while Message:
                if Message[0] == 'SetStatus':
                    self.StatusBar.SetStatusText(*Message[1])
                if Message[0] == 'FunctionFinished':
                    self.Running = False
                    Macro,FunctionPanel,FunctionText = self.TheQueue.pop(0)
                    FunctionPanel.Destroy()
                    self.m_QueueWindow.FitInside()
                if Message[0] == "ExceptionThrown":
                    if not self.Paused:
                        Macro,FunctionPanel,FunctionText = self.TheQueue.pop(0)
                        exception,FunctionName = Message[1]
                        FunctionPanel.SetBackgroundColour('red')
                        FunctionPanel.Refresh()
                        MyMessage = wx.MessageDialog(self,message=f"There was an error from the function '{FunctionName}' in the Macro '{FunctionText.GetLabel()}':\n\n{exception}",caption=f"Error - {FunctionText.GetLabel()}")
                        self.Running = False
                        self.Pause()
                        MyMessage.ShowModal()
                        FunctionPanel.Destroy()
                        self.m_QueueWindow.FitInside()
                Message = self.OutgoingQueue.get(False)
        except queue.Empty:
            pass
        if not self.Paused and not self.Running and len(self.TheQueue) > 0:
            self.Running = True
            Macro,FunctionPanel,FunctionText = self.TheQueue[0]
            FunctionPanel.SetBackgroundColour('green')
            FunctionPanel.Refresh()
            self.IncomingQueue.put(("StartFunction",Macro))
            self.StatusBar.SetStatusText(f"Macro: {FunctionText.GetLabel()}",0)
            self.StatusBar.SetStatusText("",1)
        if len(self.AddToQueue) > 0  and len(self.TheQueue) < 500:
            AddN = 5
            AddN = AddN if len(self.AddToQueue) > AddN else len(self.AddToQueue)
            for i in range(AddN):
                MacroName,Macro = self.AddToQueue.pop(0)
                self.AddSingleMacroToQueue(MacroName,Macro)
            self.m_QueueWindow.FitInside()
            # self.m_QueueWindow.Layout()

        return
    def IdleLoop(self, event):
        if len(self.AddToQueue) > 0 and len(self.TheQueue) < 500:
            AddN = 3
            AddN = AddN if len(self.AddToQueue) > AddN else len(self.AddToQueue)
            for i in range(AddN):
                MacroName,Macro = self.AddToQueue.pop(0)
                self.AddSingleMacroToQueue(MacroName,Macro)
            self.m_QueueWindow.FitInside()
    def OnClose(self,event):
        self.ClearQueue()
        self.IncomingQueue.put(['OnClose'])
        self.Process.join()
        self.Destroy()
    def MakeFunctionButtons(self):
        for child in self.m_FunctionButtonWindow.GetChildren():
            child.Destroy()
        FunctionButtonSizer = wx.FlexGridSizer(0,2,0,0)
        
        if os.path.exists(self.MacroPath):
            with open(self.MacroPath, 'r') as fp:
                AllTheMacros = json.load(fp)
        else:
            AllTheMacros = {}
        
        def WriteFile(AllTheMacros):
            os.makedirs("Macros",exist_ok=True)
            with open(self.MacroPath, 'w') as fp:
                json.dump(AllTheMacros, fp,indent=1)

        # for FunctionName in self.Functions[self.SettingsDict['Software']].keys():
        for FunctionName in AllTheMacros.keys():
            FunctionButton = wx.Button( self.m_FunctionButtonWindow, wx.ID_ANY, FunctionName, wx.DefaultPosition, wx.Size( 100,30 ), 0 )
            FunctionButton.Bind( wx.EVT_BUTTON, self.OnFunctionButton )
            FunctionButtonSizer.Add(FunctionButton,0, wx.ALL, 5)
            def FunctionRightClick(event):
                ThisButton = event.GetEventObject()
                popupmenu = wx.Menu()
                menuItem = popupmenu.Append(-1, 'Add to Queue')
                def Queued(event2):
                    self.OnFunctionButton(event)
                self.Bind(wx.EVT_MENU, Queued, menuItem)
                menuItem = popupmenu.Append(-1, 'Edit')
                def Edit(event):
                    MacroLabel = ThisButton.GetLabel()
                    MyMacroDialog = MacroDialog(self,MacroName=MacroLabel,InitalMacro=AllTheMacros[MacroLabel])
                    MyMacroDialog.ShowModal()
                self.Bind(wx.EVT_MENU, Edit, menuItem)
                menuItem = popupmenu.Append(-1, 'Delete')
                def Delete(event):
                    MacroLabel = ThisButton.GetLabel()
                    MyMessage = wx.MessageDialog(self,message=f"Are you sure that you want to delete {MacroLabel}?\nThis cannot be undone.",caption="Delete Macro",style=wx.YES_NO)
                    YesOrNo = MyMessage.ShowModal()
                    if YesOrNo == wx.ID_YES:
                        with open(self.MacroPath, 'r') as fp:
                            AllTheMacros = json.load(fp)
                        AllTheMacros.pop(MacroLabel)
                        with open(self.MacroPath, 'w') as fp:
                            json.dump(AllTheMacros, fp,indent=1)
                        self.MakeFunctionButtons()
                        self.m_FunctionButtonWindow.Layout()
                self.Bind(wx.EVT_MENU, Delete, menuItem)
                ThisButton.PopupMenu(popupmenu)
            FunctionButton.Bind( wx.EVT_RIGHT_DOWN, FunctionRightClick )
        self.m_FunctionButtonWindow.SetSizer(FunctionButtonSizer)
        self.m_FunctionButtonWindow.Layout()



    def OnFunctionButton(self,event):
        MacroLabel = event.GetEventObject().GetLabel()
        with open(self.MacroPath, 'r') as fp:
            AllTheMacros = json.load(fp)
        ThisMacro = AllTheMacros[MacroLabel]
        MyStartMacroDialog = StartMacroDialog(self,MacroLabel,ThisMacro)
        MyStartMacroDialog.ShowModal()
        
    def OnRFunctionClick(self, event):
        ThisText = event.GetEventObject()
        if ThisText.GetLabel() != "panel":
            ThisText = ThisText.GetParent()
        for ThisIndex,(Function,Panel,Text) in enumerate(self.TheQueue):
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
            self.m_QueueWindow.FitInside()
            pass
        self.Bind(wx.EVT_MENU, MoveUp, menuItem)
        if Index == 0 or (Index == 1 and self.Running):
            menuItem.Enable(False)
        
        menuItem = popupmenu.Append(-1, 'Move Down')
        def MoveDown(event):
            Function = self.TheQueue.pop(Index)
            self.TheQueue.insert(Index+1,Function)
            self.m_FunctionNameSizer.Remove(Index)
            self.m_FunctionNameSizer.Insert(Index+1,ThisText, 0, wx.ALL|wx.EXPAND, 5)
            self.m_QueueWindow.FitInside()
        if Index == 0 and self.Running:
            menuItem.Enable(False)

        self.Bind(wx.EVT_MENU, MoveDown, menuItem)
        if Index == len(self.TheQueue)-1:
            menuItem.Enable(False)

        menuItem = popupmenu.Append(-1, 'Edit Parameters')
        def Edit(event):
            OriginallyPaused = self.Paused
            self.Paused = True
            MacroLabel = self.TheQueue[Index][2].GetLabel()
            ThisMacroInfo = [[Function['Name'],{key:{"DefaultValue":f"{Parameter}",'Frozen':False} for key,Parameter in Function['Parameters'].items()},Included] for Function,Included in self.TheQueue[Index][0]]
            MyStartMacroDialog = StartMacroDialog(self,MacroLabel,ThisMacroInfo,EdittingMode=True,Index=Index)
            MyStartMacroDialog.ShowModal()
            self.Paused = OriginallyPaused
            thisSettingString = ""
            ThisMacro = self.TheQueue[Index][0]
            for Function,Included in ThisMacro:
                if Included:
                    for key, value in Function['Parameters'].items():
                        thisSettingString+=f"{key} = {value}, "
            thisSettingString = thisSettingString[:-2]
            for child in self.TheQueue[Index][1].GetChildren():
                child.SetToolTip(thisSettingString)
            self.TheQueue[Index][1].GetChildren()[-1].SetLabel(thisSettingString)
        self.Bind(wx.EVT_MENU, Edit, menuItem)
        # menuItem.Enable(False)
        if Index == 0 and self.Running:
            menuItem.Enable(False)

        menuItem = popupmenu.Append(-1, 'Copy')
        def Copy(event):
            MacroLabel = self.TheQueue[Index][2].GetLabel()
            Macro = self.TheQueue[Index][0]
            self.AddSingleMacroToQueue(MacroName=MacroLabel,Macro=Macro)
            CopiedIndex = len(self.TheQueue)-1
            Function = self.TheQueue.pop(CopiedIndex)
            self.TheQueue.insert(Index+1,Function)
            self.m_FunctionNameSizer.Remove(CopiedIndex)
            self.m_FunctionNameSizer.Insert(Index+1,Function[1], 0, wx.ALL|wx.EXPAND, 5)
            self.m_QueueWindow.FitInside()
            pass
        self.Bind(wx.EVT_MENU, Copy, menuItem)
        # menuItem.Enable(False)
    

        if Index == 0 and self.Running:
            menuItem = popupmenu.Append(-1, 'Cancel')
            def Cancel(event):
                ThisText.SetBackgroundColour('red')
                ThisText.Refresh()
                # self.IncomingQueue.put(("Cancel",))
                self.Cancel()
            self.Bind(wx.EVT_MENU, Cancel, menuItem)
        else:
            menuItem = popupmenu.Append(-1, 'Remove')
            def Remove(event):
                self.TheQueue.pop(Index)
                ThisText.Destroy()
                self.m_QueueWindow.FitInside()
            self.Bind(wx.EVT_MENU, Remove, menuItem)

        menuItem = popupmenu.Append(-1, 'Clear All Below')
        def RemoveBelow(event):
            for RemoveIndex,(Function,RemovePanel,Text) in enumerate(self.TheQueue):
                if RemoveIndex > Index:
                    RemovePanel.Destroy()
            self.AddToQueue = []
            self.TheQueue = self.TheQueue[:Index+1]
            self.m_QueueWindow.FitInside()
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
    def ClearQueue(self,event=None):
        self.AddToQueue = []
        if len(self.TheQueue) > 0:
            if self.Running:
                for RemoveIndex,(Function,RemovePanel,Text) in enumerate(self.TheQueue):
                    if RemoveIndex >= 1:
                        RemovePanel.Destroy()
                self.TheQueue = self.TheQueue[:1]
                self.TheQueue[0][1].SetBackgroundColour('red')
                self.TheQueue[0][1].Refresh()
                # self.IncomingQueue.put(("Cancel",))
                self.Cancel()
            else:
                for Function,RemovePanel,Text in self.TheQueue:
                    RemovePanel.Destroy()
                self.TheQueue = []
            self.m_QueueWindow.FitInside()
    def Pause(self, event=None):
        if self.Paused:
            self.Paused = False
            self.m_PauseAfterButton.SetLabel("Pause After Function")
            for i,Macro in enumerate(self.TheQueue):
                if (i > 0 and self.Running) or not self.Running:
                    Macro[1].SetBackgroundColour(wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ))
                    Macro[1].Refresh()
        else:
            self.Paused = True
            self.m_PauseAfterButton.SetLabel("Resume")
            for i,Macro in enumerate(self.TheQueue):
                if (i > 0 and self.Running) or not self.Running:
                    Macro[1].SetBackgroundColour(wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE))
                    Macro[1].Refresh()
        return
    def Cancel(self):
        if not self.Paused:
            self.Pause()
        self.Functions[self.Software].Cancel = True
        self.Functions["General"].Cancel = True

    def StartMakeNewMacro(self,event):
        MyMacroDialog = MacroDialog(self)
        MyMacroDialog.ShowModal()

        # # https://docs.python.org/3/library/inspect.html
        # # RHKFunctionsNames = dir(RHKFunctions)
        
        # FunctionSettings = {}
        # for Name,Function in getmembers(RHKFunctions, isfunction):
        #     print(Name)
        #     print(getcomments(Function))
        #     print(type(getcomments(Function)))
        #     Settings = {Key:Value for Key,Value in zip(inspect.getfullargspec(Function)[0],inspect.getfullargspec(Function)[3])} if len(inspect.getfullargspec(Function)[0]) > 0 else {}
        #     FunctionSettings[Name] = Settings
        # print(FunctionSettings)
        pass
    def DefineMacroSettings(self,Name,TheMacro):
        MyMacroSettingsDialog = MacroSettingsDialog(self,Name,TheMacro)
        MyMacroSettingsDialog.ShowModal()
    def AddMacroToQueue(self,TheMacro,MacroName):
        TheExpandedMacros = []
        for Function in TheMacro:
            Included = Function['Included']
            Name = Function['Name']
            Parameters = Function['Parameters']


            nDataPoints = 1
            ExpandedInputSpace = {}
            for key, Parameter in Parameters.items():
                value = Parameter['Value']
                if type(value) != list:
                    value = [value]
                #pair each input...
                ListLength = len(value)
                for ExpandedKey, ExpandedValues in ExpandedInputSpace.items():
                    #...with each input that came before it.
                    ExpandedInputSpace[ExpandedKey] = [ExpandedValues[i] for j in range(ListLength) for i in range(nDataPoints)]
                ExpandedInputSpace[key] = [value[j] for j in range(ListLength) for i in range(nDataPoints)]
                nDataPoints *= ListLength
            ExpandedInputSpace = [{ExpandedKey: ExpandedValues[i] for ExpandedKey, ExpandedValues in ExpandedInputSpace.items()} for i in range(nDataPoints)]
            if Included:
                # print(Name,ExpandedInputSpace)
                if len(TheExpandedMacros) == 0:
                    for ParameterSet in ExpandedInputSpace:
                        ExpandedMacroFunction = {"Name":Name}
                        ExpandedMacroFunction['Parameters'] = {}
                        for ParameterName, ParameterValue in ParameterSet.items():
                            ExpandedMacroFunction['Parameters'][ParameterName] = ParameterValue
                        TheExpandedMacros.append([[ExpandedMacroFunction,True]])
                        
                else:
                    TheUpdatedExpandedMacros = []
                    for MacroIndex,Macro in enumerate(TheExpandedMacros):
                        for FunctionIndex,ParameterSet in enumerate(ExpandedInputSpace):
                            MacroCopy = Macro.copy()
                            ExpandedMacroFunction = {"Name":Name}
                            ExpandedMacroFunction['Parameters'] = {}
                            for ParameterName, ParameterValue in ParameterSet.items():
                                ExpandedMacroFunction['Parameters'][ParameterName] = ParameterValue
                            if FunctionIndex == 0:
                                MacroCopy.append([ExpandedMacroFunction,True])
                                TheUpdatedExpandedMacros.append(MacroCopy)
                            else:
                                MacroCopy = [[Function[0],False] for Function in MacroCopy]
                                MacroCopy.append([ExpandedMacroFunction,True])
                                TheUpdatedExpandedMacros.append(MacroCopy)
                    TheExpandedMacros = TheUpdatedExpandedMacros
            else:
                if len(TheExpandedMacros) == 0:
                    ParameterSet = ExpandedInputSpace[0]
                    ExpandedMacroFunction = {"Name":Name}
                    ExpandedMacroFunction['Parameters'] = {}
                    for ParameterName, ParameterValue in ParameterSet.items():
                        ExpandedMacroFunction['Parameters'][ParameterName] = ParameterValue
                    TheExpandedMacros.append([[ExpandedMacroFunction,False]])
                        
                else:
                    TheUpdatedExpandedMacros = []
                    for MacroIndex,Macro in enumerate(TheExpandedMacros):
                        ParameterSet = ExpandedInputSpace[0]
                        ExpandedMacroFunction = {"Name":Name}
                        ExpandedMacroFunction['Parameters'] = {}
                        for ParameterName, ParameterValue in ParameterSet.items():
                            ExpandedMacroFunction['Parameters'][ParameterName] = ParameterValue
                        Macro.append([ExpandedMacroFunction,False])
                        TheUpdatedExpandedMacros.append(Macro)
        for Macro in TheExpandedMacros:
            self.AddToQueue.append([MacroName,Macro])
            # self.AddSingleMacroToQueue(MacroName,Macro)
    def AddSingleMacroToQueue(self,MacroName,Macro):
        StartTime = timer()
        thisSettingString = ""
        for Function,Included in Macro:
            if Included:
                for key, value in Function['Parameters'].items():
                    thisSettingString+=f"{key} = {value}, "
        thisSettingString = thisSettingString[:-2]

        YBitmapSize = 30
        m_FunctionWindow = wx.Panel( self.m_QueueWindow, wx.ID_ANY, (5000,5000), wx.Size(-1,-1), wx.TAB_TRAVERSAL | wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        m_FunctionWindow.Hide()
        m_FunctionWindow.SetPosition(wx.DefaultPosition)
        m_FunctionWindow.Show()

        # self.m_FunctionNameSizer.Add( m_FunctionWindow, 0, wx.ALL|wx.EXPAND, 5 )
        m_FunctionWindow.Bind(wx.EVT_MOTION, self.OnStartDrag)
        Color = wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) if (not self.Paused or self.m_PauseAfterButton.GetLabel() == "Start") else wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE)
        m_FunctionWindow.SetBackgroundColour(Color)
        m_FunctionWindow.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
        bSizer1 = wx.FlexGridSizer( 1, 10, 0, 0 )
        bSizer1.SetFlexibleDirection( wx.BOTH )
        bSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        bSizer1.AddGrowableCol(6)
        # bSizer1 = wx.BoxSizer( wx.HORIZONTAL )

        m_FunctionNameText = wx.StaticText( m_FunctionWindow, wx.ID_ANY, MacroName, wx.DefaultPosition, wx.Size( -1,-1), wx.ALIGN_RIGHT)
        m_FunctionNameText.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
        bSizer1.Add( m_FunctionNameText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 2 )

        Text = wx.StaticText( m_FunctionWindow, wx.ID_ANY, "", wx.DefaultPosition, wx.Size( 10,YBitmapSize), wx.ALIGN_CENTER_HORIZONTAL)
        Text.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
        bSizer1.Add( Text, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2 )

        m_Up = wx.BitmapButton( m_FunctionWindow, wx.ID_ANY, self.UpBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        bSizer1.Add( m_Up, 0, wx.ALL|wx.ALIGN_CENTER, 2 )
        m_Up.Bind( wx.EVT_BUTTON, self.MoveUpInQueue)

        m_Down = wx.BitmapButton( m_FunctionWindow, wx.ID_ANY, self.DownBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        bSizer1.Add( m_Down, 0, wx.ALL|wx.ALIGN_CENTER, 2 )

        m_Down.Bind( wx.EVT_BUTTON, self.MoveDowninQueue)
            
        m_Remove = wx.BitmapButton( m_FunctionWindow, wx.ID_ANY, self.RemoveBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
        bSizer1.Add( m_Remove, 0, wx.ALL|wx.ALIGN_CENTER, 2 )

        m_Remove.Bind( wx.EVT_BUTTON, self.RemoveFromQueue)



        m_Edit = wx.Button( m_FunctionWindow, wx.ID_ANY, u"Edit", wx.DefaultPosition, wx.Size(40,YBitmapSize), 0 )
        bSizer1.Add( m_Edit, 0, wx.ALL|wx.ALIGN_CENTER, 2 )

        m_Edit.Bind( wx.EVT_BUTTON, self.EditMacroInQueue)
        # m_Edit.Enable(False)


        
        SettingText = wx.StaticText( m_FunctionWindow, wx.ID_ANY, thisSettingString, wx.DefaultPosition, wx.Size( 10,YBitmapSize), wx.ALIGN_RIGHT)
        SettingText.Bind( wx.EVT_RIGHT_DOWN, self.OnRFunctionClick )
        bSizer1.Add( SettingText, 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.ALL, 2 )

        m_FunctionWindow.SetToolTip(thisSettingString)
        for child in m_FunctionWindow.GetChildren():
                child.SetToolTip(thisSettingString)

        m_FunctionWindow.SetSizer( bSizer1 )
        # m_FunctionWindow.Layout()
        bSizer1.Fit( m_FunctionWindow )
        Index = len(self.TheQueue)
        self.TheQueue.append([Macro,m_FunctionWindow,m_FunctionNameText])
        self.m_FunctionNameSizer.Add( m_FunctionWindow, 0, wx.ALL|wx.EXPAND, 5 )
        # self.m_FunctionNameSizer.Insert(Index,m_FunctionWindow, 0, wx.ALL|wx.EXPAND, 5)
        # gauge = wx.Gauge(m_FunctionWindow, range = 20, size = m_FunctionWindow.GetSize(), style = wx.GA_HORIZONTAL)
        # self.m_FunctionNameSizer.Add( gauge, 0, wx.ALL|wx.EXPAND, 5 )
        # gauge.SetPosition((0,0))
        self.m_QueueWindow.FitInside()
        self.m_QueueWindow.Layout()

    def MoveUpInQueue(self,event):
        ThisPanel = event.GetEventObject().GetParent()
        for ThisIndex,(Function,Panel,t) in enumerate(self.TheQueue):
            Index = ThisIndex
            if ThisPanel.GetId() == Panel.GetId():
                break
        if Index == 0 or (Index == 1 and self.Running):
            pass
        else:
            Function = self.TheQueue.pop(Index)
            self.TheQueue.insert(Index-1,Function)
            self.m_FunctionNameSizer.Remove(Index)
            self.m_FunctionNameSizer.Insert(Index-1,ThisPanel, 0, wx.ALL|wx.EXPAND, 5)
            self.m_QueueWindow.FitInside()
    def MoveDowninQueue(self,event):
        ThisPanel = event.GetEventObject().GetParent()
        for ThisIndex,(Function,Panel,t) in enumerate(self.TheQueue):
            Index = ThisIndex
            if ThisPanel.GetId() == Panel.GetId():
                break
        if (Index == 0 and self.Running) or (Index == len(self.TheQueue)-1):
            pass
        else:
            Function = self.TheQueue.pop(Index)
            self.TheQueue.insert(Index+1,Function)
            self.m_FunctionNameSizer.Remove(Index)
            self.m_FunctionNameSizer.Insert(Index+1,ThisPanel, 0, wx.ALL|wx.EXPAND, 5)
            self.m_QueueWindow.FitInside()
    def RemoveFromQueue(self,event):
        ThisPanel = event.GetEventObject().GetParent()
        for ThisIndex,(Function,Panel,t) in enumerate(self.TheQueue):
            Index = ThisIndex
            if ThisPanel.GetId() == Panel.GetId():
                break
        if Index == 0 and self.Running:
            ThisPanel.SetBackgroundColour('red')
            ThisPanel.Refresh()
            self.Cancel()
            # self.IncomingQueue.put(("Cancel",))
        else:
            self.TheQueue.pop(Index)
            ThisPanel.Destroy()
            self.m_QueueWindow.FitInside()
    def EditMacroInQueue(self,event):
        ThisPanel = event.GetEventObject().GetParent()
        for ThisIndex,(Function,Panel,t) in enumerate(self.TheQueue):
            Index = ThisIndex
            if ThisPanel.GetId() == Panel.GetId():
                break
        if Index == 0 and self.Running:
            pass
        else:
            OriginallyPaused = self.Paused
            self.Paused = True
            MacroLabel = self.TheQueue[Index][2].GetLabel()
            ThisMacroInfo = [[Function['Name'],{key:{"DefaultValue":f"{Parameter}",'Frozen':False} for key,Parameter in Function['Parameters'].items()},Included] for Function,Included in self.TheQueue[Index][0]]
            MyStartMacroDialog = StartMacroDialog(self,MacroLabel,ThisMacroInfo,EdittingMode=True,Index=Index)
            MyStartMacroDialog.ShowModal()
            self.Paused = OriginallyPaused
            thisSettingString = ""
            ThisMacro = self.TheQueue[Index][0]
            for Function, Included in ThisMacro:
                if Included:
                    for key, value in Function['Parameters'].items():
                        thisSettingString+=f"{key} = {value}, "
            thisSettingString = thisSettingString[:-2]
            for child in self.TheQueue[Index][1].GetChildren():
                child.SetToolTip(thisSettingString)
            self.TheQueue[Index][1].GetChildren()[-1].SetLabel(thisSettingString)
            self.Layout()
    def OnStartDrag(self, event):
        if event.Dragging():
            ThisPanel = event.GetEventObject()
            ThisPanel.SetBackgroundColour('Blue')
            ThisPanel.Refresh()
            for ThisIndex,(Function,Panel,t) in enumerate(self.TheQueue):
                Index = ThisIndex
                if ThisPanel.GetId() == Panel.GetId():
                    break
            data = wx.TextDataObject()
            data.SetText(f"{Index}")
            dropSource = wx.DropSource(ThisPanel)
            dropSource.SetData(data)
            result = dropSource.DoDragDrop()
    def AddConnectToQueue(self, event=None):
        Initialize = [['Initialize',{},True]]
        MyStartMacroDialog = StartMacroDialog(self,"Connect",Initialize)
        MyStartMacroDialog.AddToQueue()
        return
    def AddDisconnectToQueue(self, event=None):
        OnClose = [['OnClose',{},True],['Pause',{},True]]
        MyStartMacroDialog = StartMacroDialog(self,"Disconnect",OnClose)
        MyStartMacroDialog.AddToQueue()
        self.AddConnectToQueue()
        return
    def OnRHKSoftware(self, event):
        ThisChooseSoftwareDialog = ChooseSoftwareDialog(self)
        ThisChooseSoftwareDialog.OnRHK()
        return
    def OnCreaTecSoftware(self, event):
        ThisChooseSoftwareDialog = ChooseSoftwareDialog(self)
        ThisChooseSoftwareDialog.OnCreaTec()
        return
    def OnSXMSoftware(self, event):
        ThisChooseSoftwareDialog = ChooseSoftwareDialog(self)
        ThisChooseSoftwareDialog.OnSXM()
        return
    def BasicUseageHelp(self, event):
        HelpMessage = "Not yet written.\n"
        HelpMessage += "Saving for last.\n"
        MyMessage = wx.MessageDialog(self,message=HelpMessage,caption="Help - Basic Usage")
        MyMessage.ShowModal()
        return 
    def MakeAMacroHelp(self, event):
        HelpMessage = "Not yet written.\n"
        HelpMessage += "Saving for last.\n"
        MyMessage = wx.MessageDialog(self,message=HelpMessage,caption="Help - Make a Macro")
        MyMessage.ShowModal()
        return
    def WriteANewFunctionHelp(self, event):
        HelpMessage = "Not yet written.\n"
        HelpMessage += "Saving for last.\n"
        MyMessage = wx.MessageDialog(self,message=HelpMessage,caption="Help - Write a new function")
        MyMessage.ShowModal()
        return
    def OpenSourceFolder(self, event):
        if getattr(sys, 'frozen', False):
            MyMessage = wx.MessageDialog(self,message=f"This will take you to the software source files for the MacroQueue.exe on this computer.  Any changes will be forgotten when the EXE file is remade or updated.\nWould you like to continue?.",caption="Warning - Exe Source Files",style=wx.YES_NO)
            YesOrNo = MyMessage.ShowModal()
            if YesOrNo == wx.ID_NO:
                return
        FolderPath = os.path.realpath("Functions/")
        os.startfile(FolderPath)
        return
    def OpenMacroFile(self, event):
        FolderPath = os.path.realpath("Macros/")
        os.startfile(FolderPath)
        return
class MyPanelDropTarget(wx.DropTarget):
    def __init__(self, window,Parent): 
        wx.DropTarget.__init__(self)
        self.window = window
        self.Parent = Parent
        self.data = wx.TextDataObject()
        self.SetDataObject(self.data)
	
    def OnDragOver(self, x, y, d):
        if not self.GetData():
            return wx.DragNone

        Index = int(self.data.GetText())
        
        ThisPanel = self.Parent.TheQueue[Index][1]
        for ThisIndex,(Function,Panel,t) in enumerate(self.Parent.TheQueue):
            NewIndex = ThisIndex
            MinY = Panel.GetPosition()[1]
            MaxY = MinY + Panel.GetSize()[1]
            if y < (MinY+MaxY)/2:
                break
        if self.Parent.Running and NewIndex == 0:
            NewIndex == 1

        data = wx.TextDataObject()
        data.SetText(f"{NewIndex}")
        self.data = data
        Function = self.Parent.TheQueue.pop(Index)
        self.Parent.TheQueue.insert(NewIndex,Function)
        self.Parent.m_FunctionNameSizer.Remove(Index)
        self.Parent.m_FunctionNameSizer.Insert(NewIndex,ThisPanel, 0, wx.ALL|wx.EXPAND, 5)
        self.Parent.m_QueueWindow.FitInside()
        return d

    def OnData(self, x, y, d):
        if not self.GetData():
            return wx.DragNone
        Index = int(self.data.GetText())
        
        ThisPanel = self.Parent.TheQueue[Index][1]
        # for ThisIndex,(Function,Panel,t) in enumerate(self.Parent.TheQueue):
        #     NewIndex = ThisIndex
        #     MinY = Panel.GetPosition()[1]
        #     MaxY = MinY + Panel.GetSize()[1]
        #     if y < (MinY+MaxY)/2:
        #         break
        # Function = self.Parent.TheQueue.pop(Index)
        # self.Parent.TheQueue.insert(NewIndex,Function)
        # self.Parent.m_FunctionNameSizer.Remove(Index)
        # self.Parent.m_FunctionNameSizer.Insert(NewIndex,ThisPanel, 0, wx.ALL|wx.EXPAND, 5)
        # self.Parent.m_QueueWindow.FitInside()
        Color = wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) if (not self.Parent.Paused or self.Parent.m_PauseAfterButton.GetLabel() == "Start") else wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE)
        ThisPanel.SetBackgroundColour( Color)
        ThisPanel.Refresh()

        return d

def Thread(self,IncomingQueue,OutgoingQueue):
    Functions = {"RHK":RHKFunctions,"CreaTec":CreaTecFunctions,"SXM":SXMFunctions,"General":GeneralFunctions}
    Functions["General"].MacroQueueSelf = self
    while True:
        Message = IncomingQueue.get() # Blocks until there's a message
        if Message[0] == "SoftwareChange":
            Software = Message[1]
            FunctionDict = {Name.replace("_"," "):Function for Name,Function in (getmembers(Functions[Software], isfunction) + getmembers(Functions["General"], isfunction))}
            Functions[Software].OutgoingQueue = OutgoingQueue
            Functions["General"].OutgoingQueue = OutgoingQueue
        if Message[0] == "OnClose":
            if "OnClose" in FunctionDict.keys():
                try:
                    FunctionDict["OnClose"]()
                except:
                    pass
            break
        if Message[0] == 'StartFunction':
            Name = None
            try:
                Macro = Message[1]
                Functions[Software].CurrentMacro = Macro
                for ThisFunction,Included in Macro:
                    Name = ThisFunction['Name']
                    Parameters = ThisFunction['Parameters']
                    if Included:
                        Function = FunctionDict[Name]
                        if not Functions[Software].Cancel:
                            OutgoingQueue.put(("SetStatus",(f"Function: {Name}",1)))
                            Function(**Parameters)
                OutgoingQueue.put(("FunctionFinished",None))
                Functions[Software].Cancel = False
                Functions["General"].Cancel = False


            except Exception as e:
                OutgoingQueue.put(("ExceptionThrown",[e,Name]))



if __name__ == '__main__':
    mp.freeze_support()
    app = wx.App() 
    MyMainFrame = MainFrame()
    MyMainFrame.Show()
    app.MainLoop()


# pyinstaller -F --noconsole --icon=Compass.ico --additional-hooks-dir=. --add-data="Compass.ico;." --add-data="Actions-go-next-icon.bmp;." --add-data="Actions-go-previous-icon.bmp;." --add-data="Actions-go-next-icon2.bmp;." --add-data="Actions-go-previous-icon2.bmp;."  CapNav.py
