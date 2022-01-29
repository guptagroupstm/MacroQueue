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
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1150,800 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )

		self.m_menubar1 = wx.MenuBar( 0 )
		self.m_FileMenu = wx.Menu()
		self.m_SettingsMenuItem = wx.MenuItem( self.m_FileMenu, wx.ID_ANY, u"Settings", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_FileMenu.Append( self.m_SettingsMenuItem )

		self.m_ExitMenuItem = wx.MenuItem( self.m_FileMenu, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_FileMenu.Append( self.m_ExitMenuItem )

		self.m_menubar1.Append( self.m_FileMenu, u"File" )

		self.SetMenuBar( self.m_menubar1 )

		self.m_statusBar = self.CreateStatusBar( 5, wx.STB_SIZEGRIP, wx.ID_ANY )
		self.m_statusBar.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		self.m_statusBar.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_SCROLLBAR ) )

		self.m_CheckQueueTimer = wx.Timer()
		self.m_CheckQueueTimer.SetOwner( self, wx.ID_ANY )
		self.m_CheckQueueTimer.Start( 500 )


		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.OnClose )
		self.Bind( wx.EVT_IDLE, self.IdleLoop )
		self.Bind( wx.EVT_MENU, self.OpenSettings, id = self.m_SettingsMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.OnClose, id = self.m_ExitMenuItem.GetId() )
		self.Bind( wx.EVT_TIMER, self.CheckQueue, id=wx.ID_ANY )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def OnClose( self, event ):
		event.Skip()

	def IdleLoop( self, event ):
		event.Skip()

	def OpenSettings( self, event ):
		event.Skip()


	def CheckQueue( self, event ):
		event.Skip()


