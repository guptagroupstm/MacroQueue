from time import sleep

Cancel = False
MacroQueueSelf = None

def test():
    pass

# WaitTime=s;The time to wait in seconds
def Wait(WaitTime=1):
    while WaitTime > 1 and not Cancel:
        WaitTime-=1
        sleep(1)
    if not Cancel:
        sleep(WaitTime)


# {"Name":"SomeBoolean","Tooltip":"A Boolean parameter produces a checkbox"}
# {"Name":"SomeString","Tooltip":"A String parameter produces a textbox"}
# {"Name":"SomeFilePath","Tooltip":"A filepath parameter produces a 'browse' button"}
# {"Name":"SomeChoice","Tooltip":"A Choice parameter produces a dropdown menu"}
def Complex_Function(SomeBoolean=True,SomeString="String",SomeFilePath="C:\\",SomeChoice=['Choice','Combo','3rd','4th']):
    if SomeBoolean:
        print(SomeString, SomeChoice)
        
# Index=This has no impact.  It's solely used to repeat the functions.
def Null(Index=0):
    pass

# Pauses the queue until the resume button is pressed.
def Pause():
    MacroQueueSelf.Pause()

def Print(Number=0):
    print(Number)
    print('')

# # Boolean=Does something if it's true
# # Choice=Make a choice
# def Test(Boolean=True,String="String",Choice=['Choice','Combo','3rd','4th']):
#     a = 'hi'*5.3
#     pass