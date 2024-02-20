import unittest
import os
from MacroQueue import *


class STMThread_test(unittest.TestCase):
    def test_thread(self):
        mp.freeze_support()
        self.app = wx.App() 
        self.MyMainFrame = MainFrame()
        self.MyMainFrame.Show()
        TestMacro = [[{'Name':"test","Parameters":[]},False]]
        self.MyMainFrame.IncomingQueue.put(("StartFunction",TestMacro))
        Message = self.MyMainFrame.OutgoingQueue.get()
        self.assertEqual(f"{Message}","('FunctionFinished', None)")
        self.MyMainFrame.OnClose()

        pass

if __name__ == '__main__':
    unittest.main()