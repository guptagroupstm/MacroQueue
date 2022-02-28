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
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"MacroQueue", pos = wx.DefaultPosition, size = wx.Size( 800,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( 600,300 ), wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )

		self.m_menubar1 = wx.MenuBar( 0|wx.TRANSPARENT_WINDOW )
		self.m_FileMenu = wx.Menu()
		self.m_SourceMenuItem = wx.MenuItem( self.m_FileMenu, wx.ID_ANY, u"Open Source Folder", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_FileMenu.Append( self.m_SourceMenuItem )
		self.m_SourceMenuItem.Enable( False )

		self.m_ExitMenuItem = wx.MenuItem( self.m_FileMenu, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_FileMenu.Append( self.m_ExitMenuItem )

		self.m_menubar1.Append( self.m_FileMenu, u"File" )

		self.m_MacroMenu = wx.Menu()
		self.m_MakeMacroMenuItem = wx.MenuItem( self.m_MacroMenu, wx.ID_ANY, u"Make New Macro", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_MacroMenu.Append( self.m_MakeMacroMenuItem )

		self.m_OpenMacroMenuItem = wx.MenuItem( self.m_MacroMenu, wx.ID_ANY, u"Open Macro File", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_MacroMenu.Append( self.m_OpenMacroMenuItem )
		self.m_OpenMacroMenuItem.Enable( False )

		self.m_menubar1.Append( self.m_MacroMenu, u"Macro" )

		self.m_SettingsMenu = wx.Menu()
		self.m_SettingsMenuItem = wx.MenuItem( self.m_SettingsMenu, wx.ID_ANY, u"Settings", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_SettingsMenu.Append( self.m_SettingsMenuItem )

		self.m_OpenSettingsMenuItem = wx.MenuItem( self.m_SettingsMenu, wx.ID_ANY, u"Open Settings File", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_SettingsMenu.Append( self.m_OpenSettingsMenuItem )
		self.m_OpenSettingsMenuItem.Enable( False )

		self.m_menubar1.Append( self.m_SettingsMenu, u"Settings" )

		self.SetMenuBar( self.m_menubar1 )

		self.m_statusBar = self.CreateStatusBar( 5, wx.STB_SIZEGRIP, wx.ID_ANY )
		self.m_statusBar.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		self.m_statusBar.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_SCROLLBAR ) )

		self.m_CheckQueueTimer = wx.Timer()
		self.m_CheckQueueTimer.SetOwner( self, wx.ID_ANY )
		self.m_CheckQueueTimer.Start( 500 )

		MainSizer = wx.FlexGridSizer( 0, 3, 0, 0 )
		MainSizer.AddGrowableCol( 2 )
		MainSizer.AddGrowableRow( 0 )
		MainSizer.SetFlexibleDirection( wx.BOTH )
		MainSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_FunctionButtonWindow = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 220,-1 ), wx.HSCROLL|wx.VSCROLL )
		self.m_FunctionButtonWindow.SetScrollRate( 5, 5 )
		MainSizer.Add( self.m_FunctionButtonWindow, 1, wx.EXPAND |wx.ALL, 5 )

		OptionButtonsSizer = wx.FlexGridSizer( 0, 1, 0, 0 )
		OptionButtonsSizer.SetFlexibleDirection( wx.BOTH )
		OptionButtonsSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_PauseASAPButton = wx.Button( self, wx.ID_ANY, u"Pause ASAP", wx.DefaultPosition, wx.Size( 120,40 ), 0 )
		self.m_PauseASAPButton.Hide()

		OptionButtonsSizer.Add( self.m_PauseASAPButton, 0, wx.ALL, 5 )

		self.m_PauseAfterButton = wx.Button( self, wx.ID_ANY, u"Start", wx.DefaultPosition, wx.Size( 120,40 ), 0 )
		OptionButtonsSizer.Add( self.m_PauseAfterButton, 0, wx.ALL, 5 )

		self.m_button1 = wx.Button( self, wx.ID_ANY, u"Clear Queue", wx.DefaultPosition, wx.Size( 120,40 ), 0 )
		OptionButtonsSizer.Add( self.m_button1, 0, wx.ALL, 5 )


		MainSizer.Add( OptionButtonsSizer, 1, wx.ALIGN_BOTTOM|wx.EXPAND, 5 )

		self.m_QueueWindow = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.m_QueueWindow.SetScrollRate( 5, 5 )
		self.m_QueueWindow.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )
		self.m_QueueWindow.SetMinSize( wx.Size( 200,-1 ) )

		MainSizer.Add( self.m_QueueWindow, 1, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( MainSizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.OnClose )
		self.Bind( wx.EVT_IDLE, self.IdleLoop )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_MENU, self.OpenSourceFolder, id = self.m_SourceMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.OnClose, id = self.m_ExitMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.StartMakeNewMacro, id = self.m_MakeMacroMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.OpenMacroFile, id = self.m_OpenMacroMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.OpenSettings, id = self.m_SettingsMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.OpenSettingsFile, id = self.m_OpenSettingsMenuItem.GetId() )
		self.Bind( wx.EVT_TIMER, self.CheckQueue, id=wx.ID_ANY )
		self.m_PauseASAPButton.Bind( wx.EVT_BUTTON, self.PauseASAP )
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


	def StartMakeNewMacro( self, event ):
		event.Skip()

	def OpenMacroFile( self, event ):
		event.Skip()

	def OpenSettings( self, event ):
		event.Skip()

	def OpenSettingsFile( self, event ):
		event.Skip()

	def CheckQueue( self, event ):
		event.Skip()

	def PauseASAP( self, event ):
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
		self.m_FunctionButtonScrolledWindow = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.VSCROLL )
		self.m_FunctionButtonScrolledWindow.SetScrollRate( 0, 5 )
		self.m_FunctionButtonScrolledWindow.SetMinSize( wx.Size( -1,100 ) )

		Windowshbox.Add( self.m_FunctionButtonScrolledWindow, 1, wx.EXPAND |wx.ALL, 5 )

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
		self.m_FunctionButtonScrolledWindow.Bind( wx.EVT_SIZE, self.OnScrolledButtonWindowSize )
		self.applyButton.Bind( wx.EVT_BUTTON, self.Accept )
		self.closeButton.Bind( wx.EVT_BUTTON, self.OnExit )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def OnScrolledButtonWindowSize( self, event ):
		event.Skip()

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

		self.BottomPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.BottomPanel.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTION ) )

		bSizer3 = wx.BoxSizer( wx.VERTICAL )

		self.m_panel7 = wx.Panel( self.BottomPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer8 = wx.FlexGridSizer( 1, 0, 0, 0 )
		fgSizer8.AddGrowableRow( 0 )
		fgSizer8.SetFlexibleDirection( wx.BOTH )
		fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.StartButton = wx.Button( self.m_panel7, wx.ID_ANY, u"Add to Queue", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer8.Add( self.StartButton, 0, wx.ALL, 5 )

		self.CancelButton = wx.Button( self.m_panel7, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer8.Add( self.CancelButton, 0, wx.ALL, 5 )


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
		self.StartButton.Bind( wx.EVT_BUTTON, self.AddToQueue )
		self.CancelButton.Bind( wx.EVT_BUTTON, self.OnCancel )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def AddToQueue( self, event ):
		event.Skip()

	def OnCancel( self, event ):
		event.Skip()


