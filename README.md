# Manipular Boletos em PDF no python

Módulos criados com base na biblioteca ```pypdfium2```, que é mantida pelo Google, para abrir pdf's e fornecer algumas soluções, entre elas:
	- Obter o tamanho do arquivo;
	- Renderizar uma página do pdf como um array do *numpy* (imagem);
	- Extrair o texto do pdf (com ou sem OCR);
	- Extrair o Valor do Boleto;
	- Obter um caminho de arquivo com a interface gráfica padrao (```tkinter```);
	- Abrir um arquivo na aplicação padrão do OS.

Se o seu PDF for um boleto, o método *ticket_value* tenta extrair o valor dele.

O módulo [BoletoPdf](/BoletoPdf.py) foi criado para facilitar a abertura de um arquivo direto pelo seu caminho sem precisar utilizar a função ```open``` do *python*

> Se você desejar utilizar OCR para auxiliar na extração do valor as bibliotecas ```PIL``` e ```pytesseract``` são um requisito.

## Exemplo de Código
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

> [See this text in english](/README_EN.md)