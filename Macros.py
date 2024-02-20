import queue
from time import sleep

class Macro:
    def __init__(self,Settings):
    #     settingsDialog = SettingsDialog(self.GetMainFrame(),self.Settings,self.SettingsType, Title = 'Settings')
    #     settingsDialog.ShowModal()
        self.Settings = Settings

    def StartMacro(self,OutgoingQueue,IncomingQueue):
        self.OutgoingQueue = OutgoingQueue
        self.IncomingQueue = IncomingQueue
        self.MakeFunctionList()
        for Function,Status,ETC in self.FunctionList:
            try:
                Message = self.IncomingQueue.get(False)
                # if Message[0] == "Pause":
                #     Message = self.IncomingQueue.get()
                #     #Blocks until it gets a message
                if Message[0] == 'Cancel':
                    self.OnCancel()
                    break
                
            except queue.Empty:
                pass

            self.SetStatus(Status,1)
            Function()
            self.OutgoingQueue.put(("UpdateTime",ETC))
        self.OutgoingQueue.put(("FunctionFinished",None))
    def MakeFunctionList(self):
        SomeFunction = lambda: 0
        self.FunctionList = [SomeFunction,"Status",5]
        # self.FunctionList = [(Function,"Status",ETC),(Function1,"Status1",ETC1),...]
    def OnCancel(self):
        pass

    def SetStatus(self,Text,Index):
        self.OutgoingQueue.put(("SetStatus",(Text,Index)))


class RHK_Scan(Macro):
    DefaultSettings = {"Setting1":0,"Setting2":0,"Setting3":0}
    SettingsType = {"Setting1":["Numerical"],"Setting2":["Numerical"],"Setting3":["Numerical"]}
    def __init__(self,Settings):
        super().__init__(Settings)

    def MakeFunctionList(self):
        def Wait():
            print("Hi")
            sleep(5+self.Settings["Setting1"])
        
        # self.FunctionList = [(Function,"Status",ETC),(Function1,"Status1",ETC1),...]
        self.FunctionList = [(Wait,f"Passing{i}",5+self.Settings["Setting1"]) for i in range(5)]

    def OnCancel(self):
        pass

class TestClass:
    hi = 5

if __name__ == "__main__":
    pass