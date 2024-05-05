CurrentMacro = None
OutgoingQueue = None
Cancel = False
MacroQueueSelf = None



def Initialize():
    pass


# {"Name":"Parameter","Units":"s","Max":10,"Min":-10,"Tooltip":"Example Tooltip"}
# {"Name":"Parameter2","Units":"m","Max":13,"Tooltip":"Example Tooltip"}
# {"Name":"Parameter3","Units":"m","Min":-12,"Tooltip":"Example Tooltip"}
def Test(Parameter=5,Parameter2=3,Parameter3=-2):
    print(Parameter2)
    pass

def OnClose():
    pass

