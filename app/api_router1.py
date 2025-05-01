from fastapi import APIRouter, Depends
from app import api_authen, api_lookup, api_ticket, pwd_utils

router = APIRouter()
router.include_router(api_authen.router)
router.include_router(api_lookup.router, dependencies=[Depends(pwd_utils.checkAuthorized)])#    router.include_router(api_lookup.router)
router.include_router(api_ticket.router, dependencies=[Depends(pwd_utils.checkAuthorized)])#    router.include_router(api_ticket.router)