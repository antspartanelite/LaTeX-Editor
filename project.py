import os
import time
from tkinter import *
from tkinter import filedialog
import tkinter.messagebox
from PIL import Image,ImageTk
from pdf2image import convert_from_path

texFilePath = False

has_prev_key_release = None

liveRender = False

waitingList = []

try:
    os.remove("cachedPDF.pdf")
except:
    print("No pdf")

def newDocument():
    textBox.delete("1.0", END)
    displayBox.configure(state="normal")
    displayBox.delete("1.0", END)
    displayBox.configure(state="disabled")
    global texFilePath
    texFilePath = False

    try:
        os.remove("cachedPDF.pdf")
    except:
        print("No pdf")

def openDocument():  
    global texFilePath
    tmp = texFilePath
    texFilePath = filedialog.askopenfilename(filetypes=(("TeX Files", "*.tex"),))
    
    if len(texFilePath) == 0:
        texFilePath = tmp
        return
    
    textBox.delete("1.0", END)
    displayBox.configure(state="normal")
    displayBox.delete("1.0", END)
    displayBox.configure(state="disabled")

    texFile = open(texFilePath, "r")
    content = texFile.read()

    textBox.insert(END, content)
    texFile.close()

    try:
        os.remove("cachedPDF.pdf")
    except:
        print("No pdfn")
    
    updateTexFile(textBox, "my_file.tex", displayBox)
    if(len(textBox.get("1.0", END)) != 1):
        updateDisplayBox(displayBox, "cachedTeX.tex")
        
    

def saveAs():
    global texFilePath
    texFilePath = filedialog.asksaveasfilename(defaultextension=".tex", title = "New File", filetypes=(("TeX Files","*.tex"),))
    
    if len(texFilePath) == 0:
        texFilePath = False
        return

    texFile = open(texFilePath, 'w')
    texFile.write(textBox.get("1.0",END))
    texFile.close()

def save():
    global texFilePath
    if texFilePath == False:
        saveAs()
    else:
        texFile = open(texFilePath, 'w')
        texFile.write(textBox.get("1.0",END))
        texFile.close()


def cut():
    textBox.event_generate('<Control-x>')

def copy():
    textBox.event_generate('<Control-c>')

def paste():
    textBox.event_generate('<Control-v>')
    

def export():
    updateDisplayBox(displayBox, "cachedTeX.tex")
    filePath = filedialog.asksaveasfilename(defaultextension=".pdf", title = "New File", filetypes=(("PDF Files","*.pdf"),))
    os.rename("cachedPDF.pdf", filePath)
    updateDisplayBox(displayBox, "cachedTeX.tex")

def redo():
    textBox.edit_redo()


def renderPDF():
    if liveRender:
        updateTexFile(textBox, texFilePath, displayBox)
    else:
        if(len(textBox.get("1.0", END)) != 1):
            updateDisplayBox(displayBox, "cachedTeX.tex")

def toggleAutoRender():
    global liveRender
    if os.name == 'nt':
        tkinter.messagebox.showinfo('Denied','Due to performance issues auto rendering is disabled for windows')
    else:
        if liveRender:
            tkinter.messagebox.showinfo('Message','Auto rendering of the target pdf has been disabled')
            liveRender = False
        else:
            result=tkinter.messagebox.askquestion('Warning','Enabling auto rendering may cause performance issues are you sure you wish to continue?')
            if result=='yes':
                liveRender = True

def onKeyRelease(textBox, texFilePath, displayBox):
    global waitingList
    waitingList.append(1)
    textBox.after(500, updateCheck, textBox, texFilePath, displayBox)

def updateCheck(textBox, texFilePath, displayBox):
    global waitingList
    waitingList.pop()
    if len(waitingList) == 0:
        updateTexFile(textBox, texFilePath, displayBox)


def updateTexFile(textBox, texFilePath, displayBox):
    f = open("cachedTeX.tex", "w")
    f.write(textBox.get("1.0", END))
    f.close()
    displayBox.configure(state="disabled")
    if(len(textBox.get("1.0", END)) != 1 and liveRender):
        updateDisplayBox(displayBox, "cachedTeX.tex")


def updateDisplayBox(displayBox, texFilePath):
    scrollPos = displayBox.yview()
    print(scrollPos)
    print(texFilePath)
    errorStatus = os.system("pdflatex -jobname=cachedPDFN -halt-on-error "+texFilePath)
    if(errorStatus == 0):
        try:
            os.remove("cachedPDF.pdf")
            os.rename("cachedPDFN.pdf","cachedPDF.pdf")
        except:
            os.rename("cachedPDFN.pdf","cachedPDF.pdf")
    else:
        if liveRender == False:
            tkinter.messagebox.showinfo('Message','Unable to render PDF please check that your syntax is correct')
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

def printSymbol(text):
    textBox.insert(INSERT, text)
    updateTexFile(textBox, texFilePath, displayBox)
    



window = Tk()
window.title("Python LaTeX editor")
window.geometry("1700x800")
window.bind_all("<Control-s>", lambda x: save())

textFrame = Frame(window)


# Adding Scrollbar to the text frame
textScrollY = Scrollbar(textFrame,orient=VERTICAL)

# Adding Scrollbar to the PDF frame
pdfScrollY = Scrollbar(textFrame,orient=VERTICAL)

horizontalScroll = Scrollbar(textFrame, orient=HORIZONTAL)

#Sets height of texboxes relative to font
textBox = Text(textFrame, width=88, height=53, font=("Helvetica", 12), yscrollcommand = textScrollY.set, xscrollcommand = horizontalScroll.set, selectbackground="blue", selectforeground="white", undo=True, wrap="none")


toolbar = Frame(window, bd=1, relief=RAISED)

renderImg = ImageTk.PhotoImage(Image.open("cog2.png").resize((40, 50)))
fractionImg = ImageTk.PhotoImage(Image.open("fraction.png").resize((40, 50)))
superscriptImg = ImageTk.PhotoImage(Image.open("superscript.png").resize((40, 50)))
subscriptImg = ImageTk.PhotoImage(Image.open("subscript.png").resize((40, 50)))
sqrtImg = ImageTk.PhotoImage(Image.open("sqrt.png").resize((40, 50)))
sumImg = ImageTk.PhotoImage(Image.open("sum.png").resize((40, 50)))
integrationImg = ImageTk.PhotoImage(Image.open("integration.png").resize((40, 50)))

renderButton = Button(toolbar, image=renderImg, relief=FLAT, command=renderPDF)
renderButton.image = renderImg
renderButton.pack(side=LEFT, padx=2, pady=2)

fractionButton = Button(toolbar, image=fractionImg, relief=FLAT, command=lambda:printSymbol("\\frac{}{}"))
fractionButton.image = fractionImg
fractionButton.pack(side=LEFT, padx=2, pady=2)

superscriptButton = Button(toolbar, image=superscriptImg, relief=FLAT, command=lambda:printSymbol("{}^{}"))
superscriptButton.image = superscriptImg
superscriptButton.pack(side=LEFT, padx=2, pady=2)

subscriptButton = Button(toolbar, image=subscriptImg, relief=FLAT, command=lambda:printSymbol("{}_{}"))
subscriptButton.image = superscriptImg
subscriptButton.pack(side=LEFT, padx=2, pady=2)

sqrtButton = Button(toolbar, image=sqrtImg, relief=FLAT, command=lambda:printSymbol("\\sqrt{}"))
sqrtButton.image = sqrtImg
sqrtButton.pack(side=LEFT, padx=2, pady=2)

sumButton = Button(toolbar, image=sumImg, relief=FLAT, command=lambda:printSymbol("\\Sigma"))
sumButton.image = sumImg
sumButton.pack(side=LEFT, padx=2, pady=2)

integrationButton = Button(toolbar, image=integrationImg, relief=FLAT, command=lambda:printSymbol("\\int"))
integrationButton.image = integrationImg
integrationButton.pack(side=LEFT, padx=2, pady=2)

toolbar.pack(side=TOP, fill=X)


textFrame.pack(pady=10)
horizontalScroll.pack(side=BOTTOM, fill=X)
horizontalScroll.config(command=textBox.xview)
textBox.pack(side=LEFT,padx=10)

displayBox = Text(textFrame, width=66, height=40, font=("Helvetica", 16), yscrollcommand = pdfScrollY.set, selectbackground="yellow", selectforeground="black", bg="grey")

displayBox.configure(state="disabled")



# Setting the scrollbar to the right side of each frame
textScrollY.pack(side=LEFT,fill=Y)
textScrollY.config(command=textBox.yview)
pdfScrollY.pack(side=RIGHT,fill=Y)
pdfScrollY.config(command=displayBox.yview)


displayBox.pack(side=RIGHT,padx=10)
textBox.bind("<KeyRelease>", lambda event, arg=(0): onKeyRelease(textBox, texFilePath, displayBox))
textBox.bind("<Control-y>", lambda x: redo())



displayBox.configure(state="disabled")


myMenu = Menu(window)
window.config(menu = myMenu)

fileMenu = Menu(myMenu)
myMenu.add_cascade(label="File",menu=fileMenu)
fileMenu.add_command(label="New", command=newDocument)
fileMenu.add_command(label="Open", command=openDocument)
fileMenu.add_command(label="Save", command=save, accelerator="(Ctrl+s)")
fileMenu.add_command(label="Save As", command=saveAs)
fileMenu.add_command(label="Export", command=export)

editMenu = Menu(myMenu)
myMenu.add_cascade(label="Edit",menu=editMenu)
editMenu.add_command(label="Undo", command=textBox.edit_undo, accelerator="(Ctrl+z)")
editMenu.add_command(label="Redo", command=textBox.edit_redo, accelerator="(Ctrl+y)")
editMenu.add_command(label="Cut", command=cut, accelerator="(Ctrl+x)")
editMenu.add_command(label="Copy", command=copy, accelerator="(Ctrl+c)")
editMenu.add_command(label="Paste",command=paste, accelerator="(Ctrl+v)")


insertMenu = Menu(myMenu)
myMenu.add_cascade(label="Insert",menu=insertMenu)
lowerGreekMenu = Menu(insertMenu)
upperGreekMenu = Menu(insertMenu)
insertMenu.add_cascade(label="Lowercase Greek", menu=lowerGreekMenu)

lowerGreekMenu.add_command(label="Alpha", command=lambda:printSymbol("\\alpha"))
lowerGreekMenu.add_command(label="Beta", command=lambda:printSymbol("\\beta"))
lowerGreekMenu.add_command(label="Gamma", command=lambda:printSymbol("\\gamma"))
lowerGreekMenu.add_command(label="Delta", command=lambda:printSymbol("\\delta"))
lowerGreekMenu.add_command(label="Epsilon", command=lambda:printSymbol("\\epsilon"))
lowerGreekMenu.add_command(label="Zeta", command=lambda:printSymbol("\\zeta"))
lowerGreekMenu.add_command(label="Eta", command=lambda:printSymbol("\\eta"))
lowerGreekMenu.add_command(label="Theta", command=lambda:printSymbol("\\theta"))
lowerGreekMenu.add_command(label="Iota", command=lambda:printSymbol("\\iota"))
lowerGreekMenu.add_command(label="Kappa", command=lambda:printSymbol("\\kappa"))
lowerGreekMenu.add_command(label="Lambda", command=lambda:printSymbol("\\lambda"))
lowerGreekMenu.add_command(label="Mu", command=lambda:printSymbol("\\mu"))
lowerGreekMenu.add_command(label="Nu", command=lambda:printSymbol("\\nu"))
lowerGreekMenu.add_command(label="Xi", command=lambda:printSymbol("\\xi"))
lowerGreekMenu.add_command(label="Omicron", command=lambda:printSymbol("o"))
lowerGreekMenu.add_command(label="Pi", command=lambda:printSymbol("\\pi"))
lowerGreekMenu.add_command(label="Rho", command=lambda:printSymbol("\\rho"))
lowerGreekMenu.add_command(label="Sigma", command=lambda:printSymbol("\\sigma"))
lowerGreekMenu.add_command(label="Tau", command=lambda:printSymbol("\\tau"))
lowerGreekMenu.add_command(label="Upsilon", command=lambda:printSymbol("\\upsilon"))
lowerGreekMenu.add_command(label="Phi", command=lambda:printSymbol("\\phi"))
lowerGreekMenu.add_command(label="Chi", command=lambda:printSymbol("\\chi"))
lowerGreekMenu.add_command(label="Psi", command=lambda:printSymbol("\\psi"))
lowerGreekMenu.add_command(label="Omega", command=lambda:printSymbol("\\omega"))


insertMenu.add_cascade(label="Uppercase Greek", menu=upperGreekMenu)

upperGreekMenu.add_command(label="Alpha", command=lambda:printSymbol("A"))
upperGreekMenu.add_command(label="Beta", command=lambda:printSymbol("B"))
upperGreekMenu.add_command(label="Gamma", command=lambda:printSymbol("\\Gamma"))
upperGreekMenu.add_command(label="Delta", command=lambda:printSymbol("\\Delta"))
upperGreekMenu.add_command(label="Epsilon", command=lambda:printSymbol("E"))
upperGreekMenu.add_command(label="Zeta", command=lambda:printSymbol("Z"))
upperGreekMenu.add_command(label="Eta", command=lambda:printSymbol("H"))
upperGreekMenu.add_command(label="Theta", command=lambda:printSymbol("\\Theta"))
upperGreekMenu.add_command(label="Iota", command=lambda:printSymbol("I"))
upperGreekMenu.add_command(label="Kappa", command=lambda:printSymbol("K"))
upperGreekMenu.add_command(label="Lambda", command=lambda:printSymbol("\\Lambda"))
upperGreekMenu.add_command(label="Mu", command=lambda:printSymbol("M"))
upperGreekMenu.add_command(label="Nu", command=lambda:printSymbol("N"))
upperGreekMenu.add_command(label="Xi", command=lambda:printSymbol("\\Xi"))
upperGreekMenu.add_command(label="Omicron", command=lambda:printSymbol("O"))
upperGreekMenu.add_command(label="Pi", command=lambda:printSymbol("\\Pi"))
upperGreekMenu.add_command(label="Rho", command=lambda:printSymbol("P"))
upperGreekMenu.add_command(label="Sigma", command=lambda:printSymbol("\\Sigma"))
upperGreekMenu.add_command(label="Tau", command=lambda:printSymbol("T"))
upperGreekMenu.add_command(label="Upsilon", command=lambda:printSymbol("\\Upsilon"))
upperGreekMenu.add_command(label="Phi", command=lambda:printSymbol("\\Phi"))
upperGreekMenu.add_command(label="Chi", command=lambda:printSymbol("X"))
upperGreekMenu.add_command(label="Psi", command=lambda:printSymbol("\\Psi"))
upperGreekMenu.add_command(label="Omega", command=lambda:printSymbol("\\Omega"))


settingsMenu = Menu(myMenu)
myMenu.add_cascade(label="Settings",menu=settingsMenu)
settingsMenu.add_command(label="Toggle autorender", command=toggleAutoRender)


window.mainloop()
