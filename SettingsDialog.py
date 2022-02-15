import wx
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