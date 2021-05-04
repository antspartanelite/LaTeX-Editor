#imports required libraries
import os
import time
from tkinter import *
from tkinter import filedialog
import tkinter.messagebox
from PIL import Image,ImageTk
#pdf2image requires the dependency poppler to be installed look up
#the documentation if you want to know more
from pdf2image import convert_from_path

#stores the filepath to the currently loaded tex file
#is set to false if no tex file for current session is on hard disk
texFilePath = False

#stores the state of the key having been released
has_prev_key_release = None

#sets autorendering to false by default
liveRender = False

#initialises a waiting list for input operations
waitingList = []

#removes cached pdf to render if it exists in directory from previous sessions
try:
    os.remove("cachedPDF.pdf")
except:
    print("No pdf")


#function called when the user creates a new document
def newDocument():
    #the program clears the textbox and resets the texpath preventing linking to last file when saving new file
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

#function called to open an existing tex document
def openDocument():
    #links the tex document opened to current session for saving purposes
    global texFilePath
    tmp = texFilePath
    texFilePath = filedialog.askopenfilename(filetypes=(("TeX Files", "*.tex"),))

    #returns if the user cancels file dialog
    if len(texFilePath) == 0:
        texFilePath = tmp
        return

    #if file is valid to open the document will read it into the textbox
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

    #the program will then render the file in the display box if it contains valid latex code
    updateTexFile(textBox, "my_file.tex", displayBox)
    print(len(textBox.get("1.0", END)))
    if len(textBox.get("1.0", END)) > 2:
        updateDisplayBox(displayBox, "cachedTeX.tex")
        
    
#function called then saving as a new file
def saveAs():
    #links the saved file to the current session for future saving operations
    global texFilePath
    texFilePath = filedialog.asksaveasfilename(defaultextension=".tex", title = "New File", filetypes=(("TeX Files","*.tex"),))

    #returns if the user cancels file dialog
    if len(texFilePath) == 0:
        texFilePath = False
        return

    #writes textbox content to a new tex file
    texFile = open(texFilePath, 'w')
    texFile.write(textBox.get("1.0",END))
    texFile.close()

#saves the document
def save():
    #if the session is linked to an existing document the document will be ovewritten otherwise the user will be asked to save as a new file
    global texFilePath
    if texFilePath == False:
        saveAs()
    else:
        texFile = open(texFilePath, 'w')
        texFile.write(textBox.get("1.0",END))
        texFile.close()

#adds cut function which generates the cut event for the textbox
def cut():
    textBox.event_generate('<Control-x>')

#adds copy function which generates the copy event for the textbox
def copy():
    textBox.event_generate('<Control-c>')

#adds paste function which generates the paste event for the textbox
def paste():
    textBox.event_generate('<Control-v>')
    
#exports the tex file as a pdf
def export():
    #attempts to render the current tex file and save it in given location
    global liveRender
    try:
        updateDisplayBox(displayBox, "cachedTeX.tex")
        filePath = filedialog.asksaveasfilename(defaultextension=".pdf", title = "New File", filetypes=(("PDF Files","*.pdf"),))
        os.rename("cachedPDF.pdf", filePath)
        updateDisplayBox(displayBox, "cachedTeX.tex")
    #if unable to render pdf gives user error message
    except:
        if liveRender:
            tkinter.messagebox.showinfo('Message','Unable to render PDF please check that your syntax is correct')

#function performs the redo operation
def redo():
    textBox.edit_redo()

#function forces render of the pdf
def renderPDF():
    #updates the texfile which will then render if liverendering is enabled
    if liveRender:
        updateTexFile(textBox, texFilePath, displayBox)
    #otherwise directly runs the function to render the document
    else:
        if(len(textBox.get("1.0", END)) > 2):
            updateDisplayBox(displayBox, "cachedTeX.tex")

#Function handles when autorendering should be enabled
def toggleAutoRender():
    #Disables autorendering for windows due to performance issues
    global liveRender
    if os.name == 'nt':
        tkinter.messagebox.showinfo('Denied','Due to performance issues auto rendering is disabled for windows')
    #toggles the auto rendring on or off and gives the user appropriate feedback
    else:
        if liveRender:
            tkinter.messagebox.showinfo('Message','Auto rendering of the target pdf has been disabled')
            liveRender = False
        else:
            result=tkinter.messagebox.askquestion('Warning','Enabling auto rendering may cause performance issues are you sure you wish to continue?')
            if result=='yes':
                liveRender = True

#If a key has been released stores the inputs occurence into a list which will be checked after 0.5 seconds
def onKeyRelease(textBox, texFilePath, displayBox):
    global waitingList
    waitingList.append(1)
    textBox.after(500, updateCheck, textBox, texFilePath, displayBox)

#Run 0.5 seconds after an input checks if any other inputs have been made, if not it will update the text file and clear the waiting queue
def updateCheck(textBox, texFilePath, displayBox):
    global waitingList
    waitingList.pop()
    if len(waitingList) == 0:
        updateTexFile(textBox, texFilePath, displayBox)

#Function writes changes to a cached texfile that will be used for rendering
def updateTexFile(textBox, texFilePath, displayBox):
    f = open("cachedTeX.tex", "w")
    f.write(textBox.get("1.0", END))
    f.close()
    displayBox.configure(state="disabled")
    #Checks if the textbox is not empty, and auto rendering is enabled if so the pdf will attempt to render and update the display box
    if(len(textBox.get("1.0", END)) > 2 and liveRender):
        updateDisplayBox(displayBox, "cachedTeX.tex")

#Function renders the latex into a pdf and displays it
def updateDisplayBox(displayBox, texFilePath):
    #Stores current scroll position as rerendering the pdf will cause scrollabr to move
    scrollPos = displayBox.yview()
    #prints variables for debugging purposes
    print(scrollPos)
    print(texFilePath)
    #gets pdflatex to render document and stores the error status
    errorStatus = os.system("pdflatex -jobname=cachedPDFN -halt-on-error "+texFilePath)

    #if there is no error the program will update the currently rendered pdf with the new one that has just been rendered
    if(errorStatus == 0):
        try:
            os.remove("cachedPDF.pdf")
            os.rename("cachedPDFN.pdf","cachedPDF.pdf")
        except:
            os.rename("cachedPDFN.pdf","cachedPDF.pdf")
    #if the program encounters an error rendering the pdf the application will report this to the user if live rendering is disabled
    else:
        if liveRender == False:
            tkinter.messagebox.showinfo('Message','Unable to render PDF please check that your syntax is correct')
            
    #enables editing of the display box and clears the current content
    displayBox.configure(state="normal")
    displayBox.delete("1.0", END)
    
    #PDF is converted to a list of images
    pages = convert_from_path("cachedPDF.pdf",size=(800,900))

    #Empty list is created for storing images
    global pageImages 
    pageImages = []

    #Stores the converted images into the created list
    for i in range(len(pages)):
      pageImages.append(ImageTk.PhotoImage(pages[i]))
    #Adds all the images to the display box
    for pageImage in pageImages:
      displayBox.image_create(END,image=pageImage)
      
      #Gives a page divide in between each of the pages
      displayBox.insert(END,'\n\n')

    #resets the scrollbar to the initial position so that it doesn't jump around each time a render occurs
    displayBox.configure(state="disabled")
    print(scrollPos)
    displayBox.yview_moveto(scrollPos[0])
    displayBox.after(3, displayBox.yview_moveto, scrollPos[0])


#Function inserts the text for a macro into the textbox
def printSymbol(text):
    textBox.insert(INSERT, text)
    updateTexFile(textBox, texFilePath, displayBox)
    


#Creates a 1700x800 window for the application
window = Tk()
window.title("Python LaTeX editor")
window.geometry("1700x800")

#Binds the control+s shortcut to the save function
window.bind_all("<Control-s>", lambda x: save())

#Creates the text frame to store the text widgets
textFrame = Frame(window)


#Adds the textbox scrollbar to the text frame
textScrollY = Scrollbar(textFrame,orient=VERTICAL)

#Adds the displaybox scrollbar to the text frame
pdfScrollY = Scrollbar(textFrame,orient=VERTICAL)

horizontalScroll = Scrollbar(textFrame, orient=HORIZONTAL)

#Sets height of texboxes relative to font
textBox = Text(textFrame, width=88, height=53, font=("Helvetica", 12), yscrollcommand = textScrollY.set, xscrollcommand = horizontalScroll.set, selectbackground="blue", selectforeground="white", undo=True, wrap="none")

#Creates a new frame for the toolbar
toolbar = Frame(window, bd=1, relief=RAISED)

#Converts all the images for toolbar icons into PIL image objects so that they can be rendered by tkinter
renderImg = ImageTk.PhotoImage(Image.open("cog2.png").resize((40, 50)))
fractionImg = ImageTk.PhotoImage(Image.open("fraction.png").resize((40, 50)))
superscriptImg = ImageTk.PhotoImage(Image.open("superscript.png").resize((40, 50)))
subscriptImg = ImageTk.PhotoImage(Image.open("subscript.png").resize((40, 50)))
sqrtImg = ImageTk.PhotoImage(Image.open("sqrt.png").resize((40, 50)))
sumImg = ImageTk.PhotoImage(Image.open("sum.png").resize((40, 50)))
integrationImg = ImageTk.PhotoImage(Image.open("integration.png").resize((40, 50)))

#Creates render button and inserts it into the toolbar
renderButton = Button(toolbar, image=renderImg, relief=FLAT, command=renderPDF)
renderButton.image = renderImg
renderButton.pack(side=LEFT, padx=2, pady=2)

#Creates the fraction macro button and inserts it into the toolbar
fractionButton = Button(toolbar, image=fractionImg, relief=FLAT, command=lambda:printSymbol("\\frac{}{}"))
fractionButton.image = fractionImg
fractionButton.pack(side=LEFT, padx=2, pady=2)

#Creates the superscript macro button and inserts it into the toolbar
superscriptButton = Button(toolbar, image=superscriptImg, relief=FLAT, command=lambda:printSymbol("{}^{}"))
superscriptButton.image = superscriptImg
superscriptButton.pack(side=LEFT, padx=2, pady=2)

#Creates the subscript macro button and inserts it into the toolbar
subscriptButton = Button(toolbar, image=subscriptImg, relief=FLAT, command=lambda:printSymbol("{}_{}"))
subscriptButton.image = superscriptImg
subscriptButton.pack(side=LEFT, padx=2, pady=2)

#Creates the square root macro button and inserts it into the toolbar
sqrtButton = Button(toolbar, image=sqrtImg, relief=FLAT, command=lambda:printSymbol("\\sqrt{}"))
sqrtButton.image = sqrtImg
sqrtButton.pack(side=LEFT, padx=2, pady=2)

#Creates the summation macro button and inserts it into the toolbar
sumButton = Button(toolbar, image=sumImg, relief=FLAT, command=lambda:printSymbol("\\Sigma"))
sumButton.image = sumImg
sumButton.pack(side=LEFT, padx=2, pady=2)

#Creates the integral macro button and inserts it into the toolbar
integrationButton = Button(toolbar, image=integrationImg, relief=FLAT, command=lambda:printSymbol("\\int"))
integrationButton.image = integrationImg
integrationButton.pack(side=LEFT, padx=2, pady=2)

#Inserts the toolbar into the application window
toolbar.pack(side=TOP, fill=X)

#Inserts the frame for the text widgets into the window
textFrame.pack(pady=10)

#Creates a horizontal scroll bar
horizontalScroll.pack(side=BOTTOM, fill=X)
horizontalScroll.config(command=textBox.xview)

#Inserts the textbox into the text frame
textBox.pack(side=LEFT,padx=10)

#Creates the displaybox text widget
displayBox = Text(textFrame, width=66, height=40, font=("Helvetica", 16), yscrollcommand = pdfScrollY.set, selectbackground="yellow", selectforeground="black", bg="grey")

#Disables user input into the displaybox text widget
displayBox.configure(state="disabled")



#Setting the scrollbar to the right side of each frame
textScrollY.pack(side=LEFT,fill=Y)
textScrollY.config(command=textBox.yview)
pdfScrollY.pack(side=RIGHT,fill=Y)
pdfScrollY.config(command=displayBox.yview)

#Inserts the displaybox into the text frame
displayBox.pack(side=RIGHT,padx=10)
#Binds functions to the key release and control+y events
textBox.bind("<KeyRelease>", lambda event, arg=(0): onKeyRelease(textBox, texFilePath, displayBox))
textBox.bind("<Control-y>", lambda x: redo())

#Creates menu widget for dropdown menu
myMenu = Menu(window)
window.config(menu = myMenu)

#Creates file menu dropdown widget
fileMenu = Menu(myMenu)
myMenu.add_cascade(label="File",menu=fileMenu)
fileMenu.add_command(label="New", command=newDocument)
fileMenu.add_command(label="Open", command=openDocument)
fileMenu.add_command(label="Save", command=save, accelerator="(Ctrl+s)")
fileMenu.add_command(label="Save As", command=saveAs)
fileMenu.add_command(label="Export", command=export)

#creates edit menu dropdown widget
editMenu = Menu(myMenu)
myMenu.add_cascade(label="Edit",menu=editMenu)
editMenu.add_command(label="Undo", command=textBox.edit_undo, accelerator="(Ctrl+z)")
editMenu.add_command(label="Redo", command=textBox.edit_redo, accelerator="(Ctrl+y)")
editMenu.add_command(label="Cut", command=cut, accelerator="(Ctrl+x)")
editMenu.add_command(label="Copy", command=copy, accelerator="(Ctrl+c)")
editMenu.add_command(label="Paste",command=paste, accelerator="(Ctrl+v)")

#creates insert menu dropdown widget
insertMenu = Menu(myMenu)
myMenu.add_cascade(label="Insert",menu=insertMenu)
lowerGreekMenu = Menu(insertMenu)
upperGreekMenu = Menu(insertMenu)
insertMenu.add_cascade(label="Lowercase Greek", menu=lowerGreekMenu)

#Adds macros for all lower case greek symbols to insert menu dropdown
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

#Adds macros for all upper case greek symbols to insert menu dropdown
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

#creates settings menu dropdown widget
settingsMenu = Menu(myMenu)
myMenu.add_cascade(label="Settings",menu=settingsMenu)
settingsMenu.add_command(label="Toggle autorender", command=toggleAutoRender)


window.mainloop()
