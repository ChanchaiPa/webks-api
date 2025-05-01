from fastapi import APIRouter, Request, status, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from typing import Annotated, List
from asyncio import run
from sqlalchemy import text
from sqlalchemy.orm import Session
from app import configs
from app.app_utils import _Utils
from app.schemas import schema
from app.cachedata import Cache, logging
from app.database import get_db_session
import json
from pathlib import Path
from datetime import datetime

from jpype import  JClass, JPackage, isJVMStarted, startJVM, shutdownJVM, getDefaultJVMPath, java, imports
if not isJVMStarted():
    startJVM(convertStrings=False, classpath=[configs.info["jarpath"]])
imports.registerDomain('ii.am.ticket') 


router = APIRouter()
@router.post("/ticket/onhand")
def onhand(request: Request, searchCond: schema.SearchCond): 
    agent_id: int = _Utils.toInt(request.state.agent_id)
    #return {"Ticket": "Onhand"}
    from ii.am.ticket import TicketEngine # type: ignore
    ticketEngine = TicketEngine(configs.info["db_host"], configs.info["db_user"], configs.info["db_pass"], configs.info["db_name"])
    _json = str(ticketEngine.ticketOnhand(searchCond.pageNo, searchCond.pageSize, searchCond.totalRec, agent_id))
    try:
        return json.loads(_json)
    except Exception as e:    
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error" : str(e)})


@router.post("/ticket/inproc")
def inproc(request: Request, searchCond: schema.SearchCond): 
    agent_id: int = _Utils.toInt(request.state.agent_id)
    from ii.am.ticket import TicketEngine # type: ignore
    ticketEngine = TicketEngine(configs.info["db_host"], configs.info["db_user"], configs.info["db_pass"], configs.info["db_name"])
    _json = str(ticketEngine.ticketInProcessing(searchCond.pageNo, searchCond.pageSize, searchCond.totalRec, agent_id))
    try:
        return json.loads(_json)
    except Exception as e:    
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error" : str(e)})


@router.get("/ticket/create")
def create(request: Request, db_session: Session = Depends(get_db_session)): 
    agent_id: int = _Utils.toInt(request.state.agent_id)
    group_id: int = _Utils.toInt(request.state.group_id)    
    sysconfig = run( Cache.getHdSystemConfig(db_session) )

    from ii.am.ticket import TicketEngine # type: ignore
    ticketEngine = TicketEngine(configs.info["db_host"], configs.info["db_user"], configs.info["db_pass"], configs.info["db_name"])
    _json = str(ticketEngine.newTicket( sysconfig["def_call_code"], sysconfig["def_severity_level"], sysconfig["def_priority_level"], sysconfig["def_system_code"], agent_id, group_id ))
    try:
        return json.loads(_json)
    except Exception as e:    
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error" : str(e)})


@router.post("/ticket/update")
def update(ticket: schema.Ticket, request: Request): 
    from ii.am.ticket import TicketEngine # type: ignore
    ticketEngine = TicketEngine(configs.info["db_host"], configs.info["db_user"], configs.info["db_pass"], configs.info["db_name"])
    print("============")
    print(str(ticket.model_dump()))
    _json = str(ticketEngine.updateTicket( str(ticket.model_dump()) ))
    try:
        return json.loads(_json)
    except Exception as e:    
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error" : str(e)})
    

@router.get("/ticket/content/{ticket_id}")
def content(request: Request, ticket_id: int): 
    agent_id: int = _Utils.toInt(request.state.agent_id)
    from ii.am.ticket import TicketEngine # type: ignore
    ticketEngine = TicketEngine(configs.info["db_host"], configs.info["db_user"], configs.info["db_pass"], configs.info["db_name"])
    _json = str(ticketEngine.getTicket( ticket_id, agent_id ))
    try:
        return json.loads(_json)
    except Exception as e:    
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error" : str(e)})    


@router.post("/ticket/reminder")    
def cal_reminder(ssim: schema.Ssim):
    from ii.am.ticket import TicketEngine2 # type: ignore
    print(ssim)
    ticketEngine2 = TicketEngine2(configs.info["db_host"], configs.info["db_user"], configs.info["db_pass"], configs.info["db_name"])
    _json = str(ticketEngine2.reminderInfo( ssim.system_id, ssim.subsystem_id, ssim.item_id, ssim.module_id, ssim.description ))     #description is open_date
    try:
        return json.loads(_json)
    except Exception as e:    
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error" : str(e)})  


@router.post("/ticket/transfer")
async def transfer(request: Request):
    agent_id: int = _Utils.toInt(request.state.agent_id)
    _json = json.loads(await request.body())
    from ii.am.ticket import TicketEngine # type: ignore
    ticketEngine = TicketEngine(configs.info["db_host"], configs.info["db_user"], configs.info["db_pass"], configs.info["db_name"])    
    result = ticketEngine.transferTicket(agent_id, str(_json))
    return result


@router.get("/ticket/takeowner/{ticket_id}")
def takeowner(request: Request, ticket_id: int): 
    agent_id: int = _Utils.toInt(request.state.agent_id)
    from ii.am.ticket import TicketEngine # type: ignore
    ticketEngine = TicketEngine(configs.info["db_host"], configs.info["db_user"], configs.info["db_pass"], configs.info["db_name"])
    result = str(ticketEngine.takeOwnerTicket( ticket_id, agent_id )) # 'Success' or 'Currenty Take Owner by=x'
    print("=====" + str(result))
    if (result!="Success"):
        return JSONResponse(status_code=status.HTTP_304_NOT_MODIFIED, content={"reason" : result})
    else:
        _json = str(ticketEngine.getTicket( ticket_id, agent_id ))
        try:
            return json.loads(_json)
        except Exception as e:    
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error" : str(e)})  
        

@router.get("/ticket/close/{ticket_id}")
def close(ticket_id: int):
    from ii.am.ticket import TicketEngine # type: ignore
    ticketEngine = TicketEngine(configs.info["db_host"], configs.info["db_user"], configs.info["db_pass"], configs.info["db_name"])
    ticketEngine.closeTicket( ticket_id )
    _json = str(ticketEngine.getTicket( ticket_id, 0 ))
    return json.loads(_json)


@router.get("/ticket/void/{ticket_id}")
def void(ticket_id: int):
    from ii.am.ticket import TicketEngine # type: ignore
    ticketEngine = TicketEngine(configs.info["db_host"], configs.info["db_user"], configs.info["db_pass"], configs.info["db_name"])
    ticketEngine.voidTicket( ticket_id )
    _json = str(ticketEngine.getTicket( ticket_id, 0 ))
    return json.loads(_json)




###################################################
@router.get("/ticket/attachment/{ticket_id}")
def attachfile(ticket_id: int, db_session: Session = Depends(get_db_session)):
    datalist: list = list()
    cmd = "select seq_id, file_name, file_type, file_size, to_char(create_date, 'DD-MM-YYYY HH24:MI') as create_date, create_user_id from hd_attachment where ticket_id='"+ str(ticket_id) +"' and is_active=1 order by seq_id"
    rows = db_session.execute(text(cmd))
    for row in rows:
        datalist.append( row._asdict() )
    return datalist

from asyncio import run
@router.post("/ticket/upload/{ticket_id}")
async def uploadfile(request: Request, db_session: Session = Depends(get_db_session), ticket_id: int=0, files: List[UploadFile]|None = File(...)):
    if (ticket_id==0 or files==None):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message" : "Not found input"})

    cmd1 = "select to_char(open_date, 'yyyy-mm') from problems where ticket_id=" + str(ticket_id)
    open_date  = db_session.execute(text(cmd1)).scalar()
    uploadpath = configs.info["uploadpath"] +'/'+ open_date +'/'+  str(ticket_id)
    Path(uploadpath).mkdir(parents=True, exist_ok=True)
    logging("[Upload] Create Path " + uploadpath)

    cmd2 = "select max(seq_id) as i from hd_attachment where ticket_id=" + str(ticket_id)
    i = db_session.execute(text(cmd2)).scalar()
    if (i == None):
        i = 0
    logging("[Upload] " + cmd2 + "  ["+ str(i) +"]")
    agent_id = request.state.agent_id
    current  =_Utils.formatDateTime(datetime.now(), "%d-%m-%Y %H:%M:%S")

    for file in files:
        i = i+1
        fileName = file.filename
        fileType = fileName[fileName.rindex(".")+1 :].lower()
        newfName = str(ticket_id) + "_" + str(i) + "." + fileType
        fileSize = file.size        
        try:
            #pathObjc = Path(uploadpath +"/"+ newfName)
            #with pathObjc.open("wb") as buffer: shutil.copyfileobj(await file.read(), buffer)
            #with open(uploadpath +"/"+ newfName, "wb+") as file_object: file_object.write(await file.read())
            with open(uploadpath +"/"+ newfName, "wb+") as file_object: 
                while contents := await file.read(1024 * 1024): 
                    file_object.write(contents) 
            cmd3 = "insert into hd_attachment (ticket_id, seq_id, file_name, file_type, create_date, create_user_id, file_size, is_active) values "
            cmd3 = cmd3 + "('"+str(ticket_id)+"', '"+str(i)+"', '"+fileName+"', '"+fileType+"', TO_TIMESTAMP('"+current+"', 'DD-MM-YYYY HH24:MI:SS'), '"+ str(agent_id) +"', '"+_Utils.byte_to_human_read(fileSize)+"', '1')"
            logging(cmd3)
            db_session.execute(text(cmd3))
        except Exception as e: 
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error" : str(e)})

    db_session.commit()
    return "Success"

@router.get("/ticket/download/{ticket_id}/{seq_id}")
def downloadfile(ticket_id: int, seq_id: int, db_session: Session = Depends(get_db_session)):
    cmd1 = "select to_char(open_date, 'yyyy-mm') from problems where ticket_id=" + str(ticket_id)
    open_date  = db_session.execute(text(cmd1)).scalar()
    uploadpath = configs.info["uploadpath"] +'/'+ open_date +'/'+  str(ticket_id)

    file_name = ""
    file_type = ""
    cmd = "select file_name, file_type from hd_attachment where ticket_id='"+ str(ticket_id) +"' and seq_id='"+ str(seq_id) +"'"
    rows = db_session.execute(text(cmd))
    for row in rows:
        data = row._asdict()
        file_name = data["file_name"]
        file_type = data["file_type"]
    if (file_name=="" or file_type==""): 
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message" : "Not found data"})  

    downloadfile = uploadpath + "/" + str(ticket_id)+"_"+str(seq_id)+"."+file_type
    return FileResponse(downloadfile, media_type='application/octet-stream',filename=file_name) 



###################################################
@router.get("/ticket/inbox")
def inbox(request: Request): 
    agent_id: int = _Utils.toInt(request.state.agent_id)
    from ii.am.ticket import TicketEngine2 # type: ignore
    ticketEngine2 = TicketEngine2(configs.info["db_host"], configs.info["db_user"], configs.info["db_pass"], configs.info["db_name"])    
    _json = str(ticketEngine2.getInBox(agent_id))  
    print(_json)  
    try:
        return json.loads(_json)
    except Exception as e:    
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error" : str(e)})  

@router.get("/ticket/outbox")
def outbox(request: Request, pageNo: int|None = 1, pageSize: int|None = 5, totalRec: int|None = 0): 
    agent_id: int = _Utils.toInt(request.state.agent_id)
    from ii.am.ticket import TicketEngine2 # type: ignore
    ticketEngine2 = TicketEngine2(configs.info["db_host"], configs.info["db_user"], configs.info["db_pass"], configs.info["db_name"])    
    _json = str(ticketEngine2.getOutBox(agent_id, pageNo, pageSize, totalRec))    
    try:
        return json.loads(_json)
    except Exception as e:    
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error" : str(e)})  
    


@router.post("/ticket/tracking")
def tracking(request: Request, param: schema.TrackingParam): 
    agent_id: int = _Utils.toInt(request.state.agent_id)
    level_id: int = _Utils.toInt(request.state.level_id) 
    group_id: int = _Utils.toInt(request.state.group_id)  

    from ii.am.ticket import TicketEngine # type: ignore
    ticketEngine = TicketEngine(configs.info["db_host"], configs.info["db_user"], configs.info["db_pass"], configs.info["db_name"])    
    _json = str(ticketEngine.ticketTracking(str(param.model_dump()), agent_id, level_id, group_id))    
    try:
        return json.loads(_json)
    except Exception as e:    
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error" : str(e)})    

