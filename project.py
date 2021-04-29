import tkinter as tk
import os
import time
from tkinter import *
from tkinter import filedialog
from PIL import Image,ImageTk
from pdf2image import convert_from_path

texFilePath = "my_file.tex"

has_prev_key_release = None

def newDocument():
    textBox.delete("1.0", END)
    displayBox.configure(state="normal")
    displayBox.delete("1.0", END)
    displayBox.configure(state="disabled")

def openDocument():  
    latexFile = filedialog.askopenfilename(filetypes=(("TeX Files", "*.tex"),))
    
    if len(latexFile) == 0:
        return
    
    textBox.delete("1.0", END)
    displayBox.configure(state="normal")
    displayBox.delete("1.0", END)
    displayBox.configure(state="disabled")

    latexFile = open(latexFile, "r")
    content = latexFile.read()

    textBox.insert(END, content)
    latexFile.close()
    updateTexFile(textBox, "my_file.tex", displayBox)
    

def on_key_release(textBox, texFilePath, displayBox):
    global has_prev_key_release
    has_prev_key_release = None
    updateTexFile(textBox, texFilePath, displayBox)

def on_key_release_repeat(textBox, texFilePath, displayBox):
    global has_prev_key_release
    has_prev_key_release = textBox.after_idle(on_key_release, textBox, texFilePath, displayBox)


def updateTexFile(textBox, texFilePath, displayBox):
    f = open("cachedTeX.tex", "w")
    f.write(textBox.get("1.0", END))
    f.close()
    displayBox.configure(state="disabled")
    updateDisplayBox(displayBox, "cachedTeX.tex")


def updateDisplayBox(displayBox, texFilePath):
    scrollPos = displayBox.yview()
    print(scrollPos)
    errorStatus = os.system("pdflatex -jobname=cachedPDFN -halt-on-error "+texFilePath)
    if(errorStatus == 0):
        try:
            os.remove("cachedPDF.pdf")
            os.rename("cachedPDFN.pdf","cachedPDF.pdf")
        except:
            os.rename("cachedPDFN.pdf","cachedPDF.pdf")
    displayBox.configure(state="normal")
    displayBox.delete("1.0", END)
    # Here the PDF is converted to list of images
    pages = convert_from_path("cachedPDF.pdf",size=(800,900))

    # Empty list for storing images
    global pageImages 
    pageImages = []

    # Storing the converted images into list
    for i in range(len(pages)):
      pageImages.append(ImageTk.PhotoImage(pages[i]))
    # Adding all the images to the text widget
    for pageImage in pageImages:
      displayBox.image_create(END,image=pageImage)
      
      # For Seperating the pages
      displayBox.insert(END,'\n\n')

    displayBox.configure(state="disabled")
    print(scrollPos)
    displayBox.yview_moveto(scrollPos[0])
    displayBox.after(3, displayBox.yview_moveto, scrollPos[0])



window = Tk()
window.title("Python LaTeX editor")
window.geometry("1620x700")

textFrame = Frame(window)
textFrame.pack(pady=10)

# Adding Scrollbar to the text frame
textScrollY = Scrollbar(textFrame,orient=VERTICAL)

# Adding Scrollbar to the PDF frame
pdfScrollY = Scrollbar(textFrame,orient=VERTICAL)

#Sets height of texboxes relative to font
textBox = Text(textFrame, width=88, height=33, font=("Helvetica", 12), yscrollcommand = textScrollY.set, selectbackground="blue", selectforeground="white")
textBox.pack(side=tk.LEFT,padx=10)
displayBox = Text(textFrame, width=66, height=25, font=("Helvetica", 16), yscrollcommand = pdfScrollY.set, selectbackground="yellow", selectforeground="black", bg="grey")


# Setting the scrollbar to the right side of each frame
textScrollY.pack(side=LEFT,fill=Y)
textScrollY.config(command=textBox.yview)
pdfScrollY.pack(side=RIGHT,fill=Y)
pdfScrollY.config(command=displayBox.yview)



displayBox.pack(side=tk.RIGHT,padx=10)
textBox.bind("<KeyRelease>", lambda event, arg=(0): on_key_release_repeat(textBox, texFilePath, displayBox)) 

f = open(texFilePath)
content = f.readlines()

content = "".join(content)

textBox.insert("1.0",content)

f.close()


displayBox.configure(state="disabled")

updateDisplayBox(displayBox, texFilePath)

myMenu = Menu(window)
window.config(menu = myMenu)

fileMenu = Menu(myMenu)
myMenu.add_cascade(label="File",menu=fileMenu)
fileMenu.add_command(label="New", command=newDocument)
fileMenu.add_command(label="Open", command=openDocument)
fileMenu.add_command(label="Save")
fileMenu.add_command(label="Save As")
fileMenu.add_command(label="Export")

editMenu = Menu(myMenu)
myMenu.add_cascade(label="Edit",menu=editMenu)
editMenu.add_command(label="Undo")
editMenu.add_command(label="Redo")
editMenu.add_command(label="Cut")
editMenu.add_command(label="Copy")
editMenu.add_command(label="Paste")


window.mainloop()
