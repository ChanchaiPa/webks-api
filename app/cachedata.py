#from fastapi import Depends
import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from app import configs
from app.database import get_db_session
from aiocache import Cache

cache = Cache(Cache.MEMORY)
class Cache:    
    @staticmethod
    async def get_count(): #for test
        count = await cache.get("count", default=0)
        if (count==0):
            print("INIT count => 1")
            await cache.set("count", 1)
        else:
            print("count is {}".format(count))    
        return count    
    

    @staticmethod
    async def getPrioritys(db_session: Session):
        prioritys = await cache.get("prioritys", default=[])
        if (len(prioritys)==0):
            cmd = "select priority_level, description from priority_levels"
            rows = db_session.execute(text(cmd))
            for row in rows:
                prioritys.append( row._asdict() ) 
            logging(cmd + " ["+ str(len(prioritys)) +"]")
            await cache.set("prioritys", prioritys)                    
        return prioritys


    @staticmethod
    async def getSeveritys(db_session: Session):
        severitys = await cache.get("severitys", default=[])
        if (len(severitys)==0):
            cmd = "select severity_level, description from severity_levels"
            rows = db_session.execute(text(cmd))
            for row in rows:
                severitys.append( row._asdict() )
            logging(cmd + " ["+ str(len(severitys)) +"]")
            await cache.set("severitys", severitys)                  
        return severitys


    @staticmethod
    async def getCallcodes(db_session: Session):
        callcodes = await cache.get("callcodes", default=[]) 
        if (len(callcodes)==0):
            cmd = "select call_code, description from call_codes"
            rows = db_session.execute(text(cmd))
            for row in rows:
                callcodes.append( row._asdict() )
            logging(cmd + " ["+ str(len(callcodes)) +"]")  
            await cache.set("callcodes", callcodes)             
        return callcodes    


    @staticmethod
    async def getHdAlertConfig(db_session: Session):
        hd_alert_config = await cache.get("hd_alert_config", default=[]) 
        if (len(hd_alert_config)==0):
            cmd = "select * from hd_alert_config order by alert_id"
            rows = db_session.execute(text(cmd))
            for row in rows:
                hd_alert_config.append( row._asdict() )
            logging(cmd + " ["+ str(len(hd_alert_config)) +"]")  
            await cache.set("hd_alert_config", hd_alert_config)             
        return hd_alert_config  


    @staticmethod
    async def getHdSystemConfig(db_session: Session):
        hd_system_config = await cache.get("hd_system_config", default={}) 
        if (len(hd_system_config)==0):
            cmd = "select * from hd_system_config"
            rows = db_session.execute(text(cmd))
            for row in rows:
                hd_system_config = row._asdict()
            logging(cmd + " ["+ str(len(hd_system_config)) +"]")  
            await cache.set("hd_system_config", hd_system_config)             
        return hd_system_config  


    @staticmethod
    async def getProblemStatus(db_session: Session):
        problem_status = await cache.get("problem_status", default=[]) 
        if (len(problem_status)==0):
            cmd = "select problem_status_id, description from problem_status"
            rows = db_session.execute(text(cmd))
            for row in rows:
                problem_status.append( row._asdict() )
            logging(cmd + " ["+ str(len(problem_status)) +"]")  
            await cache.set("problem_status", problem_status)             
        return problem_status  


    @staticmethod
    async def getRuleTicketInfo(db_session: Session):
        rule_ticket_info = await cache.get("rule_ticket_info", default=[]) 
        if (len(rule_ticket_info)==0):
            cmd = "select field_name, mandatory, can_edit from rule_ticket_info"
            rows = db_session.execute(text(cmd))
            for row in rows:
                rule_ticket_info.append( row._asdict() )
            logging(cmd + " ["+ str(len(rule_ticket_info)) +"]")  
            await cache.set("rule_ticket_info", rule_ticket_info)             
        return rule_ticket_info    


    @staticmethod
    async def getTicketRight(db_session: Session):
        ticket_right = await cache.get("ticket_right", default=[]) 
        if (len(ticket_right)==0):
            cmd = "select * from ticket_right"
            rows = db_session.execute(text(cmd))
            for row in rows:
                ticket_right.append( row._asdict() )
            logging(cmd + " ["+ str(len(ticket_right)) +"]")  
            await cache.set("ticket_right", ticket_right)             
        return ticket_right  


    @staticmethod
    async def getMockData():
        mock_data = await cache.get("mock_data", default=[]) 
        if (len(mock_data)==0):
            print("READ===> public/MOCK_DATA.json")
            with open( "public/MOCK_DATA.json", 'r' ) as file:
                mock_data = json.load(file)
            await cache.set("mock_data", mock_data)             
        return mock_data  






import logging
import logging.handlers as handlers
import time

logger = logging.getLogger('webks')
logger.setLevel(logging.INFO)

logHandler = handlers.TimedRotatingFileHandler('./webksapi.log', when='M', interval=1)
logHandler.setLevel(logging.INFO)
logHandler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s]  %(message)s")
)
logger.addHandler(logHandler)

streamhandler = logging.StreamHandler()
streamhandler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s]  %(message)s")
)
logger.addHandler(streamhandler)

def logging(message: str):
    logger.info(message)