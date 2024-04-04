import pyvisa
import numpy as np
from CreaTec import Edit_Memo_Line

CurrentMacro = None
OutgoingQueue = None
Cancel = False
MacroQueueSelf = None

def Connect_To_RF_Generator(RF_Name='USB0::0x03EB::0xAFFF::481-34B6D0608-2368::INSTR'):
    global RFGenerator

    rm = pyvisa.ResourceManager()
    RFGenerator = rm.open_resource(RF_Name)
    RFGenerator.write_termination = '\n'
    RFGenerator.read_termination = '\n'
    pass

def Turn_On_RF_Generator():
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    else:
        try:
            Stat = RFGenerator.query('OUTP:STAT?')
        except:
            Connect_To_RF_Generator()
            RFGenerator=None
    RFGenerator.write(f'OUTP:STAT {1}')
    RFOn = True
    FreqMode = RFGenerator.query(f'SOUR:FREQ:MODE?')
    PowMode = RFGenerator.query(f'SOUR:POW:MODE?')
    print(FreqMode,PowMode)
    if FreqMode =="CW":
        Freq = float(RFGenerator.query(f'SOUR:FREQ?'))
        Edit_Memo_Line("RF_Freq",Freq)
    else:
        Edit_Memo_Line("RF_Freq",FreqMode)
    if PowMode =="CW":
        Power = float(RFGenerator.query(f'SOUR:POW?'))
        Edit_Memo_Line("RF_Power",Power)
    else:
        Edit_Memo_Line("RF_Power",PowMode)



def Turn_Off_RF_Generator():
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'OUTP:STAT {0}')
    RFOn = False
    Edit_Memo_Line("RF_Freq","Off")
    Edit_Memo_Line("RF_Power","Off")



# # Filepath;The path to the excel (.csv) sheet with the power & freq parameters
# def StartRFListSweep(Filepath="C:\\"):
#     global RFGenerator
#     if RFGenerator is None: 
#         Connect_To_RF_Generator()
#     pass

# {"Name":"Amplitude","Units":"mV","Min":10,"Max":7080,"Tooltip":"The amplitude for the RF generator in mV in continuous wave mode"}
def Set_RF_Amplitude(Amplitude=10):
    mVoltageToPower = lambda mV: 20*np.log10(mV / (1000 * (2**0.5 * (50/1000)**(0.5))))
    Set_RF_Power(mVoltageToPower(Amplitude))

# {"Name":"Power","Units":"dBm","Min":-30,"Max":27,"Tooltip":"The amount of power for the RF generator in dBm in continuous wave mode"}
def Set_RF_Power(Power=-10):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:POW {Power}')
    if RFOn:
        Edit_Memo_Line("Power",Power)

# {"Name":"Freq","Units":"Hz","Min":1e5,"Max":30e9,"Tooltip":"The RF frequency in Hz in continuous wave mode"}
def Set_RF_Freq(Freq=1e9):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:FREQ {Freq}')
    if RFOn:
        Edit_Memo_Line("RF Freq",Freq)


def Set_RF_Freq_Mode(Mode=["CW","LIST","SWE"]):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:FREQ:MODE {Mode}')

def Set_RF_Power_Mode(Mode=["CW","LIST","SWE"]):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:POW:MODE {Mode}')
    
    if Mode == "SWE":
        Start = RFGenerator.query(f'SOUR:SWE:STAR?')
        Stop = RFGenerator.query(f'SOUR:SWE:STOP?')
        N_Datapoints = RFGenerator.query(f'SOUR:SWE:POIN?')
        Edit_Memo_Line("SweepStart",f'{Start}')
        Edit_Memo_Line("SweepEnd",f'{Stop}')
        Edit_Memo_Line("SweepSteps",f'{N_Datapoints}')




    

# {"Name":"count","Min":1,"Tooltip":"The number of sweeps to perform after a trigger"}
def Set_RF_LIST_Count(count=1,Infinite = False):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    if Infinite:
        RFGenerator.write(f'SOUR:LIST:COUN INF') #Number of sweeps
    else:
        RFGenerator.write(f'SOUR:LIST:COUN {count}') #Number of sweeps
# {"Name":"count","Min":1,"Tooltip":"The number of sweeps to perform after a trigger"}
def Set_RF_SWE_Count(count=1,Infinite = False):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    if Infinite:
        RFGenerator.write(f'SOUR:SWE:COUN INF') #Number of sweeps
    else:
        RFGenerator.write(f'SOUR:SWE:COUN {count}') #Number of sweeps


# {"Name":"direction","Tooltip":"Up is increasing, down is decreasing."}
def Set_RF_SWE_Direction(direction=["UP","DOWN"]):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:SWE:DIR {direction}')

# {"Name":"points","Min":1,"Tooltip":"The number of points in a sweep."}
def Set_RF_SWE_Points(points=3000):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:SWE:POIN {points}')
    Edit_Memo_Line("SweepSteps",f'{points}')
# {"Name":"dwell","Units":"s","Tooltip":"Dwell time on each point.  RF On time."}
def Set_RF_SWE_Dwell(dwell=0.1):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:SWE:DWEL {dwell}')
# {"Name":"delay","Units":"s","Min":0,"Tooltip":"Delay time before going to next point.  RF Off time."}
def Set_RF_SWE_Del(delay=0):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:SWE:DEL {delay}')

def Set_RF_SWE_Spacing(Spacing=["Linear","Log"]):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    if Spacing == 'Linear':
        RFGenerator.write(f'SOUR:SWE:SPAC LIN')
    elif Spacing == 'Log':
        RFGenerator.write(f'SOUR:SWE:SPAC LOG')

def Set_RF_SWE_Start(Start=1e8):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:SWE:STAR {Start}')
    Edit_Memo_Line("SweepStart",f'{Start}')

def Set_RF_SWE_Stop(Stop=26e9):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:SWE:STOP {Stop}')

def Set_RF_SWE_Blanking(Blanking=False):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    if Blanking:
        RFGenerator.write(f'SOUR:SWE:BLAN 1')
    else:
        RFGenerator.write(f'SOUR:SWE:BLAN 0')
def Set_RF_LIST_Blanking(Blanking=False):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    if Blanking:
        RFGenerator.write(f'SOUR:LIST:BLAN 1')
    else:
        RFGenerator.write(f'SOUR:LIST:BLAN 0')



def Set_RF_Trig_Sour(Trig=["EXT","IMM","KEY","BUS"]):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'TRIG:SOUR {Trig}')
    RFGenerator.write(f'TRIG:TYPE NORM')
    RFGenerator.write(f"INIT:CONT 1")

def Set_RF_Trig_Dir(Dir=["POS","NEG"]):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'TRIG:SLOP {Dir}')

# {"Name":"TrigType","Tooltip":"NORMal trigger = edge initiates/stops sweeps; GATE trigger level starts/stops sweep."}
def Set_RF_Trig_Type(TrigType=["NORM","GATE"]):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'TRIG:TYPE {TrigType}')

def RF_Write(Command="OUTP:STAT 0"):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
        RFGenerator.write(Command)
