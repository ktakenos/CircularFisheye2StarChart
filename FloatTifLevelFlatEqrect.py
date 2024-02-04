# -*- coding: utf-8 -*-
"""
Created on Sat Dec 11 21:36:20 2021

@author: ktake
"""
import cv2
import numpy as np
import tkinter as Tk
#from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
#import time
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#from skimage import io           #scikit image version 0.13.1
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 9

fig = plt.Figure()

root = Tk.Tk()
root.title('Float Tif Viewer + Flattener for Equirectangular format')
#Image View Frame
frame1 = ttk.Frame(root, padding=10)
frame1.grid(row=0, rowspan=12, column=0, sticky=Tk.N+Tk.W+Tk.S)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().grid(row=0,column=4, columnspan=3)

# Open File Dialog
FileNameList = []
LabelString1 = Tk.StringVar()
fFileNamesLoaded = 0
idxFileName = 0
currentFileName =""
def LoadFiles():
    global FileNameList, fFileNamesLoaded, idxFileName, currentFileName
    filetypes = (("Tiffs", "*.tif"),("Tiffs", "*.tiff"),('All files', '*.*'))
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
        LoadTif(FileNameList[idxFileName])
LoadButton = ttk.Button(frame1, text='Select Float Tif Image Files', width=25, command=LoadFiles)
LoadButton.grid(row=0, column=0, columnspan=2, sticky=Tk.W+Tk.E)

# choose from FileList
ListValue = Tk.StringVar()
def ListSelect(event):
    global fFileNamesLoaded, FileNameList, idxFileName, currentFileName
    if(fFileNamesLoaded==0):
        return
    currentFileName = ListValue.get()
    LoadTif(currentFileName)
ListBox = ttk.Combobox(frame1, textvariable=ListValue, values=["Select File"], width = 80, justify='left')
ListBox.grid(row=0, column=2, columnspan=4, sticky=Tk.W+Tk.E)
ListBox.bind('<<ComboboxSelected>>', ListSelect)



LUT16bit = np.zeros((256*256), dtype = np.uint16)
Center=float(0.3)
Slope0=float(1.0)
Slope1=float(1.0)

#Level Adjustment with S-curve (Arctan curve)
def ChangeSlope0(vSlope):
    global Center, Slope0, imgShow_rgb
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    Slope0 = float(vSlope)
    # start = time.time()
    UpdateLUT()
    # end = time.time()
    # print("Indexing time: ", end-start)
Slope0Label = ttk.Label(root, text="Linear Slope", width=10)
Slope0Label.grid(row=3,column=4,sticky='ew')
Slope0Scale = Tk.Scale(root, orient='horizontal', command=ChangeSlope0, cursor='arrow',
                      from_=0, to=2, resolution=0.05,length=100)
Slope0Scale.set(Slope0)
Slope0Scale.grid(row=3,column=5, columnspan=3,sticky='ew')

def ChangeSlope1(vSlope):
    global Center, Slope1, imgShow_rgb
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    Slope1 = 1.0 * float(vSlope) ** 2.0
    UpdateLUT()
Slope1Label = ttk.Label(root, text="Contrast Slope", width=10)
Slope1Label.grid(row=4,column=4,sticky='ew')
Slope1Scale = Tk.Scale(root, orient='horizontal', command=ChangeSlope1, cursor='arrow',
                      from_=1, to=30, resolution=0.5,length=100)
Slope1Scale.set(Slope1)
Slope1Scale.grid(row=4,column=5, columnspan=3,sticky='ew')

def ChangeCenter(vCenter):
    global Center, Slope
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    Center = float(vCenter)
    UpdateLUT()
CenterLabel = ttk.Label(root, text="Center", width=10)
CenterLabel.grid(row=5,column=4,sticky='ew')
CenterScale = Tk.Scale(root, orient='horizontal', command=ChangeCenter, cursor='arrow',
                      from_=0, to=0.5, resolution=0.002,length=100)
CenterScale.set(Center)
CenterScale.grid(row=5,column=5, columnspan=3,sticky='ew')


MinLUT=np.arctan(Slope1*(0-Center))
MaxLUT=np.arctan(Slope1*(1.0-Center))+Slope0
# for i in range(256*256):
#     LUT16bit[i] = int(65535*(np.arctan(float(Slope1)*(float(i)/65535.0-float(Center)))+float(i)/float(65535)*float(Slope0)-MinLUT)/(MaxLUT-MinLUT))
def UpdateLUT():
    global LUT16bit, Center, Slope0, Slope1, MinLUT, MaxLUT
    MinLUT=np.arctan(float(Slope1)*(0-float(Center)))
    MaxLUT=np.arctan(float(Slope1)*(1.0-float(Center)))+float(Slope0)
    for i in range(256*256):
        LUT16bit[i] = int(65535*(np.arctan(float(Slope1)*(float(i)/65535.0-float(Center)))+float(i)/float(65535)*float(Slope0)-MinLUT)/(MaxLUT-MinLUT))
UpdateLUT()

def ApplyLUT():
    global LUT16bit, Center, Slope, imgShow, imgShow_rgb, imgMask, vGamma, fFlatten, TifViewH, TifViewW
    global fBilat, BilatDist, fThres, ThresLevel, f180Mask, fMaskReplace
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    global Level, LevelR, LevelG, LevelB
    global imgShow, imgShowBk
    imgShow = np.copy(imgShowBk)
    if(fFlatten>0):
        imgShowH, imgShowW, dep = imgShow.shape
        ShowBlurDiameter = int(BlurDiameter*imgShowW/TifViewW)
        if(ShowBlurDiameter%2==0):
            ShowBlurDiameter+=1
        imgShowBlur = cv2.GaussianBlur(imgShow, (ShowBlurDiameter, ShowBlurDiameter), 0)
        AverageValue = imgShow.mean()
        imgShowDiff = np.clip( imgShow - imgShowBlur + AverageValue, 0, 1.0)
        imgShow = imgShowDiff
        if(f180Mask==1):
            Mask180 = np.zeros((180, 1, 3), np.float32)
            for i in range(180):
                Mask180[i]=1.0
                if(i>85):
                    if(i<105):
                        Mask180[i]=1.0-(float(i)-85)*0.05
                    else:
                        Mask180[i]=0
            MaskEr = cv2.resize(Mask180, (imgShowW, imgShowH))
            imgShow = imgShow*MaskEr
    imgShow[:,:,0] = np.clip((imgShow[:,:,0] + LevelB),0,1.0)
    imgShow[:,:,1] = np.clip((imgShow[:,:,1] + LevelG),0,1.0)
    imgShow[:,:,2] = np.clip((imgShow[:,:,2] + LevelR),0,1.0)
    imgShow = np.clip((imgShow + Level),0,1.0)
    if(fEqr>0):
        if(f180Mask==1):
            if(fMaskReplace==1):
                MaskErInv = 1.0 - MaskEr
                MaskEr = MaskErInv*(cv2.resize(imgMask, (imgShowW, imgShowH)))
                imgShow = np.maximum(imgShow, MaskEr)
    imgShow16bit = np.uint16(imgShow*65535)
    imgShowLUT = LUT16bit[imgShow16bit]
    imgShow_bgr = np.uint8(imgShowLUT/256)
    imgShow_rgb = cv2.cvtColor( imgShow_bgr, cv2.COLOR_BGR2RGB ) 
    imgShowTk = Image.fromarray(imgShow_rgb)
    imgtk = ImageTk.PhotoImage(image=imgShowTk)
    TifView.imgtk = imgtk
    TifView.configure(image=imgtk)
ApplyButton = Tk.Button(root, text='Apply Look Up Table', width=10, command=ApplyLUT)
ApplyButton.grid(row=2, column=4, columnspan=3, sticky=Tk.W+Tk.E)


Level=0
# def ChangeLevel(vLevel):
#     global Level, LevelR, LevelG, LevelB
#     global fFileNamesLoaded
#     if(fFileNamesLoaded==0):
#         return
#     global imgShow, imgShowBk
#     imgShow[:,:,0] = np.clip((imgShowBk[:,:,0] + LevelB),0,1.0)
#     imgShow[:,:,1] = np.clip((imgShowBk[:,:,1] + LevelG),0,1.0)
#     imgShow[:,:,2] = np.clip((imgShowBk[:,:,2] + LevelR),0,1.0)
#     imgShow = np.clip((imgShow + Level),0,1.0)

def ChangeGray(vLevel):
    global Level, LevelR, LevelG, LevelB
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    Level = float(vLevel)
LevelLabel = ttk.Label(root, text="Gray Level", width=10)
LevelLabel.grid(row=6,column=4,sticky='ew')
LevelScale = Tk.Scale(root, orient='horizontal', command=ChangeGray, cursor='arrow',
                      from_=-0.1, to=0.3, resolution=0.0001,length=100)
LevelScale.set(0)
LevelScale.grid(row=6,column=5, columnspan=3,sticky='ew')

LevelR=0
def ChangeLevelR(vLevel):
    global Level, LevelR
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    LevelR = float(vLevel)
#    ChangeLevel(Level)
LevelRLabel = ttk.Label(root, text="Red Level", width=10)
LevelRLabel.grid(row=7,column=4,sticky='ew')
LevelRScale = Tk.Scale(root, orient='horizontal', command=ChangeLevelR, cursor='arrow',
                      from_=0, to=0.3, resolution=0.0001,length=100)
LevelRScale.set(0)
LevelRScale.grid(row=7,column=5, columnspan=3,sticky='ew')

LevelG=0
def ChangeLevelG(vLevel):
    global LevelG, Level
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    LevelG = float(vLevel)
#    ChangeLevel(Level)
LevelGLabel = ttk.Label(root, text="Green Level", width=10)
LevelGLabel.grid(row=8,column=4,sticky='ew')
LevelGScale = Tk.Scale(root, orient='horizontal', command=ChangeLevelG, cursor='arrow',
                      from_=0, to=0.3, resolution=0.0001,length=100)
LevelGScale.set(0)
LevelGScale.grid(row=8,column=5, columnspan=3,sticky='ew')

LevelB=0
def ChangeLevelB(vLevel):
    global LevelB, Level
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    LevelB = float(vLevel)
#    ChangeLevel(Level)
LevelBLabel = ttk.Label(root, text="Blue Level", width=10)
LevelBLabel.grid(row=9,column=4,sticky='ew')
LevelBScale = Tk.Scale(root, orient='horizontal', command=ChangeLevelB, cursor='arrow',
                      from_=0, to=0.3, resolution=0.0001,length=100)
LevelBScale.set(0)
LevelBScale.grid(row=9,column=5, columnspan=3,sticky='ew')

# Set Flatten
fFlatten=0
def ToggleFlatten():
    global fFlatten, imgShow, imgShowBk, Level
    global fFileNamesLoaded
    if(fFlatten==0):
        fFlatten =1
        Flatten.configure(bg='blue',  fg='white')
        Flatten.configure(relief = Tk.SUNKEN)
        ApplyLUT()
    else:
        fFlatten =0
        Flatten.configure(bg='SystemButtonFace', fg='black')
        Flatten.configure(relief = Tk.RAISED)
        imgShow = np.float32(imgShowBk)
        ApplyLUT()
Flatten = Tk.Button(root, text='Flatten', width = 10, command=ToggleFlatten)
Flatten.grid(row=10,column=4,sticky="ew")

BlurDiameter = 100
def ChangeBlur(value):
    global BlurDiameter
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    BlurDiameter = int(value)
#    ChangeLevel(Level)
BlurScale = Tk.Scale(root, orient='horizontal', command=ChangeBlur, cursor='arrow',
                      from_=10, to=800, resolution=10,length=100)
BlurScale.set(BlurDiameter)
BlurScale.grid(row=10,column=5, columnspan=3,sticky='ew')

# 360 image?
fEqr=0
def ToggleEqr():
    global fEqr, imgShow, imgShowBk, Level
    global fFileNamesLoaded
    if(fEqr==0):
        fEqr =1
        Eqr.configure(bg='blue',  fg='white')
        Eqr.configure(relief = Tk.SUNKEN)
    else:
        fEqr =0
        Eqr.configure(bg='SystemButtonFace', fg='black')
        Eqr.configure(relief = Tk.RAISED)
Eqr = Tk.Button(root, text='Equirectangular', width = 5, command=ToggleEqr)
Eqr.grid(row=11,column=4,sticky="ew")

f180Mask=0
def Toggle180Mask():
    global f180Mask, imgShow, imgShowBk, Level
    global fFileNamesLoaded
    if(f180Mask==0):
        f180Mask =1
        Mask180.configure(bg='blue',  fg='white')
        Mask180.configure(relief = Tk.SUNKEN)
        ApplyLUT()
    else:
        f180Mask =0
        Mask180.configure(bg='SystemButtonFace', fg='black')
        Mask180.configure(relief = Tk.RAISED)
        ApplyLUT()
Mask180 = Tk.Button(root, text='180 Degree Mask', width = 5, command=Toggle180Mask)
Mask180.grid(row=11,column=5,sticky="ew")

global imgMask
fMaskReplace=0
def ReplaceMask():
    global f180Mask, fMaskReplace, imgShow, imgShowBk, imgMask
    global fFileNamesLoaded
    if(f180Mask==0):
        return
    else:
        if(fMaskReplace==0):
            filetypes = (("Jpeg", "*.jpg"),("PNG", "*.png"),('All files', '*.*'))
            Maskfile_name = filedialog.askopenfilename(initialdir='~/Pictures', filetypes=filetypes)
            if(len(Maskfile_name)>0):
                fMaskReplace=1
                imgRead = cv2.imread(Maskfile_name)
                imgMask = imgRead/255.0
#                imgMask = np.float32(imgFloatTemp)
                fMaskReplace =1
                MaskReplace.configure(bg='blue',  fg='white')
                MaskReplace.configure(relief = Tk.SUNKEN)
                ApplyLUT()
        else:
            fMaskReplace =0
            MaskReplace.configure(bg='SystemButtonFace', fg='black')
            MaskReplace.configure(relief = Tk.RAISED)
            ApplyLUT()
MaskReplace = Tk.Button(root, text='Replace Mask', width = 5, command=ReplaceMask)
MaskReplace.grid(row=11,column=6,sticky="ew")


# # Set Bilateral
# fBilat=0
# def ToggleBilat():
#     global fBilat, imgShow, imgShowBk, Level
#     global fFileNamesLoaded
#     if(fBilat==0):
#         fBilat =1
#         Bilat.configure(bg='blue',  fg='white')
#         Bilat.configure(relief = Tk.SUNKEN)
#         ApplyLUT()
#     else:
#         fBilat =0
#         Bilat.configure(bg='SystemButtonFace', fg='black')
#         Bilat.configure(relief = Tk.RAISED)
#         imgShow = np.copy(imgShowBk)
#         ApplyLUT()
# Bilat = Tk.Button(root, text='Bilateral', width = 25, command=ToggleBilat)
# Bilat.grid(row=11,column=4,sticky="ew")

# BilatDist = 10
# def ChangeBilat(value):
#     global BilatDist
#     global fFileNamesLoaded
#     if(fFileNamesLoaded==0):
#         return
#     BilatDist = int(value)
# #    ChangeLevel(Level)
# BilatScale = Tk.Scale(root, orient='horizontal', command=ChangeBilat, cursor='arrow',
#                       from_=5, to=500, resolution=5,length=200)
# BilatScale.set(BilatDist)
# BilatScale.grid(row=11,column=5,sticky='ew')

# # Set Threshold
# fThres=0
# def ToggleThres():
#     global fThres, imgShow, imgShowBk, Level
#     global fFileNamesLoaded
#     if(fThres==0):
#         fThres =1
#         Thres.configure(bg='blue',  fg='white')
#         Thres.configure(relief = Tk.SUNKEN)
#         ApplyLUT()
#     else:
#         fThres =0
#         Thres.configure(bg='SystemButtonFace', fg='black')
#         Thres.configure(relief = Tk.RAISED)
#         imgShow = np.copy(imgShowBk)
#         ApplyLUT()
# Thres = Tk.Button(root, text='Threshold', width = 25, command=ToggleThres)
# Thres.grid(row=12,column=4,sticky="ew")

# ThresLevel = 0.2
# def ChangeThres(value):
#     global ThresLevel
#     global fFileNamesLoaded
#     if(fFileNamesLoaded==0):
#         return
#     ThresLevel = float(value)
# #    ChangeLevel(Level)
# ThresScale = Tk.Scale(root, orient='horizontal', command=ChangeThres, cursor='arrow',
#                       from_=0, to=1.0, resolution=0.01,length=200)
# ThresScale.set(ThresLevel)
# ThresScale.grid(row=12,column=5,sticky='ew')


#Save LUT converted Image
def SaveImage():
    global fFileNamesLoaded, FileNameList, idxFileName, currentFileName
    global LUT16bit, Level, LevelR, LevelG, LevelB, BlurDiameter, TifViewW
    global fEqr, fMaskReplace, imgMask, imgRead
    if fFileNamesLoaded == 0:
        return
    imgRead = cv2.imread(currentFileName, -1) #unchanged
    # Binning(4)
    print("File %s loaded" % currentFileName)
    if(imgRead.dtype == np.float32):
        MaxV=np.amax(imgRead)
        imgFloat = np.float32(imgRead/float(MaxV))
    elif(imgRead.dtype == np.uint16):
        imgFloat = np.float32(imgRead/65535.0)
    elif(imgRead.dtype == np.uint8):
        imgFloat = np.float32(imgRead/255.0)
    else:
        return
    imgTemp = np.copy(imgFloat)
    if(fFlatten>0):
        print("Flattening Process Started")
        imgH, imgW, dep = imgTemp.shape
        SaveBlurDiameter = int(BlurDiameter*imgW/TifViewW)
        if(SaveBlurDiameter%2==0):
            SaveBlurDiameter+=1
        imgTempBlur=np.array(imgTemp)
        if(fEqr>0):
            print("Blur Image Array to be Enlarged")
            imgEnlarge = np.array(cv2.resize(imgTemp,(int(imgW+2*SaveBlurDiameter),imgH)))
            print("Image Data to be Copied")
            imgEnlarge[0:imgH, 0:SaveBlurDiameter]=imgTemp[0:imgH, imgW-SaveBlurDiameter:imgW]
            imgEnlarge[0:imgH, imgW+SaveBlurDiameter:imgW+2*SaveBlurDiameter]=imgTemp[0:imgH, 0:SaveBlurDiameter]
            imgEnlarge[0:imgH, SaveBlurDiameter:imgW+SaveBlurDiameter]=imgTemp[0:imgH, 0:imgW]
            print("Blurred Image being Generated")
            imgEnlargeBlur = cv2.GaussianBlur(imgEnlarge, (SaveBlurDiameter, SaveBlurDiameter), 0)
            print("Blurred Image to be Cropped for Equirectangular Format")
            imgTempBlur[0:imgH, 0:imgW]=imgEnlargeBlur[0:imgH, SaveBlurDiameter:imgW+SaveBlurDiameter]
        else:
            imgTempBlur = cv2.GaussianBlur(imgTemp, (SaveBlurDiameter, SaveBlurDiameter), 0)
            print("Blurred Image being Generated")
#        imgFloatBlur = cv2.blur(imgFloat, (100,100))
        AverageValue = imgTemp.mean()
        imgTempDiff = np.clip( imgTemp - imgTempBlur + AverageValue, 0, 1.0)
        imgTemp = imgTempDiff
        if(f180Mask==1):
            Mask180 = np.zeros((180, 1, 3), np.float32)
            for i in range(180):
                Mask180[i]=1.0
                if(i>85):
                    if(i<105):
                        Mask180[i]=1.0-(float(i)-85)*0.05
                    else:
                        Mask180[i]=0
            MaskEr = cv2.resize(Mask180, (imgW, imgH))
            imgTemp = imgTemp*MaskEr
    print("Level & Colar to be Adjusted")
    imgTemp[:,:,0] = np.clip((imgTemp[:,:,0] + LevelB),0,1.0)
    imgTemp[:,:,1] = np.clip((imgTemp[:,:,1] + LevelG),0,1.0)
    imgTemp[:,:,2] = np.clip((imgTemp[:,:,2] + LevelR),0,1.0)
    imgTemp = np.clip((imgTemp + Level),0,1.0)
    if(fEqr>0):
        if(f180Mask==1):
            if(fMaskReplace==1):
                MaskErInv = 1.0 - MaskEr
                MaskEr = MaskErInv*(cv2.resize(imgMask, (imgW, imgH)))
                imgTemp = np.maximum(imgTemp, MaskEr)
    imgTemp16bit = np.uint16(imgTemp*65535)
    imgSave = LUT16bit[imgTemp16bit]
    SaveFileName=currentFileName + ".LUT.tif"
    cv2.imwrite(SaveFileName, imgSave)
    SaveFileName=currentFileName + ".LUT.jpg"
    imgSaveJpg = np.uint8(imgSave/256) 
    cv2.imwrite(SaveFileName, imgSaveJpg)
    print('LUT Applied Image is Saved')
SaveButton=Tk.Button(root, text="Save Image", width=10, command =SaveImage)
SaveButton.grid(row=15,column=4,sticky="ew")


#Batch Save 
fBatchSave = 0
def RunBatchSave():
    global fFileNamesLoaded, FileNameList, idxFileName, currentFileName, fBatchSave
    if(fBatchSave==1):
        BatchSaveButton.update()
        SaveImage()
        idxFileName += 1
        if(idxFileName<len(FileNameList)):
            currentFileName=FileNameList[idxFileName]
        else:
            fBatchSave=0
            print("Batch processing Ended")
            BatchSaveButton.configure(bg='SystemButtonFace', fg='black')
            BatchSaveButton.configure(relief = Tk.RAISED)
            return
        root.after(5, RunBatchSave())
        return

    

def BatchSaveImage():
    global fFileNamesLoaded, FileNameList, idxFileName, currentFileName, fBatchSave
    if fFileNamesLoaded == 0:
        return
    if(fBatchSave==0):
        fBatchSave =1
        BatchSaveButton.configure(bg='blue',  fg='white')
        BatchSaveButton.configure(relief = Tk.SUNKEN)
        idxFileName=0
        currentFileName=FileNameList[idxFileName]
        RunBatchSave()
    else:
        fBatchSave =0
        BatchSaveButton.configure(bg='SystemButtonFace', fg='black')
        BatchSaveButton.configure(relief = Tk.RAISED)

BatchSaveButton=Tk.Button(root, text="Batch Save Image", width=10, command =BatchSaveImage)
BatchSaveButton.grid(row=15,column=5, sticky="ew")

#Image Frame
TifViewW=1000
TifViewH=750
imageView = Tk.Frame(frame1, width=TifViewW, height=TifViewH, bg='black')
imageView.grid(row=5, column=0, columnspan=6, sticky=Tk.NW+Tk.SE)
TifView = Tk.Label(imageView)
TifView.grid(row=0, column=0, columnspan=2, sticky=Tk.NW+Tk.SE)
imgShow_blank = np.zeros((10, 10, 3), np.float32)
imgShow = np.array(cv2.resize(imgShow_blank,(TifViewW,TifViewH)))
imgShowBk = np.float32(imgShow)
imgShow_rgb = cv2.cvtColor(imgShow.astype(np.uint8), cv2.COLOR_BGR2RGB ) 
imgShowTk = Image.fromarray((imgShow*256).astype(np.uint8))
imgtk = ImageTk.PhotoImage(image=imgShowTk)
TifView.imgtk = imgtk
TifView.configure(image=imgtk)
imgRead = np.zeros((1, 1, 3), dtype=np.float32 )
imgBin = np.zeros((1, 1, 3), dtype=np.float32 )
imgNew = np.copy(cv2.resize(imgBin, (2,2)))


def Binning(Wpixel):
    global FileNameList, imgShow, imgShowBk, imgShow_rgb, nBitDepth, imgRead, imgBin, imgNew
    row, col, dep = imgRead.shape
    pw = int(Wpixel)
    hr = int(row/pw)
    hc = int(col/pw)
    imgBin = np.zeros((hr, hc, dep), dtype=np.float32 )
    imgBin[:,:,0] = imgRead[:,:,0].reshape(hr, pw, hc, pw).sum(-1).sum(1)
    imgBin[:,:,1] = imgRead[:,:,1].reshape(hr, pw, hc, pw).sum(-1).sum(1)
    imgBin[:,:,2] = imgRead[:,:,2].reshape(hr, pw, hc, pw).sum(-1).sum(1)
    imgNew = np.copy(cv2.resize(imgBin, (col,row)))
    imgRead = np.zeros((hr, hc, dep), dtype=np.float32 )
    imgRead = np.copy(imgBin)

nBitDepth=8
def LoadTif(FileName):
    global FileNameList, imgShow, imgShowBk, imgShow_rgb, nBitDepth, imgRead, imgBin, imgNew
    global TifViewW, TifViewH, Level, fFlatten
    if fFileNamesLoaded == 0:
        return
    imgRead = cv2.imread(FileName, -1) #unchanged
    Binning(4)
    row, col, dep = imgRead.shape
    if(col>row):
        imgShowW= TifViewW
        imgShowH=int(row*TifViewW/col)
    else:
        imgShowW=int(col*TifViewH/row)
        imgShowH= TifViewH
    imgShow = np.float32(cv2.resize(imgRead,(imgShowW,imgShowH)))
#    imgShowBk = np.float32(imgShow)
    if(imgRead.dtype == np.float32):
        MaxV=np.amax(imgShow)
        imgShow = imgShow/float(MaxV)
        nBitDepth=32
    elif(imgRead.dtype == np.uint16):
        imgShow = imgShow/65535.0 
        nBitDepth=16
    elif(imgRead.dtype == np.uint8):
        imgShow = imgShow/255.0
        nBitDepth=8
    else:
        return
    imgShowBk = np.copy(imgShow) #imgShow and imgShowBk are float32 0.0-1.0
    ApplyLUT()
    UpdateHistPlots()
    UpdateCurvePlots()

# def hist_rgb(img):
#     #Function to create a histogram of rgb
#     #The variable res that stores the result[brightness, channel]
#     res = np.zeros([256, 3])   
#     for channel in range(3):
#         #Extract a channel
#         img_tmp = img[:,:,channel]
#         #Make the image one-dimensional
#         img_tmp =img_tmp.reshape(img_tmp.size)
#         for i in img_tmp:
#             res[i, channel] += 1
#     return res

# def mat_hist_rgb(hist, ylim = 0.06):
#     #hist_Display the histogram calculated by the function of rgb
#     x = np.arange(hist.shape[0])
#     ax1 = fig.add_subplot(211)
#     #Specify the color of the histogram
#     colors = ["red", "green", "blue"]
#     for i, color in enumerate(colors):
#         ax1.bar(x,hist[:, i], color=color, alpha=0.3, width=1.0)
#     ax1.set_xlabel("Brightness")
#     ax1.set_ylabel("Frequency")
#     ax1.set_xlim(0, 255)
#     ax1.set_yticks([])
#     canvas.draw()
    
#    plt.show()

def UpdateHistPlots():
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    global imgShow_rgb
    row, col, dep = imgShow_rgb.shape
    imgShow_hist = cv2.resize(imgShow_rgb,(int(col/10), int(row/10)))
    histogram_color = np.zeros([256, 3])  
    for channel in range(3):
        SingleColor = imgShow_hist[:,:,channel]
        SingleColor = SingleColor.reshape(SingleColor.size)
        for i in SingleColor:
            histogram_color[i, channel] += 1
    x = np.arange(histogram_color.shape[0])
    ax_hist = fig.add_subplot(212)
    #Specify the color of the histogram
    colors = ["red", "green", "blue"]
    for i, color in enumerate(colors):
        ax_hist.bar(x,histogram_color[:, i], color=color, alpha=0.3, width=1.0)
    ax_hist.set_xlabel("Brightness")
    ax_hist.set_ylabel("Frequency")
    ax_hist.set_xlim(0, 255)
    ax_hist.set_yticks([])
    canvas.draw()
    UpdateCurvePlots()
PlotButton = Tk.Button(root, text='Update Histogram Plots', width=10, command=UpdateHistPlots)
PlotButton.grid(row=1, column=4, columnspan=3, sticky=Tk.W+Tk.E)

def UpdateCurvePlots():
    global fFileNamesLoaded
    if(fFileNamesLoaded==0):
        return
    global LUT16bit
    x = np.arange(0, 65535)
    ax_curve = fig.add_subplot(211)
    ax_curve.plot(x, LUT16bit[x], color='black', linestyle='solid')
    ax_curve.set_xlabel("Input")
    ax_curve.set_ylabel("Output")
    ax_curve.set_xlim(0, 65535)
    ax_curve.set_ylim(0, 65535)
    ax_curve.set_xticks([])
    ax_curve.set_yticks([])
    canvas.draw()


root.mainloop()
