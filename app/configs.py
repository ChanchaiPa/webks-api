from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Configs(BaseSettings) :
    model_config = SettingsConfigDict(env_file='app/configs.env', env_file_encoding='utf-8')
    db_host: str = Field(alias='db_host')
    db_user: str = Field(alias='db_user')
    db_pass: str = Field(alias='db_pass')
    db_name: str = Field(alias='db_name')
    jarpath: str = Field(alias='jarpath')
    uploadpath: str = Field(alias='uploadpath')

info = Configs().model_dump()