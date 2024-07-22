import pyvisa
import numpy as np
from CreaTec import Edit_Memo_Line

CurrentMacro = None
OutgoingQueue = None
Cancel = False
MacroQueueSelf = None
RFOn=False
RFGenerator=None
def Connect_To_RF_Generator(RF_Name='USB0::0x03EB::0xAFFF::481-34B6D0608-2368::INSTR'):
    global RFGenerator

    rm = pyvisa.ResourceManager()
    RFGenerator = rm.open_resource(RF_Name)
    RFGenerator.write_termination = '\n'
    RFGenerator.read_termination = '\n'
    pass

def Turn_On_RF_Generator():
    global RFGenerator, RFOn, OutgoingQueue
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    else:
        try:
            Stat = RFGenerator.query('OUTP:STAT?')
        except:
            Connect_To_RF_Generator()

    RFGenerator.write(f'OUTP:STAT {1}')
    RFOn = True
    try:
        FreqMode = RFGenerator.query(f'SOUR:FREQ:MODE?')
        PowMode = RFGenerator.query(f'SOUR:POW:MODE?')
        if FreqMode =="FIX":
            Freq = RFGenerator.query(f'SOUR:FREQ?')
            Edit_Memo_Line("RF_Freq",Freq)
        else:
            Edit_Memo_Line("RF_Freq","Not_CW")
        if PowMode =="FIX":
            Power = RFGenerator.query(f'SOUR:POW?')
            Edit_Memo_Line("RF_Power",Power)
        else:
            Edit_Memo_Line("RF_Power","Not_CW")
    except:
        print("Umm why tho")



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
        Edit_Memo_Line("RF_Power",Power)

# {"Name":"Freq","Units":"Hz","Min":1e5,"Max":30e9,"Tooltip":"The RF frequency in Hz in continuous wave mode"}
def Set_RF_Freq(Freq=1e9):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:FREQ {Freq}')
    if RFOn:
        Edit_Memo_Line("RF_Freq",Freq)


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
        Edit_Memo_Line("SweepStart",f'{float(Start)}')
        Edit_Memo_Line("SweepEnd",f'{float(Stop)}')
        Edit_Memo_Line("SweepSteps",f'{float(N_Datapoints)}')




    

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
    Edit_Memo_Line("SweepSteps",f'{float(points)}')
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

def Set_RF_PowerSWE_Start(Start=1e8):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:POW:STAR {Start}')
    Edit_Memo_Line("SweepStart",f'{float(Start)}')

def Set_RF_PowerSWE_Stop(Stop=26e9):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:POW:STOP {Stop}')
    Edit_Memo_Line("SweepEnd",f'{float(Stop)}')

def Set_RF_FREQSWE_Start(Start=1e8):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:FREQ:STAR {Start}')
    Edit_Memo_Line("SweepStart",f'{float(Start)}')

def Set_RF_FREQSWE_Stop(Stop=26e9):
    global RFGenerator, RFOn
    if RFGenerator is None: 
        Connect_To_RF_Generator()
    RFGenerator.write(f'SOUR:FREQ:STOP {Stop}')
    Edit_Memo_Line("SweepEnd",f'{float(Stop)}')

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

if __name__ == "__main__":
    Connect_To_RF_Generator()
    # Turn_On_RF_Generator()
    # Turn_Off_RF_Generator()
    # Set_RF_Freq_Mode(Mode="SWE")
    # freqmode = RFGenerator.query(f'SOUR:FREQ:MODE?')
    # print(freqmode )
    # Set_RF_Trig_Type("NORM")
    # Set_RF_Trig_Sour("EXT")
    # FREQSTART = RFGenerator.query(f'TRIG:SOUR?')
    # print(FREQSTART)