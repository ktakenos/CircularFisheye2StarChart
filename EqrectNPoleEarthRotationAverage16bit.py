# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 21:36:05 2021

@author: ktake
"""
import cv2
import numpy as np
import tkinter as Tk
#from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
from equilib import equi2pers
from equilib import equi2equi


root = Tk.Tk()
root.title('Equirectangular Image Processing')
#Test View Frame
frame1 = ttk.Frame(root, padding=10)
frame1.grid(row=0, rowspan=2, column=0, sticky=Tk.N+Tk.W+Tk.S)
#Perspective View Frame
frame3 = ttk.Frame(root, padding=10)
frame3.grid(row=0, column=1, sticky=Tk.N+Tk.W)
#North Pole Adjustment
frame4 = ttk.Frame(root, padding=10)
frame4.grid(row=1, column=1, sticky=Tk.N+Tk.W+Tk.E)

global NorthPole20deg
NorthPole20deg = cv2.imread("NorthPole20deg.png")
NPMaskBK = np.copy(NorthPole20deg)

# Open File Dialog
FileNameList = []
LabelString1 = Tk.StringVar()
fFileNamesLoaded = 0
idxFileName = 0
currentFileName =""
def LoadFiles():
    global FileNameList, fFileNamesLoaded, idxFileName, currentFileName
    filetypes = (('Tiffs', '*.tif'),('All files', '*.*'))
    file_names = filedialog.askopenfilenames(initialdir='~/Pictures', filetypes=filetypes)
    if file_names:
        FileNameList = root.splitlist(file_names)
        fFileNamesLoaded = 1
        idxFileName = 0
        currentFileName=FileNameList[idxFileName]
        ListBox.configure(values=FileNameList)
#        ListBox.configure(text=FileNameList[idxFileName])
        ListValue.set(FileNameList[idxFileName])
        ListBox.update()
        Total=len(FileNameList)
        TextBox.insert((Tk.END), "[System] %d Files selected\n" % Total)
        UpdateEqui(FileNameList[idxFileName])
LoadButton = ttk.Button(frame1, text='Click to Select Equirectangular Images', width=30, command=LoadFiles)
LoadButton.grid(row=0, column=0, columnspan=2, sticky=Tk.W+Tk.E)

# choose from FileList
ListValue = Tk.StringVar()
def ListSelect(event):
    global fFileNamesLoaded, FileNameList, idxFileName, currentFileName
    if(fFileNamesLoaded==0):
        return
    currentFileName = ListValue.get()
    TextBox.insert((Tk.END), "[Equirectangular View] %s is Shown\n" % ListValue.get())
    TextBox.yview_moveto(1.0)
    UpdateEqui(currentFileName)
ListBox = ttk.Combobox(frame1, textvariable=ListValue, values=["Select File"], width = 80, justify='left')
ListBox.grid(row=0, column=2, columnspan=4, sticky=Tk.W+Tk.E)
ListBox.bind('<<ComboboxSelected>>', ListSelect)

#Pole Alignment Option
fNorthPole=0
def ToggleNP():
    global fNorthPole
    global fFileNamesLoaded, FileNameList
    if(fFileNamesLoaded==0):
        return
    if(fNorthPole==0):
        fNorthPole=1
        NPoleButton.configure(bg='blue',  fg='white')
        NPoleButton.configure(relief = Tk.SUNKEN)
        UpdatePers()
    else:
        fNorthPole=0
        NPoleButton.configure(bg='SystemButtonFace', fg='black')
        NPoleButton.configure(relief = Tk.RAISED)
        UpdatePers()
NPoleLabel = Tk.Label(frame1, text='Find Porais', width=20)
NPoleLabel.grid(row=1, column=0, columnspan=2, sticky=Tk.W+Tk.E, ipadx=0)
NPoleButton = Tk.Button(frame1, text='North Pole Alignment', width=30, command=ToggleNP)
NPoleButton.grid(row=1, column=2, sticky=Tk.W+Tk.E, ipadx=0)

#Earth Rotation Options
StepLabel = Tk.Label(frame1, text='Shutter Interval [s]', width=20)
StepLabel.grid(row=1, column=3, sticky=Tk.W, ipadx=0, padx=0)
StepValue = Tk.StringVar()
StepEntry = Tk.Entry(frame1, textvariable=StepValue, width=5, justify='right')
StepEntry.insert(0, '15.3')
StepValue = StepEntry.get()
StepEntry.grid(row=1, column=4, sticky=Tk.W+Tk.E, ipadx=0, padx=0)
fEarthRot=0
def ToggleEarthRot():
    global fEarthRot
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    if(fEarthRot==0):
        fEarthRot=1
        ERotButton.configure(bg='blue',  fg='white')
        ERotButton.configure(relief = Tk.SUNKEN)
    else:
        fEarthRot=0
        ERotButton.configure(bg='SystemButtonFace', fg='black')
        ERotButton.configure(relief = Tk.RAISED)
ERotButton = Tk.Button(frame1, text='Earth Rotation Software track', width=30, command=ToggleEarthRot)
ERotButton.grid(row=1, column=5, sticky=Tk.W+Tk.E)

#Image Averaging
AveLabel = Tk.Label(frame1, text='Averaging # of Frames:', width=40)
AveLabel.grid(row=2, column=0, sticky=Tk.W, ipadx=0, padx=0)
AveValue = Tk.StringVar()
AveEntry = Tk.Entry(frame1, textvariable=StepValue, width=5, justify='right')
AveEntry.insert(0, '8')
AveValue = AveEntry.get()
AveEntry.grid(row=2, column=1, sticky=Tk.W+Tk.E, ipadx=0, padx=0)

fAverage=0
def ToggleAverage():
    global fAverage, fLighten
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    if(fAverage==0):
        fAverage =1
        Average.configure(bg='blue',  fg='white')
        Average.configure(relief = Tk.SUNKEN)
    else:
        fAverage =0
        Average.configure(bg='SystemButtonFace', fg='black')
        Average.configure(relief = Tk.RAISED)
        fLighten =1
        ToggleLighten()
Average = Tk.Button(frame1, text='Averaging', width = 20, command=ToggleAverage)
Average.grid(row=2, column=2, sticky=Tk.W+Tk.E)

fLighten=0
def ToggleLighten():
    global fLighten
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    if(fAverage==0):
        return
    if(fLighten==0):
        fLighten =1
        Lighten.configure(bg='blue',  fg='white')
        Lighten.configure(relief = Tk.SUNKEN)
    else:
        fLighten =0
        Lighten.configure(bg='SystemButtonFace', fg='black')
        Lighten.configure(relief = Tk.RAISED)
Lighten = Tk.Button(frame1, text='Lighten', width = 20, command=ToggleLighten)
Lighten.grid(row=2, column=3, columnspan=2, sticky=Tk.W+Tk.E)

fAveRot=0
def ToggleAveRot():
    global fAveRot
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    if(fAveRot==0):
        fAveRot =1
        AveRot.configure(bg='blue',  fg='white')
        AveRot.configure(relief = Tk.SUNKEN)
    else:
        fAveRot =0
        AveRot.configure(bg='SystemButtonFace', fg='black')
        AveRot.configure(relief = Tk.RAISED)
AveRot = Tk.Button(frame1, text='Stationary Earth', width = 30, command=ToggleAveRot)
AveRot.grid(row=2, column=5, sticky=Tk.W+Tk.E)

# Set Output Image Size
SizeLabel = Tk.Label(frame1, text='Output Image Width [pixels]', width=40)
SizeLabel.grid(row=3, column=0, sticky=Tk.W, ipadx=0, padx=0)
SizeValueW = Tk.StringVar()
SizeEntryW = Tk.Entry(frame1, textvariable=SizeValueW, width=5, justify='right')
SizeEntryW.insert(0, '6000')
SizeW = SizeEntryW.get()
SizeH = int(int(SizeW)/2)
SizeEntryW.grid(row=3, column=1, sticky=Tk.W+Tk.E, ipadx=0, padx=0)

# Set Flatten
fFlatten=0
def ToggleFlatten():
    global fFlatten
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    if(fFlatten==0):
        fFlatten =1
        Flatten.configure(bg='blue',  fg='white')
        Flatten.configure(relief = Tk.SUNKEN)
    else:
        fFlatten =0
        Flatten.configure(bg='SystemButtonFace', fg='black')
        Flatten.configure(relief = Tk.RAISED)
Flatten = Tk.Button(frame1, text='Flatten', width = 25, command=ToggleFlatten)
Flatten.grid(row=3, column=2, sticky=Tk.W+Tk.E)


# Run Batch conversion
fRunBatch=0
def RunBatch():
    global fRunBatch
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    if(fRunBatch==0):
        fRunBatch =1
        RunBatch.configure(bg='blue',  fg='white')
        RunBatch.configure(relief = Tk.SUNKEN)
        RunConversion()
    else:
        fRunBatch =0
        RunBatch.configure(bg='SystemButtonFace', fg='black')
        RunBatch.configure(relief = Tk.RAISED)
RunBatch = Tk.Button(frame1, text='Batch Conversion', width = 25, command=RunBatch)
RunBatch.grid(row=3, column=5, sticky=Tk.W+Tk.E)

#Image Frame
EquiViewW=1000
EquiViewH=500
imageView = Tk.Frame(frame1, width=EquiViewW, height=EquiViewH, bg='black')
imageView.grid(row=5, column=0, columnspan=6, sticky=Tk.NW+Tk.SE)
EquiView = Tk.Label(imageView)
EquiView.grid(row=0, column=0, columnspan=2, sticky=Tk.NW+Tk.SE)
imgShow_blank = np.zeros((100, 50, 3), np.uint8)
imgShow = Image.fromarray(cv2.resize(imgShow_blank,(EquiViewW,EquiViewH)))
imgtk = ImageTk.PhotoImage(image=imgShow)
EquiView.imgtk = imgtk
EquiView.configure(image=imgtk)

IntEq = imgShow.resize((EquiViewW*4 , EquiViewH*4))

def UpdateEqui(FileName):
    global FileNameList, IntEq
    global EquiViewW, EquiViewH
    if fFileNamesLoaded == 0:
        return
    IntEq16 = cv2.imread(FileName, -1) #16bit Tiff assumed
    IntEq = np.array(IntEq16/256, dtype=np.uint8)
    imgShow_rgb = cv2.cvtColor( IntEq, cv2.COLOR_BGR2RGB ) 
    imgShow = Image.fromarray(cv2.resize(imgShow_rgb,(1000,500)))
    imgtk = ImageTk.PhotoImage(image=imgShow)
    EquiView.imgtk = imgtk
    EquiView.configure(image=imgtk)
    UpdatePers()

#Text Frame
TextBox = Tk.Text(frame1, height=15, width=80)
TextBox.grid(row=6, rowspan=2, column=0, columnspan=6, stick=Tk.NW+Tk.SE)
TextBox.insert((Tk.END), "[System] Please select Input file (Equirectangular images) \n")
TextScroll=Tk.Scrollbar(frame1, orient="vertical",command=TextBox.yview)
TextScroll.grid(row=6, rowspan=2, column=6, stick=(Tk.NS))


#For Perspective View
AnglePitch = 0
AngleYaw = 0
FOV_Deg = 90.0
rot = {
    'roll': 0.,
    'pitch': -AnglePitch,  # rotate vertical
    'yaw': -AngleYaw,  # rotate horizontal
    }
PersViewW = EquiViewH
Level = 0
def UpdatePers():
    global rot, FOV_Deg, PersViewW, IntEq, fNorthPole, Level
    rot = {
        'roll': 0.,
        'pitch': -AnglePitch,  # rotate vertical
        'yaw': -AngleYaw,  # rotate horizontal
        }
    TempEq = np.zeros_like(IntEq, dtype=np.int16)
    TempEq = IntEq+Level
    TempEq = np.clip(TempEq, 0, 255)
    EqImage = np.transpose(TempEq.astype(np.uint8), (2, 0, 1))
    PersImage = equi2pers(EqImage,
                     rots=rot,
                     width=int(PersViewW),
                     height=int(PersViewW/4*3),
                     fov_x=FOV_Deg,
                     # skew=0,
                     # sampling_method="default",
                     mode="bilinear",)
    PersImage = np.transpose(PersImage, (1, 2, 0))
    PersImage_rgb = cv2.cvtColor( PersImage, cv2.COLOR_BGR2RGB ) 
    if(fNorthPole==1):
        cv2.circle(PersImage_rgb, (int(PersViewW/2), int(PersViewW/4*3/2)), 8, (255,255,255), 1)
        NorthPoleScaled = cv2.resize(NorthPole20deg, (PersViewW, PersViewW))
        NorthPoleCropped = NorthPoleScaled[int(PersViewW/8):int(PersViewW/8*7), 0:PersViewW]
#        PersImage_sum = np.array(PersImage_rgb, dtype=np.uint16)
        PersImage_rgb = np.maximum(PersImage_rgb, NorthPoleCropped)
#        PersImage_rgb = np.clip(PersImage_sum, 0, 255)
#        PersImage_rgb = np.array(PersImage_rgb, dtype=np.uint8)
    pers_img = Image.fromarray(PersImage_rgb)
    imgtk = ImageTk.PhotoImage(image=pers_img)
    PersView.imgtk = imgtk
    PersView.configure(image=imgtk)
    # TextBox.insert((Tk.END), "[Perspective View] rot Yaw=%4.3f Pitch=%4.3f, " % (AngleYaw, AnglePitch))
    # TextBox.insert((Tk.END), "FOV = %d\n" % FOV_Deg)
    # TextBox.yview_moveto(1.0)
    # TextScroll.update()
PersView = Tk.Label(frame3)
PersView.grid(row=12, column=12)
pers_img = Image.fromarray(cv2.resize(imgShow_blank,(PersViewW,int(PersViewW*3/4))))
imgtk = ImageTk.PhotoImage(image=pers_img)
PersView.imgtk = imgtk
PersView.configure(image=imgtk)


#Perspective View Mouse Drag Adjustment
PersMouseX=0
PersMouseY=0
def PersStartPosition(event):
    global PersMouseX, PersMouseY
    PersMouseX=event.x
    PersMouseY=event.y
def PersEndPosition(event):
    global PersMouseX, PersMouseY, AnglePitch, AngleYaw, PersViewW
    DeltaX=event.x - PersMouseX
    DeltaY=event.y - PersMouseY
#    print ('Drag X=%s Y=%s' % (DeltaX, DeltaY))
    AngleYaw += -float(DeltaX)/float(PersViewW)*np.pi/2
    AnglePitch += float(DeltaY)/float(PersViewW)*np.pi/2
    if(AnglePitch>np.pi/2):
        AnglePitch=np.pi/2
    elif(AnglePitch<-np.pi/2):
        AnglePitch=-np.pi/2
    if(AngleYaw>2*np.pi):
        AngleYaw -= np.pi*2
    elif(AngleYaw<-np.pi*2):
        AngleYaw +=np.pi*2
#    print ('rot Yaw=%3.2f Pitch=%3.2f' % (AngleYaw, AnglePitch))
    UpdatePers()
def ChangeFOV(event):
    global FOV_Deg
    if(event.delta<0):
        FOV_Deg+=10.0
        if(FOV_Deg>120):
            FOV_Deg=120.0
    elif(event.delta>0):
        FOV_Deg-=10
        if(FOV_Deg<20.0):
            FOV_Deg=20.0
#    print("FOV = %f" % FOV_Deg)
    UpdatePers()
PersView.bind('<ButtonPress-1>', PersStartPosition)
PersView.bind('<ButtonRelease-1>', PersEndPosition)
PersView.bind('<MouseWheel>', ChangeFOV)

# Perspective North Pole Locater Adustment
def PersUpButton_clicked():
    global AnglePitch
    AnglePitch -= 0.0005*np.pi
    UpdatePers()
PersUpButton = ttk.Button(frame3, text='Up', width = 10,command=PersUpButton_clicked)
PersUpButton.grid(row=11, column=12, sticky=(Tk.EW))
def PersDownButton_clicked():
    global AnglePitch
    AnglePitch += 0.0005*np.pi
    UpdatePers()
PersDownButton = ttk.Button(frame3, text='Down', width = 10,command=PersDownButton_clicked)
PersDownButton.grid(row=13, column=12, sticky=(Tk.EW))
def PersLeftButton_clicked():
    global AngleYaw
    AngleYaw += 0.0005*np.pi
    UpdatePers()
PersLeftButton = ttk.Button(frame3, text='<', width = 2,command=PersLeftButton_clicked)
PersLeftButton.grid(row=12, column=11, sticky=(Tk.NS))
def PersRightButton_clicked():
    global AngleYaw
    AngleYaw -= 0.0005*np.pi
    UpdatePers()
PersRightButton = ttk.Button(frame3, text='>', width = 2,command=PersRightButton_clicked)
PersRightButton.grid(row=12, column=13, sticky=(Tk.NS))




#North Pole Adjustment
NPLabel = Tk.Label(frame4, text='North Pole Adjustment (input date and time when it was captured)')
NPLabel.grid(row=0, column=0, columnspan=3, sticky=Tk.W, ipadx=0, padx=0)
NPDate = Tk.Label(frame4, text='Date[MM.DD]: ')
NPDate.grid(row=1, column=0, sticky=Tk.E, ipadx=0, padx=0)
MMValue = Tk.StringVar()
MMEntry = Tk.Entry(frame4, textvariable=MMValue, width=10, justify='right')
MMEntry.insert(0, '03')
MMValue = MMEntry.get()
MMEntry.grid(row=1, column=1, sticky=Tk.W+Tk.E, ipadx=0, padx=0)
DDValue = Tk.StringVar()
DDEntry = Tk.Entry(frame4, textvariable=DDValue, width=10, justify='right')
DDEntry.insert(0, '21')
DDValue = DDEntry.get()
DDEntry.grid(row=1, column=2, sticky=Tk.W+Tk.E, ipadx=0, padx=0)
DateEnter = Tk.Label(frame4, text='  Type 2digits numbers')
DateEnter.grid(row=1, column=3, sticky=Tk.W, ipadx=0, padx=0)
NPTime = Tk.Label(frame4, text='Time[HH:MM]: ')
NPTime.grid(row=2, column=0, sticky=Tk.E, ipadx=0, padx=0)
hhValue = Tk.StringVar()
hhEntry = Tk.Entry(frame4, textvariable=hhValue, width=10, justify='right')
hhEntry.insert(0, '12')
hhValue = hhEntry.get()
hhEntry.grid(row=2, column=1, sticky=Tk.W+Tk.E, ipadx=0, padx=0)
mmValue = Tk.StringVar()
mmEntry = Tk.Entry(frame4, textvariable=mmValue, width=10, justify='right')
mmEntry.insert(0, '00')
mmValue = mmEntry.get()
mmEntry.grid(row=2, column=2, sticky=Tk.W+Tk.E, ipadx=0, padx=0)
TimeEnter = Tk.Label(frame4, text='  Type 2digits numbers in 24hour format')
TimeEnter.grid(row=2, column=3, sticky=Tk.W, ipadx=0, padx=0)
AngleAdjust = 0
NPAngle = 0.0
def RotateNPMask():
    global fNorthPole, NPMaskBK, NorthPole20deg, AngleAdjust, NPAngle
    if(fNorthPole==0):
        return
    DaysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    DaysTotal = 0
    Month = int(MMEntry.get())
    for i in range(Month-1):
        DaysTotal += DaysInMonth[i]
    DaysTotal += int(DDEntry.get())
    NPAngle = -360.0 * float(DaysTotal - 80)/365.0
    TimeDiff = float(hhEntry.get())+float(mmEntry.get())/60.0 - 12.0
    NPAngle += -360 * TimeDiff/24.0
    NPAngle += AngleAdjust
    # print("Days: %d, Time: %4.2f" % (DaysTotal, TimeDiff))
    #Rotating Mask image
    (IH, IW) = NorthPole20deg.shape[:2]
    M=cv2.getRotationMatrix2D((IW/2,IH/2),-NPAngle,1)
    NorthPole20deg =cv2.warpAffine(NPMaskBK , M, (IW,IH))
    UpdatePers()
RotateNPButton = ttk.Button(frame4, text='Mask Rotate', width = 30 ,command=RotateNPMask)
RotateNPButton.grid(row=3, column=3, sticky=(Tk.W))

def ChangeAngleAdjust(position):
    global AngleAdjust
    AngleAdjust = float(position)
    RotateNPMask()
AdjustLabel = ttk.Label(frame4, text="Adjust a bit")
AdjustLabel.grid(row=4,column=0,sticky=Tk.E)
AdjustScale = Tk.Scale(frame4, orient='horizontal', command=ChangeAngleAdjust, cursor='arrow', \
                      from_=-10, to=10, resolution=0.02)
AdjustScale.set(AngleAdjust)
AdjustScale.grid(row=4,column=1, columnspan=3,sticky='ew')

#Level Adjustment with S-curve (Arctan curve)
def ChangeLevel(vLevel):
    global fFileNamesLoaded, Level
    if(fFileNamesLoaded==0):
        return
    Level = int(vLevel)
    UpdatePers()
LevelLabel = ttk.Label(frame4, text="Level Adjustment")
LevelLabel.grid(row=6,column=0,sticky='e')
LevelScale = Tk.Scale(frame4, orient='horizontal', command=ChangeLevel, cursor='arrow',
                      from_=-100, to=100, resolution=1,length=300)
LevelScale.set(0)
LevelScale.grid(row=6,column=1, columnspan=3,sticky='ew')




fAverage=0
def ToggleAverage():
    global fAverage, fLighten
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    if(fAverage==0):
        fAverage =1
        Average.configure(bg='blue',  fg='white')
        Average.configure(relief = Tk.SUNKEN)
    else:
        fAverage =0
        Average.configure(bg='SystemButtonFace', fg='black')
        Average.configure(relief = Tk.RAISED)
        fLighten =1
        ToggleLighten()
Average = Tk.Button(frame1, text='Averaging', width = 20, command=ToggleAverage)
Average.grid(row=2, column=2, sticky=Tk.W+Tk.E)




SavedFileNames = []
# Run Batch conversion
def RunConversion():
    global FileNameList,fFileNamesLoaded, fNorthPole, fEarthRot, fRunBatch
    global AnglePitch, AngleYaw
    global fAverage, SavedFileNames, SizeW, SizeH, fAveRot, fLighten, fFlatten, NPAngle
    SizeW = SizeEntryW.get()
    SizeH = int(int(SizeW)/2)
    AngleERot = 0
    if (fFileNamesLoaded == 0):
        return
    index=1
    Total=len(FileNameList)
    TextBox.insert((Tk.END), "[System] Batch conversion started\n")
    TextBox.yview_moveto(1.0)
    TextBox.update()
    for i in FileNameList:
        RunBatch.update()
        if(fRunBatch==0):
            TextBox.insert((Tk.END), "[System] Batch conversion terminated\n")
            TextBox.yview_moveto(1.0)
            TextBox.update()
            return
        ImgRead = cv2.imread(i, -1) #16bit tiff assumed
        Eqrect = np.array(ImgRead/65536, dtype=np.float32)
        row, col, dep = Eqrect.shape
        W=int(SizeW)
        H=int(SizeH)
        imgSave = Eqrect[0:row, 0:col-1]
        if(fNorthPole == 1):
            ER_org = Eqrect[0:row, 0:col-1]
            rot = {
                'roll': 0.,
                'pitch': -(np.pi/2.0 - AnglePitch),  # rotate vertical Angle from the apex to the Polaris
                'yaw': -(AngleYaw + np.pi),  # rotate horizontal Facing south
                }
            ER_org = np.transpose(ER_org, (2, 0, 1))
            NP_ER = equi2equi(ER_org, rots=rot, width=W, height=H, mode="bilinear",)
            NP_ER = np.transpose(NP_ER, (1, 2, 0))
            AngleERot = np.pi*2.0/float(24*60*60)*float(StepEntry.get())*float(index)
            if(fEarthRot == 1):
                rot = {
                    'roll': 0.,
                    'pitch': (np.pi/2.0 - AnglePitch),  # rotate vertical
                    'yaw': -AngleERot,  # rotate horizontal
                    }
                
                NP_ER = np.transpose(NP_ER, (2, 0, 1))
                NPER_ER = equi2equi(NP_ER, rots=rot, width=W, height=H, mode="bilinear",)
                NPER_ER = np.transpose(NPER_ER, (1, 2, 0))
                imgSave = NPER_ER
            else:
                rot = {
                    'roll': 0.,
                    'pitch': 0.,  # rotate vertical
                    'yaw': np.pi*2.0/360.0*NPAngle - AngleERot,  # rotate horizontal
                    }
                NP_ER = np.transpose(NP_ER, (2, 0, 1))
                NPER_VE = equi2equi(NP_ER, rots=rot, width=W, height=H, mode="bilinear",)
                NPER_VernalEquinox = np.transpose(NPER_VE, (1, 2, 0))
                imgSave = NPER_VernalEquinox
        j=i
        Lower=j.lower()
        OutFileName = Lower.replace(".tif", ".ER.tif")
        SavedFileNames.append(OutFileName)
        imgSave16bit=np.array(imgSave*65535, dtype=np.uint16)
        cv2.imwrite(OutFileName, imgSave16bit)
        TextBox.insert((Tk.END), "[System] (%d/%d) %s is converted\n" % (index, Total, OutFileName))
        TextBox.yview_moveto(1.0)
        TextBox.update()
        if(fAverage==1):
            idxAve = 0
            idxAveStart = index - int(AveEntry.get())
            if(idxAveStart>=0):
                imgRead = cv2.imread(SavedFileNames[idxAveStart], -1) #16bit tif
                imgSum = np.array(imgRead, dtype=np.float32)
                imgAve = np.array(imgRead, dtype=np.float32)
                idxAve+=1
                while(idxAve<int(AveEntry.get())):
                    imgRead = cv2.imread(SavedFileNames[idxAveStart+idxAve], -1) #16bit tif
                    imgReadFloat = np.array(imgRead, dtype=np.float32)
                    imgSum += imgReadFloat
                    idxAve+=1
                    if(fLighten==1):
                        imgAve = np.maximum(imgAve/65535, imgReadFloat)
                if(fLighten==0):
                    imgAve = np.array((imgSum/float(idxAve*65535)), dtype=np.float32) # 0-1.0
                # SumFileName = OutFileName.replace(".tif", ".SUM.tif")
                # cv2.imwrite(SumFileName, imgSum)
                if(fAveRot==1):
                    rot = {                             # For Polaris to be at the apex
                        'roll': 0.,
                        'pitch': -(np.pi/2.0 - AnglePitch),  # rotate vertical
                        'yaw': 0.,  # rotate horizontal
                        }
                    EQ0 = np.transpose(imgAve, (2, 0, 1))
                    EQ1 = equi2equi(EQ0, rots=rot, width=W, height=H, mode="bilinear",)
                    rot = {                            
                        'roll': 0.,
                        'pitch': 0.,  # rotate vertical
                        'yaw': AngleERot,  # rotate horizontal
                        }
                    EQ0 = equi2equi(EQ1, rots=rot, width=W, height=H, mode="bilinear",)
                    rot = {                             
                        'roll': 0.,
                        'pitch': np.pi/2.0 - AnglePitch,  # rotate vertical
                        'yaw': 0.,  # rotate horizontal
                        }
                    EQ1 = equi2equi(EQ0, rots=rot, width=W, height=H, mode="bilinear",)
                    imgAve = np.transpose(EQ1, (1, 2, 0))
                AveFileName = OutFileName.replace(".tif", ".AVE.Rot.tif")
                imgSaveFloat = np.float32(imgAve)
                if(fFlatten>0):
                    imgAveBlur = cv2.blur(imgAve, (int(W/20),int(W/20)))
                    AverageValue = imgAve.mean()
                    imgAveDiff = np.clip( imgAve - imgAveBlur + AverageValue, 0, 1.0)
                    imgSaveFloat = imgAveDiff
                cv2.imwrite(AveFileName, imgSaveFloat*float(65535))
                TextBox.insert((Tk.END), "[System] Averaged Image %s is saved\n" % AveFileName)
                TextBox.yview_moveto(1.0)
                TextBox.update()
        index+=1
    TextBox.insert((Tk.END), "[System] Batch Conversion Finished\n")
    TextBox.insert((Tk.END), "[System] Please select Input file (Fisheye image) \n")
    TextBox.yview_moveto(1.0)
    fRunBatch =0
    RunBatch.configure(bg='SystemButtonFace', fg='black')
    RunBatch.configure(relief = Tk.RAISED)

root.mainloop()

# sample command for ffmpeg to convert jpgs to mp4
# ffmpeg -framerate 5 -start_number 8112 -i DSCF%04d.ER.jpg -s 4320x2160 -c:v libx264 -r 5 -pix_fmt yuv420p out.mp4
