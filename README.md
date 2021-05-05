# LaTeX-Editor
Installation instructions:
For this LaTeX editor to run correctly you need to have a couple of things installed.

1. First you must have a working setup of TeX and pdflatex installed. To ensure this is the case open the command prompt in the directory of a complete tex file and run 
pdflatex to ensure that it is functioning correctly.

2. Next the user must ensure they have installed PIL, and pdf2image using pip
The commands to do so are the following:
pip install pillow
pip install pdf2image

3. At this point the program may function correctly however if it still cannot be run using python you may need to install poppler
I did this by installing and extracting the file from this link http://blog.alivate.com.au/wp-content/uploads/2018/10/poppler-0.68.0_x86.7z and then adding the /bin folder to
path. 

The instructions for this on the pdf2image pypi page can be found here: https://pypi.org/project/pdf2image/
