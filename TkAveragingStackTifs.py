# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 09:40:36 2021

@author: ktake
"""
import tkinter as Tk
from tkinter import filedialog
import cv2
import numpy as np

root = Tk.Tk()
root.title('Averaging Image stacking')

FileNameList = []
LabelString1 = Tk.StringVar()
fFileNamesLoaded = 0
idxFileName = 0
def LoadFiles():
    global FileNameList, fFileNamesLoaded, idxFileName, currentFileName
    filetypes = (('Jpegs', '*.jpg'),('Tiffs', '*.tif'),('All files', '*.*'))
    file_names = filedialog.askopenfilenames(initialdir='~/Pictures', filetypes=filetypes)
    if file_names:
        FileNameList = root.splitlist(file_names)
        fFileNamesLoaded = 1
        idxFileName = 0
LoadButton = Tk.Button(root, text='Select Files', command=LoadFiles)
LoadButton.grid(row=0, column=0, columnspan=4, sticky=Tk.W+Tk.E)

AveLabel = Tk.Label(root, text='# of Averaging')
AveLabel.grid(row=1, column=0, sticky=Tk.W, ipadx=0, padx=0)
AveValue = Tk.StringVar()
AveEntry = Tk.Entry(root, textvariable=AveValue, width=5, justify='right')
AveEntry.insert(0, '8')
AveValue = AveEntry.get()
AveEntry.grid(row=1, column=1, sticky=Tk.W+Tk.E, ipadx=0, padx=0)

# RwdLabel = Tk.Label(root, text='# of Rewind Frames')
# RwdLabel.grid(row=1, column=2, sticky=Tk.W, ipadx=0, padx=0)
# RwdEntry = Tk.Entry(root, width=5, justify='right')
# RwdEntry.insert(0, '8')
# RwdEntry.grid(row=1, column=3, sticky=Tk.W+Tk.E, ipadx=0, padx=0)

OutLabel = Tk.Label(root, text='# of Frames to output')
OutLabel.grid(row=2, column=0, sticky=Tk.W+Tk.E, ipadx=0, padx=0)
OutEntry = Tk.Entry(root, width=5, justify='right')
OutEntry.insert(0, '4')
OutEntry.grid(row=2, column=1, sticky=Tk.W+Tk.E, ipadx=0, padx=0)


# NumLabel = Tk.Label(root, text='Start Number in 4digits')
# NumLabel.grid(row=1, column=1, sticky=Tk.W, ipadx=0, padx=0)
# NumValue = Tk.StringVar()
# NumEntry = Tk.Entry(root, textvariable=NumValue, width=5, justify='center')
# NumEntry.insert(0, '0000')
# NumValue = NumEntry.get()
# NumEntry.grid(row=2, column=1, sticky=Tk.W+Tk.E, ipadx=0, padx=0)

# ExtLabel = Tk.Label(root, text='Extention')
# ExtLabel.grid(row=1, column=2, sticky=Tk.W, ipadx=0, padx=0)
# ExtValue = Tk.StringVar()
# ExtEntry = Tk.Entry(root, textvariable=ExtValue, width=5, justify='left')
# ExtEntry.insert(0, '.jpg')
# ExtValue = ExtEntry.get()
# ExtEntry.grid(row=2, column=2, sticky=Tk.W+Tk.E, ipadx=0, padx=0)

def RunAveraging():
    global fFileNamesLoaded, FileNameList, idxFileName, AveValue
    if(fFileNamesLoaded==0):
        return
    # StartNumber = int(NumEntry.get())
    idxFileName = 0
    ImgRead = cv2.imread(FileNameList[idxFileName], -1) #16bit tiff assumed
    ImgSum  = np.array(ImgRead, dtype=np.float32)
    ImgSum  = 0
    nAve = float(AveEntry.get())
    # nRwd = int(RwdEntry.get())
    nOut = int(OutEntry.get())
    while ( idxFileName < len(FileNameList)):
    # for i in FileNameList:
        if(idxFileName - int(nAve) >0):
            for j in range(int(nAve)):
                print("[%d/%d] Loading %s" % (idxFileName -j, len(FileNameList), FileNameList[idxFileName] ))
                ImgRead = cv2.imread(FileNameList[idxFileName - j] , -1)
        
                if(ImgRead.dtype == np.float32):
                    MaxV=np.amax(ImgRead)
                    ImgFloat = np.float32(ImgRead/float(MaxV))
                elif(ImgRead.dtype == np.uint16):
                    ImgFloat = np.float32(ImgRead/65535.0)
                elif(ImgRead.dtype == np.uint8):
                    ImgFloat = np.float32(ImgRead/255.0)
                else:
                    return
                ImgSum += ImgFloat

            ImgAve  = np.array(ImgSum, dtype=np.float32)
            ImgAve = ImgSum/nAve*65535.0
            AveragedFileName = FileNameList[idxFileName] + ".AVE.tif"
            cv2.imwrite(AveragedFileName, ImgAve)
            print("Saving %s" % (AveragedFileName))
            ImgSum = 0
        idxFileName+=nOut
    print("Averaging Stacking Finished")

RunAve = Tk.Button(root, text='Run Averaging Stacking',  command=RunAveraging)
RunAve.grid(row=3, column=0, columnspan=4, sticky=Tk.W+Tk.E)

root.mainloop()

