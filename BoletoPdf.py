from os import startfile
from os.path import isfile, splitext
from tkinter import filedialog
from pathlib import Path

from Boleto import Boleto


class BoletoPDF(Boleto):
    def __init__(self, source: str) -> None:
        
        if isfile(source):
            self.__path = Path(source)
        else:
            info = 'File Not Found:\n>>>\t(' + source + ')'
            raise FileNotFoundError(info)

        self.__file_extension = splitext(self.__path)[1]

        if self.__file_extension.lower() != '.pdf':
            info = 'Only files whose extension is \'.pdf\' could be instantiate'
            raise Exception(info)

        super().__init__(source=open(Path(source), 'rb'))

    @property
    def path(self) -> str:
        return str(self.__path)
    
    @property
    def file_extension(self) -> str:
        return self.__file_extension

    def __repr__(self) -> str:
        caminho = str(self.__path).replace('\\', '\\\\')
        return f'BoletoPDF(source="{caminho}")'

    def show(self) -> None:
        """ Open PDF in default OS application """
        
        startfile(self.__path)
        
    @staticmethod
    def get_file_name() -> str:
        path = filedialog.askopenfilename()
        return path

if __name__ == '__main__':
    from time import time

    path = BoletoPDF.get_file_name()
    
    x0 = time()
    b = BoletoPDF(path)
    
    print('Ticket Value:', b.ticket_value(allow_OCR=True))
    x0 = time()-x0
    print('Time:', round(x0, 2), 's')
    print('Extraction Mode:', b.last_extraction_mode)

    input('Exit...')
