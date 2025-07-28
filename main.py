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
    appPath = AppPath()
    logging("Hello....." + appPath.get_path())
    return configs.info 



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

"""
@app.get("/test")
async def test(request: Request) :
    #cmd = "select to_char(open_date, 'yyyy-mm') from problems where ticket_id=" + str(ticket_id)
    #open_date = db_session.execute(text(cmd)).scalar()
    #pathlib.Path('D:/WorkSpace2/Python/webks/webks-api/upload/aa/bb').mkdir(parents=True, exist_ok=True)
    #cmd = "select max(seq_id) as i from hd_attachment where ticket_id=" + str(ticket_id)
    #cmd = "select max(ticket_id) as i from problems"
    #i = db_session.execute(text(cmd)).scalar()
    #_json = json.loads(await request.body())
    #print(_json)
    return "OK"
"""


from inspect import getfile
import os
class AppPath:
    def get_path(self):
        path = f"{os.path.dirname(getfile(self.__class__))}"
        return path