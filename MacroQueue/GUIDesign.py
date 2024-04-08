# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MyFrame
###########################################################################

class MyFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"MacroQueue", pos = wx.DefaultPosition, size = wx.Size( 840,210 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( 270,135 ), wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )

		self.m_menubar1 = wx.MenuBar( 0|wx.TRANSPARENT_WINDOW )
		self.m_FileMenu = wx.Menu()
		self.m_SourceMenuItem = wx.MenuItem( self.m_FileMenu, wx.ID_ANY, u"Open Source Folder", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_FileMenu.Append( self.m_SourceMenuItem )

		self.m_menubar1.Append( self.m_FileMenu, u"File" )

		self.m_OptionsMenu = wx.Menu()
		self.m_PauseAfterCancel = wx.MenuItem( self.m_OptionsMenu, wx.ID_ANY, u"Pause After Cancel", wx.EmptyString, wx.ITEM_CHECK )
		self.m_OptionsMenu.Append( self.m_PauseAfterCancel )
		self.m_PauseAfterCancel.Check( True )

		self.m_menuItem17 = wx.MenuItem( self.m_OptionsMenu, wx.ID_ANY, u"Reload Functions"+ u"\t" + u"CTRL+R", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_OptionsMenu.Append( self.m_menuItem17 )

		self.m_menubar1.Append( self.m_OptionsMenu, u"Options" )

		self.m_MacroMenu = wx.Menu()
		self.m_MakeMacroMenuItem = wx.MenuItem( self.m_MacroMenu, wx.ID_ANY, u"Make New Macro"+ u"\t" + u"CRTL+M", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_MacroMenu.Append( self.m_MakeMacroMenuItem )

		self.m_OpenMacroMenuItem = wx.MenuItem( self.m_MacroMenu, wx.ID_ANY, u"Open Macro Folder", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_MacroMenu.Append( self.m_OpenMacroMenuItem )

		self.m_menubar1.Append( self.m_MacroMenu, u"Macro" )

		self.m_Connectmenu = wx.Menu()
		self.m_menuItem7 = wx.MenuItem( self.m_Connectmenu, wx.ID_ANY, u"Connect"+ u"\t" + u"CRTL+C", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_Connectmenu.Append( self.m_menuItem7 )

		self.m_menuItem8 = wx.MenuItem( self.m_Connectmenu, wx.ID_ANY, u"Disconnect"+ u"\t" + u"CTRL+D", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_Connectmenu.Append( self.m_menuItem8 )

		self.m_menubar1.Append( self.m_Connectmenu, u"Connect" )

		self.m_SystemMenu = wx.Menu()
		self.m_menubar1.Append( self.m_SystemMenu, u"System" )

		self.m_NotSTMMenu = wx.Menu()
		self.m_menubar1.Append( self.m_NotSTMMenu, u"Included Functions" )

		self.m_menu5 = wx.Menu()
		self.m_menuItem10 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Basic Usage", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.Append( self.m_menuItem10 )

		self.m_menuItem102 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Expand Numerical Parameters", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.Append( self.m_menuItem102 )

		self.m_menuItem11 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Make a Macro", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.Append( self.m_menuItem11 )

		self.m_menuItem12 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Write New Function", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.Append( self.m_menuItem12 )

		self.m_menuItem121 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"Info", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.Append( self.m_menuItem121 )

		self.m_menuItem1211 = wx.MenuItem( self.m_menu5, wx.ID_ANY, u"License", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu5.Append( self.m_menuItem1211 )

		self.m_menubar1.Append( self.m_menu5, u"Help" )

		self.SetMenuBar( self.m_menubar1 )

		self.m_statusBar = self.CreateStatusBar( 5, wx.STB_SIZEGRIP, wx.ID_ANY )
		self.m_statusBar.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		self.m_statusBar.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_SCROLLBAR ) )

		self.m_CheckQueueTimer = wx.Timer()
		self.m_CheckQueueTimer.SetOwner( self, wx.ID_ANY )
		self.m_CheckQueueTimer.Start( 500 )

		MainSizer = wx.FlexGridSizer( 0, 3, 0, 0 )
		MainSizer.AddGrowableCol( 0 )
		MainSizer.AddGrowableRow( 0 )
		MainSizer.SetFlexibleDirection( wx.BOTH )
		MainSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_QueueWindow = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.VSCROLL )
		self.m_QueueWindow.SetScrollRate( 5, 5 )
		self.m_QueueWindow.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )
		self.m_QueueWindow.SetMinSize( wx.Size( 275,-1 ) )

		MainSizer.Add( self.m_QueueWindow, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_FunctionButtonWindow = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 280,-1 ), wx.VSCROLL )
		self.m_FunctionButtonWindow.SetScrollRate( 5, 5 )
		MainSizer.Add( self.m_FunctionButtonWindow, 1, wx.EXPAND |wx.ALL, 5 )

		self.m_panel12 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TAB_TRAVERSAL )
		self.m_panel12.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVEBORDER ) )

		OptionButtonsSizer = wx.FlexGridSizer( 0, 1, 0, 0 )
		OptionButtonsSizer.AddGrowableCol( 0 )
		OptionButtonsSizer.SetFlexibleDirection( wx.BOTH )
		OptionButtonsSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		OptionButtonsSizer.SetMinSize( wx.Size( 140,-1 ) )
		self.m_PauseAfterButton = wx.Button( self.m_panel12, wx.ID_ANY, u"Start", wx.DefaultPosition, wx.Size( 120,30 ), 0 )
		OptionButtonsSizer.Add( self.m_PauseAfterButton, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

		self.m_button1 = wx.Button( self.m_panel12, wx.ID_ANY, u"Clear Queue", wx.DefaultPosition, wx.Size( 120,30 ), 0 )
		OptionButtonsSizer.Add( self.m_button1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		self.m_panel12.SetSizer( OptionButtonsSizer )
		self.m_panel12.Layout()
		OptionButtonsSizer.Fit( self.m_panel12 )
		MainSizer.Add( self.m_panel12, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( MainSizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.OnClose )
		self.Bind( wx.EVT_IDLE, self.IdleLoop )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_MENU, self.OpenSourceFolder, id = self.m_SourceMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.ReloadFunctions, id = self.m_menuItem17.GetId() )
		self.Bind( wx.EVT_MENU, self.StartMakeNewMacro, id = self.m_MakeMacroMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.OpenMacroFile, id = self.m_OpenMacroMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.AddConnectToQueue, id = self.m_menuItem7.GetId() )
		self.Bind( wx.EVT_MENU, self.AddDisconnectToQueue, id = self.m_menuItem8.GetId() )
		self.Bind( wx.EVT_MENU, self.BasicUseageHelp, id = self.m_menuItem10.GetId() )
		self.Bind( wx.EVT_MENU, self.ExpandNumericalParameters, id = self.m_menuItem102.GetId() )
		self.Bind( wx.EVT_MENU, self.MakeAMacroHelp, id = self.m_menuItem11.GetId() )
		self.Bind( wx.EVT_MENU, self.WriteANewFunctionHelp, id = self.m_menuItem12.GetId() )
		self.Bind( wx.EVT_MENU, self.InfoHelp, id = self.m_menuItem121.GetId() )
		self.Bind( wx.EVT_MENU, self.License, id = self.m_menuItem1211.GetId() )
		self.Bind( wx.EVT_TIMER, self.CheckQueue, id=wx.ID_ANY )
		self.m_PauseAfterButton.Bind( wx.EVT_BUTTON, self.Pause )
		self.m_button1.Bind( wx.EVT_BUTTON, self.ClearQueue )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def OnClose( self, event ):
		event.Skip()

	def IdleLoop( self, event ):
		event.Skip()

	def OnSize( self, event ):
		event.Skip()

	def OpenSourceFolder( self, event ):
		event.Skip()

	def ReloadFunctions( self, event ):
		event.Skip()

	def StartMakeNewMacro( self, event ):
		event.Skip()

	def OpenMacroFile( self, event ):
		event.Skip()

	def AddConnectToQueue( self, event ):
		event.Skip()

	def AddDisconnectToQueue( self, event ):
		event.Skip()

	def BasicUseageHelp( self, event ):
		event.Skip()

	def ExpandNumericalParameters( self, event ):
		event.Skip()

	def MakeAMacroHelp( self, event ):
		event.Skip()

	def WriteANewFunctionHelp( self, event ):
		event.Skip()

	def InfoHelp( self, event ):
		event.Skip()

	def License( self, event ):
		event.Skip()

	def CheckQueue( self, event ):
		event.Skip()

	def Pause( self, event ):
		event.Skip()

	def ClearQueue( self, event ):
		event.Skip()


###########################################################################
## Class MacroDialog
###########################################################################

class MacroDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Define The Macro", pos = wx.DefaultPosition, size = wx.Size( 800,600 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.Size( -1,-1 ), wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_SCROLLBAR ) )

		vbox = wx.FlexGridSizer( 0, 1, 0, 0 )
		vbox.AddGrowableCol( 0 )
		vbox.AddGrowableRow( 1 )
		vbox.SetFlexibleDirection( wx.BOTH )
		vbox.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.TopPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.TopPanel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) )

		bSizer31 = wx.BoxSizer( wx.VERTICAL )

		self.m_panel71 = wx.Panel( self.TopPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer81 = wx.FlexGridSizer( 1, 0, 0, 0 )
		fgSizer81.AddGrowableRow( 0 )
		fgSizer81.SetFlexibleDirection( wx.BOTH )
		fgSizer81.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText8 = wx.StaticText( self.m_panel71, wx.ID_ANY, u"Macro Name:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )

		fgSizer81.Add( self.m_staticText8, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_MacroTextCtrl = wx.TextCtrl( self.m_panel71, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer81.Add( self.m_MacroTextCtrl, 0, wx.ALL, 5 )


		self.m_panel71.SetSizer( fgSizer81 )
		self.m_panel71.Layout()
		fgSizer81.Fit( self.m_panel71 )
		bSizer31.Add( self.m_panel71, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		self.TopPanel.SetSizer( bSizer31 )
		self.TopPanel.Layout()
		bSizer31.Fit( self.TopPanel )
		vbox.Add( self.TopPanel, 1, wx.EXPAND |wx.ALL, 5 )

		Windowshbox = wx.FlexGridSizer( 0, 2, 0, 0 )
		Windowshbox.AddGrowableCol( 0 )
		Windowshbox.AddGrowableRow( 0 )
		Windowshbox.SetFlexibleDirection( wx.BOTH )
		Windowshbox.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		Windowshbox.SetMinSize( wx.Size( 750,50 ) )
		self.m_panel14 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_panel14.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNSHADOW ) )
		self.m_panel14.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNSHADOW ) )

		fgSizer13 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer13.AddGrowableCol( 0 )
		fgSizer13.AddGrowableRow( 0 )
		fgSizer13.SetFlexibleDirection( wx.BOTH )
		fgSizer13.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_FunctionButtonNotebook = wx.Notebook( self.m_panel14, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_FunctionButtonNotebook.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNSHADOW ) )
		self.m_FunctionButtonNotebook.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )


		fgSizer13.Add( self.m_FunctionButtonNotebook, 1, wx.EXPAND |wx.ALL, 5 )


		self.m_panel14.SetSizer( fgSizer13 )
		self.m_panel14.Layout()
		fgSizer13.Fit( self.m_panel14 )
		Windowshbox.Add( self.m_panel14, 1, wx.EXPAND |wx.ALL, 5 )

		self.m_FunctionQueueScrolledWindow = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 300,-1 ), wx.HSCROLL|wx.VSCROLL )
		self.m_FunctionQueueScrolledWindow.SetScrollRate( 5, 5 )
		self.m_FunctionQueueScrolledWindow.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )
		self.m_FunctionQueueScrolledWindow.SetMinSize( wx.Size( 300,-1 ) )

		Windowshbox.Add( self.m_FunctionQueueScrolledWindow, 1, wx.EXPAND |wx.ALL, 5 )


		vbox.Add( Windowshbox, 1, wx.EXPAND, 5 )

		self.BottomPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.BottomPanel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )

		bSizer3 = wx.BoxSizer( wx.VERTICAL )

		self.m_panel7 = wx.Panel( self.BottomPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer8 = wx.FlexGridSizer( 1, 0, 0, 0 )
		fgSizer8.AddGrowableRow( 0 )
		fgSizer8.SetFlexibleDirection( wx.BOTH )
		fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.applyButton = wx.Button( self.m_panel7, wx.ID_ANY, u"Next", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer8.Add( self.applyButton, 0, wx.ALL, 5 )

		self.closeButton = wx.Button( self.m_panel7, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer8.Add( self.closeButton, 0, wx.ALL, 5 )


		self.m_panel7.SetSizer( fgSizer8 )
		self.m_panel7.Layout()
		fgSizer8.Fit( self.m_panel7 )
		bSizer3.Add( self.m_panel7, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		self.BottomPanel.SetSizer( bSizer3 )
		self.BottomPanel.Layout()
		bSizer3.Fit( self.BottomPanel )
		vbox.Add( self.BottomPanel, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( vbox )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.applyButton.Bind( wx.EVT_BUTTON, self.Accept )
		self.closeButton.Bind( wx.EVT_BUTTON, self.OnExit )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def Accept( self, event ):
		event.Skip()

	def OnExit( self, event ):
		event.Skip()


###########################################################################
## Class MacroSettingsDialog
###########################################################################

class MacroSettingsDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Choose the Default Parameters", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.Size( 200,250 ), wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )

		vbox = wx.FlexGridSizer( 0, 1, 0, 0 )
		vbox.AddGrowableCol( 0 )
		vbox.AddGrowableRow( 1 )
		vbox.SetFlexibleDirection( wx.BOTH )
		vbox.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.TopPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.TopPanel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )

		bSizer31 = wx.BoxSizer( wx.VERTICAL )

		self.m_panel71 = wx.Panel( self.TopPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer81 = wx.FlexGridSizer( 1, 0, 0, 0 )
		fgSizer81.AddGrowableRow( 0 )
		fgSizer81.SetFlexibleDirection( wx.BOTH )
		fgSizer81.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText8 = wx.StaticText( self.m_panel71, wx.ID_ANY, u"Macro Name:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )

		fgSizer81.Add( self.m_staticText8, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_MacroTextCtrl = wx.TextCtrl( self.m_panel71, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer81.Add( self.m_MacroTextCtrl, 0, wx.ALL, 5 )


		self.m_panel71.SetSizer( fgSizer81 )
		self.m_panel71.Layout()
		fgSizer81.Fit( self.m_panel71 )
		bSizer31.Add( self.m_panel71, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		self.TopPanel.SetSizer( bSizer31 )
		self.TopPanel.Layout()
		bSizer31.Fit( self.TopPanel )
		vbox.Add( self.TopPanel, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.EXPAND, 5 )

		self.m_MacroSettingScrolledWindow = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.VSCROLL )
		self.m_MacroSettingScrolledWindow.SetScrollRate( 5, 5 )
		self.m_MacroSettingScrolledWindow.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )

		vbox.Add( self.m_MacroSettingScrolledWindow, 1, wx.ALL|wx.EXPAND, 5 )

		self.BottomPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.BottomPanel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )

		bSizer3 = wx.BoxSizer( wx.VERTICAL )

		self.m_panel7 = wx.Panel( self.BottomPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer8 = wx.FlexGridSizer( 1, 0, 0, 0 )
		fgSizer8.AddGrowableRow( 0 )
		fgSizer8.SetFlexibleDirection( wx.BOTH )
		fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.applyButton = wx.Button( self.m_panel7, wx.ID_ANY, u"Save Macro", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer8.Add( self.applyButton, 0, wx.ALL, 5 )

		self.backButton = wx.Button( self.m_panel7, wx.ID_ANY, u"Back", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer8.Add( self.backButton, 0, wx.ALL, 5 )


		self.m_panel7.SetSizer( fgSizer8 )
		self.m_panel7.Layout()
		fgSizer8.Fit( self.m_panel7 )
		bSizer3.Add( self.m_panel7, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		self.BottomPanel.SetSizer( bSizer3 )
		self.BottomPanel.Layout()
		bSizer3.Fit( self.BottomPanel )
		vbox.Add( self.BottomPanel, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( vbox )
		self.Layout()
		vbox.Fit( self )

		self.Centre( wx.BOTH )

		# Connect Events
		self.applyButton.Bind( wx.EVT_BUTTON, self.SaveMacro )
		self.backButton.Bind( wx.EVT_BUTTON, self.OnBack )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def SaveMacro( self, event ):
		event.Skip()

	def OnBack( self, event ):
		event.Skip()


###########################################################################
## Class StartMacroDialog
###########################################################################

class StartMacroDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.Size( 200,250 ), wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )

		vbox = wx.FlexGridSizer( 0, 1, 0, 0 )
		vbox.AddGrowableCol( 0 )
		vbox.AddGrowableRow( 0 )
		vbox.SetFlexibleDirection( wx.BOTH )
		vbox.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_MacroSettingScrolledWindow = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.VSCROLL )
		self.m_MacroSettingScrolledWindow.SetScrollRate( 5, 5 )
		self.m_MacroSettingScrolledWindow.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )

		vbox.Add( self.m_MacroSettingScrolledWindow, 1, wx.ALL|wx.EXPAND, 5 )

		self.BottomPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,40 ), wx.TAB_TRAVERSAL )
		self.BottomPanel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) )

		bSizer6 = wx.BoxSizer( wx.VERTICAL )

		self.m_panel12 = wx.Panel( self.BottomPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_panel12.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVECAPTION ) )

		fgSizer8 = wx.FlexGridSizer( 1, 0, 0, 0 )
		fgSizer8.SetFlexibleDirection( wx.BOTH )
		fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.StartButton = wx.Button( self.m_panel12, wx.ID_ANY, u"Add to Queue", wx.DefaultPosition, wx.Size( 110,-1 ), 0 )
		fgSizer8.Add( self.StartButton, 0, wx.ALL, 5 )

		self.CancelButton = wx.Button( self.m_panel12, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer8.Add( self.CancelButton, 0, wx.ALL, 5 )


		self.m_panel12.SetSizer( fgSizer8 )
		self.m_panel12.Layout()
		fgSizer8.Fit( self.m_panel12 )
		bSizer6.Add( self.m_panel12, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		self.BottomPanel.SetSizer( bSizer6 )
		self.BottomPanel.Layout()
		vbox.Add( self.BottomPanel, 1, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( vbox )
		self.Layout()
		vbox.Fit( self )

		self.Centre( wx.BOTH )

		# Connect Events
		self.StartButton.Bind( wx.EVT_BUTTON, self.AddToQueue )
		self.CancelButton.Bind( wx.EVT_BUTTON, self.OnCancel )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def AddToQueue( self, event ):
		event.Skip()

	def OnCancel( self, event ):
		event.Skip()


