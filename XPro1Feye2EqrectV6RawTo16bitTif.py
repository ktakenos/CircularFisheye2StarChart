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
# from equilib import equi2equi
import rawpy

root = Tk.Tk()
root.title('Fisheye to Equirectangular Conversion')
#Test View Frame
frame1 = ttk.Frame(root, padding=10)
frame1.grid(row=0, rowspan=2, column=0, sticky=Tk.N+Tk.W+Tk.S)
#Full Circle View Frame
frame2 = ttk.Frame(root, padding=10)
frame2.grid(row=0, column=1, sticky=Tk.N+Tk.W)
#Perspective View Frame
frame3 = ttk.Frame(root, padding=10)
frame3.grid(row=1, column=1, sticky=Tk.N+Tk.W)

# Open File Dialog
FileNameList = []
LabelString1 = Tk.StringVar()
fFileNamesLoaded = 0
idxFileName = 0
currentFileName =""
def LoadFiles():
    global FileNameList, fFileNamesLoaded, idxFileName, currentFileName
    # filetypes = (("Tiffs", "*.tif"),("Tiffs", "*.tiff"),('Jpegs', '*.jpg'),('Jpegs', '*.jpeg'),('All files', '*.*'))
    Rawfiletypes = (("Raw", "*.raf"),('All files', '*.*'))
    file_names = filedialog.askopenfilenames(initialdir='~/Pictures', filetypes=Rawfiletypes)
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
        TestConversion(FileNameList[idxFileName])
LoadButton = ttk.Button(frame1, text='Select X-pro1 Fisheye Image Files', width=25, command=LoadFiles)
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
    TestConversion(currentFileName)
ListBox = ttk.Combobox(frame1, textvariable=ListValue, values=["Select File"], width = 80, justify='left')
ListBox.grid(row=0, column=2, columnspan=4, sticky=Tk.W+Tk.E)
ListBox.bind('<<ComboboxSelected>>', ListSelect)

# #Pole Alignment Option
# fNorthPole=0
# def ToggleNP():
#     global fNorthPole
#     global fFileNamesLoaded, FileNameList
#     if(fFileNamesLoaded==0):
#         return
#     if(fNorthPole==0):
#         fNorthPole=1
#         NPoleButton.configure(bg='blue',  fg='white')
#         NPoleButton.configure(relief = Tk.SUNKEN)
#         UpdatePers()
#     else:
#         fNorthPole=0
#         NPoleButton.configure(bg='SystemButtonFace', fg='black')
#         NPoleButton.configure(relief = Tk.RAISED)
#         UpdatePers()
# NPoleLabel = Tk.Label(frame1, text='Find Porais', width=20)
# NPoleLabel.grid(row=1, column=0, columnspan=2, sticky=Tk.W+Tk.E, ipadx=0)
# NPoleButton = Tk.Button(frame1, text='North Pole Alignment', width=30, command=ToggleNP)
# NPoleButton.grid(row=1, column=2, sticky=Tk.W, ipadx=0)

# #Earth Rotation Options
# StepLabel = Tk.Label(frame1, text='Shutter Interval [s]', width=20)
# StepLabel.grid(row=1, column=3, sticky=Tk.W, ipadx=0, padx=0)
# StepValue = Tk.StringVar()
# StepEntry = Tk.Entry(frame1, textvariable=StepValue, width=5, justify='right')
# StepEntry.insert(0, '15.3')
# StepValue = StepEntry.get()
# StepEntry.grid(row=1, column=4, sticky=Tk.W+Tk.E, ipadx=0, padx=0)
# fEarthRot=0
# def ToggleEarthRot():
#     global fEarthRot
#     global fFileNamesLoaded
#     if(fFileNamesLoaded==0):
#         return
#     if(fEarthRot==0):
#         fEarthRot=1
#         ERotButton.configure(bg='blue',  fg='white')
#         ERotButton.configure(relief = Tk.SUNKEN)
#     else:
#         fEarthRot=0
#         ERotButton.configure(bg='SystemButtonFace', fg='black')
#         ERotButton.configure(relief = Tk.RAISED)
# ERotButton = Tk.Button(frame1, text='Earth Rotation Compensation', width=30, command=ToggleEarthRot)
# ERotButton.grid(row=1, column=5, sticky=Tk.W)

# #Image Averaging
# AveLabel = Tk.Label(frame1, text='Image Averaging Option - Frames for Average:', width=40)
# AveLabel.grid(row=2, column=0, sticky=Tk.W, ipadx=0, padx=0)
# AveValue = Tk.StringVar()
# AveEntry = Tk.Entry(frame1, textvariable=StepValue, width=5, justify='right')
# AveEntry.insert(0, '8')
# AveValue = AveEntry.get()
# AveEntry.grid(row=2, column=1, sticky=Tk.W+Tk.E, ipadx=0, padx=0)

# fAverage=0
# def ToggleAverage():
#     global fAverage
#     global fFileNamesLoaded
#     if(fFileNamesLoaded==0):
#         return
#     if(fAverage==0):
#         fAverage =1
#         Average.configure(bg='blue',  fg='white')
#         Average.configure(relief = Tk.SUNKEN)
#     else:
#         fAverage =0
#         Average.configure(bg='SystemButtonFace', fg='black')
#         Average.configure(relief = Tk.RAISED)
# Average = Tk.Button(frame1, text='Image Averaging Option (Averaged Images will also be saved)', width = 40, command=ToggleAverage)
# Average.grid(row=2, column=2, columnspan=3, sticky=Tk.W+Tk.E)

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
RunBatch.grid(row=3, column=0, columnspan=2, sticky=Tk.W+Tk.E)

#Image Frame
TestViewW=1000
TestViewH=500
imageView = Tk.Frame(frame1, width=TestViewW, height=TestViewH, bg='black')
imageView.grid(row=5, column=0, columnspan=6, sticky=Tk.NW+Tk.SE)
TestView = Tk.Label(imageView)
TestView.grid(row=0, column=0)
imgShow_blank = np.zeros((100, 50, 3), np.uint8)
imgShow = Image.fromarray(cv2.resize(imgShow_blank,(TestViewW,TestViewH)))
imgtk = ImageTk.PhotoImage(image=imgShow)
TestView.imgtk = imgtk
TestView.configure(image=imgtk)

IntEq = imgShow.resize((TestViewW*4 , TestViewH*4))


#Mouse Drag Adjustment
MouseX=0
MouseY=0
def DragMotion(event):
    global MouseX, MouseY, PasteX,PasteY, TestViewW
    global FileNameList, idxFileName, currentFileName
#    DeltaX=event.x - MouseX
    DeltaY=event.y - MouseY
#    print ('Drag X=%s Y=%s' % (DeltaX, DeltaY))
    ShiftR=DeltaY/10
    ShiftTheta=np.pi*2.0*MouseX/float(TestViewW)-np.pi/2.0
    ShiftX=int(ShiftR*np.cos(ShiftTheta))
    ShiftY=int(-1.0*ShiftR*np.sin(ShiftTheta))
    PasteX+=ShiftX
    PasteY+=ShiftY
    TestConversion(currentFileName)
def StartPosition(event):
    global MouseX, MouseY
    MouseX=event.x
    MouseY=event.y
#    print ('X=%s Y=%s' % (event.x, event.y))
def EndPosition(event):
#    print ('X=%s Y=%s' % (event.x, event.y))
    DragMotion(event)
TestView.bind('<ButtonPress-1>', StartPosition)
TestView.bind('<ButtonRelease-1>', EndPosition)

#Text Frame
TextBox = Tk.Text(frame1, height=15, width=80)
TextBox.grid(row=6, rowspan=2, column=0, columnspan=7, stick=Tk.NW+Tk.SE)
TextBox.insert((Tk.END), "[System] Please select Input file (Fisheye image) \n")
TextScroll=Tk.Scrollbar(frame1, orient="vertical",command=TextBox.yview)
TextScroll.grid(row=6, rowspan=2, column=7, stick=(Tk.NS))

# Setting up Parameters
D360 = 4144
#Prepare Black Canvas
imgFC = np.zeros((D360, D360, 3), np.float32)

#Full Circle Image Frame
FCViewW=400
FCimageView = Tk.Frame(frame2, width=FCViewW, height=FCViewW, bg='black')
FCimageView.grid(row=3, column=12)
FCimageLabel = Tk.Label(FCimageView)
FCimageLabel.grid(row=0, column=0)
FCimgShow = Image.fromarray(cv2.resize(imgFC.astype(np.uint8),(FCViewW,FCViewW)))
FCimgtk = ImageTk.PhotoImage(image=FCimgShow)
FCimageLabel.imgtk = FCimgtk
FCimageLabel.configure(image=FCimgtk)

PasteX=430
PasteY=468
# Paste Point Shift
def UpButton_clicked():
    global PasteY, currentFileName
    PasteY-=1
    TestConversion(currentFileName)
UpButton = ttk.Button(frame2, text='Up', width = 10,command=UpButton_clicked)
UpButton.grid(row=2, column=12, sticky=(Tk.EW))
def DownButton_clicked():
    global PasteY, currentFileName
    PasteY+=1
    TestConversion(currentFileName)
DownButton = ttk.Button(frame2, text='Down', width = 10,command=DownButton_clicked)
DownButton.grid(row=4, column=12, sticky=(Tk.EW))
def LeftButton_clicked():
    global PasteX, currentFileName
    PasteX-=1
    TestConversion(currentFileName)
LeftButton = ttk.Button(frame2, text='<', width = 2,command=LeftButton_clicked)
LeftButton.grid(row=3, column=11, sticky=(Tk.NS))
def RightButton_clicked():
    global PasteX, currentFileName
    PasteX+=1
    TestConversion(currentFileName)
RightButton = ttk.Button(frame2, text='>', width = 2,command=RightButton_clicked)
RightButton.grid(row=3, column=13, sticky=(Tk.NS))

#For Perspective View
AnglePitch = 0
AngleYaw = 0
FOV_Deg = 90.0
rot = {
    'roll': 0.,
    'pitch': -AnglePitch,  # rotate vertical
    'yaw': -AngleYaw,  # rotate horizontal
    }
def UpdatePers():
    global rot, FOV_Deg, FCViewW, IntEq, fNorthPole, nBitDepth
    rot = {
        'roll': 0.,
        'pitch': -AnglePitch,  # rotate vertical
        'yaw': -AngleYaw,  # rotate horizontal
        }
    EqImage = np.transpose(IntEq, (2, 0, 1))
    PersImage = equi2pers(EqImage,
                     rots=rot,
                     width=int(FCViewW),
                     height=int(FCViewW/4*3),
                     fov_x=FOV_Deg,
                     # skew=0,
                     # sampling_method="default",
                     mode="bilinear",)
    PersImage = np.transpose(PersImage, (1, 2, 0))
    PersImage_rgb = PersImage 
    # PersImage_rgb = cv2.cvtColor( PersImage, cv2.COLOR_BGR2RGB ) 
    # if(fNorthPole==1):
    #     cv2.circle(PersImage_rgb, (int(FCViewW/2), int(FCViewW/4*3/2)), 8, (255,255,255), 1)
    pers_img = Image.fromarray(PersImage_rgb)
    # if(fNorthPole==1):
    #     cv2.circle(PersImage, (int(FCViewW/2), int(FCViewW/4*3/2)), 8, (255,255,255), 1)
    # pers_img = Image.fromarray(PersImage)
    imgtk = ImageTk.PhotoImage(image=pers_img)
    PersView.imgtk = imgtk
    PersView.configure(image=imgtk)
    TextBox.insert((Tk.END), "[Perspective View] rot Yaw=%4.3f Pitch=%4.3f, " % (AngleYaw, AnglePitch))
    TextBox.insert((Tk.END), "FOV = %d\n" % FOV_Deg)
    TextBox.yview_moveto(1.0)
    TextScroll.update()
PersView = Tk.Label(frame3)
PersView.grid(row=12, column=12)
pers_img = Image.fromarray(cv2.resize(imgFC.astype(np.uint8),(FCViewW,int(FCViewW*3/4))))
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
    global PersMouseX, PersMouseY, AnglePitch, AngleYaw, FCViewW
    DeltaX=event.x - PersMouseX
    DeltaY=event.y - PersMouseY
#    print ('Drag X=%s Y=%s' % (DeltaX, DeltaY))
    AngleYaw += -float(DeltaX)/float(FCViewW)*np.pi/2
    AnglePitch += float(DeltaY)/float(FCViewW)*np.pi/2
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



#Prepare map arrays
xmap = np.load("XproFisheye2Eqrect_X_V5.npy")
ymap = np.load("XproFisheye2Eqrect_Y_V5.npy")

D200=3284
H200=3246
# Create Full Circle Image
def CreateFC(imgIn, imgFC):
    #Enlarge image area to 360 spherical view
    #Crop Circular Image Area
    global D200, H200
    start_row=0
    end_row=H200
    start_col=828
    end_col=start_col+D200
    CropOrg = imgIn[start_row:end_row, start_col:end_col]
    #Place cropped image
    start_row=PasteY
    end_row=start_row+H200
    start_col=PasteX
    end_col=start_col+D200
    imgFC=imgFC*0
    imgFC[start_row:end_row, start_col:end_col]=CropOrg[0:H200, 0:D200]
    return imgFC

nBitDepth = 8
def TestConversion(FileName):
    global imgFC, imgOrg, xmap, ymap, FileNameList, D200, H200, IntEq
    global TestViewW, TestViewH, nBitDepth
    if fFileNamesLoaded == 0:
        return
    # imgRead = cv2.imread(FileName, -1)
    with rawpy.imread(FileName) as raw:
        imgRead = raw.postprocess(output_bps=16)
    if(imgRead.dtype == np.uint16):
        nBitDepth = 16
        Divider=256
    # elif(imgRead.dtype == np.uint8):
    #     nBitDepth = 8
    #     Divider=1
    else:
        TextBox.insert((Tk.END), "[System] Unable to handle the file\n")
        TextBox.yview_moveto(1.0)
        TextScroll.update()
        return
    imgOrg = np.array(imgRead, dtype=np.float32)
    imgFC = CreateFC(imgOrg, imgFC)
    Eqrect = cv2.remap(imgFC, xmap, ymap, cv2.INTER_LINEAR)
    row, col, dep = Eqrect.shape
#    cv2.rectangle(Eqrect, (0,int(row/180*95)), (col, row), (0,0,0), thickness=-1)
    Eqrect8bit=np.array(Eqrect/Divider, dtype=np.uint8)
    # imgShow_rgb = cv2.cvtColor( Eqrect8bit, cv2.COLOR_BGR2RGB ) 
    imgShow_rgb = Eqrect8bit 
    cv2.line(imgShow_rgb,(0,int(row/2)),(int(col),int(row/2)),(0,0,255),20)
    cv2.line(imgShow_rgb,(int(col/2),0),(int(col/2),int(row)),(0,255,0),20)
    cv2.line(imgShow_rgb,(int(col/4),0),(int(col/4),int(row)),(255,0,0),20)
    cv2.line(imgShow_rgb,(int(col/4*3),0),(int(col/4*3),int(row)),(255,0,0),20)
    imgShow = Image.fromarray(cv2.resize(imgShow_rgb,(1000,500)))
    imgtk = ImageTk.PhotoImage(image=imgShow)
    TestView.imgtk = imgtk
    TestView.configure(image=imgtk)
    imgFC8bit=np.array(imgFC/Divider, dtype=np.uint8)
    imgFC_rgb = imgFC8bit 
    # imgFC_rgb = cv2.cvtColor( imgFC8bit, cv2.COLOR_BGR2RGB ) 
    cv2.line(imgFC_rgb,(0,int(D360/2)),(int(D360),int(D360/2)),(255,0,0),20)
    cv2.line(imgFC_rgb,(int(D360/2),0),(int(D360/2),int(D360)),(0,255,0),20)
    cv2.circle(imgFC_rgb,(int(D360/2),int(D360/2)),1578,(0,0,255),20)
    cv2.rectangle(imgFC_rgb,(PasteX,PasteY),(PasteX+D200,PasteY+H200),(255,255,255),10)
    FCimgShow = Image.fromarray(cv2.resize(imgFC_rgb,(400,400)))
    FCimgtk = ImageTk.PhotoImage(image=FCimgShow)
    FCimageLabel.imgtk = FCimgtk
    FCimageLabel.configure(image=FCimgtk)
    TextBox.insert((Tk.END), "[Equirectangular View] Up Left Corner Pixel = (%d, %d)\n" % (PasteX, PasteY))
    TextBox.yview_moveto(1.0)
    TextScroll.update()
    IntEq = np.array(Eqrect8bit, dtype=np.uint8) 
    UpdatePers()

SavedFileNames = []
# Run Batch conversion
def RunConversion():
    global imgFC, imgOrg, xmap, ymap, FileNameList
    global fFileNamesLoaded, fNorthPole, fEarthRot, fRunBatch
    global AnglePitch, AngleYaw
    global fAverage, SavedFileNames, nBitDepth
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
        # imgRead = cv2.imread(i, -1)
        with rawpy.imread(i) as raw:
            imgRead = raw.postprocess(output_bps=16)
        if(imgRead.dtype == np.uint16):
           nBitDepth = 16
           # Divider=float(256*256-1)
        # elif(imgRead.dtype == np.uint8):
        #    nBitDepth = 8
        #    Divider=float(255)
        else:
           nBitDepth = 1
        imgOrg = np.array(imgRead, dtype=np.float32)
        imgFC = CreateFC(imgOrg, imgFC)
        Eqrect = cv2.remap(imgFC, xmap, ymap, cv2.INTER_LINEAR)
        row, col, dep = Eqrect.shape
#        cv2.rectangle(Eqrect, (0,int(row/180*95)), (col, row), (0,0,0), thickness=-1)
        # W=8000
        # H=4000
        imgSave = Eqrect[0:row, 0:col-1]
        # if(fNorthPole == 1):
        #     EqrectFloat=imgSave/Divider
        #     rot = {
        #         'roll': 0.,
        #         'pitch': -(np.pi/2.0 - AnglePitch),  # rotate vertical
        #         'yaw': -(AngleYaw + np.pi),  # rotate horizontal
        #         }
        #     ER_org = np.transpose(EqrectFloat, (2, 0, 1))
        #     NP_ER = equi2equi(ER_org, rot, width=W, height=H, mode="bilinear",)
        #     NP_ER = np.transpose(NP_ER, (1, 2, 0))
        #     if(fEarthRot == 1):
        #         AngleERot = np.pi*2.0/float(24*60*60)*float(StepEntry.get())*float(index)
        #         rot = {
        #             'roll': 0.,
        #             'pitch': np.pi/2.0 - AnglePitch,  # rotate vertical
        #             'yaw': -AngleERot,  # rotate horizontal
        #             }
                
        #         NP_ER = np.transpose(NP_ER, (2, 0, 1))
        #         NPER_ER = equi2equi(NP_ER, rot, width=W, height=H, mode="bilinear",)
        #         NPER_ER = np.transpose(NPER_ER, (1, 2, 0))
        #         imgSave = NPER_ER*Divider
        #     else:
        #         imgSave = NP_ER*Divider
        j=i
        Lower=j.lower()
        if(nBitDepth == 8):
            OutFileName = Lower.replace(".raf", ".ER.jpg")
            imgSave8bit=np.array(cv2.cvtColor(imgSave, cv2.COLOR_BGR2RGB), dtype=np.uint8)
            cv2.imwrite(OutFileName, imgSave8bit)
            TextBox.insert((Tk.END), "[System] (%d/%d) %s is converted\n" % (index, Total, OutFileName))
        elif(nBitDepth == 16):
            TifFileName = Lower.replace(".raf", ".ER.tif")
            imgSave16bit=np.array(cv2.cvtColor(imgSave, cv2.COLOR_BGR2RGB), dtype=np.uint16)
            cv2.imwrite(TifFileName, imgSave16bit)
            TextBox.insert((Tk.END), "[System] (%d/%d) %s is converted\n" % (index, Total, TifFileName))
#        print("%s is converted" % TifFileName)
#        print("%s is converted" % OutFileName)
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
