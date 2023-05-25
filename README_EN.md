# Working with PDF Bank Slips in python

Modules created based on the ```pypdfium2``` library, maintained by Google, to open pdf's and provide some solutions, including:
- Get the file size;
- Render a pdf page as a *numpy* array (image);
- Extract text from pdf (with or without OCR);
- Extract the Value of the bank slip;
- Get a file path with the standard GUI (```tkinter```);
- Open a file in the default OS application.

If your PDF is a bank slips, the *ticket_value* method tries to extract the value from it.

The [BoletoPdf](/BoletoPdf.py) module implements the opening of a file directly through its path without having to use the ```open``` function of *python*

> If you wish to use OCR to aid in value extraction the ```PIL``` and ```pytesseract``` libraries are a requirement.

## Code Example
```python
from BoletoPdf import BoletoPDF

# Get the File Path
path = BoletoPDF.get_file_name()

# Object Initialization
ticket = BoletoPDF(path)

# File Size
size = b.file_size

# Render a page
b.render(
	page=0,
	flag='right',
	scale=1
) 

# Extract Text from PDF
b.text(
	pages=[0,1],
	flag='all',
	allow_OCR=False
)

# Extract the Value
b.ticket_value()   

# Open File
b.show()
```
