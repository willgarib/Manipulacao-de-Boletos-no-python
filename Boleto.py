from pypdfium2 import PdfDocument
from io import BufferedReader, BufferedRandom, SEEK_END
from typing import Union, Iterable, Literal
from warnings import warn
import numpy as np
import re
from Support import Support


class Boleto:
    flag_type = Literal['left', 'right', 'top', 'bottom', '1-quadrant', '2-quadrant', '3-quadrant', '4-quadrant']
    def __init__(
        self,
        source: Union[BufferedReader, BufferedRandom],
        password: str = None):
        self.__read = PdfDocument(source, password, True)
        self.__repr = str(source)
        self.__size = Boleto.get_size(source)
        self.__extraction_mode = None
        
    def __len__(self) -> int:
        return len(self.__read)
    
    def __repr__(self) -> str:
        return f'Boleto(source={repr(self.__repr)})'
    
    def __getitem__(self, index):
        return self.__read[index]
    
    @property
    def size(self) -> tuple:
        return self.__read[0].get_size()
        
    @property
    def file_size(self) -> float:
        """ Returns the file size in Mega bytes """
        return self.__size
    
    @property
    def last_extraction_mode(self) -> Union[str, None]:
        """ Indicates the method of the last attempt to extract the text from the billet 
        
            Returns 'None' if not even an attempt was made"""
        return self.__extraction_mode
        
    @staticmethod
    def get_size(source: Union[BufferedReader, BufferedRandom]) -> float:
        pos = source.tell()
        source.seek(0, SEEK_END)
        size = source.tell()
        source.seek(pos) # Back to where we were
        return size / pow(1024, 2)
    
    def __check_text(text: str) -> bool:
        if text == '': return False
        
        lenth = len(text)
        text = np.array(list(text), dtype=str)
        text = np.vectorize(ord)(text)
        errors = text[(text < 32) & (~np.isin(text, [9,10,12,13]))].shape[0]
        
        if errors / lenth >= 0.05: return False
        return True
    
    def __quadrants_coordinates(shape: tuple, reduction_percentage: float=0) -> dict:
        row_count, column_count = shape
        rp = reduction_percentage
        
        if rp < 0 or rp >= 0.5:
            info = 'The reduction percentage must be float, less than 0.5 and greater than 0 - percent in [0, 0.5)'
            raise ValueError(info)
        
        # Line Parameters
        sup_row = int(rp * row_count)
        inf_row = int((1-rp) * row_count)
        mid_row = row_count // 2
        
        # Column Parameters
        left_col = 0
        right_col = int(column_count)
        mid_col = int(column_count)
        
        output = {
            '1': (sup_row, mid_row, int((rp + 0.5) * mid_col), right_col),
            '2': (sup_row, mid_row, left_col, int((rp - 0.5) * mid_col)),
            '3': (mid_row, inf_row, left_col, int((rp - 0.5) * mid_col)),
            '4': (mid_row, inf_row, int((rp + 0.5) * mid_col), right_col)   
        }

        return output
    
    def __get_flag_location(flag: flag_type, size: tuple, percent: float = 0) -> tuple:
        flag_config = {
            'all':   (1,3,3,1),
            'left':  (2,3,2,2),
            'right': (1,4,1,1),
            'top':   (1,1,2,1),
            'bottom':(3,3,3,4),
            '1-quadrant': (1,1,1,1),
            '2-quadrant': (2,2,2,2),
            '3-quadrant': (3,3,3,3),
            '4-quadrant': (4,4,4,4)
        }
        
        try:
            config = flag_config[flag]
        except KeyError:
            info = f'Unrecognized flag. Possible values: {Boleto.flag_type}'
            raise ValueError(info)
        
        aux = Boleto.__quadrants_coordinates(size, percent)
        output = []
        
        for i, quadrant in enumerate(config):
            output.append(aux[str(quadrant)][i]) 
               
        return tuple(output)
    
    def __render_page(self, page: int = 0, scale: float = 1.5, grayscale: bool = False) -> np.ndarray:
        """ Render a specific ticket page"""
        
        render = self.__read[page].render(scale=scale, grayscale=grayscale)
        return render.to_numpy()
    
    def page_exist(self, page: Union[Iterable, int]):
        if type(page) == int: page = [page]
        for page_index in page:
            try: self[page_index]
            except: return False
        return True
    
    def render(
        self,
        page: int = 0,
        flag: flag_type = 'all',
        scale: float = 1,
        reduction_percentage: float = 0) -> np.ndarray:
        """ Render a specific ticket page"""

        # Render all peges
        image = self.__render_page(page, scale=scale, grayscale=True)
        row_count, column_count, _ = image.shape
        row_count -= 1; column_count -= 1
        
        # Flag Coordinates
        fc = Boleto.__get_flag_location(flag, (row_count, column_count), reduction_percentage)
        
        # image[ start_row : end_row, start_column : end_column ] 
        output = image[ fc[0] : fc[1], fc[2] : fc[3] ]
            
        return output
    
    def text(
        self,
        pages: Union[Iterable[int], None] = None,
        flag: flag_type = 'all',
        allow_OCR: bool = False,
        force_OCR: bool = False,
        reduction_percentage: float = 0
        ) -> str:
        """ Returns the text from a specific page. 
            If 'pages' is None returns the text of all pages """

        # Set pages
        if pages == None: pages = range(len(self))
        
        # Set allow OCR
        if force_OCR: allow_OCR = True
        
        output = []
        text = ''
        divide = '\n~-~-~\n~-~-~\n'
        use_ocr = False
        for page in pages:
            # Extract text without OCR (if 'force_OCR' is True 'check_text' will be false in the next condition)
            if not force_OCR:
                # Coordinates of flag
                size = self[page].get_size()[::-1]
                top, bottom, left, right = Boleto.__get_flag_location(
                    flag, size, reduction_percentage)
        
                text = self.__read[page].get_textpage()
                text = text.get_text_bounded(
                    left=left, bottom=bottom, right=right, top=top)
            
            # Control Variables
            check_text = Boleto.__check_text(text)
            
            # Extract text with OCR (if the default method failed)
            if not check_text and allow_OCR:
                global image_to_string
                global Image
                from pytesseract import image_to_string
                from PIL import Image
                
                img = self.render(page, flag, scale=4, reduction_percentage=reduction_percentage)
                img = np.reshape(img, (img.shape[0], img.shape[1]))
                img = Image.fromarray(img, mode='L').convert('RGB')
                
                text = image_to_string(img, lang='por', config='--psm 6')
                use_ocr = True
            
            # Append Text to the list
            output.append(text)
        
        output = divide.join(output)
                
        # Indicate whether the text was successfully extracted
        if not Boleto.__check_text(output):
                info = 'Failed to extract ticket text.'
                if not allow_OCR: info = info + ' Maybe using OCR can help'
                warn(info, stacklevel=2)
             
        self.__extraction_mode = 'Get_text'   
        if use_ocr: self.__extraction_mode += '/OCR'
        return output
    
    def __get_possible_values(text: str, pattern: Literal['br', 'us']) -> np.array:
        match pattern:
            case 'br':
                replace = { ".": "", ",": "." }
            case 'us':
                replace = { ",": "" }
            case _:
                return None
        # Replace characters to be in the pattern
        for key in replace.keys():
            text = text.replace(key, replace[key])
        
        # Extract numeric values
        regex = '(?:\.|,|[\d])*'
        values = np.array(re.findall(regex, text))
        values = values[values != '']
        
        # Remove possible code or numeric identifier in the list
        if values.shape[0] != 0:
            condicao1 = np.vectorize(Support.is_value)(values)
        else: condicao1 = False
        condicao2 = ~(np.char.isnumeric(values))
        
        # Convert all the possible values to float
        values = values[condicao1 & condicao2].astype(float)
        
        return values
        
    def ticket_value(
        self,
        page: Union[Iterable[int], None] = None,
        limitValue: float = 500000,
        allow_OCR: bool = False,
        ) -> Union[float, None]:
        
        """ Extract the ticket value from a PDF.
            
            Returns 'None' if not found """
            
        # Check if page exist
        if page != None and not self.page_exist(page):
            info = f'Pages ({page}) not found'
            raise IndexError(info)
        
        for force_OCR in [False, True]:
            # Checks if it has already been done with OCR
            if self.last_extraction_mode == 'Get_text/OCR' and force_OCR: break
            
            # Get the page
            text = self.text(page, flag='right', allow_OCR=allow_OCR, force_OCR=force_OCR, reduction_percentage=0.2)
                
            for pattern in ['br', 'us']:
                # Extracts all possible values
                valores = Boleto.__get_possible_values(text, pattern)
                valores = valores[valores <= limitValue] # Limiting the values ​​helps reduce errors

                # Choice the value as the largest among the possibilities
                try: valor = Support.truncate(np.max(valores), 2)
                except: continue
                
                return valor
        
        return None
