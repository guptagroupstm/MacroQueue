
from time import sleep

CurrentMacro = None
OutgoingQueue = None
Cancel = False
MacroQueueSelf = None

def Initialize():
    pass


# {"Name":"WaitTime","Units":"s","Tooltip":"The time to wait"}
def Wait(WaitTime=1):
    while WaitTime > 1 and not Cancel:
        WaitTime-=1
        sleep(1)
    if not Cancel:
        sleep(WaitTime)


# Index=This has no impact.  It's solely used to repeat the functions.
def Null(Index=0):
    pass