from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from app.database import get_db_session
from app.schemas.user_entity import UserEntity
from app.schemas.group_entity import GroupEntity
from app.schemas import schema
from app import pwd_utils, configs
import json
from asyncio import run
from app.cachedata import Cache, logging


router = APIRouter()
@router.get("/lookup/agent")
def get_agent_all(db_session: Session = Depends(get_db_session), pageNo: int|None = 1, pageSize: int|None = 5, totalRec: int|None = 0): 
    if (pageNo==-1 and pageSize==-1 and totalRec==-1):
        agents = db_session.query(UserEntity).order_by("login")
        for a in agents:
            a.password = "?"
        return agents.all()  
    ################
    if (totalRec==0):
        totalRec= db_session.query(UserEntity).count()
    LIMIT:  int = pageSize
    OFFSET: int = (pageNo-1) * LIMIT  
    agents = db_session.query(UserEntity).order_by("login").offset(OFFSET).limit(LIMIT)
    for a in agents:
        a.password = "?"
    return {"totalRec": totalRec, "list": agents.all()}   

@router.get("/lookup/agent/{agent_id}")
def get_agent_byid(agent_id: int, db_session: Session = Depends(get_db_session)): 
    _user = db_session.query(UserEntity).filter( UserEntity.agent_id==agent_id ).first()
    if not _user:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message" : "Not found"})
    _user.password = "?"    
    return _user   

@router.post("/lookup/agent")
def update_agent(user: schema.User, db_session: Session = Depends(get_db_session) ):
    maxid = db_session.query(func.max(UserEntity.agent_id)).scalar()
    try:
        _user = UserEntity()
        _user.agent_id  = maxid+1
        _user.first_name= user.first_name
        _user.last_name = user.last_name
        _user.login     = user.login
        _user.password  = "?" #pwd_utils.gen_password( user.password )
        _user.level_id  = user.level_id
        _user.group_id  = user.group_id
        _user.is_active = 1
        db_session.add(_user)
        db_session.commit()
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message" : str(e)})   
    user.agent_id = maxid+1     
    return user 

@router.get("/lookup/group")
def get_group_all(db_session: Session = Depends(get_db_session)): 
    groups = db_session.query(GroupEntity).order_by("name")
    return groups.all()    




@router.get("/lookup/ssimkey")
def get_ssimkey(db_session: Session = Depends(get_db_session)):
    from ii.am.ticket import TicketEngine2 # type: ignore
    ticketEngine2 = TicketEngine2(configs.info["db_host"], configs.info["db_user"], configs.info["db_pass"], configs.info["db_name"])    
    _json = str(ticketEngine2.ssimGenTree())
    try:
        return json.loads(_json)
    except Exception as e:    
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error" : str(e)})    

@router.get("/lookup/system")
def get_system_all(db_session: Session = Depends(get_db_session)): 
    datalist: list = list()
    cmd = "select system_id, description, need_day, need_hr from system_guide where is_active=1 order by description"
    rows = db_session.execute(text(cmd))
    for row in rows:
        datalist.append( row._asdict() )
    return datalist

@router.post("/lookup/system")
def update_system(ssim: schema.Ssim, db_session: Session = Depends(get_db_session)):  
    result: dict = {}  
    cmdUp = "update system_guide set description='"+ ssim.description +"', need_day='"+ str(ssim.need_day) +"', need_hr='"+ str(ssim.need_hr) +"' where system_id=" + str(ssim.system_id)
    cmdMx = "select max(system_id) as max from system_guide"
    cmdIn = "insert into system_guide (system_id, description, need_day, need_hr, is_active) values ('#MAXID', '"+ ssim.description +"', '"+ str(ssim.need_day) +"', '"+ str(ssim.need_hr) +"', '1')"
    cmdUpResult = db_session.execute(text(cmdUp)) 
    print(cmdUp + " ["+ str(cmdUpResult.rowcount) +"]")
    if (cmdUpResult.rowcount == 0):
        cmdMxresult = db_session.execute(text(cmdMx)) 
        maxID = 0
        for rs in cmdMxresult: 
            if (rs[0] != None):
                maxID = rs[0]
        cmdIn = cmdIn.replace("#MAXID", str(maxID+1))
        cmdInResult = db_session.execute(text(cmdIn)) 
        result = {"operation": "insert", "affect": maxID+1}  
    else:
        result = {"operation": "update", "affect": cmdUpResult.rowcount}  
    db_session.commit()
    return result

@router.get("/lookup/subsystem/{system_id}")
def get_subsystem(system_id: int, db_session: Session = Depends(get_db_session)): 
    datalist: list = list()
    cmd = "select subsystem_id, description, need_day, need_hr from subsystem_guide where system_id='"+ str(system_id) +"' and is_active=1 order by description"
    rows = db_session.execute(text(cmd))
    for row in rows:
        datalist.append( row._asdict() )
    return datalist

@router.post("/lookup/subsystem")
def update_subsystem(ssim: schema.Ssim, db_session: Session = Depends(get_db_session)):  
    if (ssim.system_id == 0):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message" : "system_id required"})  
    result: dict = {}  
    cmdUp = "update subsystem_guide set description='"+ ssim.description +"', need_day='"+ str(ssim.need_day) +"', need_hr='"+ str(ssim.need_hr) +"' where system_id="+ str(ssim.system_id) +" and subsystem_id=" + str(ssim.subsystem_id)
    cmdMx = "select max(subsystem_id) as max from subsystem_guide where system_id=" + str(ssim.system_id)
    cmdIn = "insert into subsystem_guide (subsystem_id, description, need_day, need_hr, is_active, system_id) values ('#MAXID', '"+ ssim.description +"', '"+ str(ssim.need_day) +"', '"+ str(ssim.need_hr) +"', '1', '"+ str(ssim.system_id) +"')"
    cmdUpResult = db_session.execute(text(cmdUp)) 
    print(cmdUp + " ["+ str(cmdUpResult.rowcount) +"]")
    if (cmdUpResult.rowcount == 0):
        cmdMxresult = db_session.execute(text(cmdMx)) 
        maxID = 0
        for rs in cmdMxresult: 
            if (rs[0] != None):
                maxID = rs[0]
        cmdIn = cmdIn.replace("#MAXID", str(maxID+1))
        cmdInResult = db_session.execute(text(cmdIn)) 
        result = {"operation": "insert", "affect": maxID+1}  
    else:
        result = {"operation": "update", "affect": cmdUpResult.rowcount}  
    db_session.commit()
    return result       

@router.get("/lookup/item/{system_id}/{subsystem_id}")
def get_item(system_id: int, subsystem_id: int, db_session: Session = Depends(get_db_session)): 
    datalist: list = list()
    cmd = "select item_id, description, need_day, need_hr from item_guide where system_id='"+ str(system_id) +"' and subsystem_id='"+ str(subsystem_id) +"' and is_active=1 order by description"
    rows = db_session.execute(text(cmd))
    for row in rows:
        datalist.append( row._asdict() )
    return datalist

@router.post("/lookup/item")
def update_item(ssim: schema.Ssim, db_session: Session = Depends(get_db_session)):  
    if (ssim.system_id==0 or ssim.subsystem_id==0):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message" : "system_id, subsystem_id required"})  
    result: dict = {}  
    cmdUp = "update item_guide set description='"+ ssim.description +"', need_day='"+ str(ssim.need_day) +"', need_hr='"+ str(ssim.need_hr) +"' where system_id="+ str(ssim.system_id) +" and subsystem_id=" + str(ssim.subsystem_id) + " and item_id=" + str(ssim.item_id)
    cmdMx = "select max(item_id) as max from item_guide where system_id=" + str(ssim.system_id) + " and subsystem_id=" + str(ssim.subsystem_id)
    cmdIn = "insert into item_guide (item_id, description, need_day, need_hr, is_active, system_id, subsystem_id) values ('#MAXID', '"+ ssim.description +"', '"+ str(ssim.need_day) +"', '"+ str(ssim.need_hr) +"', '1', '"+ str(ssim.system_id) +"', '"+ str(ssim.subsystem_id) +"')"
    cmdUpResult = db_session.execute(text(cmdUp)) 
    print(cmdUp + " ["+ str(cmdUpResult.rowcount) +"]")
    if (cmdUpResult.rowcount == 0):
        cmdMxresult = db_session.execute(text(cmdMx)) 
        maxID = 0
        for rs in cmdMxresult: 
            if (rs[0] != None):
                maxID = rs[0]
        cmdIn = cmdIn.replace("#MAXID", str(maxID+1))
        cmdInResult = db_session.execute(text(cmdIn)) 
        result = {"operation": "insert", "affect": maxID+1}  
    else:
        result = {"operation": "update", "affect": cmdUpResult.rowcount}  
    db_session.commit()
    return result

@router.get("/lookup/module/{system_id}/{subsystem_id}/{item_id}")
def get_module(system_id: int, subsystem_id: int, item_id: int, db_session: Session = Depends(get_db_session)): 
    datalist: list = list()
    cmd = "select module_id, description, need_day, need_hr from module_guide where system_id='"+ str(system_id) +"' and subsystem_id='"+ str(subsystem_id) +"' and item_id='"+ str(item_id) +"' and is_active=1 order by description"
    rows = db_session.execute(text(cmd))
    for row in rows:
        datalist.append( row._asdict() )
    return datalist    

@router.post("/lookup/module")
def update_module(ssim: schema.Ssim, db_session: Session = Depends(get_db_session)):  
    if (ssim.system_id==0 or ssim.subsystem_id==0 or ssim.item_id==0):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message" : "system_id, subsystem_id, item_id required"})  
    result: dict = {}  
    cmdUp = "update module_guide set description='"+ ssim.description +"', need_day='"+ str(ssim.need_day) +"', need_hr='"+ str(ssim.need_hr) +"' where system_id="+ str(ssim.system_id) +" and subsystem_id=" + str(ssim.subsystem_id) + " and item_id=" + str(ssim.item_id) + " and module_id=" + str(ssim.module_id)
    cmdMx = "select max(module_id) as max from module_guide where system_id=" + str(ssim.system_id) + " and subsystem_id=" + str(ssim.subsystem_id) + " and item_id=" + str(ssim.item_id)
    cmdIn = "insert into module_guide (module_id, description, need_day, need_hr, is_active, system_id, subsystem_id, item_id) values ('#MAXID', '"+ ssim.description +"', '"+ str(ssim.need_day) +"', '"+ str(ssim.need_hr) +"', '1', '"+ str(ssim.system_id) +"', '"+ str(ssim.subsystem_id) +"', '"+ str(ssim.item_id) +"')"
    cmdUpResult = db_session.execute(text(cmdUp)) 
    print(cmdUp + " ["+ str(cmdUpResult.rowcount) +"]")
    if (cmdUpResult.rowcount == 0):
        cmdMxresult = db_session.execute(text(cmdMx)) 
        maxID = 0
        for rs in cmdMxresult: 
            if (rs[0] != None):
                maxID = rs[0]
        cmdIn = cmdIn.replace("#MAXID", str(maxID+1))
        cmdInResult = db_session.execute(text(cmdIn)) 
        result = {"operation": "insert", "affect": maxID+1}  
    else:
        result = {"operation": "update", "affect": cmdUpResult.rowcount}  
    db_session.commit()
    return result




@router.get("/lookup/priority_level")
def get_priority(db_session: Session = Depends(get_db_session)): 
    prioritys = run( Cache.getPrioritys(db_session) )
    return prioritys   

@router.get("/lookup/severity_level")
def get_severity(db_session: Session = Depends(get_db_session)): 
    severitys = run( Cache.getSeveritys(db_session) )
    return severitys    

@router.get("/lookup/call_code")
def get_callcode(db_session: Session = Depends(get_db_session)): 
    callcodes = run( Cache.getCallcodes(db_session) )
    return callcodes       
    

@router.get("/lookup/hd_alert_config")
def get_alert_config(db_session: Session = Depends(get_db_session)): 
    hd_alert_config = run( Cache.getHdAlertConfig(db_session) )
    return hd_alert_config    

@router.get("/lookup/hd_system_config")
def get_system_config(db_session: Session = Depends(get_db_session)): 
    hd_system_config = run( Cache.getHdSystemConfig(db_session) )
    return hd_system_config

@router.get("/lookup/problem_status")
def get_problem_status(db_session: Session = Depends(get_db_session)): 
    problem_status = run( Cache.getProblemStatus(db_session) )
    return problem_status  

@router.get("/lookup/rule_ticket_info")
def get_ruleticket_info(db_session: Session = Depends(get_db_session)): 
    rule_ticket_info = run( Cache.getRuleTicketInfo(db_session) )
    return rule_ticket_info 

@router.get("/lookup/ticket_right")
def get_ticket_right(db_session: Session = Depends(get_db_session)): 
    ticket_right = run( Cache.getTicketRight(db_session) )
    return ticket_right     