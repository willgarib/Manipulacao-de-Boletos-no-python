class Support():

    @staticmethod
    def is_value(x) -> bool:
        try:
            float(x)
        except:
            return False
        return True
        
    @staticmethod
    def truncate(number: float, ndigits: int) -> float:
        temp = pow(10, ndigits)
        return int(number * temp)/ temp
