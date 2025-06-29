from asyncio import run
from fastapi import FastAPI, Request
from app import api_router1, configs, pwd_utils
from fastapi.staticfiles import StaticFiles
from app.cachedata import Cache, logging
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
@app.get("/hello")
def hello():
    #from asyncio import run
    #x= run( Cache.get_count() )
    #print(x)
    logging("Hello.....")
    return configs.info 

@app.get("/webks/mock_data")
def mock_data(wording: str = ""):
    mock_data = run( Cache.getMockData() )
    if (wording==""):
        return mock_data

    _wording = wording.lower()
    new_data = []
    for data in mock_data:
        _fname = data["first_name"].lower()
        if len(wording)>1 and _fname.startswith(_wording) :
            if len(new_data)>10:
                break
            else:
                new_data.append(data)  
    if len(new_data)>10:
        return new_data            

    for data in mock_data:
        _fname = data["first_name"].lower()
        if len(wording)>1 and _fname.startswith( _wording )==False and _wording in _fname :
            if len(new_data)>10:
                break
            else:
                new_data.append(data)
    return new_data




##################
appname = "/webks"
app.mount(appname+"/public", StaticFiles(directory="public",html=True), name="public")
app.mount(appname+"/page",   StaticFiles(directory="page"  ,html=True), name="page")
app.include_router(api_router1.router, prefix=appname+"/v1")    

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], #allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


"""
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
@app.get("/enpwd") ##for-test## /enpwd?pwd=xxxx
def enpwd(pwd:str|None = None):
    if (pwd == None or pwd == "") :
        return "??????"
    else :   
        return pwd_context.hash(pwd)    
"""


import json
@app.post("/test")
async def test(request: Request) :
    #cmd = "select to_char(open_date, 'yyyy-mm') from problems where ticket_id=" + str(ticket_id)
    #open_date = db_session.execute(text(cmd)).scalar()
    #pathlib.Path('D:/WorkSpace2/Python/webks/webks-api/upload/aa/bb').mkdir(parents=True, exist_ok=True)
    #cmd = "select max(seq_id) as i from hd_attachment where ticket_id=" + str(ticket_id)
    #cmd = "select max(ticket_id) as i from problems"
    #i = db_session.execute(text(cmd)).scalar()
    _json = json.loads(await request.body())
    print(_json)
    return "OK"