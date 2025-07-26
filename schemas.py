from pydantic import BaseModel

class UserMessage(BaseModel):
    phone: str
    trigger: str = None
    response: str = None
    message: str = None

class CRMUpdate(BaseModel):
    phone: str
    field: str
    value: str

class MemoryUpdate(BaseModel):
    phone: str
    key: str
    value: str
