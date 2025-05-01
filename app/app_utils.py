from typing import Optional
from datetime import datetime
import math

class _Utils:

    @staticmethod
    def toInt(value: str, default: Optional[int]=0) -> int:
        try:
            return int(value)
        except Exception as e:
            print(e)
            if (default):
                return default
            else:
                return 0

    @staticmethod
    def toStr(value: str|None) -> str:
        if (value == None):
            return ""
        else:
            return value.strip()        
        


    @staticmethod
    def sqlValT(value :str|None) -> str:
        if (value == None or value == ""):
            return "Null"
        else:
            return "'"+value.replace("'", "").strip()+"'"
        
    @staticmethod
    def sqlValD(value :str|None) -> str:
        if (value == None or value == ""):
            return "Null"
        else:
            return value  



    @staticmethod
    def convertFormat(dt: str) -> str:  #2024-07-26 -> 26/06/2024
        #dt_ = dt.split("-")
        #return dt_[2] + "/" + dt_[1] + "/" + dt_[0] 
        return dt[8:10] + "/" + dt[5:7] + "/" +dt[0:4]   

    @staticmethod  
    def formatDateTime(dt: datetime, format: str) -> str:
        if (format == ""):
            format  = "%d/%m/%Y %H:%M:%S"
        return dt.strftime(format)
    
    @staticmethod  
    def parseDateTime(dt: str, format: str) -> datetime:
        if (format == ""):
            format  = "%d/%m/%Y %H:%M:%S"
        return datetime.strptime(dt, '%d/%m/%Y %H:%M:%S')   



    @staticmethod
    def byte_to_human_read(byte):
        if byte == 0:
            raise ValueError("Size is not valid.")
        byte = int(byte)
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        index = int(math.floor(math.log(byte, 1024)))
        power = math.pow(1024, index)
        size = round(byte / power, 2)
        return "{} {}".format(size, size_name[index])