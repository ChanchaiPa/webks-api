from pydantic import BaseModel, ConfigDict
from typing import Optional


class Login(BaseModel):
    username: str
    password: Optional[str] = None    

class User(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    agent_id: int
    login: str
    first_name: str
    last_name: Optional[str] = None
    level_id: int
    group_id: int
    is_active: int


class Ssim(BaseModel):
    system_id: Optional[int] = 0
    subsystem_id: Optional[int] = 0
    item_id: Optional[int] = 0
    module_id: Optional[int] = 0
    description: str
    need_day: int
    need_hr: int


class Ticket(BaseModel):
    ticket_id: int
    open_date: str
    add_user_id: int
    owner_id: int
    group_id: int
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    caller_name: Optional[str] = None
    caller_phoneno: Optional[str] = None
    system_id: Optional[int] = None
    subsystem_id: Optional[int] = None
    item_id: Optional[int] = None
    module_id: Optional[int] = None
    call_code: str
    severity_level: int
    priority_level: int
    reminder_date: str
    need_day: int
    need_hr: int
    problem_detail: Optional[str] = None
    resolved_detail: Optional[str] = None
    modified_date: str
    close_date: Optional[str] = None
    problem_status_id: int


class SearchCond(BaseModel):
    param1: Optional[str] = None
    param2: Optional[str] = None
    param3: Optional[str] = None
    param4: Optional[str] = None
    param5: Optional[str] = None
    param6: Optional[str] = None
    param7: Optional[str] = None
    param8: Optional[str] = None
    param9: Optional[str] = None
    pageNo: int
    pageSize: int
    totalRec: int


class TrackingParam(BaseModel):
    pageNo: int
    pageSize: int
    totalRec: int

    fr_open_date: str
    to_open_date: str
    ticket_id: str
    problem_status_id: int
    customer_id: str
    system_id: int
    subsystem_id: int
    item_id: int 