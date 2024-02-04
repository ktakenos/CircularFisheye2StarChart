# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 09:40:36 2021

@author: ktake
"""
import tkinter as Tk
from tkinter import filedialog
import os

root = Tk.Tk()
root.title('File Name Renumbering')

FileNameList = []
LabelString1 = Tk.StringVar()
fFileNamesLoaded = 0
idxFileName = 0
def LoadFiles():
    global FileNameList, fFileNamesLoaded, idxFileName, currentFileName
    filetypes = (('Jpegs', '*.jpg'),('Tiffs', '*.tif'),('Fujifim Raw', '*.raf'),('Sony Raw', '*.arw'),('All files', '*.*'))
    file_names = filedialog.askopenfilenames(initialdir='~/Pictures', filetypes=filetypes)
    if file_names:
        FileNameList = root.splitlist(file_names)
        fFileNamesLoaded = 1
        idxFileName = 0
        # currentFileName=FileNameList[idxFileName]
        # head, tail = os.path.split(currentFileName)
        # print("Directory= %s, File= %s" %(head, tail))
        # newFileName = head+'/'+'NewFile.new'
        # print(newFileName)
#        os.rename(currentFileName, newFileName)
#        Total=len(FileNameList)
#        TextBox.insert((Tk.END), "[System] %d Files selected\n" % Total)
LoadButton = Tk.Button(root, text='Select Files', command=LoadFiles)
LoadButton.grid(row=0, column=0, columnspan=3, sticky=Tk.W+Tk.E)

PreLabel = Tk.Label(root, text='FileNamePrefix')
PreLabel.grid(row=1, column=0, sticky=Tk.W, ipadx=0, padx=0)
PreValue = Tk.StringVar()
PreEntry = Tk.Entry(root, textvariable=PreValue, width=5, justify='right')
PreEntry.insert(0, 'DSCF')
PreValue = PreEntry.get()
PreEntry.grid(row=2, column=0, sticky=Tk.W+Tk.E, ipadx=0, padx=0)

NumLabel = Tk.Label(root, text='Start Number in 4digits')
NumLabel.grid(row=1, column=1, sticky=Tk.W, ipadx=0, padx=0)
NumValue = Tk.StringVar()
NumEntry = Tk.Entry(root, textvariable=NumValue, width=5, justify='center')
NumEntry.insert(0, '0000')
NumValue = NumEntry.get()
NumEntry.grid(row=2, column=1, sticky=Tk.W+Tk.E, ipadx=0, padx=0)

ExtLabel = Tk.Label(root, text='Extention')
ExtLabel.grid(row=1, column=2, sticky=Tk.W, ipadx=0, padx=0)
ExtValue = Tk.StringVar()
ExtEntry = Tk.Entry(root, textvariable=ExtValue, width=5, justify='left')
ExtEntry.insert(0, '.jpg')
ExtValue = ExtEntry.get()
ExtEntry.grid(row=2, column=2, sticky=Tk.W+Tk.E, ipadx=0, padx=0)

def RunRenum():
    global fFileNamesLoaded, FileNameList, idxFileName
    if(fFileNamesLoaded==0):
        return
    StartNumber = int(NumEntry.get())
    for i in FileNameList:
        head, tail = os.path.split(i)
        newNumberStr="%04d" % int(NumEntry.get())
        newNumberFilename = PreEntry.get()+newNumberStr+ExtEntry.get()
        newFileName = head+'/'+newNumberFilename
        print("Renaming %s to new Filename %s" %(tail, newNumberFilename))
        os.rename(i, newFileName)
        idxFileName+=1
        NumEntry.delete(0,4)
        NumEntry.insert(0, "%04d" % int(StartNumber+idxFileName))
        NumEntry.update()



RunRenum = Tk.Button(root, text='Run Renumbering',  command=RunRenum)
RunRenum.grid(row=3, column=0, columnspan=3, sticky=Tk.W+Tk.E)

root.mainloop()

