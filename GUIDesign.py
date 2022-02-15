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
		self.m_ExitMenuItem = wx.MenuItem( self.m_FileMenu, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_FileMenu.Append( self.m_ExitMenuItem )

		self.m_menubar1.Append( self.m_FileMenu, u"File" )

		self.m_SettingsMenu = wx.Menu()
		self.m_SettingsMenuItem = wx.MenuItem( self.m_SettingsMenu, wx.ID_ANY, u"Settings", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_SettingsMenu.Append( self.m_SettingsMenuItem )

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

		self.m_PauseAfterButton = wx.Button( self, wx.ID_ANY, u"Pause After Function", wx.DefaultPosition, wx.Size( 120,40 ), 0 )
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
		self.Bind( wx.EVT_MENU, self.OnClose, id = self.m_ExitMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.OpenSettings, id = self.m_SettingsMenuItem.GetId() )
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


	def OpenSettings( self, event ):
		event.Skip()

	def CheckQueue( self, event ):
		event.Skip()

	def PauseASAP( self, event ):
		event.Skip()

	def Pause( self, event ):
		event.Skip()

	def ClearQueue( self, event ):
		event.Skip()


