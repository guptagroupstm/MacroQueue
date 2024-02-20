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